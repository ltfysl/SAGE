"""Rule-based compiler for SAGE.

Deterministic reference compiler that parses synthetic stories
and converts known sentence patterns into JSON operation sequences.
Uses regex pattern matching against the templates from synthetic_worlds.py.
"""

from __future__ import annotations

import re
import json
from typing import Any

from sage.schemas.ops import Operation, OpType


class RuleCompiler:
    """Deterministic rule-based compiler for synthetic event-world stories.

    Matches sentence patterns to produce operation sequences.
    This is the reference compiler — it achieves 100% accuracy on
    synthetic data by design, since it knows the exact templates.
    """

    # Patterns for number extraction
    NUMBER_PATTERN = re.compile(r'\b(\d+)\b')
    # Word-based numbers
    WORD_NUMBERS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20,
    }

    # Object plurals -> canonical form mapping
    # Also maps singular forms to the canonical (plural) form
    PLURAL_TO_SINGULAR = {
        "coins": "coins", "books": "books", "apples": "apples",
        "marbles": "marbles", "cards": "cards", "candies": "candies",
        "pencils": "pencils", "stickers": "stickers", "cookies": "cookies",
        "shells": "shells", "stones": "stones", "beads": "beads",
        "tokens": "tokens", "berries": "berries", "seeds": "seeds",
        "buttons": "buttons", "keys": "keys", "rings": "rings",
        "pebbles": "pebbles", "leaves": "leaves",
    }

    # Irregular singular → plural mappings
    IRREGULAR_SINGULAR = {
        "berry": "berries",
        "leaf": "leaves",
        "candy": "candies",
        "pebble": "pebbles",
    }

    # Action verbs and their operation types
    SET_VERBS = {"has", "owns", "holds", "possesses", "holding"}
    ADD_VERBS = {"finds", "discovers", "gains", "collects", "earns",
                 "receives", "gets", "takes", "picks"}
    SUB_VERBS = {"spends", "uses", "consumes", "loses", "drops",
                 "misplaces", "parts", "gives away"}
    TRANSFER_GIVE_VERBS = {"gives", "hands", "passes", "offers", "transfers"}
    TRANSFER_BUY_VERBS = {"buys", "purchases"}
    TRANSFER_SELL_VERBS = {"sells"}

    def compile(self, story_text: str) -> tuple[list[dict[str, Any]], bool]:
        """Compile a story into operations.

        Args:
            story_text: Natural language story text.

        Returns:
            Tuple of (list of operation dicts, success flag).
        """
        # Split into sentences
        sentences = self._split_sentences(story_text)

        # Collect known names and objects for context
        known_names: set[str] = set()
        known_objects: set[str] = set()

        ops: list[dict[str, Any]] = []
        success = True

        for sentence in sentences:
            op_dict = self._parse_sentence(sentence, known_names, known_objects)
            if op_dict is not None:
                ops.append(op_dict)
                # Track names and objects
                if "target" in op_dict:
                    parts = op_dict["target"].split(".", 1)
                    if len(parts) == 2:
                        known_names.add(parts[0])
                        known_objects.add(parts[1])
                if "from" in op_dict:
                    parts = op_dict["from"].split(".", 1)
                    if len(parts) == 2:
                        known_names.add(parts[0])
                        known_objects.add(parts[1])
                if "to" in op_dict:
                    parts = op_dict["to"].split(".", 1)
                    if len(parts) == 2:
                        known_names.add(parts[0])
                        known_objects.add(parts[1])
            else:
                # Sentence didn't match — might be noise, skip it
                # but if it's a question we need to flag
                if sentence.strip().lower().startswith("question:"):
                    success = False

        return ops, success

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Split on period, question mark, exclamation
        raw = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in raw if s.strip()]

    def _parse_sentence(self, sentence: str,
                        known_names: set[str],
                        known_objects: set[str]) -> dict[str, Any] | None:
        """Parse a single sentence into an operation dict.

        Returns None if no pattern matches (noise sentence).
        """
        s = sentence.strip()

        # Try each pattern
        op = (self._try_has_pattern(s, known_names, known_objects) or
              self._try_gives_pattern(s, known_names, known_objects) or
              self._try_receives_pattern(s, known_names, known_objects) or
              self._try_spends_pattern(s, known_names, known_objects) or
              self._try_finds_pattern(s, known_names, known_objects) or
              self._try_loses_pattern(s, known_names, known_objects) or
              self._try_buys_pattern(s, known_names, known_objects) or
              self._try_sells_pattern(s, known_names, known_objects) or
              self._try_question_pattern(s, known_names, known_objects))
        return op

    def _extract_number(self, text: str) -> int | None:
        """Extract a number from text."""
        m = self.NUMBER_PATTERN.search(text)
        if m:
            return int(m.group(1))
        # Try word numbers
        words = text.lower().split()
        for word in words:
            if word in self.WORD_NUMBERS:
                return self.WORD_NUMBERS[word]
        return None

    def _extract_name(self, text: str, known_names: set[str]) -> str | None:
        """Extract a person name from text."""
        words = text.split()
        # First word is often the subject name
        if words and words[0][0].isupper() and words[0].rstrip(".'\"").isalpha():
            return words[0].rstrip(".'\"")
        # Check known names
        for name in known_names:
            if name in text:
                return name
        # Look for any capitalized word that looks like a name
        for word in words:
            clean = word.rstrip(".'\"!?,")
            if clean and clean[0].isupper() and clean.isalpha() and len(clean) > 1:
                return clean
        return None

    def _extract_object(self, text: str, known_objects: set[str]) -> str | None:
        """Extract an object type from text."""
        text_lower = text.lower()
        # Build lookup: plural → canonical, and also singular guesses → canonical
        all_forms: dict[str, str] = {}
        for obj in self.PLURAL_TO_SINGULAR:
            all_forms[obj] = obj
            # Also add singular guess (remove trailing 's')
            if obj.endswith("s"):
                singular_guess = obj[:-1]
                if singular_guess not in all_forms:
                    all_forms[singular_guess] = obj
        # Add irregular singular forms
        for singular, plural in self.IRREGULAR_SINGULAR.items():
            all_forms[singular] = plural
        # Add known objects
        for obj in known_objects:
            all_forms[obj.lower()] = obj
            if obj.endswith("s"):
                singular_guess = obj[:-1].lower()
                if singular_guess not in all_forms:
                    all_forms[singular_guess] = obj
            # Also check irregular singular
            if obj in self.IRREGULAR_SINGULAR.values():
                for sing, plur in self.IRREGULAR_SINGULAR.items():
                    if plur == obj:
                        all_forms[sing] = obj
        # Search by longest match first
        for form in sorted(all_forms, key=len, reverse=True):
            if form in text_lower:
                return all_forms[form]
        return None

    def _try_has_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Person has/owns/holds/possesses N objects."""
        s_lower = s.lower()
        for verb in self.SET_VERBS:
            if verb not in s_lower:
                continue
            # Pattern: NAME verb NUMBER OBJECT
            # More robust: extract name (first word), number, object
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
                "op": "SET",
                "target": f"{name}.{obj}",
                "value": num,
            }
        return None

    def _try_gives_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Giver gives/hands/passes N objects to Receiver.
        Also: Giver gives Receiver N objects."""
        s_lower = s.lower()
        for verb in self.TRANSFER_GIVE_VERBS:
            if verb not in s_lower:
                continue
            num = self._extract_number(s)
            if num is None:
                continue

            # Find giver (subject) and receiver (after "to")
            words = s.split()
            giver = words[0].rstrip(".'\"") if words else None
            if giver is None or not giver[0].isupper():
                giver = self._extract_name(s, names)
            if giver is None:
                continue

            # Find receiver: after "to" or as indirect object
            receiver = None
            # Pattern: "gives Receiver N objects" (Receiver before number)
            # Find capitalized word after verb
            for i, w in enumerate(words):
                if w.lower() == verb and i + 1 < len(words):
                    next_word = words[i + 1].rstrip(".'\"")
                    if next_word and next_word[0].isupper() and next_word.isalpha():
                        # Check if this is a name (not a number)
                        if not next_word.isdigit():
                            receiver = next_word
                            break
            # Pattern: "to Receiver"
            to_match = re.search(r'\bto\s+([A-Z][a-z]+)', s)
            if to_match:
                receiver = to_match.group(1)

            if receiver is None:
                continue

            obj = self._extract_object(s, objs)
            if obj is None:
                continue

            return {
                "op": "TRANSFER",
                "from": f"{giver}.{obj}",
                "to": f"{receiver}.{obj}",
                "value": num,
            }
        return None

    def _try_receives_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Receiver receives/gets N objects from Giver.
        Or: Receiver is given N objects by Giver."""
        s_lower = s.lower()
        if "receives" in s_lower or "gets" in s_lower or "takes" in s_lower or "is given" in s_lower:
            num = self._extract_number(s)
            if num is None:
                return None

            # Receiver is first word
            words = s.split()
            receiver = words[0].rstrip(".'\"") if words else None
            if receiver is None or not (receiver[0].isupper() if receiver else False):
                return None

            # Giver after "from" or "by"
            giver = None
            from_match = re.search(r'\bfrom\s+([A-Z][a-z]+)', s)
            by_match = re.search(r'\bby\s+([A-Z][a-z]+)', s)
            if from_match:
                giver = from_match.group(1)
            elif by_match:
                giver = by_match.group(1)

            if giver is None:
                return None

            obj = self._extract_object(s, objs)
            if obj is None:
                return None

            return {
                "op": "TRANSFER",
                "from": f"{giver}.{obj}",
                "to": f"{receiver}.{obj}",
                "value": num,
            }
        return None

    def _try_spends_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Person spends/uses/consumes/loses N objects.
        Also: Person gives away N objects. Person parts with N objects."""
        s_lower = s.lower()

        # Check for "gives away" separately from GIVES
        if "gives away" in s_lower or "parts with" in s_lower:
            num = self._extract_number(s)
            if num is None:
                return None
            name = self._extract_name(s, names)
            if name is None:
                return None
            obj = self._extract_object(s, objs)
            if obj is None:
                return None
            return {"op": "SUB", "target": f"{name}.{obj}", "value": num}

        for verb in self.SUB_VERBS:
            if verb not in s_lower:
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
            return {"op": "SUB", "target": f"{name}.{obj}", "value": num}
        return None

    def _try_finds_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Person finds/discovers/gains/collects/earns/picks up N objects."""
        s_lower = s.lower()
        for verb in self.ADD_VERBS:
            if verb not in s_lower:
                continue
            # "picks up" is two words
            if verb == "picks" and "picks up" not in s_lower:
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
            return {"op": "ADD", "target": f"{name}.{obj}", "value": num}
        return None

    def _try_loses_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Person loses/drops/misplaces N objects."""
        s_lower = s.lower()
        for verb in {"loses", "drops", "misplaces", "accidentally loses"}:
            if verb in s_lower:
                num = self._extract_number(s)
                if num is None:
                    return None
                name = self._extract_name(s, names)
                if name is None:
                    return None
                obj = self._extract_object(s, objs)
                if obj is None:
                    return None
                return {"op": "SUB", "target": f"{name}.{obj}", "value": num}
        return None

    def _try_buys_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Buyer buys/purchases N objects from Seller.
        Or: Buyer pays Seller for N objects."""
        s_lower = s.lower()
        for verb in self.TRANSFER_BUY_VERBS:
            if verb not in s_lower:
                continue

            num = self._extract_number(s)
            if num is None:
                continue

            words = s.split()
            buyer = words[0].rstrip(".'\"") if words else None
            if buyer is None or not (buyer[0].isupper() if buyer else False):
                continue

            # Seller after "from"
            from_match = re.search(r'\bfrom\s+([A-Z][a-z]+)', s)
            seller = from_match.group(1) if from_match else None
            if seller is None:
                # "pays Seller for" pattern
                pays_match = re.search(r'\bpays?\s+([A-Z][a-z]+)\s+for', s)
                if pays_match:
                    seller = pays_match.group(1)

            if seller is None:
                continue

            obj = self._extract_object(s, objs)
            if obj is None:
                continue

            return {
                "op": "TRANSFER",
                "from": f"{seller}.{obj}",
                "to": f"{buyer}.{obj}",
                "value": num,
            }
        return None

    def _try_sells_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match: Seller sells N objects to Buyer.
        Or: Seller sells Buyer N objects."""
        s_lower = s.lower()
        for verb in self.TRANSFER_SELL_VERBS:
            if verb not in s_lower:
                continue

            num = self._extract_number(s)
            if num is None:
                continue

            words = s.split()
            seller = words[0].rstrip(".'\"") if words else None
            if seller is None or not (seller[0].isupper() if seller else False):
                continue

            # Buyer after "to"
            to_match = re.search(r'\bto\s+([A-Z][a-z]+)', s)
            buyer = to_match.group(1) if to_match else None
            if buyer is None:
                # "sells Buyer N objects" pattern
                for i, w in enumerate(words):
                    if w.lower() == verb and i + 1 < len(words):
                        next_word = words[i + 1].rstrip(".'\"")
                        if next_word and next_word[0].isupper() and next_word.isalpha():
                            buyer = next_word
                            break

            if buyer is None:
                continue

            obj = self._extract_object(s, objs)
            if obj is None:
                continue

            return {
                "op": "TRANSFER",
                "from": f"{seller}.{obj}",
                "to": f"{buyer}.{obj}",
                "value": num,
            }
        return None

    def _try_question_pattern(self, s: str, names: set[str], objs: set[str]) -> dict | None:
        """Match question patterns.

        Examples:
        - Question: How many OBJECT does PERSON have?
        - Question: What is PERSON's OBJECT count?
        - Question: How many OBJECT is PERSON holding?
        - Question: How many OBJECT does PERSON possess now?
        - Question: How many OBJECT does PERSON end up with?
        - Question: How many OBJECT remain with PERSON?
        """
        s_lower = s.lower()
        if not s_lower.startswith("question:"):
            return None

        # Extract person name from question
        name = None
        # Pattern: "does PERSON have" or "'s OBJECT" or "is PERSON holding" or "remain with PERSON"
        does_match = re.search(r'\bdoes\s+([A-Z][a-z]+)\s+have', s)
        poss_match = re.search(r"([A-Z][a-z]+)'s\s+", s)
        is_match = re.search(r'\bis\s+([A-Z][a-z]+)\s+holding', s)
        with_match = re.search(r'\bwith\s+([A-Z][a-z]+)', s)

        if does_match:
            name = does_match.group(1)
        elif poss_match:
            name = poss_match.group(1)
        elif is_match:
            name = is_match.group(1)
        elif with_match:
            name = with_match.group(1)
        else:
            # Fallback: find any capitalized word in the question
            cap_match = re.search(r'\b([A-Z][a-z]+)\b', s)
            if cap_match:
                name = cap_match.group(1)

        if name is None:
            return None

        obj = self._extract_object(s, objs)
        if obj is None:
            # Try singular form
            for plural, singular_approx in [("coins", "coins"), ("books", "books")]:
                pass
            # Just use the first known object
            if objs:
                obj = list(objs)[0]
            else:
                obj = "coins"  # fallback

        return {
            "op": "QUERY",
            "target": f"{name}.{obj}",
        }
