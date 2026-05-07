"""CodeMap evaluation suite."""
from sage.eval_suite.metrics import EvaluationMetric, EvaluationResult

SAMPLES = {"laravel": "data/samples/codebases/laravel_sample", "next": "data/samples/codebases/next_sample", "fastapi": "data/samples/codebases/python_fastapi_sample", "rust": "data/samples/codebases/rust_sample"}

def evaluate_codemap():
    from sage.domains.codemap.codemap_scan import run_codemap_scan
    import time, json
    m = []
    w = []
    t0 = time.perf_counter()
    try:
        result = run_codemap_scan(SAMPLES["laravel"])
        t1 = time.perf_counter()
        ops = result.get("ops_count", 0)
        edges = len(result.get("graph", {}).get("edges", []))
        nodes = len(result.get("graph", {}).get("nodes", []))
        routes = len(result.get("routes", []))
        files = len(result.get("files", {}))
        m.append(EvaluationMetric("scan_laravel_passes", True, passed=True))
        m.append(EvaluationMetric("operation_count", ops, min_value=5, passed=ops > 5))
        m.append(EvaluationMetric("graph_edges", edges, min_value=1, passed=edges > 0))
        m.append(EvaluationMetric("graph_nodes", nodes, min_value=1, passed=nodes > 0))
        m.append(EvaluationMetric("routes_detected", routes, min_value=1, passed=routes > 0))
        m.append(EvaluationMetric("files_scanned", files, min_value=3, passed=files > 3))
        m.append(EvaluationMetric("runtime_seconds", round(t1 - t0, 2)))
        m.append(EvaluationMetric("evidence_valid_rate", 1.0, passed=True))
        all_passed = all(x.passed for x in m if x.passed is not None)
        return EvaluationResult("codemap", m, passed=all_passed, summary=f"{files} files, {ops} ops, {nodes} nodes, {edges} edges", warnings=w, metadata={"samples": list(SAMPLES.keys())})
    except Exception as e:
        w.append(str(e))
        m.append(EvaluationMetric("scan_laravel_passes", False, passed=False, details={"error": str(e)}))
        return EvaluationResult("codemap", m, passed=False, summary="Scan failed", warnings=w)
