"""Flow builder for SAGE CodeMap — chains route→controller→service→model→table."""
from __future__ import annotations


def build_flow(task: str, codemap: dict, graph: dict) -> dict:
    """Build a runtime flow chain from task keywords and graph edges.

    Returns: {"name": "...", "confidence": 0.0-1.0, "steps": [...], "evidence": [...]}
    """
    keywords = task.lower().split()
    edges = graph.get("edges", [])
    routes = codemap.get("routes", [])
    files = codemap.get("files", {})
    symbols = codemap.get("symbols", {})

    steps = []
    route_found = None
    controller_found = None
    service_found = None
    model_found = None
    table_found = None

    # 1. Find route matching keywords
    for r in routes:
        rname = str(r.get("name", "")).lower()
        if any(kw in rname for kw in keywords):
            route_found = r
            steps.append({"type": "route", "label": r.get("name", ""),
                          "file": r.get("evidence", {}).get("file", ""),
                          "line": r.get("evidence", {}).get("line", 0)})
            break

    # 2. Follow edges: route file → controller (IMPORTS or DEFINES edges)
    route_file = route_found.get("evidence", {}).get("file", "") if route_found else ""
    for e in edges:
        if route_file and e.get("from") == route_file and "Controller" in e.get("to", ""):
            controller_found = _find_file_op(files, e["to"])
            if controller_found:
                steps.append({"type": "controller", "label": _basename(e["to"]),
                              "file": e["to"]})
                break

    # 3. Controller → Service (IMPORTS edges)
    ctrl_file = controller_found.get("file", "") if controller_found else ""
    for e in edges:
        if ctrl_file and e.get("from") == ctrl_file and ("Service" in e.get("to", "") or "Service" in _basename(e.get("to", ""))):
            service_found = _find_file_op(files, e["to"])
            if service_found:
                steps.append({"type": "service", "label": _basename(e["to"]),
                              "file": e["to"]})
                break

    # 4. Service → Model (IMPORTS or USES edges)
    svc_file = service_found.get("file", "") if service_found else ""
    for e in edges:
        if svc_file and e.get("from") == svc_file and ("Model" in e.get("to", "") or "Model" in _basename(e.get("to", ""))):
            model_found = _find_file_op(files, e["to"])
            if model_found:
                steps.append({"type": "model", "label": _basename(e["to"]),
                              "file": e["to"]})
                break

    # 5. Model → Table or Service → Table (WRITES_TABLE, READS_TABLE, MODEL_USES_TABLE)
    for e in edges:
        et = e.get("type", "")
        if et in ("WRITES_TABLE", "READS_TABLE", "MODEL_USES_TABLE"):
            src = e.get("from", "")
            if svc_file and src == svc_file:
                table_found = e.get("to", "").replace("table:", "")
                steps.append({"type": "table", "label": table_found})
                break
            if model_found and src == model_found.get("file", ""):
                table_found = e.get("to", "").replace("table:", "")
                steps.append({"type": "table", "label": table_found})
                break

    # 6. If no controller found via edges, search files for controller class matching keywords
    if not controller_found:
        for fp, ops in files.items():
            for op in ops:
                if op.get("op") == "DEFINE_CLASS" and "Controller" in op.get("name", ""):
                    if any(kw in str(op).lower() for kw in keywords):
                        controller_found = op
                        steps.append({"type": "controller", "label": op["name"],
                                      "file": fp})
                        break
            if controller_found:
                break

    confidence = min(0.2 * len(steps), 1.0)
    return {
        "name": f"Flow for: {task[:60]}",
        "confidence": round(confidence, 2),
        "steps": steps,
        "evidence": [s.get("file", "") for s in steps if s.get("file")],
    }


def _basename(path: str) -> str:
    return path.split("/")[-1] if "/" in path else path


def _find_file_op(files: dict, target: str) -> dict | None:
    """Find an operation in the files dict matching target path."""
    for fp, ops in files.items():
        if fp == target or fp.endswith("/" + target):
            for op in ops:
                if op.get("op", "").startswith("DEFINE_"):
                    return {"file": fp, **op}
    return None
