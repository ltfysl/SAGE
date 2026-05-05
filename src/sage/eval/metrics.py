"""Evaluation metrics for SAGE — with evidence and event-bucket support."""

from __future__ import annotations

import json
from typing import Any

from sage.verifier.verifier import Verifier
from sage.engine.executor import Executor
from sage.config import EngineConfig


def exact_match(predicted: str, ground_truth: str) -> bool:
    return str(predicted).strip() == str(ground_truth).strip()


def answer_accuracy(predictions: list[str], ground_truths: list[str]) -> float:
    if not predictions:
        return 0.0
    return sum(1 for p, g in zip(predictions, ground_truths) if exact_match(p, g)) / len(predictions)


def json_valid_rate(compiled_outputs: list[str]) -> float:
    if not compiled_outputs:
        return 0.0
    valid = 0
    for raw in compiled_outputs:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                valid += 1
        except (json.JSONDecodeError, TypeError):
            pass
    return valid / len(compiled_outputs)


def ops_valid_rate(compiled_outputs: list[str]) -> float:
    if not compiled_outputs:
        return 0.0
    verifier = Verifier()
    valid = 0
    for raw in compiled_outputs:
        _, result = verifier.verify(raw)
        if result.valid_ops:
            valid += 1
    return valid / len(compiled_outputs)


def evidence_valid_rate(results: list[dict]) -> float:
    """Rate of results where evidence checks passed."""
    if not results:
        return 0.0
    valid = sum(1 for r in results if r.get("evidence_valid", False))
    return valid / len(results)


def execution_success_rate(results: list[dict]) -> float:
    if not results:
        return 0.0
    success = sum(1 for r in results if r.get("execution_success", False))
    return success / len(results)


def unsupported_operation_rate(results: list[dict]) -> float:
    """Rate of ground-truth ops that the compiler failed to compile (missing)."""
    total_gt = 0
    total_missing = 0
    for r in results:
        gt = r.get("ground_truth_ops", [])
        missing = r.get("missing_ops", [])
        total_gt += len(gt)
        total_missing += len(missing)
    return total_missing / total_gt if total_gt > 0 else 0.0


def hallucinated_operation_rate(results: list[dict]) -> float:
    """Rate of compiled ops that don't correspond to ground truth (extra)."""
    total_comp = 0
    total_extra = 0
    for r in results:
        comp = r.get("compiled_ops_raw", [])
        extra = r.get("extra_ops", [])
        total_comp += len(comp)
        total_extra += len(extra)
    return total_extra / total_comp if total_comp > 0 else 0.0


def accuracy_by_event_buckets(results: list[dict]) -> dict:
    """Group accuracy by event count buckets."""
    buckets = {
        "1-5": [], "6-25": [], "26-100": [], "101-500": [],
    }
    for r in results:
        n = r.get("num_events", 0)
        match = r.get("answer_match", False)
        if n <= 5:
            buckets["1-5"].append(match)
        elif n <= 25:
            buckets["6-25"].append(match)
        elif n <= 100:
            buckets["26-100"].append(match)
        else:
            buckets["101-500"].append(match)
    return {
        bucket: {
            "samples": len(matches),
            "accuracy": sum(matches) / len(matches) if matches else 0.0,
        }
        for bucket, matches in buckets.items()
    }


def compute_all_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute all metrics from per-sample result dicts."""
    if not results:
        return {}

    by_system: dict[str, list[dict]] = {}
    for r in results:
        by_system.setdefault(r.get("system", "unknown"), []).append(r)

    metrics: dict[str, Any] = {}
    for system, samples in by_system.items():
        n = len(samples)
        predictions = [str(s.get("predicted_answer", "")) for s in samples]
        ground_truths = [str(s.get("ground_truth_answer", "")) for s in samples]
        compiled_outputs = [str(s.get("compiled_output", "")) for s in samples]
        latencies = [s.get("latency_ms", 0.0) or 0.0 for s in samples]
        events = [s.get("num_events", 0) for s in samples]

        metrics[system] = {
            "num_samples": n,
            "accuracy": answer_accuracy(predictions, ground_truths),
            "json_valid_rate": json_valid_rate(compiled_outputs),
            "ops_valid_rate": ops_valid_rate(compiled_outputs),
            "evidence_valid_rate": evidence_valid_rate(samples),
            "execution_success_rate": execution_success_rate(samples),
            "unsupported_operation_rate": unsupported_operation_rate(samples),
            "hallucinated_operation_rate": hallucinated_operation_rate(samples),
            "avg_events": sum(events) / n if n else 0,
            "avg_latency_ms": sum(latencies) / n if n else 0.0,
        }

    # Overall
    all_pred = [str(r.get("predicted_answer", "")) for r in results]
    all_gt = [str(r.get("ground_truth_answer", "")) for r in results]
    all_comp = [str(r.get("compiled_output", "")) for r in results]
    all_lat = [r.get("latency_ms", 0.0) or 0.0 for r in results]
    all_events = [r.get("num_events", 0) for r in results]
    metrics["overall"] = {
        "num_samples": len(results),
        "accuracy": answer_accuracy(all_pred, all_gt),
        "json_valid_rate": json_valid_rate(all_comp),
        "ops_valid_rate": ops_valid_rate(all_comp),
        "evidence_valid_rate": evidence_valid_rate(results),
        "execution_success_rate": execution_success_rate(results),
        "unsupported_operation_rate": unsupported_operation_rate(results),
        "hallucinated_operation_rate": hallucinated_operation_rate(results),
        "avg_events": sum(all_events) / len(results) if results else 0,
        "avg_latency_ms": sum(all_lat) / len(results) if results else 0.0,
    }

    return metrics
