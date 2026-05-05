"""Report generator for SAGE — enhanced with evidence and event-bucket metrics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _ms(v: float) -> str:
    return f"{v:.1f} ms"


def _opt(v: Any) -> str:
    if v is None:
        return "—"
    return str(v)


def print_report(results: dict[str, Any]) -> None:
    """Print a Rich-formatted comparison table."""
    console = Console()
    metrics = results.get("metrics", {})
    benchmark = results.get("benchmark", "unknown")
    num_samples = results.get("num_samples", 0)

    console.print()
    console.print(f"[bold]SAGE Benchmark Report[/bold]")
    console.print(f"Benchmark: [cyan]{benchmark}[/cyan]")
    console.print(f"Samples:   {num_samples}")
    console.print()

    # Per-system table
    table = Table(title="System Comparison", title_style="bold")
    table.add_column("System", style="cyan")
    table.add_column("Samples", justify="right")
    table.add_column("Accuracy", justify="right")
    table.add_column("JSON OK", justify="right")
    table.add_column("Ops OK", justify="right")
    table.add_column("Evid OK", justify="right")
    table.add_column("Exec OK", justify="right")
    table.add_column("Unsup Rate", justify="right")
    table.add_column("Halluc Rate", justify="right")
    table.add_column("Avg Events", justify="right")
    table.add_column("Avg Latency", justify="right")

    for name in sorted([k for k in metrics if k != "overall"]):
        m = metrics[name]
        table.add_row(
            name,
            str(m.get("num_samples", 0)),
            _pct(m.get("accuracy", 0.0)),
            _pct(m.get("json_valid_rate", 0.0)),
            _pct(m.get("ops_valid_rate", 0.0)),
            _pct(m.get("evidence_valid_rate", 0.0)),
            _pct(m.get("execution_success_rate", 0.0)),
            _pct(m.get("unsupported_operation_rate", 0.0)),
            _pct(m.get("hallucinated_operation_rate", 0.0)),
            _opt(m.get("avg_events", "—")),
            _ms(m.get("avg_latency_ms", 0.0)),
        )

    overall = metrics.get("overall", {})
    if overall:
        table.add_section()
        table.add_row(
            "[bold]overall[/bold]",
            str(overall.get("num_samples", 0)),
            _pct(overall.get("accuracy", 0.0)),
            _pct(overall.get("json_valid_rate", 0.0)),
            _pct(overall.get("ops_valid_rate", 0.0)),
            _pct(overall.get("evidence_valid_rate", 0.0)),
            _pct(overall.get("execution_success_rate", 0.0)),
            _pct(overall.get("unsupported_operation_rate", 0.0)),
            _pct(overall.get("hallucinated_operation_rate", 0.0)),
            _opt(overall.get("avg_events", "—")),
            _ms(overall.get("avg_latency_ms", 0.0)),
            style="bold",
        )

    console.print(table)

    # Event bucket breakdown
    event_buckets = results.get("event_buckets")
    if event_buckets:
        console.print()
        btable = Table(title="Accuracy by Event Count", title_style="bold")
        btable.add_column("Event Bucket", style="cyan")
        btable.add_column("Samples", justify="right")
        btable.add_column("Accuracy", justify="right")
        for bucket, data in event_buckets.items():
            btable.add_row(bucket, str(data.get("samples", 0)),
                          _pct(data.get("accuracy", 0.0)))
        console.print(btable)

    console.print()


def save_report(results: dict[str, Any], output_path: Path) -> None:
    """Save the full benchmark report as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), **results}
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)
    console = Console()
    console.print(f"[green]Report saved to[/green] {output_path}")
