from sage.core.domain import SageDomain
from sage.core.operation import Operation
from sage.core.evidence import Evidence
from sage.core.query import QueryResult

class SpecSyncDomain(SageDomain):
    def __init__(self):
        super().__init__("specsync", version="0.1.0", description="Requirement-to-code tracing and coverage")

    def compile(self, input_data, context=None):
        from pathlib import Path
        p = Path(input_data)
        if not p.exists():
            return []
        from sage.domains.specsync.markdown_parser import parse_markdown_files
        return parse_markdown_files(p)

    def answer(self, state, question, context=None):
        from sage.domains.specsync.specsync_ask import SpecSyncAsk
        ask = SpecSyncAsk(state)
        result = ask.ask(question)
        return QueryResult(answer=result.get("text", result.get("answer", "")), evidence=result.get("evidence", []))

    def render(self, state, fmt="text", context=None):
        from sage.domains.specsync.specsync_renderer import render_specsync
        return render_specsync(state, fmt)
