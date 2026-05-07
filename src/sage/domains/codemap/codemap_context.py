"""CodeMap context generator — produces high-quality context packs for coding agents.

v0.5: structured output, task intent extraction, graph-boosted ranking, JSON support.
"""
from __future__ import annotations
from pathlib import Path
import json


def generate_context(
    map_path: str | Path,
    task: str,
    max_results: int = 20,
    max_evidence_per_file: int = 3,
    max_span_chars: int = 220,
    format: str = "markdown",
) -> str | dict:
    """Generate a coding context pack from a codemap.

    Args:
        map_path: Path to codemap JSON file.
        task: Natural language task description.
        max_results: Maximum files to include.
        max_evidence_per_file: Max evidence snippets per file.
        max_span_chars: Max characters per evidence span.
        format: 'markdown', 'text', or 'json'.

    Returns:
        Markdown string, plain text, or dict (for JSON format).
    """
    from sage.domains.codemap.codemap_scan import load_codemap
    from sage.domains.codemap.codemap_ask import CodemapAsk

    data = load_codemap(map_path)
    ask = CodemapAsk(data)
    intent = _infer_intent(task)
    graph = data.get("graph", {})

    # Search with boosted scoring
    files = _search_boosted(ask, task, graph, intent, max_results)

    # Build flow
    flow = _infer_flow(files, data, task)

    # Build impact
    impact = _infer_impact_section(files, data)

    # Suggested tests
    tests = _suggest_tests(data, task)

    # Agent prompt
    prompt = _build_agent_prompt(task, intent, files, flow, impact, tests, max_span_chars)

    result = {
        "task": task,
        "intent": intent,
        "short_answer": _short_answer(intent, files, flow),
        "relevant_files": [
            {
                "file": f["file"],
                "score": f["score"],
                "why": f.get("matches", [])[:3],
                "ops": f.get("ops_count", 0),
                "evidence": _truncate_evidence(f.get("evidence_snippets", []), max_evidence_per_file, max_span_chars),
            }
            for f in files[:max_results]
        ],
        "likely_flow": flow,
        "impact_risks": impact,
        "suggested_tests": tests,
        "agent_prompt": prompt,
        "limitations": [
            "Static analysis only — dynamic calls and metaprogramming may be missed.",
            "File paths are evidence-bound to source; runtime resolution may differ.",
            "Graph edges are based on symbol matching, not full dataflow analysis.",
        ],
    }

    if format == "json":
        return result

    return _render_markdown(result, max_results, max_evidence_per_file, max_span_chars)


# ── Intent detection ──

def _infer_intent(task: str) -> str:
    t = task.lower()
    if any(w in t for w in ("fix", "bug", "not updating", "broken", "error", "fails", "crash")):
        return "bugfix"
    if any(w in t for w in ("refactor", "clean up", "restructure", "extract")):
        return "refactor"
    if any(w in t for w in ("add", "implement", "create", "build", "feature")):
        return "implementation"
    if any(w in t for w in ("test", "spec", "coverage")):
        return "testing"
    if any(w in t for w in ("understand", "explain", "how does", "what is", "find", "identify")):
        return "exploration"
    return "exploration"


# ── Boosted search ──

def _search_boosted(ask, task, graph, intent, max_results):
    """Search with graph neighbor and intent-based boosting."""
    keywords = task.lower().split()
    base = ask._search_fulltext(task, max_results=100, min_score=0)

    # Get raw scored files
    raw_files = []
    for f in base.get("evidence", []):
        fn = f.get("name") or f.get("evidence", {}).get("file", "")
        sc = int(f.get("op", "score=0").replace("score=", ""))
        raw_files.append({"file": fn, "score": sc, "matches": [], "ops_count": 0})

    # Boost: table names in task → boost table-related files
    for f in raw_files:
        fp = f["file"].lower()
        for kw in keywords:
            if kw in fp:
                f["score"] += 10

        # Graph neighbor boost
        edges = graph.get("edges", [])
        neighbor_score = 0
        for e in edges:
            if f["file"] in (e.get("from", ""), e.get("to", "")):
                neighbor_score += 2
        f["score"] += min(neighbor_score, 30)

        # Intent-based tuning
        if intent in ("bugfix", "implementation"):
            if any(p in fp for p in ("Controller", "Service", "Model", "route", "Job")):
                f["score"] += 5
        if "table" in task.lower() or "writes" in task.lower():
            if "migration" in fp or "Model" in fp or "Service" in fp:
                f["score"] += 10

    raw_files.sort(key=lambda x: -x["score"])
    return raw_files[:max_results]


# ── Flow inference ──

