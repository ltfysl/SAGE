"""SpecSync ask — deterministic question answering."""
from sage.domains.specsync.coverage_engine import CoverageState

class SpecSyncAsk:
    def __init__(self, state):
        ops = state.operations if hasattr(state, "operations") else []
        self.cov = CoverageState()
        for op in ops:
            self.cov.apply(op)
        self.summary = self.cov.summary()

    def ask(self, question):
        q = question.lower()
        if "missing" in q or "incomplete" in q:
            items = self.cov.missing
            text = str(len(items))+" missing items found." if items else "No missing items."
            return {"text":text,"evidence":items[:10]}
        if "task" in q or "progress" in q:
            s = self.summary
            text = str(s.get("tasks_done",0))+"/"+str(s.get("tasks_total",0))+" tasks done."
            return {"text":text,"evidence":self.cov.tasks[:10]}
        if "requirement" in q or "req" in q:
            return {"text":str(self.summary.get("requirements",0))+" requirements defined.","evidence":self.cov.requirements[:10]}
        if "release" in q or "ready" in q:
            s = self.summary
            total = s.get("tasks_total",0)
            done = s.get("tasks_done",0)
            if total == 0:
                return {"text":"No tasks defined yet."}
            if done == total and len(self.cov.missing)==0:
                return {"text":"Ready for release — all "+str(total)+" tasks done, no missing items."}
            return {"text":"Not ready — "+str(done)+"/"+str(total)+" tasks done, "+str(len(self.cov.missing))+" items missing."}
        return {"text":"SpecSync summary: "+str(self.summary.get("requirements",0))+" reqs, "+str(self.summary.get("tasks_done",0))+"/"+str(self.summary.get("tasks_total",0))+" tasks."}
