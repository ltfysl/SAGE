"""Pydantic schemas for SAGE operations."""

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


class Operation(BaseModel):
    """A single state operation."""

    op: OpType
    target: str | None = Field(default=None, description="Target state key (e.g. 'Latif.coins').")
    value: int | None = Field(default=None, description="Numeric value for the operation.")
    from_target: str | None = Field(default=None, description="Source for TRANSFER operations.")
    to_target: str | None = Field(default=None, description="Destination for TRANSFER operations.")

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
            # SET, ADD, SUB
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


# Aliases for JSON-serialization fields
# We need to use aliases because the JSON format uses "from" and "to"
# but those are Python keywords.
class OperationJSON(Operation):
    """Operation with JSON-friendly field aliases."""

    @model_validator(mode="before")
    @classmethod
    def map_aliases(cls, data: dict) -> dict:
        """Map JSON keys 'from' and 'to' to Python-safe field names."""
        if isinstance(data, dict):
            if "from" in data:
                data["from_target"] = data.pop("from")
            if "to" in data:
                data["to_target"] = data.pop("to")
        return data
