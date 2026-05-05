"""Benchmark runner for SAGE — with oracle eval, failure diagnostics, and evidence tracking.

Evaluates every system on JSONL benchmark files.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from sage.config import EvalConfig, EngineConfig
from sage.engine.executor import Executor
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.schemas.ops import Operation, OpType

logger = logging.getLogger(__name__)

# ── Optional imports ──────────────────────────────────────────────

_RuleCompiler = None
try:
    from sage.compiler.rule_compiler import RuleCompiler as _RC
    _RuleCompiler = _RC
except ImportError:
    pass

_HeuristicBaseline = None
try:
    from sage.baselines.heuristic_baseline import HeuristicBaseline as _HB
    _HeuristicBaseline = _HB
except ImportError:
    pass


# ── Helpers ───────────────────────────────────────────────────────

def _load_benchmark(path: Path) -> list[dict[str, Any]]:
    samples = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def _ops_dicts_to_operations(op_dicts: list[dict]) -> list[Operation]:
    """Convert raw op dicts to Operation objects."""
    ops = []
    for d in op_dicts:
        dc = dict(d)
        if "from" in dc:
            dc["from_target"] = dc.pop("from")
        if "to" in dc:
            dc["to_target"] = dc.pop("to")
        try:
            ops.append(Operation(**dc))
        except Exception:
            pass
    return ops


def _compute_diff(gt_ops: list[dict], comp_ops: list[dict]) -> tuple[list[dict], list[dict]]:
    """Compute missing and extra ops by (op+target+value) matching."""
    def key(op):
        return (op.get("op"), op.get("target") or op.get("from", ""),
                op.get("value"))
    gt_keys = {key(o) for o in gt_ops}
    comp_keys = {key(o) for o in comp_ops}
    missing = [o for o in gt_ops if key(o) not in comp_keys]
    extra = [o for o in comp_ops if key(o) not in gt_keys]
    return missing, extra


def _save_failures(results: list[dict], benchmark_path: Path):
    """Save failed samples to data/reports/failures_{difficulty}.jsonl."""
    out_dir = Path("data/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    difficulty = benchmark_path.stem  # e.g., "easy"
    out_path = out_dir / f"failures_{difficulty}.jsonl"

    failures = [r for r in results if not r.get("answer_match", False)]
    with open(out_path, "w", encoding="utf-8") as f:
        for failure in failures:
            f.write(json.dumps(failure, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(failures)} failures to {out_path}")


# ── Oracle eval ───────────────────────────────────────────────────

def run_oracle(benchmark_path: Path, max_samples: int | None = None) -> dict[str, Any]:
    """Evaluate using ground-truth ops directly. Oracle SAGE should be ~100%."""
    samples = _load_benchmark(benchmark_path)
    if max_samples:
        samples = samples[:max_samples]

    executor = Executor(EngineConfig())
    renderer = Renderer()
    all_results: list[dict] = []

    for sample in samples:
        story = sample.get("story", "")
        gt_answer = str(sample.get("answer", ""))
        gt_ops_dicts = sample.get("ops", [])

        ops = _ops_dicts_to_operations(gt_ops_dicts)
        result = executor.execute(ops)

        predicted = renderer.render_raw(result) if result.valid else ""
        answer_match = str(predicted).strip() == gt_answer.strip()

        all_results.append({
            "id": sample.get("id", ""),
            "system": "oracle",
            "ground_truth_answer": gt_answer,
            "predicted_answer": predicted,
            "answer_match": answer_match,
            "compiled_output": json.dumps(gt_ops_dicts),
            "execution_success": result.valid,
            "valid_json": True,
            "valid_ops": True,
            "evidence_valid": True,
            "num_events": sample.get("metadata", {}).get("num_events", len(gt_ops_dicts)),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": 0.0,
            "ground_truth_ops": gt_ops_dicts,
            "compiled_ops_raw": gt_ops_dicts,
            "missing_ops": [],
            "extra_ops": [],
            "failure_reason": "" if answer_match else "answer_mismatch",
        })

    _save_failures(all_results, benchmark_path)

    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": all_results,
        "metrics": compute_all_metrics(all_results),
    }


# ── Rule-only eval ────────────────────────────────────────────────

def run_rule_only(benchmark_path: Path, max_samples: int = 100) -> dict[str, Any]:
    """Evaluate using the rule-based compiler with evidence and diagnostics."""
    samples = _load_benchmark(benchmark_path)[:max_samples]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    if _RuleCompiler is None:
        raise ImportError("RuleCompiler not available")

    rc = _RuleCompiler()
    all_results: list[dict] = []

    for sample in samples:
        story = sample.get("story", "")
        gt_answer = str(sample.get("answer", ""))
        gt_ops_dicts = sample.get("ops", [])

        t0 = time.perf_counter()
        compiled_ops_raw, compile_success = rc.compile(story)
        compiled_json = json.dumps(compiled_ops_raw)

        # Verify with evidence
        ops, vr = verifier.verify(compiled_json, story_text=story)

        # Execute
        exec_result = executor.execute(ops) if ops else None
        predicted = renderer.render_raw(exec_result) if exec_result and exec_result.valid else ""
        answer_match = str(predicted).strip() == gt_answer.strip()

        # Compute diff
        missing, extra = _compute_diff(gt_ops_dicts, compiled_ops_raw)

        # Determine failure reason
        failure_reason = ""
        if not compile_success or not compiled_ops_raw:
            failure_reason = "compile_failed"
        elif exec_result is None or not exec_result.valid:
            failure_reason = "execution_failed"
        elif not vr.valid_ops:
            failure_reason = "evidence_invalid"
        elif not answer_match:
            failure_reason = "answer_mismatch"

        latency = (time.perf_counter() - t0) * 1000

        all_results.append({
            "id": sample.get("id", ""),
            "system": "rule_compiler",
            "ground_truth_answer": gt_answer,
            "predicted_answer": predicted,
            "answer_match": answer_match,
            "compiled_output": compiled_json,
            "execution_success": exec_result.valid if exec_result else False,
            "valid_json": vr.valid_json,
            "valid_ops": vr.valid_ops,
            "evidence_valid": vr.execution_success,
            "num_events": sample.get("metadata", {}).get("num_events", len(gt_ops_dicts)),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": latency,
            "ground_truth_ops": gt_ops_dicts,
            "compiled_ops_raw": compiled_ops_raw,
            "missing_ops": missing,
            "extra_ops": extra,
            "failure_reason": failure_reason,
        })

    _save_failures(all_results, benchmark_path)

    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": all_results,
        "metrics": compute_all_metrics(all_results),
    }


# ── Full benchmark ────────────────────────────────────────────────

def run_benchmark(benchmark_path: Path, config: EvalConfig | None = None) -> dict[str, Any]:
    """Run full benchmark across all available systems."""
    cfg = config or EvalConfig()
    samples = _load_benchmark(benchmark_path)
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()
    all_results: list[dict] = []

    # Rule Compiler
    if _RuleCompiler is not None:
        rc = _RuleCompiler()
        for sample in samples:
            story = sample.get("story", "")
            gt_answer = str(sample.get("answer", ""))
            gt_ops = sample.get("ops", [])
            t0 = time.perf_counter()
            comp_raw, _ = rc.compile(story)
            comp_json = json.dumps(comp_raw)
            ops, vr = verifier.verify(comp_json, story_text=story)
            er = executor.execute(ops) if ops else None
            pred = renderer.render_raw(er) if er and er.valid else ""
            match = str(pred).strip() == gt_answer.strip()
            missing, extra = _compute_diff(gt_ops, comp_raw)
            all_results.append({
                "id": sample.get("id", ""),
                "system": "rule_compiler",
                "ground_truth_answer": gt_answer,
                "predicted_answer": pred,
                "answer_match": match,
                "compiled_output": comp_json,
                "execution_success": er.valid if er else False,
                "valid_json": vr.valid_json,
                "valid_ops": vr.valid_ops,
                "evidence_valid": vr.execution_success,
                "num_events": sample.get("metadata", {}).get("num_events", len(gt_ops)),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": (time.perf_counter() - t0) * 1000,
                "ground_truth_ops": gt_ops,
                "compiled_ops_raw": comp_raw,
                "missing_ops": missing,
                "extra_ops": extra,
                "failure_reason": "" if match else "answer_mismatch",
            })

    # Heuristic Baseline
    if _HeuristicBaseline is not None:
        hb = _HeuristicBaseline()
        for sample in samples:
            story = sample.get("story", "")
            gt_answer = str(sample.get("answer", ""))
            t0 = time.perf_counter()
            pred = hb.answer(story)
            match = str(pred).strip() == gt_answer.strip()
            all_results.append({
                "id": sample.get("id", ""),
                "system": "heuristic",
                "ground_truth_answer": gt_answer,
                "predicted_answer": str(pred),
                "answer_match": match,
                "compiled_output": "",
                "execution_success": False,
                "valid_json": False,
                "valid_ops": False,
                "evidence_valid": False,
                "num_events": sample.get("metadata", {}).get("num_events", len(sample.get("ops", []))),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": (time.perf_counter() - t0) * 1000,
                "ground_truth_ops": sample.get("ops", []),
                "compiled_ops_raw": [],
                "missing_ops": [],
                "extra_ops": [],
                "failure_reason": "" if match else "answer_mismatch",
            })

    _save_failures([r for r in all_results if r.get("system") == "rule_compiler"], benchmark_path)

    from sage.eval.metrics import compute_all_metrics
    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": all_results,
        "metrics": compute_all_metrics(all_results),
    }
