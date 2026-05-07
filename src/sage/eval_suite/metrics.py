"""Evaluation metrics for SAGE eval suite."""
import json

class EvaluationMetric:
    def __init__(self, name, value, max_value=None, passed=None, details=None):
        self.name = name
        self.value = value
        self.max_value = max_value
        self.passed = passed
        self.details = details or {}

    def to_dict(self):
        d = {"name": self.name, "value": self.value}
        if self.max_value is not None: d["max_value"] = self.max_value
        if self.passed is not None: d["passed"] = self.passed
        if self.details: d["details"] = self.details
        return d


class EvaluationResult:
    def __init__(self, suite, metrics=None, passed=None, summary="", warnings=None, metadata=None):
        self.suite = suite
        self.metrics = metrics or []
        self.passed = passed if passed is not None else all(m.passed for m in self.metrics if m.passed is not None)
        self.summary = summary
        self.warnings = warnings or []
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "suite": self.suite,
            "metrics": [m.to_dict() for m in self.metrics],
            "passed": self.passed,
            "summary": self.summary,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, default=str)
