"""Sentence splitting for story text."""
import re

def split_sentences(text: str) -> list[str]:
    """Split text into sentences on period/exclamation/question mark."""
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if s.strip()]
