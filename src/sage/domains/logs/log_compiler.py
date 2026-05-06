"""Rule-based log compiler for SAGE Incident Lens.

Compiles parsed Laravel log blocks into evidence-bound incident operations.
"""

from __future__ import annotations
import re
from .log_ops import (
    ERROR_EVENT, WARNING_EVENT, EXCEPTION_EVENT, HTTP_ERROR,
    FAILED_JOB, MAIL_FAILURE, QUEUE_FAILURE, DATABASE_ERROR,
    AUTH_ERROR, RECOVERY_EVENT, QUERY_INCIDENT,
)


class LaravelLogCompiler:
    """Compiles log blocks into incident operations using rule-based classification."""

    # Classification rules: (regex pattern, operation type)
    RULES = [
        # Mail failures
        (r'\b(Mail|SMTP|Swift_?Mailer|Symfony.*Mailer|mail|Mandrill|Mailgun|Postmark|Sendmail)\b', MAIL_FAILURE),
        (r'\b(Failed\s+to\s+send\s+mail|mail\s+delivery\s+failed|Unable\s+to\s+send\s+email)\b', MAIL_FAILURE),
        # Queue / Job failures
        (r'\b(queue|failed_jobs|Illuminate\\\\Queue|MaxAttemptsExceededException|job\s+failed)\b', QUEUE_FAILURE),
        (r'\b(Failed\s+job|job\s+has\s+been\s+attempted|tries\s+attempts)\b', FAILED_JOB),
        # Database errors
        (r'\b(SQLSTATE|QueryException|Illuminate\\\\Database|database|deadlock|SQL.*error|syntax\s+error)\b', DATABASE_ERROR),
        (r'\b(Connection\s+refused|too\s+many\s+connections|MySQL\s+server\s+has\s+gone)\b', DATABASE_ERROR),
        # Auth errors
        (r'\b(403|401|Unauthorized|Unauthenticated|AuthenticationException|AccessDeniedHttpException)\b', AUTH_ERROR),
        # HTTP errors
        (r'\b(500|502|503|504|Internal\s+Server\s+Error|Bad\s+Gateway|Service\s+Unavailable)\b', HTTP_ERROR),
        # Recovery events
        (r'\b(restarted|recovered|cleared|cache\s+cleared|config\s+cached|horizon\s+restarted)\b', RECOVERY_EVENT),
        # Generic exceptions
        (r'\b(Exception|Error|Throwable|Fatal|ParseError|TypeError)\b', EXCEPTION_EVENT),
    ]

    def compile(self, log_blocks: list[dict]) -> list[dict]:
        """Compile log blocks into incident operations."""
        ops = []
        for block in log_blocks:
            op = self._classify_block(block)
            if op is not None:
                ops.append(op)
        return ops

    def _classify_block(self, block: dict) -> dict | None:
        """Classify a single log block into an operation."""
        level = block.get("level", "INFO").upper()
        message = block.get("message", "")
        raw = block.get("raw_block", message)
        evidence = block.get("evidence", {})

        # Try rule-based classification
        for pattern, op_type in self.RULES:
            if re.search(pattern, raw, re.IGNORECASE):
                return {
                    "op": op_type,
                    "timestamp": block.get("timestamp", ""),
                    "level": level,
                    "component": "laravel",
                    "exception": block.get("exception", ""),
                    "message": message[:200],
                    "file": block.get("file", ""),
                    "line_number": block.get("line_number", 0),
                    "evidence": evidence,
                }

        # Fallback: use log level
        if level == "ERROR":
            return {
                "op": ERROR_EVENT,
                "timestamp": block.get("timestamp", ""),
                "level": level,
                "component": "laravel",
                "exception": "",
                "message": message[:200],
                "file": block.get("file", ""),
                "line_number": block.get("line_number", 0),
                "evidence": evidence,
            }
        elif level == "WARNING":
            return {
                "op": WARNING_EVENT,
                "timestamp": block.get("timestamp", ""),
                "level": level,
                "component": "laravel",
                "exception": "",
                "message": message[:200],
                "file": block.get("file", ""),
                "line_number": block.get("line_number", 0),
                "evidence": evidence,
            }

        return None
