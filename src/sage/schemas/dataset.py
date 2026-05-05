"""Pydantic schemas for SAGE datasets."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from sage.schemas.ops import Operation


class DatasetRecord(BaseModel):
    """A single record in the SAGE dataset (JSONL format)."""

    id: str
    story: str
    ops: list[dict[str, Any]]  # Raw JSON operations
    answer: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DifficultyLevel(str):
    """Difficulty levels for benchmarks."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LONG = "long"


class BenchmarkConfig(BaseModel):
    """Configuration for a specific benchmark."""

    name: str
    difficulty: str
    num_samples: int = 1000
    min_events: int = 3
    max_events: int = 50
    noise_level: float = 0.0
    distractor_people: int = 0
    distractor_objects: int = 0
    irrelevant_sentences: int = 0
