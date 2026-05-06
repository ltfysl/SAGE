"""LLM compiler interface for SAGE (optional, stub implementation).

Defines the interface for an LLM-based operation compiler.
Currently provides a mock that returns empty ops.
"""

from __future__ import annotations
from typing import Any


class LLMCompiler:
    """Interface for LLM-based sentence-to-operation compilation.
    
    Can be backed by Ollama, OpenAI, or any LLM API.
    Currently a stub that always returns None (no op).
    """
    
    def __init__(self, backend: str = "mock", model_name: str = ""):
        self.backend = backend
        self.model_name = model_name
        self._loaded = False
    
    def load(self):
        """Load/connect to backend. Stub does nothing."""
        self._loaded = True
    
    def compile_sentence(self, sentence: str, story_context: str = "") -> dict | None:
        """Compile a single sentence into an operation dict.
        
        Args:
            sentence: The sentence to compile
            story_context: Full story for context
        
        Returns:
            Operation dict or None if compilation fails.
        """
        if self.backend == "mock":
            return None
        
        # Future: call LLM API
        return None
    
    def compile(self, story_text: str) -> str:
        """Compile full story. Stub returns empty JSON array."""
        return "[]"
