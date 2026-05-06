"""Number extraction from text — digits and words."""
from __future__ import annotations
import re
from .patterns import NUMBER_RE

WORD_NUMBERS = {
    "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,
    "nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,
    "fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,
}

def extract_number(text: str) -> int | None:
    """Extract a number (digit or word) from text."""
    m = NUMBER_RE.search(text)
    if m:
        return int(m.group(1))
    words = text.lower().split()
    for w in words:
        if w in WORD_NUMBERS:
            return WORD_NUMBERS[w]
    return None
