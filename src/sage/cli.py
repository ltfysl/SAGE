"""CLI for SAGE: State-Aware Generative Engine.

Commands:
    generate-data            Generate synthetic training data and benchmarks.
    generate-ood-benchmarks  Generate out-of-distribution benchmarks.
    train-compiler           Train the SAGE compiler model.
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


# ── generate-ood-benchmarks ──────────────────────────────────────

@app.command("generate-ood-benchmarks")
def generate_ood_benchmarks_cmd(
    output_dir: Path = typer.Option(Path("data/benchmarks"), "--output-dir", "-o",
                                    help="Directory to write OOD benchmark files"),
    samples: int = typer.Option(200, "--samples", "-n", help="Samples per benchmark"),
):
    """Generate out-of-distribution benchmarks (ood_{names,phrasing,numbers,mixed})."""
    from sage.generator.ood_benchmarks import generate_all_ood_benchmarks

    console.print(f"[bold blue]SAGE OOD Benchmark Generator[/]")
    console.print(f"  Output: {output_dir}")
    console.print(f"  Samples per benchmark: {samples}")

    output_dir.mkdir(parents=True, exist_ok=True)

    generate_all_ood_benchmarks(output_dir, num_samples=samples)

    for name in ["ood_names", "ood_phrasing", "ood_numbers", "ood_mixed"]:
        bp = output_dir / f"{name}.jsonl"
        if bp.exists():
            lines = sum(1 for _ in open(bp))
            console.print(f"  [green]{name}[/]: {bp} ({lines} samples)")


# ── train-compiler ───────────────────────────────────────────────

@app.command("train-compiler")
def train_compiler_cmd(
    model: str = typer.Option("google/flan-t5-small", "--model", "-m"),
    train_path: Path = typer.Option(..., "--train", "-t", help="Path to training JSONL"),
    dev_path: Optional[Path] = typer.Option(None, "--dev", "-d", help="Path to dev JSONL"),
    epochs: int = typer.Option(3, "--epochs", "-e"),
    batch_size: int = typer.Option(8, "--batch-size"),
    output_dir: Path = typer.Option(Path("models/sage-compiler-flan-t5-small"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
    learning_rate: float = typer.Option(5e-5, "--lr"),
    max_input_length: int = typer.Option(1024, "--max-input-length"),
    max_target_length: int = typer.Option(1024, "--max-target-length"),
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
        max_input_length=max_input_length,
        max_output_length=max_target_length,
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
    output_dir: Path = typer.Option(Path("models/direct-flan-t5-small"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
    learning_rate: float = typer.Option(5e-5, "--lr"),
    max_input_length: int = typer.Option(1024, "--max-input-length"),
    max_target_length: int = typer.Option(32, "--max-target-length"),
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
        max_input_length=max_input_length,
        max_output_length=max_target_length,
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


# ── eval-oracle ──────────────────────────────────────────────────

@app.command("eval-oracle")
def eval_oracle_cmd(
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    max_samples: int = typer.Option(100, "--max-samples", "-n", help="Max samples"),
):
    """Evaluate using ground-truth ops directly (oracle SAGE). Should be ~100%."""
    from sage.eval.run_benchmark import run_oracle

    console.print(f"[bold blue]SAGE Oracle Eval[/]")
    console.print(f"  Benchmark: {benchmark}")

    results = run_oracle(benchmark, max_samples)

    from sage.eval.report import print_report
    print_report(results)


# ── inspect-failures ─────────────────────────────────────────────

@app.command("inspect-failures")
def inspect_failures_cmd(
    file: Path = typer.Option(..., "--file", "-f", help="Path to failures JSONL"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max failures to show"),
):
    """Print readable failure examples from a failures JSONL file."""
    import json as _json

    if not file.exists():
        console.print(f"[red]File not found: {file}[/]")
        raise typer.Exit(1)

    with open(file) as fh:
        lines = fh.readlines()[:limit]

    console.print(f"[bold]Failure Inspection[/] — {file} ([dim]{len(lines)} shown[/])")
    for i, line in enumerate(lines):
        rec = _json.loads(line)
        console.print()
        console.print(f"[bold cyan]#{i+1}[/] [yellow]{rec.get('id', '?')}[/] "
                      f"reason=[red]{rec.get('failure_reason', '?')}[/]")
        console.print(f"  Expected: [green]{rec.get('ground_truth_answer', '?')}[/]  "
                      f"Got: [red]{rec.get('predicted_answer', '?')}[/]")
        console.print(f"  Story: {rec.get('story', '')[:200]}...")
        miss = rec.get("missing_ops", [])
        extra = rec.get("extra_ops", [])
        if miss:
            console.print(f"  [red]Missing ops ({len(miss)}):[/] {[o.get('op') for o in miss]}")
        if extra:
            console.print(f"  [yellow]Extra ops ({len(extra)}):[/] {[o.get('op') for o in extra]}")


# ── eval-direct ──────────────────────────────────────────────────

@app.command("eval-direct")
def eval_direct_cmd(
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    max_samples: int = typer.Option(100, "--max-samples", "-n", help="Max samples to evaluate"),
):
    """Evaluate direct heuristic baseline on a benchmark."""
    from sage.eval.compare import run_direct_eval

    console.print(f"[bold blue]Direct Heuristic Eval[/]")
    console.print(f"  Benchmark: {benchmark}")

    results = run_direct_eval(benchmark, max_samples=max_samples)

    from sage.eval.report import print_report
    print_report(results)


# ── compare ──────────────────────────────────────────────────────

@app.command("compare")
def compare_cmd(
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b",
                                        help="Directory containing benchmark JSONL files"),
    max_per: int = typer.Option(100, "--max-samples", "-n", help="Max samples per benchmark"),
    output_dir: Path = typer.Option(Path("data/reports"), "--output-dir", "-o",
                                    help="Output directory for reports"),
):
    """Run full SAGE vs Direct comparison on all benchmarks."""
    from sage.eval.compare import run_full_comparison, generate_comparison_md, save_comparison_json

    console.print(f"[bold blue]SAGE vs Direct — Full Comparison[/]")
    console.print(f"  Benchmarks dir: {benchmarks_dir}")
    console.print(f"  Max per benchmark: {max_per}")

    with console.status("[bold green]Running comparison..."):
        comparison = run_full_comparison(benchmarks_dir, max_per=max_per)

    # Print summary table
    table = Table(title="SAGE vs Direct — Accuracy Summary")
    table.add_column("Benchmark", style="cyan")
    table.add_column("Events", justify="right")
    table.add_column("Oracle SAGE", justify="right")
    table.add_column("Rule SAGE", justify="right")
    table.add_column("Direct", justify="right")
    table.add_column("Advantage", justify="right")

    for name, data in comparison.get("benchmarks", {}).items():
        oracle = data["oracle_accuracy"]
        rule = data["rule_accuracy"]
        direct = data["direct_accuracy"]
        events = data.get("avg_events", 0)
        advantage = f"+{((rule - direct) / max(direct, 0.001) * 100):.0f}%" if direct > 0 else "N/A"
        table.add_row(
            name, str(int(events)),
            f"{oracle*100:.0f}%", f"{rule*100:.0f}%", f"{direct*100:.0f}%",
            advantage,
        )

    console.print(table)

    # Generate reports
    console.print("\n[dim]Generating reports...[/]")
    md_path = output_dir / "comparison_report.md"
    json_path = output_dir / "comparison_report.json"

    generate_comparison_md(comparison, md_path)
    save_comparison_json(comparison, json_path)

    console.print(f"  [green]Markdown report:[/] {md_path}")
    console.print(f"  [green]JSON report:[/]     {json_path}")

    # Print context advantage
    ca = comparison.get("context_advantage", {})
    console.print("\n[bold]Context-Scaling Advantage[/]")
    for key, data in ca.items():
        thresh = key.replace("threshold_", "")
        console.print(
            f"  At {thresh}% accuracy: SAGE handles up to {data['sage_max_events']} events, "
            f"Direct handles up to {data['direct_max_events']} events "
            f"({data['advantage_ratio']}x advantage)"
        )


# ── train-sklearn-compiler ─────────────────────────────────────

@app.command("train-sklearn-compiler")
def train_sklearn_compiler_cmd(
    train: Path = typer.Option(..., "--train", "-t", help="Path to sentence-level training JSONL"),
    output: Path = typer.Option(Path("models/sklearn-op-classifier.joblib"), "--output", "-o"),
):
    """Train sklearn operation classifier on sentence-level data."""
    from sage.baselines.sklearn_compiler import train_sklearn_compiler
    console.print("[bold blue]Training Sklearn Compiler[/]")
    train_sklearn_compiler(train, output)
    console.print(f"[green]Model saved to {output}[/]")


# ── train-sklearn-direct ────────────────────────────────────────

@app.command("train-sklearn-direct")
def train_sklearn_direct_cmd(
    train: Path = typer.Option(..., "--train", "-t", help="Path to story-level training JSONL"),
    output: Path = typer.Option(Path("models/sklearn-direct.joblib"), "--output", "-o"),
):
    """Train sklearn direct answer model."""
    from sage.baselines.sklearn_direct import train_sklearn_direct
    console.print("[bold blue]Training Sklearn Direct Model[/]")
    train_sklearn_direct(train, output)
    console.print(f"[green]Model saved to {output}[/]")


# ── eval-sklearn-compiler ───────────────────────────────────────

@app.command("eval-sklearn-compiler")
def eval_sklearn_compiler_cmd(
    model: Path = typer.Option(..., "--model", "-m", help="Path to sklearn compiler model"),
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    max_samples: int = typer.Option(100, "--max-samples", "-n"),
):
    """Evaluate sklearn compiler on a benchmark."""
    from sage.baselines.sklearn_compiler import load_sklearn_compiler
    from sage.eval.run_benchmark import _load_benchmark, _save_failures, _compute_diff
    from sage.engine.executor import Executor
    from sage.verifier.verifier import Verifier
    from sage.renderer.renderer import Renderer
    from sage.config import EngineConfig

    console.print("[bold blue]Sklearn Compiler Eval[/]")
    compiler = load_sklearn_compiler(model)

    samples = _load_benchmark(benchmark)[:max_samples]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    results = []
    for sample in samples:
        story = sample["story"]
        gt = str(sample["answer"])
        t0 = time.perf_counter()
        comp_raw, success = compiler.compile(story)
        comp_json = json.dumps(comp_raw)
        ops, vr = verifier.verify(comp_json, story_text=story)
        er = executor.execute(ops) if ops else None
        pred = renderer.render_raw(er) if er and er.valid else ""
        match = str(pred).strip() == gt.strip()
        missing, extra = _compute_diff(sample.get("ops", []), comp_raw)
        latency = (time.perf_counter() - t0) * 1000

        results.append({
            "id": sample.get("id", ""), "system": "sklearn_compiler",
            "ground_truth_answer": gt, "predicted_answer": pred,
            "answer_match": match, "compiled_output": comp_json,
            "execution_success": er.valid if er else False,
            "valid_json": vr.valid_json, "valid_ops": vr.valid_ops,
            "evidence_valid": vr.execution_success,
            "num_events": sample.get("metadata", {}).get("num_events", 0),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": latency,
            "ground_truth_ops": sample.get("ops", []),
            "compiled_ops_raw": comp_raw,
            "missing_ops": missing, "extra_ops": extra,
            "failure_reason": "" if match else "answer_mismatch",
        })

    _save_failures(results, benchmark)
    from sage.eval.metrics import compute_all_metrics
    from sage.eval.report import print_report
    print_report({
        "benchmark": str(benchmark), "num_samples": len(samples),
        "results": results, "metrics": compute_all_metrics(results),
    })


# ── eval-sklearn-direct ─────────────────────────────────────────

@app.command("eval-sklearn-direct")
def eval_sklearn_direct_cmd(
    model: Path = typer.Option(..., "--model", "-m"),
    benchmark: Path = typer.Option(..., "--benchmark", "-b"),
    max_samples: int = typer.Option(100, "--max-samples", "-n"),
):
    """Evaluate sklearn direct model on a benchmark."""
    from sage.baselines.sklearn_direct import SklearnDirectModel
    from sage.eval.run_benchmark import _load_benchmark

    console.print("[bold blue]Sklearn Direct Eval[/]")
    m = SklearnDirectModel()
    m.load(model)

    samples = _load_benchmark(benchmark)[:max_samples]
    results = []
    for sample in samples:
        story = sample["story"]
        gt = str(sample["answer"])
        pred = m.answer(story)
        match = str(pred).strip() == gt.strip()
        results.append({
            "id": sample.get("id", ""), "system": "sklearn_direct",
            "ground_truth_answer": gt, "predicted_answer": pred,
            "answer_match": match, "compiled_output": "",
            "execution_success": False, "valid_json": False,
            "valid_ops": False, "evidence_valid": False,
            "num_events": sample.get("metadata", {}).get("num_events", 0),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": 0.0,
            "ground_truth_ops": [], "compiled_ops_raw": [],
            "missing_ops": [], "extra_ops": [],
            "failure_reason": "" if match else "wrong_answer",
        })

    from sage.eval.metrics import compute_all_metrics
    from sage.eval.report import print_report
    print_report({
        "benchmark": str(benchmark), "num_samples": len(samples),
        "results": results, "metrics": compute_all_metrics(results),
    })


# ── eval-hybrid ───────────────────────────────────────────────────

@app.command("eval-hybrid")
def eval_hybrid_cmd(
    benchmark: Path = typer.Option(..., "--benchmark", "-b", help="Path to benchmark JSONL"),
    sklearn_model: Path = typer.Option(Path("models/sklearn-op-classifier.joblib"), "--sklearn-model", "-s"),
    max_samples: int = typer.Option(100, "--max-samples", "-n"),
    normalizer_threshold: float = typer.Option(0.72, "--normalizer-threshold", help="Min similarity for normalizer fallback"),
    conservative: bool = typer.Option(True, "--conservative/--no-conservative", help="Enable conservative mode (adversarial guard + evidence scoring)"),
):
    """Evaluate the hybrid SAGE compiler on a benchmark."""
    import json, time
    from sage.compiler.hybrid_compiler import HybridSAGECompiler, HybridCompilerConfig
    from sage.eval.run_benchmark import _load_benchmark, _save_failures, _compute_diff
    from sage.engine.executor import Executor
    from sage.verifier.verifier import Verifier
    from sage.renderer.renderer import Renderer
    from sage.config import EngineConfig

    console.print("[bold blue]Hybrid SAGE Compiler Eval[/]")
    console.print(f"  Normalizer threshold: {normalizer_threshold}, Conservative: {conservative}")

    config = HybridCompilerConfig(
        normalizer_threshold=normalizer_threshold,
        adversarial_guard_enabled=conservative,
        require_entity_confidence=conservative,
        fallback_to_noop_on_uncertainty=conservative,
    )
    compiler = HybridSAGECompiler(config=config)
    compiler.load(sklearn_model)
    compiler.reset_stats()

    samples = _load_benchmark(benchmark)[:max_samples]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    results = []
    for sample in samples:
        story = sample["story"]
        gt = str(sample["answer"])
        t0 = time.perf_counter()
        comp_raw, success = compiler.compile(story)
        comp_json = json.dumps(comp_raw)
        ops, vr = verifier.verify(comp_json, story_text=story)
        er = executor.execute(ops) if ops else None
        pred = renderer.render_raw(er) if er and er.valid else ""
        match = str(pred).strip() == gt.strip()
        missing, extra = _compute_diff(sample.get("ops",[]), comp_raw)
        latency = (time.perf_counter() - t0) * 1000

        results.append({
            "id": sample.get("id",""), "system": "hybrid",
            "ground_truth_answer": gt, "predicted_answer": pred,
            "answer_match": match, "compiled_output": comp_json,
            "execution_success": er.valid if er else False,
            "valid_json": vr.valid_json, "valid_ops": vr.valid_ops,
            "evidence_valid": vr.execution_success,
            "num_events": sample.get("metadata",{}).get("num_events",0),
            "noise_level": sample.get("metadata",{}).get("noise_level",0.0),
            "latency_ms": latency,
            "ground_truth_ops": sample.get("ops",[]),
            "compiled_ops_raw": comp_raw,
            "missing_ops": missing, "extra_ops": extra,
            "failure_reason": "" if match else "answer_mismatch",
            "hybrid_fallback_rate": compiler.fallback_rate,
        })

    _save_failures(results, benchmark)
    from sage.eval.metrics import compute_all_metrics
    from sage.eval.report import print_report
    metrics = compute_all_metrics(results)
    print_report({"benchmark": str(benchmark), "num_samples": len(samples), "results": results, "metrics": metrics})
    console.print(f"[dim]Hybrid fallback rate: {compiler.fallback_rate*100:.1f}%[/]")


# ── compare-full ─────────────────────────────────────────────────

@app.command("compare-full")
def compare_full_cmd(
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b"),
    sklearn_model: Path = typer.Option(Path("models/sklearn-op-classifier.joblib"), "--sklearn-model", "-s"),
    max_per: int = typer.Option(50, "--max-samples", "-n"),
    output_dir: Path = typer.Option(Path("data/reports"), "--output-dir", "-o"),
):
    """Run full comparison: oracle, rule, sklearn, hybrid, sklearn direct, heuristic."""
    import json, time
    from pathlib import Path
    from sage.eval.run_benchmark import run_oracle, run_rule_only, _load_benchmark
    from sage.eval.compare import run_direct_eval
    from sage.baselines.sklearn_direct import SklearnDirectModel
    from sage.compiler.hybrid_compiler import HybridSAGECompiler
    from sage.engine.executor import Executor
    from sage.verifier.verifier import Verifier
    from sage.renderer.renderer import Renderer
    from sage.config import EngineConfig
    from sage.eval.metrics import compute_all_metrics

    console.print("[bold blue]Full SAGE Comparison[/]")

    benchmarks = ["easy","medium","hard","long","adversarial","ood_names","ood_phrasing","ood_numbers","ood_mixed"]

    hybrid = HybridSAGECompiler()
    hybrid.load(sklearn_model)
    sd = SklearnDirectModel()
    sd_model = Path("models/sklearn-direct.joblib")
    if sd_model.exists():
        sd.load(sd_model)

    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    comparison = {"benchmarks": {}}

    for name in benchmarks:
        path = benchmarks_dir / f"{name}.jsonl"
        if not path.exists():
            continue
        n = min(max_per, 50 if name in ("long","hard","ood_mixed","ood_phrasing") else 100)

        console.print(f"  {name}...", end="")

        oracle = run_oracle(path, max_samples=n)
        rule = run_rule_only(path, max_samples=n)
        heur = run_direct_eval(path, max_samples=n)

        # Hybrid
        hybrid.reset_stats()
        samples = _load_benchmark(path)[:n]
        h_res = []
        for s in samples:
            t0 = time.perf_counter()
            comp_raw, ok = hybrid.compile(s["story"])
            comp_json = json.dumps(comp_raw)
            ops, vr = verifier.verify(comp_json, story_text=s["story"])
            er = executor.execute(ops) if ops else None
            pred = renderer.render_raw(er) if er and er.valid else ""
            match = str(pred).strip() == str(s["answer"]).strip()
            h_res.append({"id":s.get("id",""),"system":"hybrid","ground_truth_answer":str(s["answer"]),"predicted_answer":pred,"answer_match":match,"compiled_output":comp_json,"execution_success":er.valid if er else False,"valid_json":vr.valid_json,"valid_ops":vr.valid_ops,"evidence_valid":vr.execution_success,"num_events":s.get("metadata",{}).get("num_events",0),"noise_level":0,"latency_ms":(time.perf_counter()-t0)*1000,"ground_truth_ops":s.get("ops",[]),"compiled_ops_raw":comp_raw,"missing_ops":[],"extra_ops":[],"failure_reason":"" if match else "answer_mismatch"})
        h_m = compute_all_metrics(h_res)

        # Sklearn direct
        d_res = []
        for s in samples:
            pred = sd.answer(s["story"])
            match = str(pred).strip() == str(s["answer"]).strip()
            d_res.append({"id":s.get("id",""),"system":"sklearn_direct","ground_truth_answer":str(s["answer"]),"predicted_answer":pred,"answer_match":match,"compiled_output":"","execution_success":False,"valid_json":False,"valid_ops":False,"evidence_valid":False,"num_events":s.get("metadata",{}).get("num_events",0),"noise_level":0,"latency_ms":0,"ground_truth_ops":[],"compiled_ops_raw":[],"missing_ops":[],"extra_ops":[],"failure_reason":"" if match else "wrong_answer"})
        d_m = compute_all_metrics(d_res)

        comparison["benchmarks"][name] = {
            "oracle": oracle["metrics"]["oracle"]["accuracy"],
            "rule": rule["metrics"]["rule_compiler"]["accuracy"],
            "hybrid": h_m["hybrid"]["accuracy"],
            "sklearn_direct": d_m["sklearn_direct"]["accuracy"],
            "heuristic": heur["metrics"]["direct_heuristic"]["accuracy"],
            "hybrid_fallback_rate": hybrid.fallback_rate,
        }
        console.print(f" oracle={oracle['metrics']['oracle']['accuracy']*100:.0f}% rule={rule['metrics']['rule_compiler']['accuracy']*100:.0f}% hybrid={h_m['hybrid']['accuracy']*100:.0f}%")

    # Print summary
    console.print("\n[bold]Full Comparison Summary[/]")
    from rich.table import Table
    table = Table(title="SAGE Full Comparison")
    table.add_column("Benchmark")
    table.add_column("Oracle")
    table.add_column("Rule")
    table.add_column("Hybrid")
    table.add_column("Sklearn D.")
    table.add_column("Heuristic")
    for name in benchmarks:
        if name not in comparison["benchmarks"]:
            continue
        d = comparison["benchmarks"][name]
        table.add_row(name, f"{d['oracle']*100:.0f}%", f"{d['rule']*100:.0f}%", f"{d['hybrid']*100:.0f}%", f"{d['sklearn_direct']*100:.0f}%", f"{d['heuristic']*100:.0f}%")
    console.print(table)

    # Save JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "full_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)
    console.print(f"[green]Saved to {output_dir / 'full_comparison.json'}[/]")


# ── tune-hybrid-thresholds ─────────────────────────────────────

@app.command("tune-hybrid-thresholds")
def tune_hybrid_thresholds_cmd(
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b"),
    sklearn_model: Path = typer.Option(Path("models/sklearn-op-classifier.joblib"), "--sklearn-model", "-s"),
    max_per: int = typer.Option(30, "--max-samples", "-n"),
):
    """Sweep normalizer thresholds to find the best tradeoff for OOD vs adversarial."""
    import json, time
    from sage.compiler.hybrid_compiler import HybridSAGECompiler, HybridCompilerConfig
    from sage.engine.executor import Executor
    from sage.verifier.verifier import Verifier
    from sage.renderer.renderer import Renderer
    from sage.config import EngineConfig
    from sage.eval.run_benchmark import _load_benchmark
    from sage.eval.metrics import compute_all_metrics

    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.72, 0.75, 0.80, 0.85]
    benchmarks = ["easy", "long", "adversarial", "ood_phrasing", "ood_mixed"]

    console.print("[bold blue]Tuning Hybrid Thresholds[/]")
    console.print(f"  Thresholds: {thresholds}")
    console.print(f"  Benchmarks: {benchmarks}")

    all_results = {}

    for thresh in thresholds:
        console.print(f"\n[bold]Threshold = {thresh:.2f}[/]")
        config = HybridCompilerConfig(
            normalizer_threshold=thresh,
            adversarial_guard_enabled=True,
            require_entity_confidence=True,
            fallback_to_noop_on_uncertainty=True,
        )
        compiler = HybridSAGECompiler(config=config)
        compiler.load(sklearn_model)

        row = {}
        for name in benchmarks:
            path = benchmarks_dir / f"{name}.jsonl"
            if not path.exists():
                continue
            n = min(max_per, 30)
            samples = _load_benchmark(path)[:n]

            engine_cfg = EngineConfig()
            verifier = Verifier(engine_cfg)
            executor = Executor(engine_cfg)
            renderer = Renderer()
            compiler.reset_stats()

            results = []
            for s in samples:
                comp_raw, ok = compiler.compile(s["story"])
                comp_json = json.dumps(comp_raw)
                ops, vr = verifier.verify(comp_json, story_text=s["story"])
                er = executor.execute(ops) if ops else None
                pred = renderer.render_raw(er) if er and er.valid else ""
                match = str(pred).strip() == str(s["answer"]).strip()
                results.append({
                    "id": s.get("id",""), "system": "hybrid",
                    "ground_truth_answer": str(s["answer"]),
                    "predicted_answer": pred, "answer_match": match,
                    "num_events": s.get("metadata",{}).get("num_events",0),
                })

            metrics = compute_all_metrics(results)
            acc = metrics["hybrid"]["accuracy"]
            row[name] = acc
            console.print(f"  {name}: {acc*100:.1f}% (fallback={compiler.fallback_rate*100:.1f}% blocked={compiler.block_rate*100:.1f}%)")

        # Weighted score: 0.35*adversarial + 0.25*ood_phrasing + 0.20*ood_mixed + 0.10*easy + 0.10*long
        weighted = (
            0.35 * row.get("adversarial", 0) +
            0.25 * row.get("ood_phrasing", 0) +
            0.20 * row.get("ood_mixed", 0) +
            0.10 * row.get("easy", 0) +
            0.10 * row.get("long", 0)
        )
        row["weighted"] = weighted
        all_results[thresh] = row

    # Print summary
    console.print("\n[bold]Threshold Sweep Results[/]")
    from rich.table import Table
    table = Table(title="Threshold Tuning")
    table.add_column("Thresh")
    table.add_column("easy", justify="right")
    table.add_column("long", justify="right")
    table.add_column("adversarial", justify="right")
    table.add_column("ood_phrasing", justify="right")
    table.add_column("ood_mixed", justify="right")
    table.add_column("weighted", justify="right")

    best_thresh = 0.72
    best_score = 0.0
    for thresh in thresholds:
        r = all_results[thresh]
        table.add_row(
            f"{thresh:.2f}",
            f"{r.get('easy',0)*100:.0f}%", f"{r.get('long',0)*100:.0f}%",
            f"{r.get('adversarial',0)*100:.0f}%", f"{r.get('ood_phrasing',0)*100:.0f}%",
            f"{r.get('ood_mixed',0)*100:.0f}%", f"{r['weighted']*100:.1f}%",
        )
        if r["weighted"] > best_score:
            best_score = r["weighted"]
            best_thresh = thresh

    console.print(table)
    console.print(f"\n[bold green]Best threshold: {best_thresh:.2f} (weighted score: {best_score*100:.1f}%)[/]")


# ── generate-neural-training-data ───────────────────────────────

@app.command("generate-neural-training-data")
def generate_neural_training_data_cmd(
    output_dir: Path = typer.Option(Path("data/generated"), "--output-dir", "-o"),
    sentence_samples: int = typer.Option(30000, "--sentence-samples"),
    story_samples: int = typer.Option(10000, "--story-samples"),
    seed: int = typer.Option(42, "--seed"),
    target_format: str = typer.Option("dsl", "--target-format", help="Target format: dsl or json"),
):
    """Generate enriched training data for the neural compiler."""
    from sage.training.neural_data_generator import generate_all_neural_data
    console.print("[bold blue]Generating Neural Training Data[/]")
    generate_all_neural_data(output_dir, sentence_samples, story_samples, seed, target_format=target_format)
    console.print("[green]Done.[/]")


# ── train-neural-sentence-compiler ──────────────────────────────

@app.command("train-neural-sentence-compiler")
def train_neural_sentence_compiler_cmd(
    train: Path = typer.Option(..., "--train", "-t"),
    dev: Optional[Path] = typer.Option(None, "--dev", "-d"),
    model: str = typer.Option("google/flan-t5-small", "--model", "-m"),
    epochs: int = typer.Option(3, "--epochs", "-e"),
    batch_size: int = typer.Option(8, "--batch-size"),
    max_input_length: int = typer.Option(256, "--max-input-length"),
    max_target_length: int = typer.Option(256, "--max-target-length"),
    output_dir: Path = typer.Option(Path("models/neural-sentence-compiler"), "--output-dir", "-o"),
    device: str = typer.Option("auto", "--device", help="Device: auto, cuda, mps, cpu"),
    learning_rate: float = typer.Option(5e-5, "--lr"),
    target_format: str = typer.Option("dsl", "--target-format"),
):
    """Train a neural sentence compiler (sentence → operation JSON)."""
    from sage.training.train_neural_sentence import train_neural_sentence_compiler
    console.print("[bold blue]Training Neural Sentence Compiler[/]")
    train_neural_sentence_compiler(
        train_path=train, dev_path=dev, model_name=model,
        output_dir=str(output_dir), num_epochs=epochs, batch_size=batch_size,
        max_input_length=max_input_length, max_output_length=max_target_length,
        learning_rate=learning_rate, device=device,
    )
    console.print(f"[green]Model saved to {output_dir}[/]")


# ── eval-neural-sentence-compiler ───────────────────────────────

@app.command("eval-neural-sentence-compiler")
def eval_neural_sentence_compiler_cmd(
    model_path: Path = typer.Option(..., "--model", "-m"),
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b"),
    max_per: int = typer.Option(30, "--max-samples", "-n"),
    device: str = typer.Option("auto", "--device", help="Device: auto, cuda, mps, cpu"),
    target_format: str = typer.Option("dsl", "--target-format"),
):
    """Evaluate a trained neural sentence compiler on all benchmarks."""
    import json, time, torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from sage.eval.run_benchmark import _load_benchmark, _save_failures
    from sage.engine.executor import Executor
    from sage.verifier.verifier import Verifier
    from sage.renderer.renderer import Renderer
    from sage.config import EngineConfig
    from sage.extraction.sentence_splitter import split_sentences
    from sage.eval.metrics import compute_all_metrics
    from sage.eval.report import print_report
    
    console.print("[bold blue]Neural Sentence Compiler Eval[/]")
    
    # Load model
    from sage.training.device import resolve_device, describe_device; dev = resolve_device(device); console.print(f"Device: {describe_device(dev)}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path)).to(dev)
    model.eval()
    
    benchmarks = ["easy","medium","hard","long","adversarial","ood_names","ood_phrasing","ood_numbers","ood_mixed"]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg); executor = Executor(engine_cfg); renderer = Renderer()
    
    for name in benchmarks:
        path = benchmarks_dir / f"{name}.jsonl"
        if not path.exists(): continue
        n = min(max_per, 50 if name in ("long","hard","ood_mixed","ood_phrasing") else 100)
        samples = _load_benchmark(path)[:n]
        
        results = []
        for sample in samples:
            story = sample["story"]
            sentences = split_sentences(story)
            
            # Compile sentence by sentence
            ops = []
            for sent in sentences:
                input_text = f"compile_sentence: {sent}"
                inputs = tokenizer(input_text, return_tensors="pt", max_length=256, truncation=True).to(dev)
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_new_tokens=256, num_beams=1)
                raw = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                if target_format == "dsl":
                    from sage.compiler.op_dsl import parse_op_dsl
                    parsed_ops = parse_op_dsl(raw, story)
                    ops.extend(parsed_ops)
                else:
                    try:
                        parsed = json.loads(raw)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            ops.append(parsed[0])
                    except:
                        pass
            
            # Normalize TRANSFER ops: convert from/to to from_target/to_target for verifier
            for op in ops:
                if op.get("op") == "TRANSFER":
                    if "from" in op:
                        op["from_target"] = op.pop("from")
                    if "to" in op:
                        op["to_target"] = op.pop("to")
            
            # Verify + execute
            comp_json = json.dumps(ops)
            ops_obj, vr = verifier.verify(comp_json, story_text=story)
            er = executor.execute(ops_obj) if ops_obj else None
            pred = renderer.render_raw(er) if er and er.valid else ""
            match = str(pred).strip() == str(sample["answer"]).strip()
            
            results.append({
                "id": sample.get("id",""), "system": "neural_sentence",
                "ground_truth_answer": str(sample["answer"]),
                "predicted_answer": pred, "answer_match": match,
                "compiled_output": comp_json,
                "execution_success": er.valid if er else False,
                "valid_json": vr.valid_json, "valid_ops": vr.valid_ops,
                "evidence_valid": vr.execution_success,
                "num_events": sample.get("metadata",{}).get("num_events",0),
                "latency_ms": 0, "ground_truth_ops": sample.get("ops",[]),
                "compiled_ops_raw": ops, "missing_ops": [], "extra_ops": [],
                "failure_reason": "" if match else "answer_mismatch",
            })
        
        _save_failures(results, path)
        metrics = compute_all_metrics(results)
        acc = metrics["neural_sentence"]["accuracy"]
        console.print(f"  {name}: {acc*100:.1f}%")
    
    console.print("[green]Done.[/]")


# ── eval-models ──────────────────────────────────────────────────

@app.command("eval-models")
def eval_models_cmd(
    benchmarks_dir: Path = typer.Option(Path("data/benchmarks"), "--benchmarks-dir", "-b"),
    compiler_model: Optional[Path] = typer.Option(None, "--compiler-model", "-c", help="Path to compiler model checkpoint"),
    direct_model: Optional[Path] = typer.Option(None, "--direct-model", "-d", help="Path to direct model checkpoint"),
    max_per: int = typer.Option(50, "--max-samples", "-n"),
    output_dir: Path = typer.Option(Path("data/reports"), "--output-dir", "-o"),
    use_cpu: bool = typer.Option(True, "--cpu/--gpu"),
):
    """Run neural SAGE vs neural Direct comparison on all benchmarks."""
    from sage.eval.neural_eval import run_neural_comparison, generate_neural_report

    console.print("[bold blue]Neural SAGE vs Direct Comparison[/]")

    results = run_neural_comparison(
        benchmarks_dir=benchmarks_dir,
        compiler_checkpoint=compiler_model,
        direct_checkpoint=direct_model,
        max_per_benchmark=max_per,
        use_cpu=use_cpu,
    )

    generate_neural_report(results, output_dir)
    console.print(f"\n[dim]Reports saved to {output_dir}[/]")



# ── test-forward ─────────────────────────────────────────────

@app.command("test-forward")
def test_forward_cmd(
    model: str = typer.Option("google/flan-t5-small", "--model", "-m"),
    device: str = typer.Option("auto", "--device", help="Device: auto, cuda, mps, cpu"),
):
    """Test that PyTorch + Transformers forward pass works on this machine."""
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from sage.training.device import resolve_device, describe_device
    dev = resolve_device(device)
    console.print(f"[bold]Device:[/] {describe_device(dev)}")
    console.print(f"[bold]Model:[/] {model}")
    console.print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model)
    console.print("Loading model...")
    model_obj = AutoModelForSeq2SeqLM.from_pretrained(model).to(dev)
    model_obj.eval()
    text = "compile_sentence: Latif gains three coins."
    console.print(f"Input: {text}")
    inputs = tokenizer(text, return_tensors="pt", max_length=64, truncation=True)
    inputs = {k: v.to(dev) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model_obj(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss.item()
        generated = model_obj.generate(**inputs, max_new_tokens=64)
        result = tokenizer.decode(generated[0], skip_special_tokens=True)
    console.print(f"[green]Forward loss: {loss:.4f}[/]")
    console.print(f"[green]Generated: {result}[/]")
    console.print("[bold green]OK — PyTorch + Transformers working on this machine[/]")

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
        "  generate-data            Create synthetic training data\n"
        "  generate-ood-benchmarks  Create OOD benchmarks\n"
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
