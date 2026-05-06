"""Incident state engine for SAGE Incident Lens.

Builds an incident state from event operations and supports queries.
"""

from __future__ import annotations
from collections import defaultdict
from .log_ops import SEVERITY


class IncidentState:
    """Tracks incident state from compiled log operations."""

    def __init__(self):
        self.first_error_at = None
        self.last_error_at = None
        self.error_count_by_type = defaultdict(int)
        self.exceptions = []
        self.affected_components = set()
        self.failed_jobs = []
        self.mail_failures = []
        self.database_errors = []
        self.queue_failures = []
        self.top_exception = ""
        self.timeline = []

    def apply(self, op: dict):
        """Apply an operation to the incident state."""
        ts = op.get("timestamp", "")
        op_type = op.get("op", "")
        exc = op.get("exception", "")
        msg = op.get("message", "")
        component = op.get("component", "")

        self.error_count_by_type[op_type] += 1
        self.timeline.append({"timestamp": ts, "op": op_type, "message": msg[:100]})

        if component:
            self.affected_components.add(component)

        if ts:
            if self.first_error_at is None or ts < self.first_error_at:
                self.first_error_at = ts
            if self.last_error_at is None or ts > self.last_error_at:
                self.last_error_at = ts

        if exc:
            self.exceptions.append(exc)

        if op_type == "FAILED_JOB":
            self.failed_jobs.append({"timestamp": ts, "message": msg[:100]})
        elif op_type == "MAIL_FAILURE":
            self.mail_failures.append({"timestamp": ts, "message": msg[:100]})
        elif op_type == "DATABASE_ERROR":
            self.database_errors.append({"timestamp": ts, "message": msg[:100]})
        elif op_type == "QUEUE_FAILURE":
            self.queue_failures.append({"timestamp": ts, "message": msg[:100]})

    def finalize(self):
        """Compute derived state after all operations are applied."""
        if self.exceptions:
            from collections import Counter
            self.top_exception = Counter(self.exceptions).most_common(1)[0][0]

    def to_dict(self) -> dict:
        return {
            "first_error_at": self.first_error_at,
            "last_error_at": self.last_error_at,
            "error_count_by_type": dict(self.error_count_by_type),
            "total_errors": sum(self.error_count_by_type.values()),
            "top_exception": self.top_exception,
            "affected_components": list(self.affected_components),
            "failed_jobs": self.failed_jobs,
            "mail_failures": self.mail_failures,
            "database_errors": self.database_errors,
            "queue_failures": self.queue_failures,
            "timeline": self.timeline[-20:],  # Last 20 events
        }

    def answer(self, question: str) -> str:
        """Answer a fixed-scope natural language question."""
        q = question.lower().strip()
        if "first error" in q or "when_first_error" in q:
            return f"First error at: {self.first_error_at or 'N/A'}"
        if "top exception" in q or "most common" in q:
            return f"Top exception: {self.top_exception or 'N/A'}"
        if "affected component" in q or "which component" in q:
            comps = ", ".join(self.affected_components) or "none"
            return f"Affected components: {comps}"
        if "mail" in q:
            count = len(self.mail_failures)
            first = self.mail_failures[0]['timestamp'] if self.mail_failures else 'N/A'
            return f"Mail failures: {count} (first: {first})"
        if "queue" in q:
            count = len(self.queue_failures)
            first = self.queue_failures[0]['timestamp'] if self.queue_failures else 'N/A'
            return f"Queue failures: {count} (first: {first})"
        if "database" in q or "db" in q:
            count = len(self.database_errors)
            first = self.database_errors[0]['timestamp'] if self.database_errors else 'N/A'
            return f"Database errors: {count} (first: {first})"
        if "timeline" in q:
            events = "\n".join(f"  {e['timestamp']} {e['op']}: {e['message']}" for e in self.timeline[-10:])
            return f"Recent timeline:\n{events}" if events else "No events."
        if "impact" in q:
            return self._build_impact_answer()
        if "checklist" in q:
            return self._build_checklist_answer()
        return f"Incident summary: {self.total_errors} errors, top: {self.top_exception}"

    def _build_impact_answer(self) -> str:
        """Build a concise impact assessment."""
        lines = ["**Likely Impact:**"]
        cats = dict(self.error_count_by_type)
        if cats.get('DATABASE_ERROR'):
            lines.append(f"  - Database: {cats['DATABASE_ERROR']} errors - check DB connectivity")
        if cats.get('MAIL_FAILURE'):
            lines.append(f"  - Mail: {cats['MAIL_FAILURE']} failures - verify SMTP")
        if cats.get('QUEUE_FAILURE') or cats.get('FAILED_JOB'):
            lines.append(f"  - Queue: {cats.get('QUEUE_FAILURE', 0) + cats.get('FAILED_JOB', 0)} failures - check workers")
        if cats.get('AUTH_ERROR') or cats.get('HTTP_ERROR'):
            lines.append(f"  - Access: {cats.get('AUTH_ERROR', 0) + cats.get('HTTP_ERROR', 0)} errors - check auth")
        if self.top_exception:
            lines.append(f"  - Top exception: {self.top_exception}")
        if self.first_error_at and self.last_error_at:
            lines.append(f"  - Window: {self.first_error_at} to {self.last_error_at}")
        return "\n".join(lines)

    def _build_checklist_answer(self) -> str:
        """Build a suggested investigation checklist."""
        items = ["**Suggested Investigation Checklist:**"]
        cats = dict(self.error_count_by_type)
        if cats.get('DATABASE_ERROR'):
            items.append("  [ ] Verify database connectivity and credentials")
            items.append("  [ ] Inspect failed queries at first error timestamp")
        if cats.get('MAIL_FAILURE'):
            items.append("  [ ] Verify SMTP host, port, and connectivity")
            items.append("  [ ] Check mail service credentials")
        if cats.get('QUEUE_FAILURE') or cats.get('FAILED_JOB'):
            items.append("  [ ] Check queue worker processes")
            items.append("  [ ] Inspect failed_jobs table")
        if cats.get('AUTH_ERROR') or cats.get('HTTP_ERROR'):
            items.append("  [ ] Check web server and application access logs")
        if not cats.get('RECOVERY_EVENT'):
            items.append("  [ ] No recovery detected - manual intervention may be required")
        items.append("  [ ] Review full timeline for correlations")
        return "\n".join(items)
