"""Evaluation metrics for SAGE.

Computes accuracy, validity, and execution rates for compiled outputs
and direct answers. All functions accept standard Python types so they
are easy to compose with benchmark result dicts.
"""

from __future__ import annotations

import json
from typing import Any

from sage.verifier.verifier import Verifier
from sage.engine.executor import Executor
from sage.config import EngineConfig


def exact_match(predicted: str, ground_truth: str) -> bool:
    """Check if predicted answer exactly matches ground truth."""
    return str(predicted).strip() == str(ground_truth).strip()


def answer_accuracy(predictions: list[str], ground_truths: list[str]) -> float:
    """Compute exact match accuracy across a batch.

    Args:
        predictions: List of predicted answer strings.
        ground_truths: List of ground-truth answer strings (same length).

    Returns:
        Accuracy as a float in [0.0, 1.0].
    """
    if not predictions:
        return 0.0
    correct = sum(
        1 for p, g in zip(predictions, ground_truths) if exact_match(p, g)
    )
    return correct / len(predictions)


def json_valid_rate(compiled_outputs: list[str]) -> float:
    """Rate of outputs that are valid JSON arrays.

    Args:
        compiled_outputs: Raw string outputs from a compiler.

    Returns:
        Fraction of outputs that parse as valid JSON arrays.
    """
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
    """Rate of outputs whose operations pass schema validation.

    Uses ``sage.verifier.Verifier`` to validate each output against the
    SAGE operation schema.

    Args:
        compiled_outputs: Raw string outputs from a compiler.

    Returns:
        Fraction of outputs with fully valid operation sequences.
    """
    if not compiled_outputs:
        return 0.0
    verifier = Verifier()
    valid = 0
    for raw in compiled_outputs:
        _, result = verifier.verify(raw)
        if result.valid_ops:
            valid += 1
    return valid / len(compiled_outputs)


def execution_success_rate(
    compiled_outputs: list[str], executor: Executor | None = None
) -> float:
    """Rate of outputs that execute without errors.

    Each output is verified and then executed against a fresh state store.

    Args:
        compiled_outputs: Raw string outputs from a compiler.
        executor: Optional pre-configured ``Executor``.  Created fresh
            when omitted.

    Returns:
        Fraction of outputs that execute successfully.
    """
    if not compiled_outputs:
        return 0.0
    if executor is None:
        executor = Executor(EngineConfig())
    verifier = Verifier()
    success = 0
    for raw in compiled_outputs:
        ops, _ = verifier.verify(raw)
        if ops is None:
            continue
        result = executor.execute(ops)
        if result.valid and result.error is None:
            success += 1
    return success / len(compiled_outputs)


def compute_all_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute every evaluation metric from a list of per-sample result dicts.

    Expected keys per dict::

        id                     – unique sample identifier
        ground_truth_answer    – expected answer string
        predicted_answer       – system-produced answer string
        compiled_output        – raw compiler output (JSON string)
        execution_success      – bool, did execution succeed
        valid_json             – bool, is output valid JSON
        valid_ops              – bool, are the ops schema-valid
        num_events             – number of events in the input
        noise_level            – noise level used (0.0 – 1.0)
        latency_ms             – compilation latency in ms
        tokens_in              – input token count (or None)
        tokens_out             – output token count (or None)

    Returns a dict with per-system aggregate metrics keyed by system name,
    plus an ``"overall"`` entry with dataset-wide sums and averages.
    """
    if not results:
        return {}

    # Group results by system
    by_system: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        system = r.get("system", "unknown")
        by_system.setdefault(system, []).append(r)

    metrics: dict[str, Any] = {}
    total_samples = len(results)

    for system, samples in by_system.items():
        n = len(samples)
        predictions = [str(s.get("predicted_answer", "")) for s in samples]
        ground_truths = [str(s.get("ground_truth_answer", "")) for s in samples]
        compiled_outputs = [str(s.get("compiled_output", "")) for s in samples]

        latencies = [s.get("latency_ms", 0.0) or 0.0 for s in samples]
        exec_success = sum(1 for s in samples if s.get("execution_success"))
        json_ok = sum(1 for s in samples if s.get("valid_json"))
        ops_ok = sum(1 for s in samples if s.get("valid_ops"))
        tokens_in = [s.get("tokens_in") for s in samples if s.get("tokens_in") is not None]
        tokens_out = [s.get("tokens_out") for s in samples if s.get("tokens_out") is not None]

        metrics[system] = {
            "num_samples": n,
            "accuracy": answer_accuracy(predictions, ground_truths),
            "json_valid_rate": json_ok / n if n else 0.0,
            "ops_valid_rate": ops_ok / n if n else 0.0,
            "execution_success_rate": exec_success / n if n else 0.0,
            "avg_latency_ms": sum(latencies) / n if n else 0.0,
            "total_tokens_in": sum(tokens_in),
            "total_tokens_out": sum(tokens_out),
            "avg_tokens_in": sum(tokens_in) / len(tokens_in) if tokens_in else None,
            "avg_tokens_out": sum(tokens_out) / len(tokens_out) if tokens_out else None,
        }

    # Overall
    all_predictions = [str(r.get("predicted_answer", "")) for r in results]
    all_ground_truths = [str(r.get("ground_truth_answer", "")) for r in results]
    all_latencies = [r.get("latency_ms", 0.0) or 0.0 for r in results]
    all_exec_ok = sum(1 for r in results if r.get("execution_success"))
    all_json_ok = sum(1 for r in results if r.get("valid_json"))
    all_ops_ok = sum(1 for r in results if r.get("valid_ops"))
    all_tokens_in = [r.get("tokens_in") for r in results if r.get("tokens_in") is not None]
    all_tokens_out = [r.get("tokens_out") for r in results if r.get("tokens_out") is not None]

    metrics["overall"] = {
        "num_samples": total_samples,
        "accuracy": answer_accuracy(all_predictions, all_ground_truths),
        "json_valid_rate": all_json_ok / total_samples if total_samples else 0.0,
        "ops_valid_rate": all_ops_ok / total_samples if total_samples else 0.0,
        "execution_success_rate": all_exec_ok / total_samples if total_samples else 0.0,
        "avg_latency_ms": sum(all_latencies) / total_samples if total_samples else 0.0,
        "total_tokens_in": sum(all_tokens_in),
        "total_tokens_out": sum(all_tokens_out),
        "avg_tokens_in": sum(all_tokens_in) / len(all_tokens_in) if all_tokens_in else None,
        "avg_tokens_out": sum(all_tokens_out) / len(all_tokens_out) if all_tokens_out else None,
    }

    return metrics
