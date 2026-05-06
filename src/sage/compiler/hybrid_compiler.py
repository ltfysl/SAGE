"""Hybrid SAGE compiler — conservative, evidence-bound, adversarial-guarded.

Architecture:
  sentence → adversarial guard (block non-events)
           → sklearn classifier (op type)
           → if confidence low, semantic normalizer (with conservative threshold)
           → entity/value extraction
           → evidence strength scoring
           → if score < threshold, reject → NOOP
"""

from __future__ import annotations
import json, logging, re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sage.extraction.entity_extractor import EntityExtractor
from sage.extraction.sentence_splitter import split_sentences
from sage.compiler.semantic_normalizer import SemanticNormalizer
from sage.compiler.adversarial_guard import AdversarialGuard

logger = logging.getLogger(__name__)


@dataclass
class HybridCompilerConfig:
    """Configuration for the hybrid compiler."""
    normalizer_threshold: float = 0.72
    evidence_strength_threshold: float = 0.50
    adversarial_guard_enabled: bool = True
    require_entity_confidence: bool = True
    fallback_to_noop_on_uncertainty: bool = True
    allow_normalizer_for_adversarial_like_sentences: bool = False


class HybridSAGECompiler:
    """Conservative hybrid compiler with adversarial guard and evidence scoring."""

    def __init__(self, config: HybridCompilerConfig | None = None):
        self.config = config or HybridCompilerConfig()
        self.sklearn_compiler = None
        self.normalizer = SemanticNormalizer()
        self.extractor = EntityExtractor()
        self.guard = AdversarialGuard()
        self._loaded = False
        self.fallback_count = 0
        self.blocked_count = 0
        self.total_sentences = 0

    def load(self, sklearn_model_path: Path):
        from sage.baselines.sklearn_compiler import load_sklearn_compiler
        self.sklearn_compiler = load_sklearn_compiler(sklearn_model_path)
        self._loaded = True

    def predict_intent(self, sentence: str) -> tuple[str, float, str]:
        """Predict operation intent with adversarial guard.

        Returns (intent, confidence, source).
        """
        # ── Adversarial guard check ──
        if self.config.adversarial_guard_enabled:
            guard_result = self.guard.check(sentence)
            if guard_result["is_blocked"]:
                self.blocked_count += 1
                if not self.config.allow_normalizer_for_adversarial_like_sentences:
                    return ("NOOP", 1.0, "adversarial_guard")

        if self.sklearn_compiler is None:
            intent, conf = self.normalizer.predict_intent(sentence, threshold=self.config.normalizer_threshold)
            return (intent, conf, "normalizer")

        # Primary: sklearn classifier
        sklearn_label = self.sklearn_compiler.predict_label(sentence)

        # Normalizer check
        norm_intent, norm_conf = self.normalizer.predict_intent(sentence, threshold=self.config.normalizer_threshold)

        # Conservative mode: if sklearn says NOOP and normalizer confidence below threshold, keep NOOP
        if sklearn_label == "NOOP":
            if norm_conf < self.config.normalizer_threshold or norm_intent == "NOOP":
                return ("NOOP", 1.0, "sklearn")
            # Normalizer is confident — only fallback if config allows
            if self.config.fallback_to_noop_on_uncertainty:
                self.fallback_count += 1
                return (norm_intent, norm_conf, "normalizer")
            else:
                return ("NOOP", 1.0, "sklearn")

        # Sklearn is confident
        return (sklearn_label, 0.9, "sklearn")

    def score_evidence(self, op_type: str, sentence: str, person: str | None,
                       obj: str | None, val: int | None, from_p: str | None = None,
                       to_p: str | None = None) -> dict:
        """Score evidence strength for a candidate operation."""
        s = sentence
        s_lower = s.lower()
        scores = {
            "has_actor": person is not None and person.lower() in s_lower,
            "has_object": obj is not None and obj.lower() in s_lower,
            "has_value": val is not None and str(val) in s,
        }

        if op_type == "TRANSFER":
            scores["has_direction_cue"] = bool(
                re.search(r'\b(to|from|by|over to)\b', s_lower) or
                (from_p and from_p.lower() in s_lower) or
                (to_p and to_p.lower() in s_lower)
            )
        else:
            scores["has_direction_cue"] = True  # Not needed for non-TRANSFER

        scores["has_positive_event_verb"] = True  # If we got this far, intent was positive

        # Check for negation/hypothetical cues
        neg_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\s+longer\b',
                        r'\bwould\b', r'\bcould\b', r'\bmight\b',
                        r'\balmost\b', r'\bnearly\b',
                        r'\bwanted\s+to\b', r'\bplanned\s+to\b',
                        r'\bclaims?\b', r'\bsays?\b']
        scores["has_negation"] = any(re.search(p, s_lower) for p in neg_patterns)

        # Compute aggregate
        if op_type == "TRANSFER":
            key_fields = ["has_actor", "has_object", "has_value", "has_direction_cue", "has_positive_event_verb"]
        else:
            key_fields = ["has_actor", "has_object", "has_value", "has_positive_event_verb"]

        present = sum(1 for k in key_fields if scores.get(k, False))
        scores["score"] = present / len(key_fields) if key_fields else 0.0
        if scores["has_negation"]:
            scores["score"] *= 0.5  # Penalize negation

        return scores

    def compile(self, story_text: str) -> tuple[list[dict], bool]:
        """Compile a story with conservative evidence checks.

        Returns (ops_list, success).
        """
        if not self._loaded:
            raise RuntimeError("Hybrid compiler not loaded.")

        sentences = split_sentences(story_text)
        self.total_sentences += len(sentences)
        self.extractor.reset()
        ops = []
        success = True

        for sentence in sentences:
            intent, confidence, source = self.predict_intent(sentence)

            if intent == "NOOP":
                continue

            # ── Build candidate operation ──
            op = None
            person = obj = val = from_p = to_p = None

            if intent in ("SET", "ADD", "SUB"):
                person = self.extractor.extract_person(sentence)
                obj = self.extractor.extract_object(sentence)
                val = self.extractor.extract_value(sentence)

                # Hardened SET extraction: try harder for OOD patterns
                if person is None:
                    # Try: first capitalized word that's not a stop word
                    caps = re.findall(r'\b([A-Z][a-z]+)\b', sentence)
                    for c in caps:
                        if c.lower() not in {"question","how","what","many","does","is","was","were","after","everything"}:
                            person = c
                            break
                if obj is None and self.extractor._seen_objects:
                    obj = list(self.extractor._seen_objects)[0]
                if val is None:
                    # Try word numbers as last resort
                    word_nums = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
                    for w, n in word_nums.items():
                        if w in sentence.lower():
                            val = n
                            break

                if person and obj and val is not None:
                    start = story_text.find(sentence)
                    evidence = {"span": sentence, "start": max(0, start),
                               "end": start + len(sentence), "confidence": confidence}
                    op = {"op": intent, "target": f"{person}.{obj}",
                          "value": val, "evidence": evidence}

            elif intent == "TRANSFER":
                obj = self.extractor.extract_object(sentence)
                val = self.extractor.extract_value(sentence)
                from_p, to_p = self.extractor.extract_transfer_direction(sentence)

                # Flexible fallback for direction
                if from_p is None or to_p is None:
                    from_p, to_p = self.extractor.extract_direction_flexible(sentence)

                if obj and val is not None and from_p and to_p:
                    start = story_text.find(sentence)
                    evidence = {"span": sentence, "start": max(0, start),
                               "end": start + len(sentence), "confidence": confidence}
                    op = {"op": "TRANSFER", "from": f"{from_p}.{obj}",
                          "to": f"{to_p}.{obj}", "value": val, "evidence": evidence}

            elif intent == "QUERY":
                person, obj = self.extractor.extract_query_target(sentence)
                if person is None:
                    caps = re.findall(r'\b([A-Z][a-z]+)\b', sentence.replace("Question:", ""))
                    for c in caps:
                        if c.lower() not in {"question","how","what","many","does","is","was","were","after","everything"}:
                            person = c
                            break
                if obj is None and self.extractor._seen_objects:
                    obj = list(self.extractor._seen_objects)[0]
                elif obj is None:
                    obj = "coins"
                if person:
                    start = story_text.find(sentence)
                    evidence = {"span": sentence, "start": max(0, start),
                               "end": start + len(sentence), "confidence": confidence}
                    op = {"op": "QUERY", "target": f"{person}.{obj}",
                          "evidence": evidence}

            # ── Evidence strength check ──
            if op is not None and self.config.require_entity_confidence:
                ev_score = self.score_evidence(intent, sentence, person, obj, val, from_p, to_p)
                op["evidence_strength"] = ev_score
                if ev_score["score"] < self.config.evidence_strength_threshold:
                    if self.config.fallback_to_noop_on_uncertainty:
                        continue  # Reject weak evidence → NOOP
                    # Otherwise still accept but warn
                    logger.debug(f"Weak evidence ({ev_score['score']:.2f}): {sentence[:60]}")

            if op is not None:
                ops.append(op)
                # Track names/objects
                if person:
                    self.extractor._seen_names.add(person)
                if obj:
                    self.extractor._seen_objects.add(obj)
                if from_p:
                    self.extractor._seen_names.add(from_p)
                if to_p:
                    self.extractor._seen_names.add(to_p)
            elif intent == "QUERY":
                success = False

        return ops, success

    def reset_stats(self):
        self.fallback_count = 0
        self.blocked_count = 0
        self.total_sentences = 0

    @property
    def fallback_rate(self) -> float:
        if self.total_sentences == 0:
            return 0.0
        return self.fallback_count / self.total_sentences

    @property
    def block_rate(self) -> float:
        if self.total_sentences == 0:
            return 0.0
        return self.blocked_count / self.total_sentences
