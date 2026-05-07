"""Incident state engine for SAGE Incident Lens."""
from __future__ import annotations
from collections import defaultdict

class IncidentState:
    def __init__(self):
        self.first_error_at = None
        self.last_error_at = None
        self.error_count_by_type = defaultdict(int)
        self.exceptions = []
        self.total_errors = 0
        self.affected_components = set()
        self.top_exception = ""
        self.timeline = []

    def apply(self, op: dict):
        ts = op.get("timestamp", "")
        op_type = op.get("op", "")
        exc = op.get("exception", "")
        msg = op.get("message", "")
        comp = op.get("component", "")
        self.error_count_by_type[op_type] += 1
        self.total_errors += 1
        self.timeline.append({"timestamp": ts, "op": op_type, "message": msg[:120]})
        if comp:
            self.affected_components.add(comp)
        if ts:
            if not self.first_error_at or ts < self.first_error_at:
                self.first_error_at = ts
            if not self.last_error_at or ts > self.last_error_at:
                self.last_error_at = ts
        if exc:
            self.exceptions.append(exc)

    def finalize(self):
        if self.exceptions:
            from collections import Counter
            self.top_exception = Counter(self.exceptions).most_common(1)[0][0]

    def to_dict(self) -> dict:
        return {
            "first_error_at": self.first_error_at,
            "last_error_at": self.last_error_at,
            "error_count_by_type": dict(self.error_count_by_type),
            "total_errors": self.total_errors,
            "top_exception": self.top_exception,
            "affected_components": list(self.affected_components),
            "timeline": self.timeline[-30:],
        }

    def answer(self, question: str) -> str:
        q = question.lower().strip()
        if "first error" in q:
            return f"First error at: {self.first_error_at or 'N/A'}"
        if "top exception" in q:
            return f"Top exception: {self.top_exception or 'N/A'}"
        if "affected component" in q:
            return f"Components: {', '.join(self.affected_components) or 'none'}"
        if "mail" in q:
            cnt = self.error_count_by_type.get("MAIL_FAILURE", 0)
            return f"Mail failures: {cnt}"
        if "queue" in q:
            cnt = self.error_count_by_type.get("QUEUE_FAILURE", 0) + self.error_count_by_type.get("FAILED_JOB", 0)
            return f"Queue failures: {cnt}"
        if "database" in q or "db" in q:
            return f"Database errors: {self.error_count_by_type.get('DATABASE_ERROR', 0)}"
        if "timeline" in q:
            evts = "\n".join(f"  {e['timestamp']} {e['op']}: {e['message']}" for e in self.timeline[-10:])
            return f"Recent timeline:\n{evts}" if evts else "No events."
        return f"Incident: {self.total_errors} errors, top: {self.top_exception}"
