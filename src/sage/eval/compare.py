"""SAGE vs Direct comparison utilities."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from sage.eval.run_benchmark import run_oracle, run_rule_only, _load_benchmark
from sage.baselines.heuristic_baseline import HeuristicBaseline


def run_direct_eval(benchmark_path: Path, max_samples: int = 100) -> dict[str, Any]:
    """Run the direct heuristic baseline on a benchmark."""
    samples = _load_benchmark(benchmark_path)[:max_samples]
    hb = HeuristicBaseline()
    results = []
    for sample in samples:
        story = sample.get("story", "")
        gt = str(sample.get("answer", ""))
        pred = hb.answer(story)
        match = str(pred).strip() == gt.strip()
        results.append({
            "id": sample.get("id", ""),
            "system": "direct_heuristic",
            "ground_truth_answer": gt,
            "predicted_answer": str(pred),
            "answer_match": match,
            "compiled_output": "",
            "execution_success": False,
            "valid_json": False,
            "valid_ops": False,
            "evidence_valid": False,
            "num_events": sample.get("metadata", {}).get("num_events", 0),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": 0.0,
            "ground_truth_ops": [],
            "compiled_ops_raw": [],
            "missing_ops": [],
            "extra_ops": [],
            "failure_reason": "" if match else "answer_mismatch",
        })
    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": results,
        "metrics": compute_all_metrics(results),
    }


def run_full_comparison(benchmarks_dir: Path = None, max_per: int = 100) -> dict:
    """Run oracle + rule + direct on all benchmarks. Returns comparison dict."""
    if benchmarks_dir is None:
        benchmarks_dir = Path("data/benchmarks")
    benchmarks_dir = Path(benchmarks_dir)
    
    benchmark_names = ["easy", "medium", "hard", "long", "adversarial"]
    comparison = {"benchmarks": {}}
    
    for name in benchmark_names:
        path = benchmarks_dir / f"{name}.jsonl"
        if not path.exists():
            continue
        n = min(max_per, 50 if name in ("long", "hard") else 100)
        
        oracle = run_oracle(path, max_samples=n)
        rule = run_rule_only(path, max_samples=n)
        direct = run_direct_eval(path, max_samples=n)
        
        comparison["benchmarks"][name] = {
            "oracle_accuracy": oracle["metrics"]["oracle"]["accuracy"],
            "rule_accuracy": rule["metrics"]["rule_compiler"]["accuracy"],
            "direct_accuracy": direct["metrics"]["direct_heuristic"]["accuracy"],
            "num_samples": n,
            "avg_events": rule["metrics"]["rule_compiler"].get("avg_events", 0),
        }
        
        # Event bucket breakdown for rule vs direct
        from sage.eval.metrics import accuracy_by_event_buckets
        comparison["benchmarks"][name]["rule_buckets"] = accuracy_by_event_buckets(rule["results"])
        comparison["benchmarks"][name]["direct_buckets"] = accuracy_by_event_buckets(direct["results"])
    
    # Compute context-scaling advantage
    comparison["context_advantage"] = compute_context_advantage(comparison)
    
    return comparison


def compute_context_advantage(comparison: dict) -> dict:
    """Compute effective context advantage: how much longer can SAGE maintain accuracy vs direct.
    
    Returns dict with thresholds (90%, 80%, 70%) and the max event count where each system
    stays above that threshold.
    """
    # Collect all results across benchmarks
    # We need per-sample data, not just aggregates
    # For now, use benchmark-level aggregates as approximation
    result = {}
    for threshold in [0.90, 0.80, 0.70]:
        sage_max_events = 0
        direct_max_events = 0
        for name, data in comparison.get("benchmarks", {}).items():
            if data["rule_accuracy"] >= threshold:
                sage_max_events = max(sage_max_events, int(data.get("avg_events", 0)))
            if data["direct_accuracy"] >= threshold:
                direct_max_events = max(direct_max_events, int(data.get("avg_events", 0)))
        
        advantage = sage_max_events / direct_max_events if direct_max_events > 0 else float('inf')
        result[f"threshold_{int(threshold*100)}"] = {
            "sage_max_events": sage_max_events,
            "direct_max_events": direct_max_events,
            "advantage_ratio": round(advantage, 1),
        }
    return result


def generate_comparison_md(comparison: dict, output_path: Path = None) -> str:
    """Generate a Markdown comparison report."""
    if output_path is None:
        output_path = Path("data/reports/comparison_report.md")
    
    lines = []
    lines.append("# SAGE vs Direct Baseline — Comparison Report")
    lines.append("")
    lines.append("## Overall Accuracy")
    lines.append("")
    lines.append("| Benchmark | Events | Oracle SAGE | Rule SAGE | Direct Heuristic | SAGE Advantage |")
    lines.append("|-----------|--------|-------------|-----------|------------------|----------------|")
    
    for name, data in comparison.get("benchmarks", {}).items():
        oracle = data["oracle_accuracy"]
        rule = data["rule_accuracy"]
        direct = data["direct_accuracy"]
        events = data.get("avg_events", 0)
        advantage = f"+{((rule - direct) / max(direct, 0.001) * 100):.0f}%" if direct > 0 else "N/A"
        lines.append(f"| {name} | {int(events)} | {oracle*100:.0f}% | {rule*100:.0f}% | {direct*100:.0f}% | {advantage} |")
    
    lines.append("")
    lines.append("## Context-Scaling Advantage")
    lines.append("")
    ca = comparison.get("context_advantage", {})
    lines.append("| Threshold | SAGE Max Events | Direct Max Events | Advantage Ratio |")
    lines.append("|-----------|----------------|-------------------|-----------------|")
    for key, data in ca.items():
        thresh = key.replace("threshold_", "")
        lines.append(f"| {thresh}% | {data['sage_max_events']} | {data['direct_max_events']} | {data['advantage_ratio']}x |")
    
    lines.append("")
    lines.append("## Event Bucket Accuracy")
    lines.append("")
    lines.append("| Benchmark | Bucket | Rule SAGE | Direct |")
    lines.append("|-----------|--------|-----------|--------|")
    for name, data in comparison.get("benchmarks", {}).items():
        rb = data.get("rule_buckets", {})
        db = data.get("direct_buckets", {})
        for bucket in ["1-5", "6-25", "26-100", "101-500"]:
            r_acc = rb.get(bucket, {}).get("accuracy", 0)
            d_acc = db.get(bucket, {}).get("accuracy", 0)
            if rb.get(bucket, {}).get("samples", 0) > 0:
                lines.append(f"| {name} | {bucket} | {r_acc*100:.0f}% | {d_acc*100:.0f}% |")
    
    md = "\n".join(lines)
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(md)
    
    return md


def save_comparison_json(comparison: dict, output_path: Path = None):
    """Save comparison as JSON."""
    if output_path is None:
        output_path = Path("data/reports/comparison_report.json")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
