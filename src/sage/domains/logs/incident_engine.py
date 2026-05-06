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
            return f"Mail failures: {count}"
        if "queue" in q:
            count = len(self.queue_failures)
            return f"Queue failures: {count}"
        if "database" in q or "db" in q:
            count = len(self.database_errors)
            return f"Database errors: {count}"
        if "timeline" in q:
            events = "\n".join(f"  {e['timestamp']} {e['op']}: {e['message']}" for e in self.timeline[-10:])
            return f"Recent timeline:\n{events}" if events else "No events."
        return f"Incident summary: {self.total_errors} errors, top: {self.top_exception}"
