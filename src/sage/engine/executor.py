"""Deterministic state engine for SAGE.

Executes operation sequences against a StateStore,
producing execution results with full trace support.
"""

from sage.config import EngineConfig
from sage.engine.state_store import StateStore
from sage.engine.errors import ExecutionError
from sage.schemas.ops import Operation, OpType, OperationSequence
from sage.schemas.state import ExecutionResult, StateTrace


class Executor:
    """Deterministic executor for SAGE operation sequences.

    The executor is the core of SAGE. It takes compiled operations
    and runs them against a deterministic state store. The model
    never produces the final answer — the executor does.

    Every operation produces a trace entry for full debuggability.
    """

    def __init__(self, config: EngineConfig | None = None):
        self.config = config or EngineConfig()
        self.store = StateStore(
            default_value=self.config.default_value,
            allow_negative=self.config.allow_negative,
        )

    def execute(self, ops: list[Operation]) -> ExecutionResult:
        """Execute a sequence of operations and return the result.

        Args:
            ops: List of validated Operation objects.

        Returns:
            ExecutionResult with answer, trace, and validity.
        """
        self.store.reset()
        trace: list[StateTrace] = []
        answer: int | None = None
        query_target: str | None = None
        error: str | None = None

        try:
            for i, op in enumerate(ops):
                state_before = self.store.snapshot()

                op_dict = op.model_dump()

                match op.op:
                    case OpType.SET:
                        self.store.set(op.target, op.value)
                    case OpType.ADD:
                        self.store.add(op.target, op.value)
                    case OpType.SUB:
                        self.store.sub(op.target, op.value)
                    case OpType.TRANSFER:
                        self.store.transfer(op.from_target, op.to_target, op.value)
                    case OpType.QUERY:
                        answer = self.store.get(op.target)
                        query_target = op.target
                    case _:
                        raise ExecutionError(f"Unknown operation type: {op.op}")

                state_after = self.store.snapshot()

                trace.append(StateTrace(
                    operations=[op_dict],
                    state_before=state_before,
                    state_after=state_after,
                ))

        except Exception as e:
            error = str(e)
            return ExecutionResult(
                answer=None,
                target=query_target,
                valid=False,
                state_snapshot=self.store.snapshot(),
                trace=trace,
                error=error,
            )

        return ExecutionResult(
            answer=answer,
            target=query_target,
            valid=True,
            state_snapshot=self.store.snapshot(),
            trace=trace,
            error=None,
        )

    def execute_batch(self, ops_list: list[list[Operation]]) -> list[ExecutionResult]:
        """Execute multiple operation sequences."""
        return [self.execute(ops) for ops in ops_list]
