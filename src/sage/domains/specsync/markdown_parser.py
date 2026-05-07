"""Parse PRD/DESIGN/TASKS/ACCEPTANCE-CRITERIA markdown into requirement operations."""
import re, json
from pathlib import Path
from sage.core.operation import Operation
from sage.core.evidence import Evidence
from .spec_ops import *

def parse_markdown_files(folder):
    ops = []
    for file in sorted(Path(folder).rglob("*.md")):
        ops.extend(_parse_md_file(file))
    return ops

def _parse_md_file(file_path):
    text = Path(file_path).read_text(errors="replace")
    lines = text.split(chr(10))
    ops = []
    current_req = None
    for i, line in enumerate(lines):
        line_no = i + 1
        ev = Evidence(file=str(file_path), line=line_no, span=line[:220], confidence=1.0, parser="specsync_markdown")
        req_m = re.match(r"#{1,3}\s+(REQ-\d+|R-\d+)\s*:\s*(.+)", line)
        ac_m = re.match(r"#{2,4}\s+(AC-\d+)\s*:\s*(.+)", line)
        task_m = re.match(r"[-*]\s+\[([ xX])\]\s+(.+)", line)
        decision_m = re.match(r"#{1,3}\s+(DECISION|Decision)\s*:\s*(.+)", line, re.IGNORECASE)
        out_m = re.match(r"#{1,3}\s+Out of Scope\s*:\s*(.+)", line, re.IGNORECASE)
        missing_m = re.match(r"[-*]\s+MISSING\s*:\s*(.+)", line)
        if req_m:
            rid, desc = req_m.groups()
            current_req = rid
            ops.append(Operation(op=DEFINE_REQUIREMENT, domain="specsync", payload={"id":rid,"description":desc.strip(),"source":str(file_path)}, evidence=ev))
        elif ac_m:
            acid, desc = ac_m.groups()
            tag = current_req or acid
            ops.append(Operation(op=DEFINE_ACCEPTANCE_CRITERION, domain="specsync", payload={"id":acid,"description":desc.strip(),"parent_id":current_req or ""}, evidence=ev, tags=[tag]))
        elif task_m:
            done, desc = task_m.groups()
            status = STATUS_IMPLEMENTED if done in ("x","X") else STATUS_MISSING
            ops.append(Operation(op=DEFINE_TASK, domain="specsync", payload={"description":desc.strip(),"status":status}, evidence=ev))
        elif decision_m:
            ops.append(Operation(op=DEFINE_DECISION, domain="specsync", payload={"description":decision_m.group(2).strip()}, evidence=ev))
        elif out_m:
            ops.append(Operation(op=DEFINE_OUT_OF_SCOPE, domain="specsync", payload={"description":out_m.group(1).strip()}, evidence=ev))
        elif missing_m:
            ops.append(Operation(op=STATUS_MISSING, domain="specsync", payload={"description":missing_m.group(1).strip()}, evidence=ev))
    return ops
