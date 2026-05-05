"""Heuristic baseline for SAGE.

A simple, rule-based baseline that extracts numbers from a story and
attempts to answer questions without any machine learning. This is
intentionally simple and will fail on complex stories — its purpose
is to establish the performance floor.
"""

from __future__ import annotations

import re
from typing import Any


class HeuristicBaseline:
    """Dumb heuristic baseline for story QA.

    Strategy:
    1. Find the question (last sentence starting with "Question:").
    2. Parse the question to extract the person and object being asked about.
    3. Scan backward through the story sentences.
    4. Find the last mention of that person with that object and a number.
    5. Return that number as the answer.

    This will fail when:
    - The answer requires arithmetic across multiple sentences.
    - The person/object is mentioned multiple times with different numbers.
    - The question is not in the expected format.
    - The story involves transfers between people.
    """

    # Question patterns
    QUESTION_PATTERN = re.compile(
        r"Question:\s*How\s+many\s+(\w+(?:\s+\w+)*?)\s+"
        r"(?:does\s+(\w+)\s+have|"
        r"is\s+(\w+)\'s\s+\w+\s+count|"
        r"is\s+(\w+)\s+holding|"
        r"does\s+(\w+)\s+possess|"
        r"does\s+(\w+)\s+end\s+up\s+with|"
        r"remain\s+with\s+(\w+))\??",
        re.IGNORECASE,
    )

    # Simpler fallback question parser
    QUESTION_SIMPLE = re.compile(
        r"Question:\s*How\s+many\s+(\w+(?:\s+\w+)?)\s+"
        r"(?:does\s+|is\s+|are\s+|do\s+)?(\w+)(?:\'s)?(?:\s+(?:have|holding|count|possess|now|remain|end\s+up\s+with))?\??",
        re.IGNORECASE,
    )

    # Pattern to find a number associated with a person and object
    # e.g. "Latif has 5 coins", "Arno gives Latif 3 coins", "Latif spends 2 coins"
    NUMBER_WITH_ENTITY = re.compile(r"(\d+)\s+(\w+)")

    def answer(self, story_text: str) -> str:
        """Extract an answer using simple heuristics.

        Args:
            story_text: The full story including the question.

        Returns:
            The predicted answer as a string.
        """
        answer, _ = self.answer_with_confidence(story_text)
        return answer

    def answer_with_confidence(self, story_text: str) -> tuple[str, float]:
        """Extract an answer with a confidence score.

        Args:
            story_text: The full story including the question.

        Returns:
            A tuple of (answer, confidence) where confidence is
            a float between 0.0 and 1.0.
        """
        sentences = self._split_sentences(story_text)
        if not sentences:
            return "", 0.0

        # The last sentence should be the question
        question = sentences[-1]
        if not question.lower().startswith("question:"):
            # No clear question found
            confidence = 0.0
            # Try scanning for a question anywhere
            for i, s in enumerate(sentences):
                if s.lower().startswith("question:"):
                    question = s
                    sentences = sentences[:i+1]
                    confidence = 0.5
                    break
            else:
                return "", 0.0

        # Parse the question to get person and object
        person, obj = self._parse_question(question)
        if person is None or obj is None:
            return "", 0.1

        # Scan backward through the story sentences (excluding the question)
        # to find the last number associated with this person and object
        story_sentences = sentences[:-1]

        answer = self._find_last_mention(person, obj, story_sentences)
        if answer is not None:
            # Higher confidence when we find a matching sentence
            confidence = 0.6
            return str(answer), confidence

        # Fallback: just find the last number mentioned in the story
        all_numbers = re.findall(r"\d+", " ".join(story_sentences))
        if all_numbers:
            return all_numbers[-1], 0.2

        return "0", 0.0

    def _split_sentences(self, text: str) -> list[str]:
        """Split story text into sentences.

        Handles the fact that sentences are already separated by
        ". " in the dataset, but the question may have a different
        format.
        """
        # The dataset joins sentences with " ", so we split on ". "
        # followed by a capital letter or "Question:"
        parts = re.split(r"(?<=\.)\s+(?=[A-Z]|Question:)", text)
        return [p.strip() for p in parts if p.strip()]

    def _parse_question(self, question: str) -> tuple[str | None, str | None]:
        """Parse a question to extract the person and object.

        Returns:
            Tuple of (person, object) or (None, None) if parsing fails.
        """
        # Try the comprehensive pattern first
        match = self.QUESTION_PATTERN.search(question)
        if match:
            obj = match.group(1)
            # Try all person capture groups
            for group_idx in range(2, 8):
                person = match.group(group_idx)
                if person:
                    return person, obj.rstrip().rstrip("?")

        # Try simpler pattern
        match = self.QUESTION_SIMPLE.search(question)
        if match:
            obj = match.group(1)
            person = match.group(2)
            return person, obj.rstrip().rstrip("?")

        # Last resort: extract any capitalized word as person
        # and any lowercase word as object
        words = question.replace("Question:", "").strip().split()
        people_candidates = [w for w in words if w and w[0].isupper()]
        obj_candidates = [w.rstrip("?") for w in words if w and w.islower() and len(w) > 2]

        person = people_candidates[0] if people_candidates else None
        obj = obj_candidates[-1] if obj_candidates else None

        return person, obj

    def _find_last_mention(self, person: str, obj: str,
                           sentences: list[str]) -> int | None:
        """Find the last number associated with a person and object.

        Scans sentences in reverse order, looking for mentions of
        both the person and object with a nearby number.

        Strategy:
        - For each sentence, check if it contains the person and object.
        - If so, extract all numbers from that sentence.
        - Return the last number found (usually the most recent state).

        Args:
            person: The person name.
            obj: The object type (e.g. "coins", "books").
            sentences: Story sentences without the question.

        Returns:
            The number found, or None.
        """
        for sentence in reversed(sentences):
            sentence_lower = sentence.lower()
            person_lower = person.lower()
            obj_lower = obj.lower()

            if person_lower in sentence_lower and obj_lower in sentence_lower:
                numbers = re.findall(r"\d+", sentence)
                if numbers:
                    # Return the last number in the sentence
                    # (in transfer sentences like "gives 3 coins to Latif",
                    #  the number is the amount transferred, not final state)
                    # For a naive heuristic, use the last number as best guess
                    return int(numbers[-1])

        # If no sentence matches both person and object,
        # try matching just the person
        for sentence in reversed(sentences):
            if person.lower() in sentence.lower():
                numbers = re.findall(r"\d+", sentence)
                if numbers:
                    return int(numbers[-1])

        return None
