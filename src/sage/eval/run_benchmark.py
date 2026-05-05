"""Benchmark runner for SAGE.

Evaluates every system (rule compiler, model compiler, direct-answer
baseline, heuristic baseline) on a JSONL benchmark file and returns
per-sample results plus aggregate metrics.

Systems that are not installed are silently skipped so the runner is
usable even when optional dependencies are missing.
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
from sage.eval.metrics import compute_all_metrics

logger = logging.getLogger(__name__)


# ── optional compiler / baseline imports ──────────────────────────────

_RuleCompiler = None
_ModelCompiler = None
_DirectAnswerModel = None
_HeuristicBaseline = None

try:
    from sage.compiler.rule_compiler import RuleCompiler as _RC
    _RuleCompiler = _RC
except ImportError:
    logger.debug("sage.compiler.rule_compiler not available")

try:
    from sage.compiler.model_compiler import ModelCompiler as _MC
    _ModelCompiler = _MC
except ImportError:
    logger.debug("sage.compiler.model_compiler not available")

try:
    from sage.baselines.direct_answer_model import DirectAnswerModel as _DAM
    _DirectAnswerModel = _DAM
except ImportError:
    logger.debug("sage.baselines.direct_answer_model not available")

try:
    from sage.baselines.heuristic_baseline import HeuristicBaseline as _HB
    _HeuristicBaseline = _HB
except ImportError:
    logger.debug("sage.baselines.heuristic_baseline not available")


# ── helpers ────────────────────────────────────────────────────────────

def _load_benchmark(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL benchmark file into a list of dicts."""
    samples: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            samples.append(json.loads(line))
    return samples


def _run_sage_pipeline(
    story: str,
    compiler: Any,
    verifier: Verifier,
    executor: Executor,
    renderer: Renderer,
) -> dict[str, Any]:
    """Run the full SAGE pipeline: compile → verify → execute → render.

    Returns a result dict suitable for ``compute_all_metrics``.
    """
    t0 = time.perf_counter()

    # Compile
    compiled_output = ""
    try:
        raw_result = compiler.compile(story)
        # Rule compiler returns (list[dict], bool); model compiler returns str
        if isinstance(raw_result, tuple):
            ops_list, success = raw_result
            compiled_output = json.dumps(ops_list) if success else ""
        else:
            compiled_output = str(raw_result)
    except Exception as exc:
        logger.warning("Compilation failed: %s", exc)
        compiled_output = ""

    # Verify
    ops, vr = verifier.verify(compiled_output)

    # Execute (only when ops are valid)
    exec_result = None
    execution_success = False
    if ops is not None:
        exec_result = executor.execute(ops)
        execution_success = exec_result.valid and exec_result.error is None

    # Render answer (raw numeric for evaluation matching)
    predicted_answer = ""
    if exec_result is not None and execution_success:
        predicted_answer = renderer.render_raw(exec_result)
    elif ops is not None and exec_result is not None:
        # Execution failed — still try to extract answer
        predicted_answer = renderer.render_raw(exec_result)

    latency_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "compiled_output": compiled_output,
        "predicted_answer": predicted_answer,
        "execution_success": execution_success,
        "valid_json": vr.valid_json,
        "valid_ops": vr.valid_ops,
        "latency_ms": latency_ms,
        "tokens_in": None,
        "tokens_out": None,
    }


def _run_direct_baseline(
    story: str,
    model: Any,
) -> dict[str, Any]:
    """Run the direct-answer baseline.

    Returns a result dict suitable for ``compute_all_metrics``.
    """
    t0 = time.perf_counter()
    try:
        predicted_answer = model.answer(story)
    except Exception as exc:
        logger.warning("Direct baseline failed: %s", exc)
        predicted_answer = ""
    latency_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "compiled_output": "",
        "predicted_answer": str(predicted_answer),
        "execution_success": False,  # not applicable for direct baselines
        "valid_json": False,
        "valid_ops": False,
        "latency_ms": latency_ms,
        "tokens_in": None,
        "tokens_out": None,
    }


