"""Rule-based log compiler for SAGE Incident Lens."""
from __future__ import annotations
import re
from .log_ops import *

class LaravelLogCompiler:
    RULES = [
        (r'\b(SQLSTATE|QueryException|database\s+error)\b', DATABASE_ERROR),
        (r'\b(Mail|SMTP|Swift.*Mailer|mail\s+delivery\s+failed)\b', MAIL_FAILURE),
        (r'\b(queue|job\s+failed|MaxAttemptsExceeded)\b', QUEUE_FAILURE),
        (r'\b(403|401|Unauthorized|AuthenticationException)\b', AUTH_ERROR),
        (r'\b(500|502|503|Server\s+Error)\b', HTTP_ERROR),
        (r'\b(restarted|recovered|cleared|re-established)\b', RECOVERY_EVENT),
    ]

    def compile(self, log_blocks: list[dict]) -> list[dict]:
        ops = []
        for block in log_blocks:
            op = self._classify(block)
            if op:
                ops.append(op)
        return ops

    def _classify(self, block: dict) -> dict | None:
        level = block.get("level", "INFO").upper()
        msg = block.get("message", "")
        raw = block.get("raw_block", msg)
        ev = block.get("evidence", {})
        for pat, op_type in self.RULES:
            if re.search(pat, raw, re.IGNORECASE):
                return {"op": op_type, "timestamp": block.get("timestamp", ""),
                        "level": level, "component": "laravel",
                        "exception": block.get("exception", ""), "message": msg[:200],
                        "file": block.get("file", ""), "line_number": block.get("line_number", 0),
                        "evidence": ev}
        if level in ("ERROR", "WARNING"):
            return {"op": ERROR_EVENT if level == "ERROR" else WARNING_EVENT,
                    "timestamp": block.get("timestamp", ""), "level": level,
                    "component": "laravel", "exception": block.get("exception", ""),
                    "message": msg[:200], "file": block.get("file", ""),
                    "line_number": block.get("line_number", 0), "evidence": ev}
        return None
