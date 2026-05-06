"""Renderer for SAGE CodeMap — outputs Markdown or plain text reports."""
from __future__ import annotations


def render_summary(state: dict) -> str:
    """Render a codemap summary as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("SAGE CodeMap — Architecture Summary")
    lines.append("=" * 60)
    lines.append("")

    files = state.get("files", {})
    lines.append(f"Files:          {len(files)}")
    lines.append(f"Operations:     {state.get('ops_count', 0)}")
    lines.append(f"Languages:      {', '.join(state.get('languages', []))}")
    lines.append(f"Frameworks:     {', '.join(state.get('frameworks', []))}")
    lines.append("")

    by_op = {}
    for ops in files.values():
        for op in ops:
            t = op.get("op", "?")
            by_op[t] = by_op.get(t, 0) + 1
    if by_op:
        lines.append("Operations by type:")
        for op_type, count in sorted(by_op.items(), key=lambda x: -x[1]):
            lines.append(f"  {op_type}: {count}")
    lines.append("")

    routes = state.get("routes", [])
    if routes:
        lines.append(f"Routes/Endpoints ({len(routes)}):")
        for r in routes[:15]:
            name = r.get("name", "?")
            fname = r.get("evidence", {}).get("file", "?").split("/")[-1]
            line = r.get("evidence", {}).get("line", "?")
            lines.append(f"  {name} → {fname}:{line}")
    lines.append("")

    services = state.get("services", [])
    if services:
        lines.append(f"Services ({len(services)}):")
        for s in services[:10]:
            lines.append(f"  {s.get('name', '?')}")
    lines.append("")

    symbols = state.get("symbols", {})
    if symbols:
        lines.append(f"Symbols: {len(symbols)} unique")
    lines.append("")

    return "\n".join(lines)


def render_ask_answer(question: str, answer: dict, ops: list[dict]) -> str:
    """Render an ask answer as plain text."""
    lines = []
    lines.append(f"Q: {question}")
    lines.append(f"A: {answer.get('text', 'No answer available.')}")
    lines.append("")

    evidence_ops = answer.get("evidence", [])
    if evidence_ops:
        lines.append("Evidence:")
        for i, op in enumerate(evidence_ops[:15]):
            name = op.get("name", op.get("path", "?"))
            fname = op.get("evidence", {}).get("file", op.get("file", "?"))
            line = op.get("evidence", {}).get("line", op.get("line", "?"))
            if isinstance(fname, str) and "/" in fname:
                fname = fname.split("/")[-1]
            lines.append(f"  {i+1}. {op.get('op','?')}: {name}")
            lines.append(f"     {fname}:{line}")
    lines.append("")

    notes = answer.get("notes", "")
    if notes:
        lines.append(f"Note: {notes}")
    return "\n".join(lines)


def render_impact(impact: dict) -> str:
    """Render impact analysis as plain text."""
    lines = []
    lines.append(f"Impact analysis for: {impact.get('file', '?')}")
    lines.append("")

    dependents = impact.get("dependents", [])
    if dependents:
        lines.append(f"Files that depend on this ({len(dependents)}):")
        for d in dependents[:10]:
            fname = d.get("file", "?")
            if isinstance(fname, str) and "/" in fname:
                fname = fname.split("/")[-1]
            lines.append(f"  - {fname} ({d.get('op', '?')})")
    else:
        lines.append("No files depend on this (based on static analysis).")
    lines.append("")

    dependencies = impact.get("dependencies", [])
    if dependencies:
        lines.append(f"Dependencies ({len(dependencies)}):")
        for d in dependencies[:10]:
            fname = d.get("file", "?")
            if isinstance(fname, str) and "/" in fname:
                fname = fname.split("/")[-1]
            lines.append(f"  - {fname} ({d.get('op', '?')})")
    lines.append("")

    notes = impact.get("notes", "")
    if notes:
        lines.append(f"Note: {notes}")
    return "\n".join(lines)
