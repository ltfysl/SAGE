"""Rule-based compiler for SAGE — evidence-bound, full template coverage.

Deterministic reference compiler that parses synthetic event-world stories
and converts known sentence patterns into JSON operation sequences with
evidence spans. Includes non-event detection for adversarial robustness.
"""

from __future__ import annotations

import re
import json
from typing import Any


# ── Object vocabulary ────────────────────────────────────────────

PLURAL_FORMS = [
    "coins", "books", "apples", "marbles", "cards", "candies",
    "pencils", "stickers", "cookies", "shells", "stones", "beads",
    "tokens", "berries", "seeds", "buttons", "keys", "rings",
    "pebbles", "leaves",
]

SINGULAR_FORMS = [
    "coin", "book", "apple", "marble", "card", "candy",
    "pencil", "sticker", "cookie", "shell", "stone", "bead",
    "token", "berry", "seed", "button", "key", "ring",
    "pebble", "leaf",
]

# Build canonical form lookup
SINGULAR_TO_PLURAL: dict[str, str] = {}
for i, plural in enumerate(PLURAL_FORMS):
    SINGULAR_TO_PLURAL[plural] = plural  # plural → self
    if i < len(SINGULAR_FORMS):
        SINGULAR_TO_PLURAL[SINGULAR_FORMS[i]] = plural  # singular → plural


# ── Non-event patterns (must be checked BEFORE event patterns) ───

NON_EVENT_PATTERNS = [
    re.compile(rf'\b(almost|nearly)\b', re.IGNORECASE),
    re.compile(rf'\b(wanted|planned|intended|meant|tried|hoped|wished)\s+to\b', re.IGNORECASE),
    re.compile(rf'\b(but\s+did\s+not|but\s+didn\'?t|but\s+never\s+did|but\s+changed\s+\w+\s+mind|but\s+kept\s+them)\b', re.IGNORECASE),
    re.compile(rf'\b(says?\s+\w+\s+has|claims?\s+to\s+have|thought\s+about)\b', re.IGNORECASE),
    re.compile(rf'\b(if\s+only|would\s+have|could\s+have)\b', re.IGNORECASE),
]

# ── Verb sets ─────────────────────────────────────────────────────

SET_VERBS = {"has", "owns", "holds", "possesses", "has exactly", "is holding"}
ADD_VERBS = {"finds", "discovers", "gains", "collects", "earns", "picks up"}
SUB_VERBS = {"spends", "uses", "consumes", "loses", "drops", "misplaces",
             "gives away", "parts with", "accidentally loses"}
GIVE_VERBS = {"gives", "hands", "passes", "offers", "transfers"}
RECEIVE_VERBS = {"receives", "gets", "takes", "is given"}
BUY_VERBS = {"buys", "purchases"}
SELL_VERBS = {"sells"}


