"""PyTorch Dataset and collation utilities for SAGE training data.

Each JSONL record has the form:
    {"id": str, "story": str, "ops": [...], "answer": str, "metadata": {...}}

The SAGEDataset supports two modes:
  - "compile":      input = "compile: {story}"    target = JSON-serialized ops
  - "direct_answer": input = "answer: {story}"     target = answer string
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset


class SAGEDataset(Dataset):
    """Dataset that loads SAGE JSONL data for compiler or direct-answer training.

    Args:
        jsonl_path: Path to a JSONL file whose lines follow the DatasetRecord schema.
        tokenizer: A HuggingFace PreTrainedTokenizer (or FastTokenizer).
        max_input_length: Maximum token length for the input sequence.
        max_output_length: Maximum token length for the target sequence.
        mode: Either ``"compile"`` (story → ops) or ``"direct_answer"`` (story → answer).
    """

    def __init__(
        self,
        jsonl_path: Path,
        tokenizer: Any,
        max_input_length: int = 2048,
        max_output_length: int = 1024,
        mode: str = "compile",
    ) -> None:
        if mode not in ("compile", "direct_answer"):
            raise ValueError(f"mode must be 'compile' or 'direct_answer', got {mode!r}")

        self.jsonl_path = Path(jsonl_path)
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.mode = mode

        self.records: list[dict[str, Any]] = []
        with open(self.jsonl_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                self.records.append(json.loads(line))

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        record = self.records[idx]
        story = record["story"]

        if self.mode == "compile":
            source = f"compile: {story}"
            target = json.dumps(record["ops"], separators=(",", ":"))
        else:  # direct_answer
            source = f"answer: {story}"
            target = str(record["answer"])

        return {"source": source, "target": target}


def get_collate_fn(
    tokenizer: Any,
    max_input_length: int = 2048,
    max_output_length: int = 1024,
) -> Any:
    """Factory: returns a collate function suitable for ``DataLoader``.

    The returned callable tokenises *source* and *target* strings and produces
    a dictionary with keys ``input_ids``, ``attention_mask``, and ``labels``.

    Args:
        tokenizer: HuggingFace tokenizer.
        max_input_length: Token limit for the encoder input.
        max_output_length: Token limit for the decoder labels.
    """

    def collate_fn(batch: list[dict[str, str]]) -> dict[str, torch.Tensor]:
        sources = [item["source"] for item in batch]
        targets = [item["target"] for item in batch]

        # Tokenize inputs
        model_inputs = tokenizer(
            sources,
            max_length=max_input_length,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Tokenize targets (labels)
        labels = tokenizer(
            targets,
            max_length=max_output_length,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Replace padding token id in labels with -100 so the loss ignores it
        labels_ids = labels["input_ids"]
        labels_ids[labels_ids == tokenizer.pad_token_id] = -100

        model_inputs["labels"] = labels_ids
        return model_inputs

    return collate_fn
