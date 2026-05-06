"""Neural model evaluation for SAGE — compare neural compiler vs neural direct model."""

from __future__ import annotations
import json, time, logging
from pathlib import Path
from typing import Any, Optional
from sage.config import EngineConfig
from sage.engine.executor import Executor
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.eval.run_benchmark import _load_benchmark, _ops_dicts_to_operations, _save_failures

logger = logging.getLogger(__name__)


def run_neural_compiler_eval(
    benchmark_path: Path,
    compiler: Any,  # ModelCompiler instance, already loaded
    max_samples: int = 50,
) -> dict[str, Any]:
    """Evaluate a neural compiler model on a benchmark.
    
    Pipeline: story → model_compiler.compile() → raw JSON string → verifier → engine → answer
    """
    samples = _load_benchmark(benchmark_path)[:max_samples]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()
    
    results = []
    for sample in samples:
        story = sample.get("story", "")
        gt_answer = str(sample.get("answer", ""))
        gt_ops = sample.get("ops", [])
        
        t0 = time.perf_counter()
        
        # Model compile
        raw_output = ""
        try:
            raw_output = compiler.compile(story)
        except Exception as e:
            raw_output = f"ERROR: {e}"
        
        # Verify with evidence
        ops, vr = verifier.verify(raw_output, story_text=story)
        
        # Execute
        exec_result = executor.execute(ops) if ops else None
        predicted = renderer.render_raw(exec_result) if exec_result and exec_result.valid else ""
        answer_match = str(predicted).strip() == gt_answer.strip()
        
        # Parse ops from raw output for diagnostics
        parsed_ops = []
        try:
            parsed_ops = json.loads(raw_output) if raw_output.strip().startswith("[") else []
        except:
            pass
        
        latency = (time.perf_counter() - t0) * 1000
        
        failure_reason = ""
        if not vr.valid_json:
            failure_reason = "invalid_json"
        elif not vr.valid_ops:
            failure_reason = "invalid_ops"
        elif not vr.execution_success:
            failure_reason = "evidence_invalid"
        elif exec_result is None or not exec_result.valid:
            failure_reason = "execution_failed"
        elif not answer_match:
            failure_reason = "answer_mismatch"
        
        results.append({
            "id": sample.get("id", ""),
            "system": "neural_compiler",
            "ground_truth_answer": gt_answer,
            "predicted_answer": predicted,
            "answer_match": answer_match,
            "compiled_output": raw_output,
            "execution_success": exec_result.valid if exec_result else False,
            "valid_json": vr.valid_json,
            "valid_ops": vr.valid_ops,
            "evidence_valid": vr.execution_success,
            "num_events": sample.get("metadata", {}).get("num_events", len(gt_ops)),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": latency,
            "ground_truth_ops": gt_ops,
            "compiled_ops_raw": parsed_ops,
            "missing_ops": [],
            "extra_ops": [],
            "failure_reason": failure_reason,
            "raw_model_output": raw_output,
            "parsed_ops": parsed_ops,
        })
    
    # Save neural-specific failures
    _save_neural_failures(results, benchmark_path, prefix="neural_compiler")
    
    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": results,
        "metrics": compute_all_metrics(results),
    }


def run_neural_direct_eval(
    benchmark_path: Path,
    model: Any,  # DirectAnswerModel instance, already loaded
    max_samples: int = 50,
) -> dict[str, Any]:
    """Evaluate a neural direct-answer model on a benchmark."""
    samples = _load_benchmark(benchmark_path)[:max_samples]
    
    results = []
    for sample in samples:
        story = sample.get("story", "")
        gt_answer = str(sample.get("answer", ""))
        
        t0 = time.perf_counter()
        raw_output = ""
        try:
            raw_output = model.answer(story)
        except Exception as e:
            raw_output = f"ERROR: {e}"
        
        # Try to parse numeric answer
        import re
        parsed_answer = ""
        num_match = re.search(r'-?\d+', str(raw_output))
        if num_match:
            parsed_answer = num_match.group(0)
        else:
            parsed_answer = str(raw_output).strip()
        
        answer_match = parsed_answer == gt_answer
        latency = (time.perf_counter() - t0) * 1000
        
        failure_reason = ""
        if not num_match:
            failure_reason = "unparseable_answer"
        elif not answer_match:
            failure_reason = "wrong_answer"
        
        results.append({
            "id": sample.get("id", ""),
            "system": "neural_direct",
            "ground_truth_answer": gt_answer,
            "predicted_answer": parsed_answer,
            "answer_match": answer_match,
            "compiled_output": "",
            "execution_success": False,
            "valid_json": False,
            "valid_ops": False,
            "evidence_valid": False,
            "num_events": sample.get("metadata", {}).get("num_events", len(sample.get("ops", []))),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": latency,
            "ground_truth_ops": sample.get("ops", []),
            "compiled_ops_raw": [],
            "missing_ops": [],
            "extra_ops": [],
            "failure_reason": failure_reason,
            "raw_model_output": raw_output,
            "parsed_answer": parsed_answer,
        })
    
    # Save failures
    _save_neural_failures(results, benchmark_path, prefix="direct_model")
    
    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": results,
        "metrics": compute_all_metrics(results),
    }


