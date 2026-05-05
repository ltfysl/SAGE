"""Pydantic schemas for SAGE operations — with evidence support."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OpType(str, Enum):
    """Valid operation types."""
    SET = "SET"
    ADD = "ADD"
    SUB = "SUB"
    TRANSFER = "TRANSFER"
    QUERY = "QUERY"


class Evidence(BaseModel):
    """Evidence for a compiled operation — links op to source text span."""
    span: str = Field(default="", description="Exact substring from the story.")
    start: int = Field(default=0, description="Character offset where span begins.")
    end: int = Field(default=0, description="Character offset where span ends.")
    confidence: float = Field(default=1.0, description="Confidence in this compilation (0-1).")


class Operation(BaseModel):
    """A single state operation with optional evidence."""

    op: OpType
    target: str | None = Field(default=None, description="Target state key (e.g. 'Latif.coins').")
    value: int | None = Field(default=None, description="Numeric value for the operation.")
    from_target: str | None = Field(default=None, description="Source for TRANSFER operations.")
    to_target: str | None = Field(default=None, description="Destination for TRANSFER operations.")
    evidence: Evidence | None = Field(default=None, description="Source text evidence for this operation.")

    @model_validator(mode="after")
    def validate_fields(self) -> "Operation":
        op = self.op
        if op == OpType.TRANSFER:
            if self.from_target is None:
                raise ValueError("TRANSFER requires 'from_target'")
            if self.to_target is None:
                raise ValueError("TRANSFER requires 'to_target'")
            if self.value is None:
                raise ValueError("TRANSFER requires 'value'")
        elif op == OpType.QUERY:
            if self.target is None:
                raise ValueError("QUERY requires 'target'")
        else:
            if self.target is None:
                raise ValueError(f"{op.value} requires 'target'")
            if self.value is None:
                raise ValueError(f"{op.value} requires 'value'")
        return self

    class Config:
        use_enum_values = True


class OperationSequence(BaseModel):
    """A sequence of operations that can be executed by the engine."""
    ops: list[Operation] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.ops)

    def __iter__(self):
        return iter(self.ops)

    def __getitem__(self, idx):
        return self.ops[idx]


class OperationJSON(Operation):
    """Operation with JSON-friendly field aliases ('from'/'to' → 'from_target'/'to_target')."""

    @model_validator(mode="before")
    @classmethod
    def map_aliases(cls, data: dict) -> dict:
        if isinstance(data, dict):
            if "from" in data:
                data["from_target"] = data.pop("from")
            if "to" in data:
                data["to_target"] = data.pop("to")
            # Handle evidence as nested dict
            if "evidence" in data and isinstance(data["evidence"], dict):
                pass  # Pydantic handles nested models automatically
        return data
