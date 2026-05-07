"""LogsDomain adapter — wraps Incident Lens as a SAGE domain."""
from sage.core.domain import SageDomain
from sage.core.evidence import Evidence
from sage.core.operation import Operation
from sage.core.query import QueryResult

class LogsDomain(SageDomain):
    def __init__(self):
        super().__init__("logs", version="0.1.0",
                         description="Laravel log incident analysis")

    def compile(self, input_data, context=None):
        from sage.domains.logs.laravel_log_parser import parse_log_file
        from sage.domains.logs.log_compiler import LaravelLogCompiler
        blocks = parse_log_file(input_data)
        compiler = LaravelLogCompiler()
        raw_ops = compiler.compile(blocks)
        ops = []
        for ro in raw_ops:
            ev = ro.get("evidence", {})
            ops.append(Operation(
                op=ro.get("op", "UNKNOWN"), domain="logs",
                payload=ro,
                evidence=Evidence(
                    file=ro.get("file"),
                    span=ev.get("span"), confidence=ev.get("confidence", 1.0)
                )
            ))
        return ops

    def answer(self, state, question, context=None):
        from sage.domains.logs.incident_engine import IncidentState
        is_state = IncidentState()
        for op in state.operations:
            if hasattr(op, 'payload'):
                is_state.apply(op.payload)
        is_state.finalize()
        return QueryResult(answer=is_state.answer(question))

    def render(self, state, fmt="text", context=None):
        from sage.domains.logs.incident_renderer import render_incident_report
        from sage.domains.logs.incident_engine import IncidentState
        is_state = IncidentState()
        for op in state.operations:
            if hasattr(op, 'payload'):
                is_state.apply(op.payload)
        is_state.finalize()
        if fmt == "markdown":
            from sage.domains.logs.incident_renderer import render_markdown_report
            from pathlib import Path
            tmp = Path("data/reports/incident_report.md")
            tmp.parent.mkdir(parents=True, exist_ok=True)
            return render_markdown_report(is_state.to_dict(), [], tmp)
        return render_incident_report(is_state.to_dict())
