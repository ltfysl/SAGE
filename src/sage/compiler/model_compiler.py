"""Model-based compiler for SAGE.

Uses a small seq2seq HuggingFace model to convert natural language
stories into JSON operation sequences.
"""

from __future__ import annotations

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class ModelCompiler:
    """Seq2seq model-based compiler for SAGE.

    Loads a small transformer model (default: flan-t5-small) and
    uses it to compile natural language stories into JSON operation
    sequences. This is the experimental target — the model that
    SAGE's hypothesis is testing.
    """

    def __init__(self, model_name: str = "google/flan-t5-small",
                 use_cpu: bool = True):
        self.model_name = model_name
        self.device = "cpu"
        if not use_cpu and torch.cuda.is_available():
            self.device = "cuda"

        self.tokenizer = None
        self.model = None
        self._loaded = False

    def load(self):
        """Load tokenizer and model from HuggingFace."""
        if self._loaded:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        self._loaded = True

    def compile(self, story_text: str,
                max_new_tokens: int = 512,
                num_beams: int = 1,
                temperature: float = 1.0) -> str:
        """Compile a story into operation sequence JSON.

        Args:
            story_text: Natural language story.
            max_new_tokens: Maximum tokens to generate.
            num_beams: Number of beams for beam search.
            temperature: Sampling temperature.

        Returns:
            Raw model output string (expected to be JSON array).
        """
        if not self._loaded:
            self.load()

        input_text = f"compile: {story_text}"

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=2048,
            truncation=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
                temperature=temperature if num_beams == 1 else None,
                do_sample=(num_beams == 1 and temperature != 1.0),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result.strip()

    def load_checkpoint(self, checkpoint_path: str | Path):
        """Load fine-tuned model weights from a checkpoint directory.

        Args:
            checkpoint_path: Path to the checkpoint directory.
        """
        checkpoint_path = Path(checkpoint_path)
        self.tokenizer = AutoTokenizer.from_pretrained(str(checkpoint_path))
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(checkpoint_path))
        self.model.to(self.device)
        self.model.eval()
        self._loaded = True

    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._loaded
