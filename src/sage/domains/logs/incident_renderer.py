"""Incident report renderer for SAGE Incident Lens."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime

def render_incident_report(state: dict) -> str:
    lines = ["=" * 60, "SAGE Incident Lens — Log Analysis", "=" * 60, ""]
    lines.append(f"First error:  {state.get('first_error_at', 'N/A')}")
    lines.append(f"Last error:   {state.get('last_error_at', 'N/A')}")
    lines.append(f"Total errors: {state.get('total_errors', 0)}")
    lines.append(f"Top exception: {state.get('top_exception', 'N/A')}")
    lines.append("")
    lines.append("Errors by type:")
    for t, c in sorted(state.get("error_count_by_type", {}).items()):
        lines.append(f"  {t}: {c}")
    lines.append("")
    lines.append("Timeline (last 20 events):")
    for e in state.get("timeline", [])[-20:]:
        lines.append(f"  {e['timestamp']} [{e['op']}] {e['message'][:100]}")
    return "\n".join(lines)

def render_markdown_report(state: dict, ops: list[dict], output_path: Path) -> str:
    lines = ["# SAGE Incident Lens Report", ""]
    lines.append(f"**Generated**: {datetime.now().isoformat()}", "")
    lines.append("## Summary", "")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| First Error | {state.get('first_error_at', 'N/A')} |")
    lines.append(f"| Last Error | {state.get('last_error_at', 'N/A')} |")
    lines.append(f"| Total Errors | {state.get('total_errors', 0)} |")
    lines.append(f"| Top Exception | `{state.get('top_exception', 'N/A')}` |")
    lines.append("")
    lines.append("## Errors by Type", "")
    for t, c in sorted(state.get("error_count_by_type", {}).items()):
        lines.append(f"- {t}: {c}")
    lines.append("")
    lines.append("## Timeline", "")
    for e in state.get("timeline", [])[-30:]:
        lines.append(f"- `{e['timestamp']}` **[{e['op']}]** {e['message'][:120]}")
    lines.append("")
    lines.append("## Evidence Highlights", "")
    for op in ops[:10]:
        ev = op.get("evidence", {}).get("span", "")[:240]
        lines.append(f"- **[{op.get('op','?')}]** {op.get('timestamp','?')}")
        lines.append(f"  {ev}")
        lines.append("")
    md = "\n".join(lines)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md)
    return md
