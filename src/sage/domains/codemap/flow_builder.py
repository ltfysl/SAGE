"""Flow builder for SAGE CodeMap — chains route→controller→service→model→table."""
from __future__ import annotations


def build_flow(task: str, codemap: dict, graph: dict) -> dict:
    """Build a runtime flow chain from task keywords and graph edges."""
    keywords = task.lower().split()
    edges = graph.get("edges", [])
    routes = codemap.get("routes", [])
    files = codemap.get("files", {})

    steps = []
    seen_files = set()
    route_file = controller_file = service_file = model_file = table_name = None

    # 1. Find route matching keywords
    for r in routes:
        rname = str(r.get("name", "")).lower()
        rfile = r.get("evidence", {}).get("file", "")
        if any(kw in rname for kw in keywords):
            route_file = rfile
            steps.append({"type": "route", "label": r.get("name", ""), "file": rfile})
            seen_files.add(rfile)
            break

    # 2. Route → Controller (via IMPORTS edges from route file)
    for e in edges:
        src = e.get("from", "")
        dst = e.get("to", "")
        if route_file and src == route_file:
            if "Controller" in dst or "controller" in dst.lower():
                controller_file = _resolve_file(dst, files)
                steps.append({"type": "controller", "label": _basename(dst), "file": controller_file or dst})
                if controller_file:
                    seen_files.add(controller_file)
                break

    # 3. Controller → Service (via CALLS, CONTROLLER_USES_SERVICE, or IMPORTS edges from controller file)
    for e in edges:
        src = e.get("from", "")
        dst = e.get("to", "")
        if controller_file and src == controller_file:
            etype = e.get("type", "")
            # Accept ALL CONTROLLER_USES_SERVICE edges and common runtime class patterns
            is_runtime = True  # always follow edges from controller
            if etype in ("CONTROLLER_USES_SERVICE", "CALLS", "IMPORTS", "USES_CLASS"):
                service_file = _resolve_file(dst, files)
                steps.append({"type": "service", "label": _basename(dst), "file": service_file or dst})
                if service_file:
                    seen_files.add(service_file)
                break

    # 4. Service → Model (via SERVICE_USES_MODEL, CALLS, or IMPORTS from service file)
    for e in edges:
        src = e.get("from", "")
        dst = e.get("to", "")
        if service_file and src == service_file:
            etype = e.get("type", "")
            if etype in ("SERVICE_USES_MODEL", "CALLS", "IMPORTS") and "Model" in dst or "model" in dst.lower():
                model_file = _resolve_file(dst, files)
                steps.append({"type": "model", "label": _basename(dst), "file": model_file or dst})
                if model_file:
                    seen_files.add(model_file)
                break

    # 5. Service/Controller/Model → Table (via WRITES_TABLE, READS_TABLE, MODEL_USES_TABLE)
    for e in edges:
        etype = e.get("type", "")
        if etype in ("WRITES_TABLE", "READS_TABLE", "MODEL_USES_TABLE"):
            src = e.get("from", "")
            dst = e.get("to", "")
            if src in (service_file, controller_file, model_file):
                table_name = dst.replace("table:", "")
                steps.append({"type": "table", "label": table_name})
                break

    # 6. If no controller found via edges, search files by keyword
    if not controller_file:
        for fp, ops in files.items():
            for op in ops:
                name = op.get("name", "")
                if "Controller" in name and any(kw in str(op).lower() for kw in keywords):
                    controller_file = fp
                    steps.append({"type": "controller", "label": name, "file": fp})
                    seen_files.add(fp)
                    break
            if controller_file:
                break

    confidence = min(0.2 * len(steps), 1.0)
    return {
        "name": f"Flow: {task[:60]}",
        "confidence": round(confidence, 2),
        "steps": steps,
        "evidence": [s.get("file", "") for s in steps if s.get("file")],
    }



def _looks_like_model(symbol: str, files: dict) -> bool:
    """Check if a symbol looks like it refers to a model class."""
    name = symbol.replace("symbol:", "").replace("table:", "")
    # Check if any file defines it as DEFINE_MODEL
    for fp, ops in files.items():
        for op in ops:
            if op.get("op") == "DEFINE_MODEL" and op.get("name", "").lower() == name.lower():
                return True
    return False


def _basename(path: str) -> str:
    return path.split("/")[-1] if "/" in path else path


def _resolve_file(target: str, files: dict) -> str | None:
    """Resolve a symbol or path to an actual file in the codemap."""
    # Direct match
    if target in files:
        return target
    # Symbol match: symbol:Namespace\ClassName → find file that defines it
    if target.startswith("symbol:"):
        sym = target.replace("symbol:", "")
        # Try exact match first
        for fp, ops in files.items():
            for op in ops:
                if op.get("name") == sym and op.get("op", "").startswith("DEFINE_"):
                    return fp
        # Try matching just the class name (last segment after \ or \)
        basename = sym.split(chr(92))[-1]
        for fp, ops in files.items():
            for op in ops:
                if op.get("name") == basename and op.get("op", "").startswith("DEFINE_"):
                    return fp
        # Try case-insensitive
        for fp, ops in files.items():
            for op in ops:
                if op.get("name", "").lower() == basename.lower() and op.get("op", "").startswith("DEFINE_"):
                    return fp
    # Partial path match
    for fp in files:
        if fp.endswith("/" + target) or target in fp:
            return fp
    return None