def _infer_flow(files, data, task=""):
    # Try flow builder first
    try:
        from sage.domains.codemap.flow_builder import build_flow
        graph = data.get("graph", {})
        flow_result = build_flow(task, data, graph)
        if flow_result.get("steps") and len(flow_result["steps"]) >= 2:
            return flow_result["steps"]
    except (ImportError, Exception):
        pass
    """Infer a likely processing flow from files."""
    steps = []
    file_paths = [f["file"] for f in files]
    routes = data.get("routes", [])
    edges = data.get("graph", {}).get("edges", [])

    # Route
    for r in routes[:10]:
        rname = r.get("name", "")
        if any(m in rname.upper() for m in ("GET", "POST", "PUT", "DELETE", "RESOURCE")):
            steps.append({"step": "Route", "detail": rname, "file": r.get("evidence", {}).get("file", "")})
            break
    # Controller
    for f in file_paths:
        if "Controller" in f and "test" not in f.lower():
            steps.append({"step": "Controller", "detail": f.split("/")[-1], "file": f})
            break
    # Service
    for f in file_paths:
        if "Service" in f and "test" not in f.lower():
            steps.append({"step": "Service", "detail": f.split("/")[-1], "file": f})
            break
    # Model
    for f in file_paths:
        if ("/Model" in f or "Models/" in f) and "test" not in f.lower():
            steps.append({"step": "Model", "detail": f.split("/")[-1], "file": f})
            break
    # Migration
    for f in file_paths:
        if "migration" in f:
            steps.append({"step": "Migration", "detail": f.split("/")[-1], "file": f})
            break
    if not steps:
        steps.append({"step": "Note", "detail": "No clear flow path found — static analysis limited", "file": ""})
    return steps


# ── Impact ──

def _infer_impact_section(files, data):
    """Infer impact areas from files."""
    impact = []
    tables = data.get("table_writes", {})
    if tables:
        impact.append(f"Tables written: {', '.join(list(tables.keys())[:5])}")
    routes = data.get("routes", [])
    if routes:
        impact.append(f"Routes/endpoints: {len(routes)} total")
    return impact[:8]


# ── Tests ──

def _suggest_tests(data, task):
    """Suggest test files based on task keywords."""
    files = data.get("files", {})
    test_files = [f for f in files if ("test" in f.lower() or "spec" in f.lower()) and ("Test.php" in f or "_test.py" in f or ".test." in f or "Spec.php" in f or "tests/" in f)]
    if test_files:
        return test_files[:8]
    kw = task.lower().split()[0] if task.split() else "codemap"
    return [f"pytest tests/ -k {kw}"]


# ── Agent prompt ──

def _build_agent_prompt(task, intent, files, flow, impact, tests, max_span):
    lines = []
    lines.append(f"## Task: {task}")
    lines.append(f"## Intent: {intent}")
    lines.append("")
    lines.append("### Relevant Files")
    for i, f in enumerate(files[:10]):
        fn = f["file"].split("/")[-1]
        lines.append(f"{i+1}. `{f['file']}` (score: {f['score']})")
    lines.append("")
    lines.append("### Likely Flow")
    for s in flow:
        lines.append(f"- {s.get('type', s.get('step', '?'))}: {s.get('detail', s.get('label', '?'))} ({s.get('file', '')})")
    lines.append("")
    lines.append("### Constraints")
    lines.append("- Do not modify neural training or Incident Lens.")
    lines.append("- Keep all operations evidence-bound.")
    lines.append("- Do not change unrelated files.")
    if tests:
        lines.append(f"- Run tests: `pytest {' '.join(tests[:3])}`")
    lines.append("")
    lines.append("### Limitations")
    lines.append("- Static analysis only. Dynamic dependencies may be missed.")
    return "\n".join(lines)


# ── Short answer ──

def _short_answer(intent, files, flow):
    if not files:
        return "No strongly relevant files found."
    top = files[0]["file"].split("/")[-1]
    if intent == "bugfix":
        return f"Likely involves {top} and related service/model files. Check flow: {' → '.join(s.get('type', s.get('step', '?')) for s in flow[:4])}."
    return f"Key files found: {top} and {len(files)} others. Flow: {' → '.join(s.get('type', s.get('step', '?')) for s in flow[:4])}."


# ── Helpers ──

def _truncate_evidence(snippets, max_count, max_chars):
    result = []
    for s in snippets[:max_count]:
        text = s if isinstance(s, str) else str(s)
        if len(text) > max_chars:
            text = text[:max_chars] + "…"
        result.append(text)
    return result


def _render_markdown(result, max_files, max_ev, max_span):
    lines = []
    lines.append("# SAGE CodeMap Context Pack")
    lines.append("")
    lines.append(f"**Task:** {result['task']}")
    lines.append(f"**Intent:** {result['intent']}")
    lines.append("")
    lines.append(f"**Short Answer:** {result['short_answer']}")
    lines.append("")

    lines.append("## Relevant Files")
    for i, f in enumerate(result["relevant_files"][:max_files]):
        fn = f["file"].split("/")[-1]
        lines.append(f"### {i+1}. {fn} (score: {f['score']})")
        lines.append(f"`{f['file']}`")
        if f.get("why"):
            lines.append(f"*Why:* {'; '.join(f['why'][:3])}")
        for ev in f.get("evidence", [])[:max_ev]:
            lines.append(f"- {ev}")
        lines.append("")

    lines.append("## Likely Flow")
    for s in result["likely_flow"]:
        lines.append(f"- **{s.get('type', s.get('step', '?'))}**: {s.get('detail', s.get('label', '?'))} ({s.get('file', '')})")
    lines.append("")

    if result.get("impact_risks"):
        lines.append("## Impact / Risk Areas")
        for i in result["impact_risks"]:
            lines.append(f"- {i}")
        lines.append("")

    if result.get("suggested_tests"):
        lines.append("## Suggested Tests")
        for t in result["suggested_tests"][:5]:
            lines.append(f"- `{t}`")
        lines.append("")

    lines.append("## Agent Prompt")
    lines.append("```")
    lines.append(result["agent_prompt"])
    lines.append("```")
    lines.append("")

    lines.append("## Limitations")
    for lim in result.get("limitations", []):
        lines.append(f"- {lim}")

    return "\n".join(lines)
