"""Report generator for SAGE benchmarks.

Produces Rich-formatted comparison tables in the terminal and JSON
reports on disk so that benchmark results are easy to inspect and share.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


def _format_pct(value: float) -> str:
    """Format a float as a percentage string with one decimal."""
    return f"{value * 100:.1f}%"


def _format_ms(value: float) -> str:
    """Format a float as milliseconds with one decimal."""
    return f"{value:.1f}"


def _format_optional_int(value: int | None) -> str:
    """Format an optional int, using '—' for None."""
    if value is None:
        return "—"
    return str(value)


def _format_optional_float(value: float | None) -> str:
    """Format an optional float, using '—' for None."""
    if value is None:
        return "—"
    return f"{value:.1f}"


def print_report(results: dict[str, Any]) -> None:
    """Print a Rich-formatted comparison table to the terminal.

    The table has one row per system and columns for accuracy, JSON
    validity, operation validity, execution success, and latency.
    An additional "overall" row shows dataset-wide aggregates.

    Args:
        results: The dict returned by ``run_benchmark``.
    """
    console = Console()
    metrics = results.get("metrics", {})
    benchmark = results.get("benchmark", "unknown")
    num_samples = results.get("num_samples", 0)

    # Header
    console.print()
    console.print(f"[bold]SAGE Benchmark Report[/bold]")
    console.print(f"Benchmark: [cyan]{benchmark}[/cyan]")
    console.print(f"Samples:   {num_samples}")
    console.print()

    # Per-system table
    table = Table(title="System Comparison", title_style="bold")
    table.add_column("System", style="cyan", no_wrap=True)
    table.add_column("Samples", justify="right")
    table.add_column("Accuracy", justify="right")
    table.add_column("JSON OK", justify="right")
    table.add_column("Ops OK", justify="right")
    table.add_column("Exec OK", justify="right")
    table.add_column("Avg Latency", justify="right")
    table.add_column("Tok In", justify="right")
    table.add_column("Tok Out", justify="right")

    system_names = [k for k in metrics if k != "overall"]
    for name in sorted(system_names):
        m = metrics[name]
        table.add_row(
            name,
            str(m.get("num_samples", 0)),
            _format_pct(m.get("accuracy", 0.0)),
            _format_pct(m.get("json_valid_rate", 0.0)),
            _format_pct(m.get("ops_valid_rate", 0.0)),
            _format_pct(m.get("execution_success_rate", 0.0)),
            _format_ms(m.get("avg_latency_ms", 0.0)) + " ms",
            _format_optional_float(m.get("avg_tokens_in")),
            _format_optional_float(m.get("avg_tokens_out")),
        )

    # Overall row
    overall = metrics.get("overall", {})
    if overall:
        table.add_section()
        table.add_row(
            "[bold]overall[/bold]",
            str(overall.get("num_samples", 0)),
            _format_pct(overall.get("accuracy", 0.0)),
            _format_pct(overall.get("json_valid_rate", 0.0)),
            _format_pct(overall.get("ops_valid_rate", 0.0)),
            _format_pct(overall.get("execution_success_rate", 0.0)),
            _format_ms(overall.get("avg_latency_ms", 0.0)) + " ms",
            _format_optional_float(overall.get("avg_tokens_in")),
            _format_optional_float(overall.get("avg_tokens_out")),
            style="bold",
        )

    console.print(table)
    console.print()


def save_report(results: dict[str, Any], output_path: Path) -> None:
    """Save the full benchmark report as a JSON file.

    The output includes a timestamp and the same structure returned by
    ``run_benchmark``, which makes it easy to load later for comparison
    or plotting.

    Args:
        results: The dict returned by ``run_benchmark``.
        output_path: Destination path (directories are created as needed).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **results,
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)

    console = Console()
    console.print(f"[green]Report saved to[/green] {output_path}")
