"""CodeMapDomain adapter — wraps CodeMap as a SAGE domain."""
from sage.core.domain import SageDomain
from sage.core.evidence import Evidence
from sage.core.operation import Operation
from sage.core.query import QueryResult

class CodeMapDomain(SageDomain):
    def __init__(self):
        super().__init__("codemap", version="0.9.0",
                         description="Framework-agnostic static code architecture mapping")

    def compile(self, input_data, context=None):
        from sage.domains.codemap.codemap_scan import run_codemap_scan
        result = run_codemap_scan(input_data)
        files = result.get("files", {})
        ops = []
        for fp, file_ops in files.items():
            for fo in file_ops:
                ev = fo.get("evidence", {})
                ops.append(Operation(
                    op=fo.get("op", "UNKNOWN"), domain="codemap",
                    payload=fo,
                    evidence=Evidence(
                        file=ev.get("file"), line=ev.get("line"),
                        span=ev.get("span"), confidence=ev.get("confidence", 1.0),
                        parser=ev.get("parser")
                    )
                ))
        return ops

    def answer(self, state, question, context=None):
        from sage.domains.codemap.codemap_ask import CodemapAsk
        from sage.domains.codemap.codemap_scan import load_codemap
        if context and "map_path" in context:
            data = load_codemap(context["map_path"])
            ask = CodemapAsk(data)
            result = ask.ask(question)
            return QueryResult(
                answer=result.get("text", "No answer"),
                evidence=result.get("evidence", []),
                limitations=["Static analysis only."]
            )
        return QueryResult(answer="No codemap loaded", limitations=["map_path not in context"])

    def render(self, state, fmt="text", context=None):
        if fmt == "markdown":
            from sage.domains.codemap.codemap_renderer import render_summary
            return render_summary(state.to_dict() if hasattr(state, 'to_dict') else state)
        return super().render(state, fmt, context)
