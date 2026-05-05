"""Pydantic schemas for SAGE state representation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from sage.schemas.ops import Operation


class StateEntry(BaseModel):
    """A single entry in the state store."""

    key: str
    value: int
    created_at: int = Field(default=0, description="Step number when this entry was first set.")
    updated_at: int = Field(default=0, description="Step number when this entry was last modified.")
    access_count: int = Field(default=0)


class StateSnapshot(BaseModel):
    """A full snapshot of the state store at a point in time."""

    entries: dict[str, int] = Field(default_factory=dict)
    step: int = Field(default=0)


class StateTrace(BaseModel):
    """A trace of state changes for debugging."""

    operations: list[dict[str, Any]] = Field(default_factory=list)
    state_before: dict[str, int] = Field(default_factory=dict)
    state_after: dict[str, int] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of executing an operation sequence."""

    answer: int | None = Field(default=None, description="The final answer value.")
    target: str | None = Field(default=None, description="The queried target.")
    valid: bool = Field(default=True)
    state_snapshot: dict[str, int] = Field(default_factory=dict)
    trace: list[StateTrace] = Field(default_factory=list)
    error: str | None = Field(default=None)


class VerificationResult(BaseModel):
    """Result of verifying an operation sequence."""

    valid_json: bool = Field(default=True)
    valid_ops: bool = Field(default=True)
    execution_success: bool = Field(default=True)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
