"""Entity extraction from sentences — persons, objects, values, transfer directions."""
from __future__ import annotations
import re
from .patterns import (
    KNOWN_NAMES, STOP_WORDS, OBJECT_LOOKUP,
    NAME_RE, TO_RE, FROM_RE, BY_RE,
    GIVE_VERBS, BUY_VERBS, SELL_VERBS, RECEIVE_VERBS,
    QUESTION_PATTERNS,
)
from .number_extractor import extract_number
from .sentence_splitter import split_sentences


class EntityExtractor:
    """Extracts entities from sentences for SAGE operations."""
    
    def __init__(self):
        self._known_names = set(KNOWN_NAMES)
        self._seen_names: set[str] = set()
        self._seen_objects: set[str] = set()
    
    def reset(self):
        """Reset seen names/objects for a new story."""
        self._seen_names.clear()
        self._seen_objects.clear()
    
    def extract_person(self, text: str) -> str | None:
        """Extract a person name from text. Prefers known names, then first capitalized word."""
        # Check known names first
        text_lower = text.lower()
        for name in sorted(self._known_names | self._seen_names, key=len, reverse=True):
            if name.lower() in text_lower:
                return name
        # Find all capitalized words, filter stop words
        for m in NAME_RE.finditer(text):
            candidate = m.group(1)
            if candidate not in STOP_WORDS and candidate.lower() not in {"question","how","what"}:
                return candidate
        return None
    
    def extract_object(self, text: str) -> str | None:
        """Extract an object type from text. Returns canonical plural form."""
        text_lower = text.lower()
        # Check seen objects first
        for obj in sorted(self._seen_objects, key=len, reverse=True):
            if obj.lower() in text_lower:
                return obj
        # Check OBJECT_LOOKUP by longest match
        for form in sorted(OBJECT_LOOKUP, key=len, reverse=True):
            if form in text_lower:
                return OBJECT_LOOKUP[form]
        return None
    
    def extract_value(self, text: str) -> int | None:
        return extract_number(text)
    
    def _first_person(self, text: str) -> str | None:
        """Find the first person name by position in the sentence."""
        all_names = self._known_names | self._seen_names
        best_idx = None
        best_name = None
        text_lower = text.lower()
        for name in all_names:
            idx = text_lower.find(name.lower())
            if idx >= 0 and (best_idx is None or idx < best_idx):
                best_idx = idx
                best_name = name
        if best_name is not None:
            return best_name
        # Fallback to first capitalized word that isn't a stop word
        for m in NAME_RE.finditer(text):
            candidate = m.group(1)
            if candidate not in STOP_WORDS and candidate.lower() not in {"question","how","what"}:
                return candidate
        return None
    
    def extract_transfer_direction(self, text: str) -> tuple[str | None, str | None]:
        """Extract (from_person, to_person) for a TRANSFER sentence.
        
        Handles:
        - "A gives B 3 coins" → from=A, to=B
        - "A gives 3 coins to B" → from=A, to=B
        - "B receives 3 coins from A" → from=A, to=B
        - "A buys 3 coins from B" → from=B, to=A  (B is seller, A is buyer)
        - "B sells A 3 coins" → from=B, to=A
        - "A pays B for 3 coins" → from=B, to=A  (B is seller, A is buyer)
        """
        s = text
        s_lower = s.lower()
        subject = self._first_person(s)
        
        # Check for BUY pattern: buyer buys from seller → from=seller, to=buyer
        for verb in BUY_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', s_lower):
                from_m = FROM_RE.search(s)
                if from_m and subject:
                    return (from_m.group(1), subject)  # seller → buyer
                pays_m = re.search(r'\bpays?\s+([A-Z][a-z]+)\s+for', s)
                if pays_m and subject:
                    return (pays_m.group(1), subject)
        
        # Check for SELL pattern: seller sells to buyer → from=seller, to=buyer
        for verb in SELL_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', s_lower):
                to_m = TO_RE.search(s)
                if to_m and subject:
                    return (subject, to_m.group(1))  # seller → buyer
                # "B sells A 3 coins": subject=seller, find buyer after verb
                words = s.split()
                for i, w in enumerate(words):
                    if w.lower() == verb and i+1 < len(words):
                        nxt = words[i+1].rstrip(".'\"")
                        if nxt and nxt[0].isupper() and nxt.isalpha():
                            return (subject, nxt)
        
        # Check for RECEIVE pattern: receiver receives from giver → from=giver, to=receiver
        for verb in RECEIVE_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', s_lower):
                from_m = FROM_RE.search(s)
                by_m = BY_RE.search(s)
                giver = from_m.group(1) if from_m else (by_m.group(1) if by_m else None)
                if giver and subject:
                    return (giver, subject)  # from=giver, to=receiver
        
        # Default GIVE pattern: giver gives to receiver → from=giver, to=receiver
        to_m = TO_RE.search(s)
        receiver = to_m.group(1) if to_m else None
        
        # "A gives B 3 coins": find indirect object after verb
        if receiver is None:
            for verb in GIVE_VERBS:
                words = s.split()
                for i, w in enumerate(words):
                    if w.lower() in GIVE_VERBS and i+1 < len(words):
                        nxt = words[i+1].rstrip(".'\"")
                        if nxt and nxt[0].isupper() and nxt.isalpha():
                            receiver = nxt
                            break
        
        if subject and receiver and subject != receiver:
            return (subject, receiver)
        
        # Flexible fallback: use structural cues when verb-specific checks fail
        flex_from, flex_to = self.extract_direction_flexible(s)
        if flex_from and flex_to and flex_from != flex_to:
            return (flex_from, flex_to)
        
        return (subject, receiver)
    
    def extract_direction_flexible(self, text: str) -> tuple[str | None, str | None]:
        """Extract transfer direction from ANY phrasing using structural cues.
        
        Strategy:
        1. Find all person names in the sentence (ordered by position)
        2. Look for direction cues: 'to', 'from', 'by', 'over to'
        3. Use cue position relative to names to determine giver/receiver
        
        Returns (from_person, to_person).
        """
        s = text
        # Find all person names ordered by position
        all_names = []
        text_lower = s.lower()
        for name in sorted(self._known_names | self._seen_names, key=len, reverse=True):
            idx = text_lower.find(name.lower())
            if idx >= 0:
                all_names.append((idx, name))
        # Also find capitalized words (potential new names)
        for m in NAME_RE.finditer(s):
            c = m.group(1)
            if c not in STOP_WORDS and c.lower() not in {"question","how","what","many","does"}:
                # Check not already found
                if not any(n == c for _, n in all_names):
                    all_names.append((m.start(), c))
        
        all_names.sort()
        
        if len(all_names) < 2:
            # Single person: look for pattern cues
            if len(all_names) == 1:
                # RECEIVE-like: "X takes N from Y" → from=Y, to=X
                from_m = FROM_RE.search(s)
                by_m = BY_RE.search(s)
                if from_m:
                    return (from_m.group(1), all_names[0][1])
                if by_m:
                    return (by_m.group(1), all_names[0][1])
                # GIVE-like: "X gives/does something to Y" → from=X, to=Y
                to_m = re.search(r'\b(to|over to)\s+([A-Z][a-z]+)', s)
                if to_m:
                    return (all_names[0][1], to_m.group(2))
            return (all_names[0][1] if all_names else None, None)
        
        # Two or more names: use position + cue heuristics
        first_name = all_names[0][1]
        last_name = all_names[-1][1]
        
        # Check direction cues
        to_match = re.search(r'\b(to|over to)\s+([A-Z][a-z]+)', s)
        from_match = FROM_RE.search(s)
        by_match = BY_RE.search(s)
        
        if from_match:
            # "Y from X" → X is source, Y is recipient
            return (from_match.group(1), first_name)
        
        if by_match:
            # "X by Y" → Y is source, X is recipient  
            return (by_match.group(1), first_name)
        
        if to_match:
            # "X to Y" → X is source, Y is recipient
            return (first_name, to_match.group(2))
        
        # Default: first name is subject (giver), last non-subject is receiver
        return (first_name, last_name)
    
    def extract_query_target(self, text: str) -> tuple[str | None, str | None]:
        """Extract (person, object) from a question sentence."""
        person = None
        for pat in QUESTION_PATTERNS:
            m = pat.search(text)
            if m:
                candidate = m.group(1)
                if candidate not in STOP_WORDS and candidate.lower() not in {"question","how","what"}:
                    person = candidate
                    break
        
        if person is None:
            # Fallback: first capitalized non-stop word after "Question:"
            clean = text.replace("Question:","").strip()
            for m in NAME_RE.finditer(clean):
                c = m.group(1)
                if c not in STOP_WORDS and c.lower() not in {"question","how","what","many","does","is","was","were"}:
                    person = c
                    break
        
        obj = self.extract_object(text)
        return (person, obj)
    
    def build_op(self, op_type: str, sentence: str, full_text: str, confidence: float = 1.0) -> dict | None:
        """Build a complete operation dict for a sentence.
        
        Args:
            op_type: "SET", "ADD", "SUB", "TRANSFER", or "QUERY"
            sentence: The sentence text
            full_text: Full story text (for evidence span)
            confidence: Confidence score for this extraction (default 1.0)
        
        Returns:
            Operation dict or None if extraction fails.
        """
        # Find evidence span
        start = full_text.find(sentence)
        end = start + len(sentence) if start >= 0 else len(sentence)
        evidence = {"span": sentence, "start": max(0, start), "end": end, "confidence": confidence}
        
        if op_type in ("SET", "ADD", "SUB"):
            person = self.extract_person(sentence)
            obj = self.extract_object(sentence)
            val = self.extract_value(sentence)
            if person is None or obj is None or val is None:
                return None
            self._seen_names.add(person)
            self._seen_objects.add(obj)
            return {"op": op_type, "target": f"{person}.{obj}", "value": val, "evidence": evidence}
        
        elif op_type == "TRANSFER":
            obj = self.extract_object(sentence)
            val = self.extract_value(sentence)
            from_p, to_p = self.extract_transfer_direction(sentence)
            if obj is None or val is None or from_p is None or to_p is None:
                return None
            self._seen_names.update([from_p, to_p])
            self._seen_objects.add(obj)
            return {"op": "TRANSFER", "from": f"{from_p}.{obj}", "to": f"{to_p}.{obj}", "value": val, "evidence": evidence}
        
        elif op_type == "QUERY":
            person, obj = self.extract_query_target(sentence)
            if person is None:
                return None
            if obj is None and self._seen_objects:
                obj = list(self._seen_objects)[0]
            elif obj is None:
                obj = "coins"
            self._seen_names.add(person)
            self._seen_objects.add(obj)
            return {"op": "QUERY", "target": f"{person}.{obj}", "evidence": evidence}
        
        return None
    
    def compile_story(self, story_text: str, predicted_labels: list[str]) -> tuple[list[dict], bool]:
        """Compile a full story using predicted sentence labels.
        
        Args:
            story_text: Full story text
            predicted_labels: Op type for each sentence (from sklearn classifier)
        
        Returns:
            (ops_list, success_flag)
        """
        self.reset()
        sentences = split_sentences(story_text)
        ops = []
        success = True
        
        for sentence, label in zip(sentences, predicted_labels):
            if label == "NOOP":
                continue
            op = self.build_op(label, sentence, story_text)
            if op is not None:
                ops.append(op)
            elif label == "QUERY":
                success = False
        
        return ops, success
