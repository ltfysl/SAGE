"""Incident report renderer for SAGE Incident Lens."""

from __future__ import annotations
from pathlib import Path
from datetime import datetime


def render_incident_report(state: dict) -> str:
    """Render incident state as a readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("SAGE Incident Lens — Laravel Log Analysis")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"First error:  {state.get('first_error_at', 'N/A')}")
    lines.append(f"Last error:   {state.get('last_error_at', 'N/A')}")
    lines.append(f"Total errors: {state.get('total_errors', 0)}")
    lines.append(f"Top exception: {state.get('top_exception', 'N/A')}")
    lines.append(f"Components:   {', '.join(state.get('affected_components', [])) or 'none'}")
    lines.append("")

    lines.append("Error Count by Type:")
    for op_type, count in sorted(state.get("error_count_by_type", {}).items()):
        lines.append(f"  {op_type}: {count}")
    lines.append("")

    for section, key, label in [
        ("Mail Failures", "mail_failures", "MAIL_FAILURE"),
        ("Queue Failures", "queue_failures", "QUEUE_FAILURE"),
        ("Database Errors", "database_errors", "DATABASE_ERROR"),
        ("Failed Jobs", "failed_jobs", "FAILED_JOB"),
    ]:
        items = state.get(key, [])
        if items:
            lines.append(f"{section} ({len(items)}):")
            for item in items[:5]:
                lines.append(f"  {item['timestamp']}: {item['message']}")
            lines.append("")

    lines.append("Timeline (last 20 events):")
    for event in state.get("timeline", []):
        lines.append(f"  {event['timestamp']} [{event['op']}] {event['message']}")

    return "\n".join(lines)


def render_markdown_report(state: dict, output_path: Path = None) -> str:
    """Render incident state as a Markdown report."""
    lines = []
    lines.append("# SAGE Incident Lens Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| First Error | {state.get('first_error_at', 'N/A')} |")
    lines.append(f"| Last Error | {state.get('last_error_at', 'N/A')} |")
    lines.append(f"| Total Errors | {state.get('total_errors', 0)} |")
    lines.append(f"| Top Exception | `{state.get('top_exception', 'N/A')}` |")
    lines.append(f"| Affected Components | {', '.join(state.get('affected_components', [])) or 'none'} |")
    lines.append("")
    lines.append("## Error Count by Type")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for op_type, count in sorted(state.get("error_count_by_type", {}).items()):
        lines.append(f"| {op_type} | {count} |")
    lines.append("")

    for section, key in [
        ("Mail Failures", "mail_failures"),
        ("Queue Failures", "queue_failures"),
        ("Database Errors", "database_errors"),
        ("Failed Jobs", "failed_jobs"),
    ]:
        items = state.get(key, [])
        if items:
            lines.append(f"## {section}")
            lines.append("")
            for item in items[:10]:
                lines.append(f"- `{item['timestamp']}`: {item['message']}")
            lines.append("")

    lines.append("## Timeline")
    lines.append("")
    for event in state.get("timeline", []):
        lines.append(f"- `{event['timestamp']}` **[{event['op']}]** {event['message']}")

    md = "\n".join(lines)
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md)
    return md
