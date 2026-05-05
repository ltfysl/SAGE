"""Operation verifier for SAGE — with evidence verification.

Validates JSON output from compilers before execution.
Catches malformed JSON, invalid operation types, missing fields,
type errors, and invalid evidence spans.
"""

from __future__ import annotations

import json
import re
from typing import Any

from sage.schemas.ops import Operation, OpType, OperationJSON, Evidence
from sage.schemas.state import VerificationResult
from sage.config import EngineConfig


class Verifier:
    """Validates compiled operation sequences before execution.

    Supports:
    - JSON syntax validation
    - Operation schema validation
    - Evidence span verification
    """

    VALID_OPS = {op.value for op in OpType}

    def __init__(self, config: EngineConfig | None = None):
        self.config = config or EngineConfig()
        self._warnings: list[str] = []
        self._errors: list[str] = []

    # ── JSON parsing ──────────────────────────────────────────────

    def verify_json(self, raw: str) -> tuple[list[dict[str, Any]] | None, VerificationResult]:
        """Parse and validate JSON from a compiler output string."""
        self._warnings = []
        self._errors = []

        parsed = None
        valid_json = False
        try:
            parsed = json.loads(raw)
            valid_json = True
        except json.JSONDecodeError as e:
            self._errors.append(f"Invalid JSON: {e}")
            recovered = self._try_recover_json(raw)
            if recovered is not None:
                parsed = recovered
                valid_json = True
                self._warnings.append("JSON was recovered from malformed output")

        if not valid_json or parsed is None:
            return None, VerificationResult(
                valid_json=False, valid_ops=False, execution_success=False,
                warnings=self._warnings, errors=self._errors,
            )

        if not isinstance(parsed, list):
            self._errors.append("Output is not a JSON array")
            return None, VerificationResult(
                valid_json=True, valid_ops=False, execution_success=False,
                warnings=self._warnings, errors=self._errors,
            )

        return parsed, VerificationResult(
            valid_json=True, valid_ops=True, execution_success=True,
            warnings=self._warnings, errors=self._errors,
        )

    # ── Operation validation ──────────────────────────────────────

    def verify_ops(self, raw_ops: list[dict[str, Any]]) -> tuple[list[Operation] | None, VerificationResult]:
        """Validate a list of raw operation dicts against the Operation schema."""
        self._warnings = []
        self._errors = []
        validated: list[Operation] = []

        for i, op_dict in enumerate(raw_ops):
            if not isinstance(op_dict, dict):
                self._errors.append(f"Operation {i} is not a dict: {type(op_dict)}")
                continue

            if "op" not in op_dict:
                self._errors.append(f"Operation {i} missing 'op' field")
                continue

            op_type = op_dict.get("op", "").upper()
            if op_type not in self.VALID_OPS:
                self._errors.append(
                    f"Operation {i} has invalid op type '{op_type}'. Valid: {self.VALID_OPS}"
                )
                continue

            try:
                clean_dict = dict(op_dict)
                if "from" in clean_dict:
                    clean_dict["from_target"] = clean_dict.pop("from")
                if "to" in clean_dict:
                    clean_dict["to_target"] = clean_dict.pop("to")
                # evidence dict will be auto-parsed by Pydantic if present
                op_obj = Operation(**clean_dict)
                validated.append(op_obj)
            except Exception as e:
                self._errors.append(f"Operation {i} validation failed: {e}")
                continue

        valid_ops = len(self._errors) == 0
        return validated, VerificationResult(
            valid_json=True, valid_ops=valid_ops,
            execution_success=valid_ops,
            warnings=self._warnings, errors=self._errors,
        )

    # ── Evidence verification ─────────────────────────────────────

    def verify_evidence(self, ops: list[Operation], story_text: str) -> VerificationResult:
        """Check that every operation's evidence span exists in the story text.

        Rules:
        - evidence.span must be an exact substring of story_text
        - story_text[evidence.start:evidence.end] must equal evidence.span
        - Operations without evidence are INVALID
        - For SET/ADD/SUB: target person and object must appear in evidence span
        - For TRANSFER: both persons and object must appear in evidence span
        - For QUERY: target person and object must appear in evidence span
        - For non-QUERY ops: the value must appear as a number in the evidence span
        """
        self._warnings = []
        self._errors = []

        for i, op in enumerate(ops):
            if op.evidence is None:
                self._errors.append(
                    f"Operation {i} ({op.op}): missing evidence — evidence is required"
                )
                continue

            ev = op.evidence
            span = ev.span
            start = ev.start
            end = ev.end

            # Check span exists at the claimed offsets
            if start < 0 or end > len(story_text) or start >= end:
                self._errors.append(
                    f"Operation {i} ({op.op}): evidence offsets [{start}:{end}] "
                    f"out of bounds (story length={len(story_text)})"
                )
                continue

            actual_span = story_text[start:end]
            if actual_span != span:
                self._errors.append(
                    f"Operation {i} ({op.op}): evidence span mismatch — "
                    f"claimed '{span[:50]}' but story[{start}:{end}] = '{actual_span[:50]}'"
                )
                continue

            span_lower = span.lower()

            # For non-QUERY ops, check the value appears
            if op.op != OpType.QUERY and op.value is not None:
                if str(op.value) not in span:
                    self._errors.append(
                        f"Operation {i} ({op.op}): value {op.value} not found "
                        f"in evidence span '{span[:80]}'"
                    )
                    continue

            # Check person and object names appear in evidence
            if op.op in (OpType.SET, OpType.ADD, OpType.SUB):
                if op.target:
                    parts = op.target.split(".", 1)
                    if len(parts) == 2:
                        person, obj = parts
                        if person.lower() not in span_lower:
                            self._warnings.append(
                                f"Operation {i} ({op.op}): person '{person}' "
                                f"not found in evidence span"
                            )
                        if obj.lower() not in span_lower:
                            self._warnings.append(
                                f"Operation {i} ({op.op}): object '{obj}' "
                                f"not found in evidence span"
                            )

            elif op.op == OpType.TRANSFER:
                if op.from_target:
                    parts = op.from_target.split(".", 1)
                    if parts and parts[0].lower() not in span_lower:
                        self._warnings.append(
                            f"Operation {i} (TRANSFER): from-person '{parts[0]}' "
                            f"not found in evidence span"
                        )
                if op.to_target:
                    parts = op.to_target.split(".", 1)
                    if parts and parts[0].lower() not in span_lower:
                        self._warnings.append(
                            f"Operation {i} (TRANSFER): to-person '{parts[0]}' "
                            f"not found in evidence span"
                        )

            elif op.op == OpType.QUERY:
                if op.target:
                    parts = op.target.split(".", 1)
                    if len(parts) == 2:
                        person, obj = parts
                        if person.lower() not in span_lower and obj.lower() not in span_lower:
                            self._warnings.append(
                                f"Operation {i} (QUERY): target info not found in evidence span"
                            )

        valid_evidence = len(self._errors) == 0
        return VerificationResult(
            valid_json=True, valid_ops=True, execution_success=valid_evidence,
            warnings=self._warnings, errors=self._errors,
        )

    # ── Full verification pipeline ────────────────────────────────

    def verify(self, raw: str, story_text: str | None = None) -> tuple[list[Operation] | None, VerificationResult]:
        """Full verification: JSON parse + operation validation + (optional) evidence check.

        Args:
            raw: Raw string from compiler.
            story_text: Original story text for evidence verification.

        Returns:
            Tuple of (Operations or None, VerificationResult).
        """
        raw_ops, json_result = self.verify_json(raw)
        if raw_ops is None:
            return None, json_result

        ops, ops_result = self.verify_ops(raw_ops)
        if ops is None:
            return None, ops_result

        # Evidence check
        ev_result = None
        if story_text is not None:
            ev_result = self.verify_evidence(ops, story_text)

        all_warnings = json_result.warnings + ops_result.warnings
        all_errors = json_result.errors + ops_result.errors
        if ev_result:
            all_warnings += ev_result.warnings
            all_errors += ev_result.errors

        return ops, VerificationResult(
            valid_json=json_result.valid_json,
            valid_ops=ops_result.valid_ops,
            execution_success=(ev_result.execution_success if ev_result else ops_result.execution_success),
            warnings=all_warnings,
            errors=all_errors,
        )

    @staticmethod
    def _try_recover_json(raw: str) -> list[dict[str, Any]] | None:
        """Try to recover a JSON array from malformed output."""
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            return None
