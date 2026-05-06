"""Adversarial guard for SAGE — detects misleading/non-event sentences.

Returns blocking decisions for sentences that should NOT produce operations.
Used by HybridSAGECompiler before semantic normalization to prevent
false-positive operations on adversarial content.
"""

from __future__ import annotations
import re


class AdversarialGuard:
    """Detects non-event and misleading sentences that should be blocked.

    Categories:
    - almost_event: "almost gave", "nearly dropped"
    - wanted_but_not: "wanted to give but did not", "planned to but never did"
    - claim_only: "says he has", "claims to have"
    - negated_receiver: "gives X to Y, not to Z"
    - hypothetical: "would have", "could have", "might give"
    - cancelled_event: "but changed his mind", "but kept them"
    - counterfactual: "if only", "should have"
    """

    BLOCK_PATTERNS = [
        # almost / nearly events
        (re.compile(r'\b(almost|nearly)\s+(gave|dropped|lost|spent|found|bought|sold|transferred)', re.IGNORECASE),
         "almost_event"),
        # wanted / planned / intended ... but didn't
        (re.compile(r'\b(wanted|planned|intended|meant|tried|hoped|wished)\s+to\s+\w+.*\b(but\s+(did\s+not|didn\'?t|never\s+did|changed|couldn\'?t|kept))', re.IGNORECASE),
         "wanted_but_not"),
        # planned/intended ... but never
        (re.compile(r'\b(planned|intended)\s+to\s+\w+.*\b(but\s+never)', re.IGNORECASE),
         "planned_but_not"),
        # changed mind
        (re.compile(r'\b(changed?\s+\w+\s+mind)\b', re.IGNORECASE),
         "cancelled_event"),
        # kept them instead
        (re.compile(r'\b(but\s+kept\s+them|but\s+saved\s+them|instead)\b', re.IGNORECASE),
         "cancelled_event"),
        # claims / says he has (unreliable)
        (re.compile(r'\b(says?\s+\w+\s+has|claims?\s+to\s+have|pretends?\s+to\s+have)\b', re.IGNORECASE),
         "claim_only"),
        # not {person} (negated receiver)
        (re.compile(r',\s*not\s+([A-Z][a-z]+)\b', re.IGNORECASE),
         "negated_receiver"),
        # instead of {person}
        (re.compile(r'\b(instead\s+of)\b', re.IGNORECASE),
         "negated_receiver"),
        # hypothetical / conditional
        (re.compile(r'\b(would\s+have|could\s+have|might\s+give|may\s+give|should\s+have)\b', re.IGNORECASE),
         "hypothetical"),
        # counterfactual
        (re.compile(r'\b(if\s+only|wish\s+\w+\s+had)\b', re.IGNORECASE),
         "counterfactual"),
        # forgot to / failed to
        (re.compile(r'\b(forgot\s+to|failed\s+to|neglected\s+to)\b', re.IGNORECASE),
         "cancelled_event"),
    ]

    def check(self, sentence: str) -> dict:
        """Check if a sentence should be blocked.

        Returns {"is_blocked": bool, "reason": str, "confidence": float}
        """
        for pattern, reason in self.BLOCK_PATTERNS:
            if pattern.search(sentence):
                return {
                    "is_blocked": True,
                    "reason": reason,
                    "confidence": 1.0,
                }
        return {
            "is_blocked": False,
            "reason": "",
            "confidence": 1.0,
        }
