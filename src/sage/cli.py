"""CLI for SAGE: State-Aware Generative Engine.

Commands:
    generate-data  Generate synthetic training data and benchmarks.
    train-compiler Train the SAGE compiler model.
    train-direct   Train the direct-answer baseline model.
    eval           Evaluate on a benchmark file.
    eval-rule      Quick eval using the rule-based compiler.
    demo           Run a single demo query through the full SAGE pipeline.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sage import __version__
from sage.config import (
    EngineConfig,
    CompilerConfig,
    TrainingConfig,
    GeneratorConfig,
    EvalConfig,
)
from sage.engine.executor import Executor
from sage.engine.errors import EngineError
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.compiler.rule_compiler import RuleCompiler

app = typer.Typer(
    name="sage",
    help="SAGE: State-Aware Generative Engine",
    add_completion=False,
)
console = Console()


# ── generate-data ────────────────────────────────────────────────

@app.command("generate-data")
def generate_data(
    samples: int = typer.Option(1000, "--samples", "-n", help="Number of samples to generate"),
    min_events: int = typer.Option(3, "--min-events", help="Minimum events per story"),
    max_events: int = typer.Option(50, "--max-events", help="Maximum events per story"),
    noise_level: float = typer.Option(0.0, "--noise-level", help="Noise fraction (0.0-1.0)"),
    output_dir: Path = typer.Option(Path("data/generated"), "--output-dir", "-o"),
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b"),
    seed: int = typer.Option(42, "--seed"),
    distractor_people: int = typer.Option(0, "--distractor-people"),
    irrelevant_sentences: int = typer.Option(0, "--irrelevant-sentences"),
    shuffle: bool = typer.Option(False, "--shuffle"),
    generate_benchmarks: bool = typer.Option(False, "--benchmarks", help="Also generate standard benchmarks"),
):
    """Generate synthetic training data and benchmarks."""
    from sage.generator.dataset_writer import DatasetWriter

    config = GeneratorConfig(
        output_dir=output_dir,
        benchmarks_dir=benchmarks_dir,
        seed=seed,
        min_events=min_events,
        max_events=max_events,
        noise_level=noise_level,
        distractor_people=distractor_people,
        irrelevant_sentences=irrelevant_sentences,
        shuffle_surface=shuffle,
    )

    console.print(f"[bold blue]SAGE Data Generator[/]")
    console.print(f"  Samples: {samples}")
    console.print(f"  Events: {min_events}–{max_events}")
    console.print(f"  Noise: {noise_level}")
    console.print(f"  Output: {output_dir}")

    writer = DatasetWriter(output_dir=output_dir, seed=seed)

    console.print("\n[dim]Generating samples...[/]")
    records = writer.generate_samples(
        num_samples=samples,
        min_events=min_events,
        max_events=max_events,
        noise_level=noise_level,
        distractor_people=distractor_people,
        irrelevant_sentences=irrelevant_sentences,
        shuffle_surface=shuffle,
    )
    console.print(f"  Generated {len(records)} samples")

    paths = writer.write_splits(records)
    for split, path in paths.items():
        console.print(f"  [green]{split}[/]: {path}")

    if generate_benchmarks:
        console.print("\n[dim]Generating benchmarks...[/]")
        writer.generate_benchmarks(benchmarks_dir)
        for name in ["easy", "medium", "hard", "long", "noise_stress"]:
            bp = benchmarks_dir / f"{name}.jsonl"
            if bp.exists():
                console.print(f"  [green]{name}[/]: {bp}")


# ── train-compiler ───────────────────────────────────────────────

@app.command("train-compiler")
def train_compiler_cmd(
    model: str = typer.Option("google/flan-t5-small", "--model", "-m"),
    train_path: Path = typer.Option(..., "--train", "-t", help="Path to training JSONL"),
    dev_path: Optional[Path] = typer.Option(None, "--dev", "-d", help="Path to dev JSONL"),
    epochs: int = typer.Option(3, "--epochs", "-e"),
    batch_size: int = typer.Option(8, "--batch-size"),
    output_dir: Path = typer.Option(Path("checkpoints/compiler"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
    learning_rate: float = typer.Option(5e-5, "--lr"),
):
    """Train the SAGE compiler model."""
    from sage.training.train_compiler import train_compiler

    config = TrainingConfig(
        model_name=model,
        output_dir=str(output_dir),
        num_epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        use_cpu=use_cpu,
    )

    console.print(f"[bold blue]SAGE Compiler Training[/]")
    console.print(f"  Model: {model}")
    console.print(f"  Train: {train_path}")
    console.print(f"  Epochs: {epochs}")
    console.print(f"  Device: {'CPU' if use_cpu else 'GPU'}")

    train_compiler(config, train_path, dev_path)


# ── train-direct ─────────────────────────────────────────────────

@app.command("train-direct")
def train_direct_cmd(
    model: str = typer.Option("google/flan-t5-small", "--model", "-m"),
    train_path: Path = typer.Option(..., "--train", "-t", help="Path to training JSONL"),
    dev_path: Optional[Path] = typer.Option(None, "--dev", "-d"),
    epochs: int = typer.Option(3, "--epochs", "-e"),
    batch_size: int = typer.Option(8, "--batch-size"),
    output_dir: Path = typer.Option(Path("checkpoints/direct"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
    learning_rate: float = typer.Option(5e-5, "--lr"),
):
    """Train the direct-answer baseline model."""
    from sage.training.train_direct_baseline import train_direct_baseline

    config = TrainingConfig(
        model_name=model,
        output_dir=str(output_dir),
        num_epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        use_cpu=use_cpu,
    )

    console.print(f"[bold blue]Direct Baseline Training[/]")
    console.print(f"  Model: {model}")
    console.print(f"  Train: {train_path}")
    console.print(f"  Epochs: {epochs}")
    console.print(f"  Device: {'CPU' if use_cpu else 'GPU'}")

    train_direct_baseline(config, train_path, dev_path)


# ── eval ─────────────────────────────────────────────────────────

@app.command("eval")
def eval_cmd(
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    compiler_checkpoint: Optional[Path] = typer.Option(None, "--compiler", "-c", help="Path to compiler checkpoint"),
    direct_checkpoint: Optional[Path] = typer.Option(None, "--direct", "-d", help="Path to direct baseline checkpoint"),
    output_dir: Path = typer.Option(Path("outputs"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
    skip_model: bool = typer.Option(False, "--skip-model", help="Skip model-based systems"),
):
    """Evaluate on a benchmark file."""
    from sage.eval.run_benchmark import run_benchmark

    config = EvalConfig(
        benchmark_path=benchmark,
        compiler_checkpoint=compiler_checkpoint,
        direct_baseline_checkpoint=direct_checkpoint,
        output_dir=output_dir,
        use_cpu=use_cpu,
    )

    console.print(f"[bold blue]SAGE Evaluation[/]")
    console.print(f"  Benchmark: {benchmark}")

    results = run_benchmark(benchmark, config)

    from sage.eval.report import print_report, save_report
    print_report(results)
    save_report(results, output_dir / "report.json")
    console.print(f"\n[dim]Report saved to {output_dir / 'report.json'}[/]")


# ── eval-rule ────────────────────────────────────────────────────

@app.command("eval-rule")
def eval_rule_cmd(
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    max_samples: int = typer.Option(100, "--max-samples", "-n", help="Max samples to evaluate"),
):
    """Quick evaluation using only the rule-based compiler (no model needed)."""
    from sage.eval.run_benchmark import run_rule_only

    console.print(f"[bold blue]SAGE Rule Compiler Eval[/]")
    console.print(f"  Benchmark: {benchmark}")

    results = run_rule_only(benchmark, max_samples)

    from sage.eval.report import print_report
    print_report(results)


# ── demo ─────────────────────────────────────────────────────────

@app.command("demo")
def demo_cmd(
    text: str = typer.Option(
        "Latif has 5 coins. Arno gives Latif 3 coins. Latif spends 2 coins. "
        "Question: How many coins does Latif have?",
        "--text", "-t",
        help="Story text to process through SAGE pipeline",
    ),
    debug: bool = typer.Option(False, "--debug", help="Show debug information"),
    compare_direct: bool = typer.Option(False, "--compare", help="Also show direct baseline answer"),
):
    """Run a single query through the full SAGE pipeline."""
    engine_config = EngineConfig()
    executor = Executor(config=engine_config)
    verifier = Verifier(config=engine_config)
    renderer = Renderer()
    rule_compiler = RuleCompiler()

    console.print(Panel.fit(text, title="[bold]Input Story[/]"))

    # Step 1: Compile with rule compiler
    t0 = time.time()
    ops_raw, success = rule_compiler.compile(text)
    compile_time = (time.time() - t0) * 1000

    if not success:
        console.print("[red]Rule compiler failed to compile the story.[/]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Compiled Operations[/] ([dim]{compile_time:.1f}ms[/]):")
    console.print_json(json.dumps(ops_raw))

    # Step 2: Verify
    ops, ver_result = verifier.verify(json.dumps(ops_raw))
    if not ver_result.valid_ops:
        console.print("[red]Verification failed:[/]")
        for err in ver_result.errors:
            console.print(f"  [red]✗[/] {err}")
        raise typer.Exit(1)

    # Step 3: Execute
    result = executor.execute(ops)

    # Step 4: Render
    answer = renderer.render(result)

    console.print(f"\n[bold green]Answer:[/] {answer}")

    if debug:
        debug_info = renderer.render_debug(result, input_text=text, compiled_ops=ops_raw)
        console.print("\n[bold]Debug Info:[/]")
        console.print_json(json.dumps(debug_info, default=str))

    if compare_direct:
        try:
            from sage.baselines.direct_answer_model import DirectAnswerModel
            direct = DirectAnswerModel(use_cpu=True)
            direct.load()
            direct_answer = direct.answer(text)
            console.print(f"\n[bold yellow]Direct Baseline:[/] {direct_answer}")
        except Exception as e:
            console.print(f"\n[dim]Direct baseline unavailable: {e}[/]")


# ── info ─────────────────────────────────────────────────────────

@app.command("info")
def info_cmd():
    """Show SAGE system information."""
    console.print(Panel.fit(
        f"[bold]SAGE v{__version__}[/]\n\n"
        "State-Aware Generative Engine\n\n"
        "Pipeline:\n"
        "  Input Text → Compiler → JSON Ops → Verifier → Engine → Renderer → Answer\n\n"
        "Commands:\n"
        "  generate-data   Create synthetic training data\n"
        "  train-compiler  Train SAGE compiler model\n"
        "  train-direct    Train direct-answer baseline\n"
        "  eval            Full evaluation on benchmarks\n"
        "  eval-rule       Quick eval with rule compiler only\n"
        "  demo            Single query demo\n",
        title="SAGE"
    ))


# ── version ──────────────────────────────────────────────────────

@app.command("version")
def version_cmd():
    """Print version."""
    console.print(f"SAGE v{__version__}")


def main():
    app()


if __name__ == "__main__":
    main()
