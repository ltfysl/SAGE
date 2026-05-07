"""SpecSync renderer — text, markdown, json output."""
import json

def render_specsync(state, fmt="text"):
    d = state.to_dict() if hasattr(state, "to_dict") else state
    if fmt == "json":
        return json.dumps(d, indent=2, default=str)
    ops = d.get("operations", state.operations if hasattr(state, "operations") else [])
    from sage.domains.specsync.coverage_engine import CoverageState
    cov = CoverageState()
    for op in ops:
        cov.apply(op)
    s = cov.summary()
    if fmt == "markdown":
        lines = ["# SpecSync Report","","## Summary",""]
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        for k,v in s.items():
            lines.append("| "+k.replace(chr(95),chr(32)).title()+" | "+str(v)+" |")
        lines.append("")
        if s.get("requirements"):
            lines.append("## Requirements")
            for r in cov.requirements:
                lines.append("- **"+r.get("id","?")+"**: "+r.get("description","")[:120])
        if s.get("missing_items"):
            lines.append("")
            lines.append("## Missing / Unclear")
            for m in cov.missing:
                lines.append("- MISSING: "+m.get("description","")[:120])
        return chr(10).join(lines)
    else:
        lines = ["="*60,"SAGE SpecSync","="*60,""]
        for k,v in s.items():
            lines.append(k.replace(chr(95),chr(32)).title()+": "+str(v))
        return chr(10).join(lines)
