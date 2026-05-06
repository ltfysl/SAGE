"""Rule-based log compiler for SAGE Incident Lens.

Compiles parsed Laravel log blocks into evidence-bound incident operations.
Classification based on message + exception context, NOT stacktrace file paths.
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

    # Rules: (regex pattern, op_type, scope)
    # scope: 'message', 'exception', 'context' (message+exception), 'raw'
    RULES = [
        # ── Recovery events (checked FIRST) ──
        (r'\b(restarted|reconnected|re-established|rebuilt|resumed|back\s+online|now\s+processing)\b',
         RECOVERY_EVENT, 'message'),
        (r'\b(connection\s+restored|transport\s+connection\s+restored|database\s+connection\s+restored)\b',
         RECOVERY_EVENT, 'message'),
        (r'\b(cache\s+cleared|config\s+cached|horizon\s+restarted|queue\s+worker\s+restarted)\b',
         RECOVERY_EVENT, 'message'),

        # ── Database errors ──
        (r'\b(SQLSTATE|QueryException|SQL.*error|syntax\s+error|deadlock|integrity\s+constraint|General\s+error|no\s+such\s+table)\b',
         DATABASE_ERROR, 'message'),
        (r'\b(Connection\s+refused|too\s+many\s+connections|MySQL\s+server\s+has\s+gone|column\s+not\s+found)\b',
         DATABASE_ERROR, 'message'),
        (r'Illuminate\\Database\\', DATABASE_ERROR, 'exception'),
        (r'SQLSTATE\[', DATABASE_ERROR, 'message'),

        # ── Mail failures (message only — file paths like app/Mail/… are NOT mail errors) ──
        (r'\b(Failed\s+to\s+send\s+mail|mail\s+delivery\s+failed|Unable\s+to\s+send\s+email|Unable\s+to\s+connect.*mail)\b',
         MAIL_FAILURE, 'message'),
        (r'\b(Expected\s+response\s+code.*but\s+got\s+code|Connection\s+could\s+not\s+be\s+established\s+with\s+host\s+smtp|Connection\s+to\s+smtp.*timed\s+out)\b',
         MAIL_FAILURE, 'message'),
        (r'\b(Swift_TransportException|TransportException|Mailer.*Exception)\b',
         MAIL_FAILURE, 'context'),
        (r'Symfony\\Component\\Mailer\\Exception', MAIL_FAILURE, 'exception'),

        # ── Queue / Job failures ──
        (r'\b(MaxAttemptsExceededException|has been attempted too many times|job\s+failed|Failed\s+job)\b',
         QUEUE_FAILURE, 'context'),
        (r'\b(queue\s+worker\s+restarted\s+after\s+memory|Queue\s+connection.*pending\s+jobs|queue\s+worker\s+timed\s+out)\b',
         QUEUE_FAILURE, 'message'),
        (r'Illuminate\\Queue\\MaxAttemptsExceededException', QUEUE_FAILURE, 'exception'),
        (r'\bqueue\s+worker\b', QUEUE_FAILURE, 'message'),

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

        # ── Specific exception types ──
        (r'\b(ParseError|FatalError|TypeError|ErrorException|RuntimeException|ViewException|ArgumentCountError|BadMethodCallException|InvalidArgumentException)\b',
         EXCEPTION_EVENT, 'exception'),
        (r'\b(CommandNotFoundException|MethodNotFoundException)\b',
         EXCEPTION_EVENT, 'exception'),
        (r'Mockery.*does not exist on this mock', EXCEPTION_EVENT, 'message'),
        (r'\b(Call\s+to\s+undefined\s+method)\b', EXCEPTION_EVENT, 'message'),
        (r'\b(Undefined\s+array\s+key)\b', EXCEPTION_EVENT, 'message'),
        (r'\b(Class\s+"[^"]*"\s+not\s+found)\b', EXCEPTION_EVENT, 'message'),
        (r'\b(require\(.*\):\s+Failed\s+to\s+open\s+stream)\b', EXCEPTION_EVENT, 'message'),
        (r'\b(SCORM\s+validation\s+error|Invalid\s+ZIP\s+structure|Invalid\s+XML\s+in\s+manifest)\b',
         EXCEPTION_EVENT, 'message'),
        (r'\b(Could\s+not\s+find\s+zip\s+member)\b', EXCEPTION_EVENT, 'message'),
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
        exception = block.get("exception", "") or ""
        raw = block.get("raw_block", message)
        evidence = block.get("evidence", {})
        context = (message + " " + exception)

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
