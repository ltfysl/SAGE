"""Build dependency graph directly from CodeMap operations (no file re-parsing)."""
from __future__ import annotations
from collections import defaultdict


def build_graph_from_ops(ops: list[dict]) -> dict:
    """Build a graph (nodes + edges) from evidence-bound operations.

    Returns: {"nodes": [...], "edges": [...]}
    """
    nodes = {}   # id -> {type, label, evidence}
    edges = []

    # ── Collect all nodes ──
    for op in ops:
        op_type = op.get("op", "")
        file = op.get("file") or op.get("evidence", {}).get("file", "")

        # File node
        if file and file not in nodes:
            nodes[file] = {"id": file, "type": "file", "label": file.split("/")[-1]}

        # Symbol node for definitions
        name = op.get("name", "")
        if op_type.startswith("DEFINE_") and name:
            nid = f"symbol:{name}"
            if nid not in nodes:
                nodes[nid] = {"id": nid, "type": _node_type_for_op(op_type), "label": name, "evidence": op.get("evidence")}

        # Table node
        if op_type in ("DEFINE_TABLE", "MODEL_USES_TABLE", "READS_TABLE", "WRITES_TABLE") and name:
            nid = f"table:{name}"
            if nid not in nodes:
                nodes[nid] = {"id": nid, "type": "table", "label": name, "evidence": op.get("evidence")}

        # Route node
        if op_type in ("DEFINE_ROUTE", "DEFINE_API_ENDPOINT") and name:
            nid = f"route:{name}"
            if nid not in nodes:
                nodes[nid] = {"id": nid, "type": "route", "label": name, "evidence": op.get("evidence")}

    # ── Build edges ──
    for op in ops:
        op_type = op.get("op", "")
        file = op.get("file") or op.get("evidence", {}).get("file", "")
        name = op.get("name", "")
        evidence = op.get("evidence")

        if op_type == "IMPORTS_SYMBOL" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "IMPORTS", "evidence": evidence})

        elif op_type in ("CALLS_FUNCTION", "CALLS_METHOD") and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "CALLS", "evidence": evidence})

        elif op_type == "ROUTE_TO_HANDLER" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "ROUTE_TO_HANDLER", "evidence": evidence})

        elif op_type == "PAGE_USES_API" and file and name:
            target = _find_route_node(nodes, name) or f"route:{name}"
            edges.append({"from": file, "to": target, "type": "PAGE_USES_API", "evidence": evidence})

        elif op_type == "SERVICE_USES_MODEL" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "SERVICE_USES_MODEL", "evidence": evidence})

        elif op_type in ("READS_TABLE", "WRITES_TABLE") and file and name:
            target = _find_table_node(nodes, name) or f"table:{name}"
            edges.append({"from": file, "to": target, "type": op_type, "evidence": evidence})

        elif op_type == "MODEL_USES_TABLE" and file and name:
            target = _find_table_node(nodes, name) or f"table:{name}"
            edges.append({"from": file, "to": target, "type": "MODEL_USES_TABLE", "evidence": evidence})

        elif op_type == "TESTS_TARGET" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "TESTS_TARGET", "evidence": evidence})

        elif op_type == "CALLS_METHOD" and file and name:
            # Try to resolve target to a file
            target = _find_symbol_node(nodes, name) or _find_method_file(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "CALLS", "evidence": evidence})

        elif op_type == "SERVICE_USES_MODEL" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "SERVICE_USES_MODEL", "evidence": evidence})

        elif op_type == "CONTROLLER_USES_SERVICE" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "CONTROLLER_USES_SERVICE", "evidence": evidence})

        elif op_type == "DISPATCHES_JOB" and file and name:
            target = _find_symbol_node(nodes, name) or f"symbol:{name}"
            edges.append({"from": file, "to": target, "type": "DISPATCHES_JOB", "evidence": evidence})

        elif op_type == "DEFINE_API_ENDPOINT" and file and name:
            target = f"route:{name}"
            edges.append({"from": file, "to": target, "type": "DEFINES", "evidence": evidence})

        elif op_type == "DEFINE_ROUTE" and file and name:
            target = f"route:{name}"
            edges.append({"from": file, "to": target, "type": "DEFINES", "evidence": evidence})

    return {"nodes": list(nodes.values()), "edges": edges}


def _node_type_for_op(op_type: str) -> str:
    m = {
        "DEFINE_FUNCTION": "function", "DEFINE_METHOD": "method",
        "DEFINE_CLASS": "class", "DEFINE_MODEL": "model",
        "DEFINE_SERVICE": "service", "DEFINE_COMPONENT": "component",
        "DEFINE_MODULE": "module", "DEFINE_JOB": "job",
    }
    return m.get(op_type, "symbol")



def _find_method_file(nodes: dict, name: str) -> str | None:
    """Find a file node that defines a method matching the call."""
    # name like 'CourseProgress::update()' or '$this->progressService->commit()'
    # Try to extract class/service name
    import re
    cls = None
    m = re.match(r'([\w\]+)::', name)
    if m: cls = m.group(1)
    m2 = re.match(r'\->(\w+)->', name)
    if m2:
        svc = m2.group(1)
        for key in nodes:
            if key.startswith('symbol:') and svc.lower() in key.lower():
                return key
    if cls:
        for key in nodes:
            if key.startswith('symbol:') and cls.lower() in key.lower():
                return key
    return None


def _find_symbol_node(nodes: dict, name: str) -> str | None:
    nid = f"symbol:{name}"
    if nid in nodes:
        return nid
    # Case-insensitive fallback
    for key in nodes:
        if key.startswith("symbol:") and key.lower() == f"symbol:{name.lower()}":
            return key
    return None


def _find_table_node(nodes: dict, name: str) -> str | None:
    nid = f"table:{name}"
    if nid in nodes:
        return nid
    for key in nodes:
        if key.startswith("table:") and name.lower() in key.lower():
            return key
    return None


def _find_route_node(nodes: dict, name: str) -> str | None:
    nid = f"route:{name}"
    if nid in nodes:
        return nid
    for key in nodes:
        if key.startswith("route:") and name.lower() in key.lower():
            return key
    return None