def run_neural_comparison(
    benchmarks_dir: Path = None,
    compiler_checkpoint: Optional[Path] = None,
    direct_checkpoint: Optional[Path] = None,
    max_per_benchmark: int = 50,
    use_cpu: bool = True,
) -> dict:
    """Run full neural comparison across all benchmarks."""
    if benchmarks_dir is None:
        benchmarks_dir = Path("data/benchmarks")
    
    # Load models
    compiler = None
    if compiler_checkpoint and compiler_checkpoint.exists():
        from sage.compiler.model_compiler import ModelCompiler
        compiler = ModelCompiler(use_cpu=use_cpu)
        compiler.load_checkpoint(compiler_checkpoint)
    
    direct_model = None
    if direct_checkpoint and direct_checkpoint.exists():
        from sage.baselines.direct_answer_model import DirectAnswerModel
        direct_model = DirectAnswerModel(use_cpu=use_cpu)
        direct_model.load_checkpoint(direct_checkpoint)
    
    comparison = {"benchmarks": {}}
    benchmark_names = ["easy", "medium", "hard", "long", "adversarial"]
    
    for name in benchmark_names:
        path = benchmarks_dir / f"{name}.jsonl"
        if not path.exists():
            continue
        n = min(max_per_benchmark, 50 if name in ("long", "hard") else 100)
        
        entry = {"name": name, "num_samples": n}
        
        # Run oracle + rule for reference
        from sage.eval.run_benchmark import run_oracle, run_rule_only
        oracle = run_oracle(path, max_samples=n)
        rule = run_rule_only(path, max_samples=n)
        entry["oracle_accuracy"] = oracle["metrics"]["oracle"]["accuracy"]
        entry["rule_accuracy"] = rule["metrics"]["rule_compiler"]["accuracy"]
        
        # Neural compiler
        if compiler:
            nc = run_neural_compiler_eval(path, compiler, max_samples=n)
            entry["neural_compiler_accuracy"] = nc["metrics"]["neural_compiler"]["accuracy"]
            entry["neural_compiler_json_valid"] = nc["metrics"]["neural_compiler"]["json_valid_rate"]
            entry["neural_compiler_exec_success"] = nc["metrics"]["neural_compiler"]["execution_success_rate"]
            entry["neural_compiler_evidence_valid"] = nc["metrics"]["neural_compiler"]["evidence_valid_rate"]
        else:
            entry["neural_compiler_accuracy"] = 0.0
        
        # Neural direct
        if direct_model:
            nd = run_neural_direct_eval(path, direct_model, max_samples=n)
            entry["neural_direct_accuracy"] = nd["metrics"]["neural_direct"]["accuracy"]
        else:
            entry["neural_direct_accuracy"] = 0.0
        
        # Heuristic
        from sage.eval.compare import run_direct_eval
        heur = run_direct_eval(path, max_samples=n)
        entry["heuristic_accuracy"] = heur["metrics"]["direct_heuristic"]["accuracy"]
        
        comparison["benchmarks"][name] = entry
    
    return comparison


def generate_neural_report(comparison: dict, output_dir: Path):
    """Generate neural comparison reports (MD + JSON)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON
    with open(output_dir / "neural_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
    
    # MD
    lines = ["# Neural SAGE vs Direct Model — Comparison Report", ""]
    lines.append("| Benchmark | Events | Oracle | Rule SAGE | Neural SAGE | Neural Direct | Heuristic |")
    lines.append("|-----------|--------|--------|-----------|-------------|---------------|-----------|")
    
    for name, data in comparison.get("benchmarks", {}).items():
        oracle = data.get("oracle_accuracy", 0)
        rule = data.get("rule_accuracy", 0)
        nc = data.get("neural_compiler_accuracy", 0)
        nd = data.get("neural_direct_accuracy", 0)
        heur = data.get("heuristic_accuracy", 0)
        ev = data.get("num_samples", 0)
        lines.append(f"| {name} | {ev} | {oracle*100:.0f}% | {rule*100:.0f}% | {nc*100:.1f}% | {nd*100:.1f}% | {heur*100:.0f}% |")
    
    lines.append("")
    lines.append("## Neural Compiler Diagnostics")
    lines.append("")
    lines.append("| Benchmark | JSON Valid | Ops Valid | Evidence Valid | Exec Success |")
    lines.append("|-----------|-----------|-----------|----------------|--------------|")
    for name, data in comparison.get("benchmarks", {}).items():
        jv = data.get("neural_compiler_json_valid", 0)
        ov = data.get("neural_compiler_evidence_valid", 0)
        ev = data.get("neural_compiler_evidence_valid", 0)
        es = data.get("neural_compiler_exec_success", 0)
        lines.append(f"| {name} | {jv*100:.1f}% | {ov*100:.1f}% | {ev*100:.1f}% | {es*100:.1f}% |")
    
    with open(output_dir / "neural_comparison.md", "w") as f:
        f.write("\n".join(lines))


def _save_neural_failures(results: list[dict], benchmark_path: Path, prefix: str = "neural"):
    """Save neural-specific failure records to JSONL."""
    out_dir = Path("data/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    difficulty = benchmark_path.stem
    out_path = out_dir / f"{prefix}_failures_{difficulty}.jsonl"
    
    failures = [r for r in results if not r.get("answer_match", False)]
    with open(out_path, "w", encoding="utf-8") as f:
        for failure in failures:
            record = {
                "id": failure.get("id", ""),
                "story": failure.get("story", ""),
                "expected_answer": failure.get("ground_truth_answer", ""),
                "predicted_answer": failure.get("predicted_answer", ""),
                "raw_model_output": failure.get("raw_model_output", ""),
                "parsed_ops": failure.get("parsed_ops", []),
                "ground_truth_ops": failure.get("ground_truth_ops", []),
                "failure_reason": failure.get("failure_reason", ""),
                "verified": {
                    "valid_json": failure.get("valid_json", False),
                    "valid_ops": failure.get("valid_ops", False),
                    "evidence_valid": failure.get("evidence_valid", False),
                },
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
