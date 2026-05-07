"""SpecSync coverage engine — tracks requirement implementation status."""
from collections import defaultdict

class CoverageState:
    def __init__(self):
        self.requirements = []
        self.acceptance_criteria = []
        self.tasks = []
        self.decisions = []
        self.missing = []
        self._req_map = {}

    def apply(self, op):
        p = op.payload if hasattr(op, "payload") else (op.get("payload",{}) if isinstance(op, dict) else {})
        ot = op.op if hasattr(op, "op") else op.get("op","")
        if ot == "DEFINE_REQUIREMENT":
            self.requirements.append(p)
            rid = p.get("id","")
            if rid:
                self._req_map[rid] = p
        elif ot == "DEFINE_ACCEPTANCE_CRITERION":
            self.acceptance_criteria.append(p)
        elif ot == "DEFINE_TASK":
            self.tasks.append(p)
        elif ot == "DEFINE_DECISION":
            self.decisions.append(p)
        elif ot in ("STATUS_MISSING","TEST_COVERAGE_MISSING"):
            self.missing.append(p)

    def summary(self):
        tasks = self.tasks
        done = sum(1 for t in tasks if t.get("status")=="STATUS_IMPLEMENTED")
        total = len(tasks)
        return {"requirements":len(self.requirements),"acceptance_criteria":len(self.acceptance_criteria),"tasks_total":total,"tasks_done":done,"tasks_pending":total-done,"decisions":len(self.decisions),"missing_items":len(self.missing)}

    def to_dict(self):
        return {"requirements":self.requirements,"acceptance_criteria":self.acceptance_criteria,"tasks":self.tasks,"decisions":self.decisions,"missing":self.missing}
