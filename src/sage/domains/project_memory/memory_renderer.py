"""Project Memory renderer."""
import json
def render_memory(state, fmt="text"):
    d = state.to_dict() if hasattr(state,"to_dict") else state
    if fmt == "json": return json.dumps(d, indent=2, default=str)
    from sage.domains.project_memory.memory_engine import MemoryState
    ms = MemoryState()
    ops = d.get("operations", state.operations if hasattr(state,"operations") else [])
    for op in ops: ms.apply(op)
    s = ms.summary()
    nl = chr(10)
    if fmt == "markdown":
        l = ["# Project Memory","","| Metric | Value |","|---|---|"]
        for k in ["decisions","tasks_total","tasks_done","blockers","open_questions","risks"]:
            l.append("| "+k.replace(chr(95),chr(32)).title()+" | "+str(s.get(k,0))+" |")
        if ms.blockers:
            l.append(""); l.append("## Blockers")
            for b in ms.blockers: l.append("- "+b.get("blocker","")[:120])
        if ms.risks:
            l.append(""); l.append("## Risks")
            for r in ms.risks: l.append("- "+r.get("risk","")[:120])
        if ms.decisions:
            l.append(""); l.append("## Decisions")
            for d in ms.decisions: l.append("- "+d.get("decision","")[:120])
        return nl.join(l)
    else:
        l = ["="*60,"SAGE Project Memory","="*60,""]
        for k,v in s.items(): l.append(k.replace(chr(95),chr(32)).title()+": "+str(v))
        if ms.blockers: l.append(""); l.append("BLOCKERS:");[l.append("  - "+b.get("blocker","")[:100])for b in ms.blockers]
        return nl.join(l)