class RuleCompiler:
    """Deterministic rule-based compiler with evidence and non-event detection."""

    NUMBER_RE = re.compile(r'\b(\d+)\b')
    NAME_RE = re.compile(r'\b([A-Z][a-z]+)\b')
    TO_RE = re.compile(r'\bto\s+([A-Z][a-z]+)')
    FROM_RE = re.compile(r'\bfrom\s+([A-Z][a-z]+)')
    BY_RE = re.compile(r'\bby\s+([A-Z][a-z]+)')
    FOR_RE = re.compile(r'\bfor\s+(\d+)\s+(\w+)')

    # Question words that are NOT person names
    QUESTION_STOP_WORDS = {"how", "what", "who", "which", "whose", "question",
                           "many", "does", "is", "are", "was", "were", "do",
                           "have", "has", "had", "now", "end", "up", "with",
                           "remain", "left", "holding", "possess", "count",
                           "final", "number", "exactly"}

    def compile(self, story_text: str) -> tuple[list[dict[str, Any]], bool]:
        """Compile a story into evidence-bound operations.

        Returns:
            (list of operation dicts, success flag).
        """
        sentences = self._split_sentences(story_text)
        known_names: set[str] = set()
        known_objects: set[str] = set()
        ops: list[dict[str, Any]] = []
        success = True

        for sentence in sentences:
            op_dict = self._parse_sentence(sentence, story_text, known_names, known_objects)
            if op_dict is not None:
                ops.append(op_dict)
                self._track_names_objects(op_dict, known_names, known_objects)
            elif sentence.strip().lower().startswith("question:"):
                success = False

        return ops, success

    # ── Sentence splitting ────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        raw = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in raw if s.strip()]

    # ── Evidence helper ───────────────────────────────────────────

    def _make_evidence(self, sentence: str, full_text: str) -> dict:
        """Build evidence dict from a sentence span in the full text."""
        start = full_text.find(sentence)
        if start == -1:
            # Fallback: try finding with stripped whitespace
            start = 0
            end = len(sentence)
        else:
            end = start + len(sentence)
        return {"span": sentence, "start": start, "end": end, "confidence": 1.0}

    # ── Name / object extraction ──────────────────────────────────

    def _track_names_objects(self, op: dict, names: set, objs: set):
        for key in ("target", "from", "to"):
            if key in op:
                parts = op[key].split(".", 1)
                if len(parts) == 2:
                    names.add(parts[0])
                    objs.add(parts[1])

    def _extract_name(self, text: str, known: set[str]) -> str | None:
        words = text.split()
        if words and words[0][0].isupper() and words[0].rstrip(".'\"").isalpha():
            return words[0].rstrip(".'\"")
        for name in sorted(known, key=len, reverse=True):
            if name in text:
                return name
        for m in self.NAME_RE.finditer(text):
            return m.group(1)
        return None

    def _extract_number(self, text: str) -> int | None:
        m = self.NUMBER_RE.search(text)
        return int(m.group(1)) if m else None

    def _extract_object(self, text: str, known: set[str]) -> str | None:
        text_lower = text.lower()
        # Build lookup: all forms → canonical plural
        lookup: dict[str, str] = dict(SINGULAR_TO_PLURAL)
        for obj in known:
            lookup[obj.lower()] = obj
        # Longest match first
        for form in sorted(lookup, key=len, reverse=True):
            if form in text_lower:
                return lookup[form]
        return None

    # ── Non-event check ───────────────────────────────────────────

    def _is_non_event(self, sentence: str) -> bool:
        """Return True if the sentence is a misleading non-event."""
        for pat in NON_EVENT_PATTERNS:
            if pat.search(sentence):
                return True
        return False

    # ── Top-level parser ──────────────────────────────────────────

    def _parse_sentence(self, sentence: str, full_text: str,
                        names: set[str], objs: set[str]) -> dict | None:
        s = sentence.strip()

        # Non-event check first
        if self._is_non_event(s):
            return None

        # Try each pattern
        for try_fn in [
            self._try_has, self._try_give, self._try_receive,
            self._try_spend, self._try_find, self._try_lose,
            self._try_buy, self._try_sell, self._try_question,
        ]:
            result = try_fn(s, full_text, names, objs)
            if result is not None:
                return result
        return None

    # ── Verb matching helper (word-boundary to avoid substring false positives) ──

    @staticmethod
    def _verb_matches(verb: str, s_lower: str) -> bool:
        """Check if a verb appears as a whole word/phrase in the sentence."""
        return bool(re.search(r'\b' + re.escape(verb) + r'\b', s_lower))

    # ── Pattern: HAS → SET ────────────────────────────────────────

    def _try_has(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in SET_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            name = self._extract_name(s, names)
            if name is None:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "SET", "target": f"{name}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: GIVE → TRANSFER ──────────────────────────────────

    def _try_give(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in GIVE_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            giver = self._extract_name(s, names)
            if giver is None:
                continue
            # Receiver: "to X" or indirect object "gives X N Y"
            receiver = None
            to_m = self.TO_RE.search(s)
            if to_m:
                receiver = to_m.group(1)
            else:
                # Check word after verb for indirect object
                words = s.split()
                for i, w in enumerate(words):
                    if w.lower() in GIVE_VERBS and i + 1 < len(words):
                        nxt = words[i + 1].rstrip(".'\"")
                        if nxt and nxt[0].isupper() and nxt.isalpha():
                            receiver = nxt
                            break
            if receiver is None or receiver == giver:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "TRANSFER", "from": f"{giver}.{obj}",
                "to": f"{receiver}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: RECEIVE → TRANSFER ───────────────────────────────

    def _try_receive(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        matched_verb = None
        for verb in RECEIVE_VERBS:
            if self._verb_matches(verb, s_lower):
                matched_verb = verb
                break
        if matched_verb is None:
            return None

        num = self._extract_number(s)
        if num is None:
            return None

        receiver = self._extract_name(s, names)
        if receiver is None:
            return None

        giver = None
        from_m = self.FROM_RE.search(s)
        by_m = self.BY_RE.search(s)
        if from_m:
            giver = from_m.group(1)
        elif by_m:
            giver = by_m.group(1)

        if giver is None:
            return None

        obj = self._extract_object(s, objs)
        if obj is None:
            return None

        return {
            "op": "TRANSFER", "from": f"{giver}.{obj}",
            "to": f"{receiver}.{obj}", "value": num,
            "evidence": self._make_evidence(s, full),
        }

    # ── Pattern: SPEND → SUB ──────────────────────────────────────

    def _try_spend(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in SUB_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            name = self._extract_name(s, names)
            if name is None:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "SUB", "target": f"{name}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: FIND → ADD ───────────────────────────────────────

    def _try_find(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in ADD_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            name = self._extract_name(s, names)
            if name is None:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "ADD", "target": f"{name}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: LOSE → SUB ───────────────────────────────────────

    def _try_lose(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in ("loses", "drops", "misplaces", "accidentally loses"):
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            name = self._extract_name(s, names)
            if name is None:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "SUB", "target": f"{name}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: BUY → TRANSFER ───────────────────────────────────

    def _try_buy(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in BUY_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            buyer = self._extract_name(s, names)
            if buyer is None:
                continue
            # Seller: "from X" or "pays X for"
            seller = None
            from_m = self.FROM_RE.search(s)
            if from_m:
                seller = from_m.group(1)
            else:
                pays_m = re.search(r'\bpays?\s+([A-Z][a-z]+)\s+for', s)
                if pays_m:
                    seller = pays_m.group(1)
            if seller is None or seller == buyer:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "TRANSFER", "from": f"{seller}.{obj}",
                "to": f"{buyer}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: SELL → TRANSFER ──────────────────────────────────

    def _try_sell(self, s: str, full: str, names: set, objs: set) -> dict | None:
        s_lower = s.lower()
        for verb in SELL_VERBS:
            if not self._verb_matches(verb, s_lower):
                continue
            num = self._extract_number(s)
            if num is None:
                continue
            seller = self._extract_name(s, names)
            if seller is None:
                continue
            buyer = None
            to_m = self.TO_RE.search(s)
            if to_m:
                buyer = to_m.group(1)
            else:
                words = s.split()
                for i, w in enumerate(words):
                    if w.lower() == verb and i + 1 < len(words):
                        nxt = words[i + 1].rstrip(".'\"")
                        if nxt and nxt[0].isupper() and nxt.isalpha():
                            buyer = nxt
                            break
            if buyer is None or buyer == seller:
                continue
            obj = self._extract_object(s, objs)
            if obj is None:
                continue
            return {
                "op": "TRANSFER", "from": f"{seller}.{obj}",
                "to": f"{buyer}.{obj}", "value": num,
                "evidence": self._make_evidence(s, full),
            }
        return None

    # ── Pattern: QUESTION → QUERY ─────────────────────────────────

    def _try_question(self, s: str, full: str, names: set, objs: set) -> dict | None:
        if not s.lower().startswith("question:"):
            return None

        # Extract person
        name = None
        for pat in [
            r'\bdoes\s+([A-Z][a-z]+)\s+have',
            r'\bis\s+([A-Z][a-z]+)\s+holding',
            r'\bwith\s+([A-Z][a-z]+)\b',
            r'\bremain\s+with\s+([A-Z][a-z]+)',
            r"([A-Z][a-z]+)'s\s+",
        ]:
            m = re.search(pat, s)
            if m:
                name = m.group(1)
                break
        if name is None:
            # Fallback: find any capitalized non-stop-word
            for fm in self.NAME_RE.finditer(s.replace("Question:", "")):
                candidate = fm.group(1)
                if candidate.lower() not in self.QUESTION_STOP_WORDS:
                    name = candidate
                    break

        obj = self._extract_object(s, objs)
        if obj is None:
            if objs:
                obj = list(objs)[0]
            else:
                obj = "coins"

        if name is None:
            return None

        return {
            "op": "QUERY", "target": f"{name}.{obj}",
            "evidence": self._make_evidence(s, full),
        }