def _run_heuristic_baseline(
    story: str,
    baseline: Any,
) -> dict[str, Any]:
    """Run the heuristic baseline.

    Returns a result dict suitable for ``compute_all_metrics``.
    """
    t0 = time.perf_counter()
    try:
        predicted_answer = baseline.answer(story)
    except Exception as exc:
        logger.warning("Heuristic baseline failed: %s", exc)
        predicted_answer = ""
    latency_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "compiled_output": "",
        "predicted_answer": str(predicted_answer),
        "execution_success": False,
        "valid_json": False,
        "valid_ops": False,
        "latency_ms": latency_ms,
        "tokens_in": None,
        "tokens_out": None,
    }


# ── public API ─────────────────────────────────────────────────────────

def run_benchmark(
    benchmark_path: Path, config: EvalConfig | None = None
) -> dict[str, Any]:
    """Run the full benchmark across all available systems.

    For each system on each sample the runner:
    1. Compiles / answers the input story.
    2. Verifies JSON validity and operation schemas (SAGE systems).
    3. Executes the operations against the deterministic engine.
    4. Compares the rendered answer to the ground truth.
    5. Records latency and token counts.

    Args:
        benchmark_path: Path to a JSONL benchmark file.  Each line must be
            a JSON object with at least ``"id"``, ``"story"``,
            ``"ops"``, and ``"answer"`` fields.
        config: Optional ``EvalConfig``; sensible defaults are used when
            omitted.

    Returns:
        A dict with ``"results"`` (list of per-sample result dicts) and
        ``"metrics"`` (aggregate per-system metrics from
        ``compute_all_metrics``).
    """
    cfg = config or EvalConfig()
    engine_cfg = EngineConfig()
    samples = _load_benchmark(benchmark_path)

    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    all_results: list[dict[str, Any]] = []

    # ── Rule Compiler ──────────────────────────────────────────────
    if _RuleCompiler is not None:
        logger.info("Running rule compiler …")
        rc = _RuleCompiler()
        for sample in samples:
            story = sample.get("story", "")
            ground_truth = str(sample.get("answer", ""))
            pipeline = _run_sage_pipeline(story, rc, verifier, executor, renderer)
            all_results.append({
                "id": sample.get("id", ""),
                "system": "rule_compiler",
                "ground_truth_answer": ground_truth,
                "predicted_answer": pipeline["predicted_answer"],
                "compiled_output": pipeline["compiled_output"],
                "execution_success": pipeline["execution_success"],
                "valid_json": pipeline["valid_json"],
                "valid_ops": pipeline["valid_ops"],
                "num_events": sample.get("metadata", {}).get("num_events",
                             len(sample.get("ops", []))),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": pipeline["latency_ms"],
                "tokens_in": pipeline["tokens_in"],
                "tokens_out": pipeline["tokens_out"],
            })

    # ── Model Compiler ─────────────────────────────────────────────
    if _ModelCompiler is not None:
        logger.info("Running model compiler …")
        mc = _ModelCompiler()
        for sample in samples:
            story = sample.get("story", "")
            ground_truth = str(sample.get("answer", ""))
            pipeline = _run_sage_pipeline(story, mc, verifier, executor, renderer)
            all_results.append({
                "id": sample.get("id", ""),
                "system": "model_compiler",
                "ground_truth_answer": ground_truth,
                "predicted_answer": pipeline["predicted_answer"],
                "compiled_output": pipeline["compiled_output"],
                "execution_success": pipeline["execution_success"],
                "valid_json": pipeline["valid_json"],
                "valid_ops": pipeline["valid_ops"],
                "num_events": sample.get("metadata", {}).get("num_events",
                             len(sample.get("ops", []))),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": pipeline["latency_ms"],
                "tokens_in": pipeline["tokens_in"],
                "tokens_out": pipeline["tokens_out"],
            })

    # ── Direct Answer Baseline ─────────────────────────────────────
    if _DirectAnswerModel is not None:
        logger.info("Running direct-answer baseline …")
        dam = _DirectAnswerModel()
        for sample in samples:
            story = sample.get("story", "")
            ground_truth = str(sample.get("answer", ""))
            out = _run_direct_baseline(story, dam)
            all_results.append({
                "id": sample.get("id", ""),
                "system": "direct_answer",
                "ground_truth_answer": ground_truth,
                "predicted_answer": out["predicted_answer"],
                "compiled_output": out["compiled_output"],
                "execution_success": out["execution_success"],
                "valid_json": out["valid_json"],
                "valid_ops": out["valid_ops"],
                "num_events": sample.get("metadata", {}).get("num_events",
                             len(sample.get("ops", []))),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": out["latency_ms"],
                "tokens_in": out["tokens_in"],
                "tokens_out": out["tokens_out"],
            })

    # ── Heuristic Baseline ─────────────────────────────────────────
    if _HeuristicBaseline is not None:
        logger.info("Running heuristic baseline …")
        hb = _HeuristicBaseline()
        for sample in samples:
            story = sample.get("story", "")
            ground_truth = str(sample.get("answer", ""))
            out = _run_heuristic_baseline(story, hb)
            all_results.append({
                "id": sample.get("id", ""),
                "system": "heuristic",
                "ground_truth_answer": ground_truth,
                "predicted_answer": out["predicted_answer"],
                "compiled_output": out["compiled_output"],
                "execution_success": out["execution_success"],
                "valid_json": out["valid_json"],
                "valid_ops": out["valid_ops"],
                "num_events": sample.get("metadata", {}).get("num_events",
                             len(sample.get("ops", []))),
                "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
                "latency_ms": out["latency_ms"],
                "tokens_in": out["tokens_in"],
                "tokens_out": out["tokens_out"],
            })

    metrics = compute_all_metrics(all_results)

    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": all_results,
        "metrics": metrics,
    }


