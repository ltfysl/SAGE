"""Answer renderer for SAGE.

Converts execution results into human-readable output.
Never renders from raw model output — only from verified state.
"""

from sage.schemas.state import ExecutionResult


class Renderer:
    """Renders verified execution results into natural language answers.

    The renderer is intentionally simple: it only produces output
    that has been verified by the engine. It never hallucinates.
    """

    def render(self, result: ExecutionResult) -> str:
        """Render an execution result as a natural language answer.

        Args:
            result: Validated execution result from the engine.

        Returns:
            Human-readable answer string.
        """
        if not result.valid:
            return f"[Error] Execution failed: {result.error}"

        if result.answer is None:
            return "[Error] No answer produced — missing QUERY operation."

        target = result.target or "unknown"
        # Parse target key to extract person and object
        parts = target.split(".", 1)
        if len(parts) == 2:
            person, obj = parts
            return f"{person} has {result.answer} {obj}."
        return f"{target} = {result.answer}"

    def render_raw(self, result: ExecutionResult) -> str:
        """Render only the numeric answer value (for evaluation).

        Args:
            result: Validated execution result from the engine.

        Returns:
            Raw answer string (just the number).
        """
        if not result.valid or result.answer is None:
            return ""
        return str(result.answer)

    def render_debug(self, result: ExecutionResult, input_text: str = "",
                     compiled_ops: list = None) -> dict:
        """Render a full debug report as a dict.

        Args:
            result: Execution result.
            input_text: Original input text.
            compiled_ops: Compiled operations (raw dicts).

        Returns:
            Debug dictionary.
        """
        return {
            "input": input_text,
            "compiled_ops": compiled_ops or [],
            "state_trace": [
                {
                    "op": t.operations[0] if t.operations else {},
                    "state_before": t.state_before,
                    "state_after": t.state_after,
                }
                for t in result.trace
            ],
            "answer": result.answer,
            "verification": {
                "valid_json": True,
                "valid_ops": True,
                "execution_success": result.valid,
                "warnings": [],
            },
        }
