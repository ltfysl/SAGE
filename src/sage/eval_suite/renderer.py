"""SAGE eval suite renderer."""
import json

def render_results(results, fmt="markdown"):
    if isinstance(results, list): results_list = results
    else: results_list = [results]
    if fmt == "json":
        return json.dumps([r.to_dict() for r in results_list], indent=2, default=str)
    nl = chr(10)
    if fmt == "markdown":
        lines = ["# SAGE Evaluation Report", ""]
        for r in results_list:
            icon = chr(9989) if r.passed else chr(10060)
            lines.append(f"## Suite: {r.suite} {icon}")
            lines.append("")
            lines.append(r.summary)
            lines.append("")
            lines.append("| Metric | Value | Passed |")
            lines.append("|---|---|---|")
            for m in r.metrics:
                p = chr(9989) if m.passed else (chr(10060) if m.passed is not None else chr(45))
                lines.append(f"| {m.name} | {m.value} | {p} |")
            if r.warnings:
                lines.append("")
                lines.append("**Warnings:**")
                for w in r.warnings:
                    lines.append(f"- {w}")
            lines.append("")
        return nl.join(lines)
    else:
        lines = []
        for r in results_list:
            icon = "PASS" if r.passed else "FAIL"
            lines.append(f"{r.suite}: {icon} — {r.summary}")
            for m in r.metrics:
                p = "OK" if m.passed else ("FAIL" if m.passed is not None else "-")
                lines.append(f"  {m.name}: {m.value} [{p}]")
        return nl.join(lines)
