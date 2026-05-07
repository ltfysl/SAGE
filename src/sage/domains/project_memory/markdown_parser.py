"""Parse meeting notes, tickets, status updates into memory operations."""
import re
from pathlib import Path
from sage.core.operation import Operation
from sage.core.evidence import Evidence
from .memory_ops import *

def parse_markdown_files(folder):
    ops = []
    for f in sorted(Path(folder).rglob("*.md")):
        ops.extend(_parse_file(f))
    return ops

def _parse_file(fp):
    text = Path(fp).read_text(errors="replace")
    lines = text.split(chr(10))
    ops = []
    for i, line in enumerate(lines):
        ln = i + 1
        s = line.strip()
        ev = Evidence(file=str(fp), line=ln, span=s[:220], confidence=1.0, parser="mem_markdown")
        dec = re.match(r"#{1,3}\s+(?:Decision|DECISION)\s*:\s*(.+)", s, re.IGNORECASE)
        task = re.match(r"[-*]\s+\[([ xX])\]\s+(?:TASK\s*:\s*)?(.+)", s, re.IGNORECASE)
        blocker = re.match(r"#{1,3}\s+(?:Blocker|BLOCKER)\s*:\s*(.+)", s, re.IGNORECASE)
        owner = re.match(r"[-*]\s+(?:Owner|OWNER)\s*:\s*(\w+)\s+(.+)", s, re.IGNORECASE)
        question = re.match(r"[-*]\s+(?:Question|Q)\s*:\s*(.+)", s, re.IGNORECASE)
        deadline = re.match(r"[-*]\s+(?:Deadline|Due)\s*:\s*(.+)", s, re.IGNORECASE)
        risk = re.match(r"#{1,3}\s+(?:Risk|RISK)\s*:\s*(.+)", s, re.IGNORECASE)
        follow = re.match(r"[-*]\s+(?:Follow.up|FOLLOW.UP)\s*:\s*(.+)", s, re.IGNORECASE)
        note = re.match(r"[-*]\s+(?:Note|NOTE)\s*:\s*(.+)", s, re.IGNORECASE)
        status = re.match(r"#{1,3}\s+(?:Status|STATUS)\s*:\s*(.+)", s, re.IGNORECASE)
        if dec: ops.append(Operation(op=DECISION, domain="project_memory", payload={"decision":dec.group(1).strip()}, evidence=ev))
        elif task:
            done, desc = task.groups()
            st = TASK_COMPLETED if done in ("x","X") else TASK_CREATED
            ops.append(Operation(op=st, domain="project_memory", payload={"description":desc.strip()}, evidence=ev))
        elif blocker: ops.append(Operation(op=BLOCKER, domain="project_memory", payload={"blocker":blocker.group(1).strip()}, evidence=ev))
        elif owner: ops.append(Operation(op=OWNER_ASSIGNED, domain="project_memory", payload={"owner":owner.group(1),"item":owner.group(2).strip()}, evidence=ev))
        elif question: ops.append(Operation(op=OPEN_QUESTION, domain="project_memory", payload={"question":question.group(1).strip()}, evidence=ev))
        elif deadline: ops.append(Operation(op=DEADLINE, domain="project_memory", payload={"deadline":deadline.group(1).strip()}, evidence=ev))
        elif risk: ops.append(Operation(op=RISK, domain="project_memory", payload={"risk":risk.group(1).strip()}, evidence=ev))
        elif follow: ops.append(Operation(op=FOLLOW_UP, domain="project_memory", payload={"follow_up":follow.group(1).strip()}, evidence=ev))
        elif note: ops.append(Operation(op=NOTE, domain="project_memory", payload={"note":note.group(1).strip()}, evidence=ev))
        elif status: ops.append(Operation(op=STATUS_CHANGE, domain="project_memory", payload={"status":status.group(1).strip()}, evidence=ev))
    return ops
