"""Rule-based log compiler for SAGE Incident Lens.

Compiles parsed Laravel log blocks into evidence-bound incident operations.
Classification is based on message + exception context, NOT stacktrace file paths.
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

    # Rules are (regex pattern, op_type, apply_to) where apply_to is:
    #   'message' — only check the message line
    #   'exception' — only check the exception field
    #   'context' — check message + exception (NOT stacktrace file paths)
    #   'raw' — check entire raw block
    RULES = [
        # ── Recovery events (checked FIRST to avoid misclassification) ──
        (r'\b(restarted|reconnected|re-established|rebuilt|resumed|back\s+online|now\s+processing)\b',
         RECOVERY_EVENT, 'message'),
        (r'\b(connection\s+restored|transport\s+connection\s+restored|database\s+connection\s+restored)\b',
         RECOVERY_EVENT, 'message'),
        (r'\b(cache\s+cleared|config\s+cached|horizon\s+restarted)\b',
         RECOVERY_EVENT, 'message'),

        # ── Database errors ──
        (r'\b(SQLSTATE|QueryException|SQL.*error|syntax\s+error|deadlock|integrity\s+constraint)\b',
         DATABASE_ERROR, 'message'),
        (r'\b(Connection\s+refused|too\s+many\s+connections|MySQL\s+server\s+has\s+gone|column\s+not\s+found)\b',
         DATABASE_ERROR, 'message'),
        (r'Illuminate\\Database\\QueryException', DATABASE_ERROR, 'exception'),
        (r'Illuminate\\Database\\[A-Za-z]+Exception', DATABASE_ERROR, 'exception'),

        # ── Mail failures (message only — file paths like app/Mail/… are NOT mail errors) ──
        (r'\b(Failed\s+to\s+send\s+mail|mail\s+delivery\s+failed|Unable\s+to\s+send\s+email|Unable\s+to\s+connect.*mail)\b',
         MAIL_FAILURE, 'message'),
        (r'\b(Expected\s+response\s+code.*but\s+got\s+code|Connection\s+could\s+not\s+be\s+established\s+with\s+host\s+smtp|Connection\s+to\s+smtp.*timed\s+out)\b',
         MAIL_FAILURE, 'message'),
        (r'\b(Swift_TransportException|TransportException|Mailer.*Exception)\b',
         MAIL_FAILURE, 'message'),
        (r'Symfony\\Component\\Mailer\\Exception', MAIL_FAILURE, 'exception'),
        (r'Swift_TransportException', MAIL_FAILURE, 'exception'),

        # ── Queue / Job failures ──
        (r'\b(MaxAttemptsExceededException|has been attempted too many times|job\s+failed|Failed\s+job)\b',
         QUEUE_FAILURE, 'context'),
        (r'\b(queue\s+worker\s+restarted\s+after\s+memory|Queue\s+connection.*pending\s+jobs)\b',
         QUEUE_FAILURE, 'message'),
        (r'Illuminate\\Queue\\MaxAttemptsExceededException', QUEUE_FAILURE, 'exception'),

        # ── HTTP errors ──
        (r'\b(500\s+Internal\s+Server\s+Error|502\s+Bad\s+Gateway|503\s+Service\s+Unavailable|504\s+Gateway\s+Timeout)\b',
         HTTP_ERROR, 'message'),
        (r'\b(MethodNotAllowedHttpException|NotFoundHttpException|HttpException)\b',
         HTTP_ERROR, 'context'),

        # ── Auth errors ──
        (r'\b(403\s+Forbidden|401\s+Unauthorized|Authentication\s+attempt\s+failed|Unauthenticated)\b',
         AUTH_ERROR, 'message'),
        (r'\b(AuthenticationException|AccessDeniedHttpException)\b',
         AUTH_ERROR, 'context'),

        # ── Generic exceptions ──
        (r'\b(Exception|FatalError|ParseError|TypeError)\b',
         EXCEPTION_EVENT, 'exception'),
        (r'\b(Class\s+"[^"]+"\s+not\s+found)\b',
         EXCEPTION_EVENT, 'message'),
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
        """Classify a single log block into an operation.

        Classification order:
        1. Recovery events (checked first — restoration phrases take priority)
        2. Rule-based on message / exception
        3. Level-based fallback (ERROR → ERROR_EVENT, WARNING → WARNING_EVENT)
        4. INFO/DEBUG lines are ignored (return None)
        """
        level = block.get("level", "INFO").upper()
        message = block.get("message", "")
        exception = block.get("exception", "") or ""
        raw = block.get("raw_block", message)
        evidence = block.get("evidence", {})
        context = (message + " " + exception)  # message + exception only, no file paths

        # Try rule-based classification
        for pattern, op_type, scope in self.RULES:
            search_text = None
            if scope == 'message':
                search_text = message
            elif scope == 'exception':
                search_text = exception
            elif scope == 'context':
                search_text = context
            elif scope == 'raw':
                search_text = raw
            else:
                search_text = context

            if search_text and re.search(pattern, search_text, re.IGNORECASE):
                return {
                    "op": op_type,
                    "timestamp": block.get("timestamp", ""),
                    "level": level,
                    "component": "laravel",
                    "exception": exception,
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
                "exception": exception,
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
                "exception": exception,
                "message": message[:200],
                "file": block.get("file", ""),
                "line_number": block.get("line_number", 0),
                "evidence": evidence,
            }

        return None
