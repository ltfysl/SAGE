"""Operation verifier for SAGE.

Validates JSON output from compilers before execution.
Catches malformed JSON, invalid operation types, missing fields,
and type errors.
"""

import json
from typing import Any

from sage.schemas.ops import Operation, OpType, OperationJSON
from sage.schemas.state import VerificationResult
from sage.config import EngineConfig


class Verifier:
    """Validates compiled operation sequences before execution."""

    VALID_OPS = {op.value for op in OpType}

    def __init__(self, config: EngineConfig | None = None):
        self.config = config or EngineConfig()
        self._warnings: list[str] = []
        self._errors: list[str] = []

    def verify_json(self, raw: str) -> tuple[list[dict[str, Any]] | None, VerificationResult]:
        """Parse and validate JSON from a compiler output string.

        Args:
            raw: Raw string output from the compiler (expected JSON array).

        Returns:
            Tuple of (parsed_ops or None, VerificationResult).
        """
        self._warnings = []
        self._errors = []

        # Try to parse JSON
        parsed = None
        valid_json = False
        try:
            parsed = json.loads(raw)
            valid_json = True
        except json.JSONDecodeError as e:
            self._errors.append(f"Invalid JSON: {e}")
            # Attempt recovery: try to find JSON array in the string
            recovered = self._try_recover_json(raw)
            if recovered is not None:
                parsed = recovered
                valid_json = True
                self._warnings.append("JSON was recovered from malformed output")

        if not valid_json or parsed is None:
            return None, VerificationResult(
                valid_json=False,
                valid_ops=False,
                execution_success=False,
                warnings=self._warnings,
                errors=self._errors,
            )

        if not isinstance(parsed, list):
            self._errors.append("Output is not a JSON array")
            return None, VerificationResult(
                valid_json=True,
                valid_ops=False,
                execution_success=False,
                warnings=self._warnings,
                errors=self._errors,
            )

        return parsed, VerificationResult(
            valid_json=True,
            valid_ops=True,
            execution_success=True,
            warnings=self._warnings,
            errors=self._errors,
        )

    def verify_ops(self, raw_ops: list[dict[str, Any]]) -> tuple[list[Operation] | None, VerificationResult]:
        """Validate a list of raw operation dicts.

        Args:
            raw_ops: List of operation dicts from parsed JSON.

        Returns:
            Tuple of (validated Operations or None, VerificationResult).
        """
        self._warnings = []
        self._errors = []
        validated: list[Operation] = []

        for i, op_dict in enumerate(raw_ops):
            if not isinstance(op_dict, dict):
                self._errors.append(f"Operation {i} is not a dict: {type(op_dict)}")
                continue

            # Check required 'op' field
            if "op" not in op_dict:
                self._errors.append(f"Operation {i} missing 'op' field")
                continue

            op_type = op_dict.get("op", "").upper()
            if op_type not in self.VALID_OPS:
                self._errors.append(
                    f"Operation {i} has invalid op type '{op_type}'. "
                    f"Valid types: {self.VALID_OPS}"
                )
                continue

            # Validate using Pydantic
            try:
                # Map 'from'/'to' to 'from_target'/'to_target' if needed
                clean_dict = dict(op_dict)
                if "from" in clean_dict:
                    clean_dict["from_target"] = clean_dict.pop("from")
                if "to" in clean_dict:
                    clean_dict["to_target"] = clean_dict.pop("to")

                op_obj = Operation(**clean_dict)
                validated.append(op_obj)
            except Exception as e:
                self._errors.append(f"Operation {i} validation failed: {e}")
                continue

        valid_ops = len(self._errors) == 0

        return validated, VerificationResult(
            valid_json=True,  # already passed JSON parse
            valid_ops=valid_ops,
            execution_success=valid_ops,  # can only execute if ops are valid
            warnings=self._warnings,
            errors=self._errors,
        )

    def verify(self, raw: str) -> tuple[list[Operation] | None, VerificationResult]:
        """Full verification pipeline: JSON parse + operation validation.

        Args:
            raw: Raw string from compiler.

        Returns:
            Tuple of (Operations or None, VerificationResult).
        """
        raw_ops, json_result = self.verify_json(raw)
        if raw_ops is None:
            return None, json_result

        ops, ops_result = self.verify_ops(raw_ops)
        if ops is None:
            return None, ops_result

        return ops, VerificationResult(
            valid_json=json_result.valid_json,
            valid_ops=ops_result.valid_ops,
            execution_success=True,
            warnings=json_result.warnings + ops_result.warnings,
            errors=json_result.errors + ops_result.errors,
        )

    @staticmethod
    def _try_recover_json(raw: str) -> list[dict[str, Any]] | None:
        """Try to recover a JSON array from malformed output."""
        # Look for the first '[' and last ']'
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError:
            return None
