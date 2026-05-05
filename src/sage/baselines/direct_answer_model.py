"""Direct Answer baseline model.

A seq2seq model (FLAN-T5-small by default) that directly answers
questions from stories. This is the comparison point for SAGE —
instead of compiling to executable operations, the model is asked
to produce the answer string directly.

Input format: "answer: {story_text}"
Target format: "{answer}"
"""

from __future__ import annotations

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class DirectAnswerModel:
    """Ask a seq2seq model to directly answer a question from a story.

    This is the baseline that SAGE aims to outperform. Instead of
    compiling the story into executable operations, the model is
    fine-tuned to produce the answer string in one shot.

    Usage:
        model = DirectAnswerModel()
        model.load()
        answer = model.answer("Latif has 5 coins. Arno gives Latif 3 coins. "
                              "Question: How many coins does Latif have?")
        # -> "6"
    """

    def __init__(self, model_name: str = "google/flan-t5-small", use_cpu: bool = True):
        self.model_name = model_name
        self.device = "cpu" if use_cpu else ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer: AutoTokenizer | None = None
        self.model: AutoModelForSeq2SeqLM | None = None

    def load(self):
        """Load tokenizer and model from HuggingFace."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

    def answer(self, story_text: str) -> str:
        """Answer a question given story text.

        Args:
            story_text: The full story including the question.
                        Expected format: sentences ending with
                        "Question: ..."

        Returns:
            The raw model output string (the predicted answer).
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        input_text = f"answer: {story_text}"

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=64,
                num_beams=4,
                early_stopping=True,
            )

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip()

    def load_checkpoint(self, checkpoint_path: str | Path):
        """Load fine-tuned weights from a checkpoint directory.

        Args:
            checkpoint_path: Path to a directory containing a
                             HuggingFace model checkpoint (saved via
                             model.save_pretrained() and
                             tokenizer.save_pretrained()).
        """
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(str(checkpoint_path))
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(checkpoint_path))
        self.model.to(self.device)
        self.model.eval()

    def answer_batch(self, stories: list[str]) -> list[str]:
        """Answer a batch of stories efficiently.

        Args:
            stories: List of story texts.

        Returns:
            List of answer strings.
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        input_texts = [f"answer: {s}" for s in stories]

        inputs = self.tokenizer(
            input_texts,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=64,
                num_beams=4,
                early_stopping=True,
            )

        answers = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return [a.strip() for a in answers]