def run_rule_only(
    benchmark_path: Path, max_samples: int = 100
) -> dict[str, Any]:
    """Quick evaluation using only the rule-based compiler.

    No model loading required. Useful for smoke-testing benchmarks
    and verifying the rule compiler's accuracy on synthetic data.

    Args:
        benchmark_path: Path to a JSONL benchmark file.
        max_samples: Maximum number of samples to evaluate.

    Returns:
        Dict with results and metrics for the rule compiler only.
    """
    samples = _load_benchmark(benchmark_path)[:max_samples]
    engine_cfg = EngineConfig()
    verifier = Verifier(engine_cfg)
    executor = Executor(engine_cfg)
    renderer = Renderer()

    if _RuleCompiler is None:
        raise ImportError("RuleCompiler not available")

    rc = _RuleCompiler()
    all_results: list[dict[str, Any]] = []

    for sample in samples:
        story = sample.get("story", "")
        ground_truth = str(sample.get("answer", ""))
        pipeline = _run_sage_pipeline(story, rc, verifier, executor, renderer)
        all_results.append({
            "id": sample.get("id", ""),
            "system": "rule_compiler",
            "ground_truth_answer": ground_truth,
            "predicted_answer": pipeline["predicted_answer"],
            "compiled_output": pipeline["compiled_output"],
            "execution_success": pipeline["execution_success"],
            "valid_json": pipeline["valid_json"],
            "valid_ops": pipeline["valid_ops"],
            "num_events": sample.get("metadata", {}).get("num_events",
                         len(sample.get("ops", []))),
            "noise_level": sample.get("metadata", {}).get("noise_level", 0.0),
            "latency_ms": pipeline["latency_ms"],
            "tokens_in": pipeline["tokens_in"],
            "tokens_out": pipeline["tokens_out"],
        })

    metrics = compute_all_metrics(all_results)

    return {
        "benchmark": str(benchmark_path),
        "num_samples": len(samples),
        "results": all_results,
        "metrics": metrics,
    }


class BenchmarkRunner:
    """Class-based interface for running benchmarks.

    Holds configuration and shared engine/verifier/renderer instances so
    that repeated calls are cheaper and logging is co-located.

    Usage::

        runner = BenchmarkRunner(EvalConfig(benchmark_path=Path("bench.jsonl")))
        report = runner.run()
        runner.print_report()
    """

    def __init__(self, config: EvalConfig | None = None):
        self.config = config or EvalConfig()
        self._engine_cfg = EngineConfig()
        self._verifier = Verifier(self._engine_cfg)
        self._executor = Executor(self._engine_cfg)
        self._renderer = Renderer()

    def run(self, benchmark_path: Path | None = None) -> dict[str, Any]:
        """Run the benchmark and return the full report dict.

        Args:
            benchmark_path: Override the path in the config.

        Returns:
            The same dict as ``run_benchmark``.
        """
        path = benchmark_path or self.config.benchmark_path
        return run_benchmark(path, self.config)

    @property
    def verifier(self) -> Verifier:
        return self._verifier

    @property
    def executor(self) -> Executor:
        return self._executor

    @property
    def renderer(self) -> Renderer:
        return self._renderer
