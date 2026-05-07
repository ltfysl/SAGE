"""Project Memory ask."""
from sage.domains.project_memory.memory_engine import MemoryState

class MemoryAsk:
    def __init__(self, state):
        ops = state.operations if hasattr(state,"operations") else []
        self.ms = MemoryState()
        for op in ops: self.ms.apply(op)
        self.summary = self.ms.summary()

    def ask(self, question):
        q = question.lower()
        if "blocker" in q:
            if self.ms.blockers:
                items = chr(10).join("- "+b.get("blocker","")[:100] for b in self.ms.blockers)
                return {"text": str(len(self.ms.blockers))+" blockers found."+chr(10)+items, "evidence": self.ms.blockers[:5]}
            return {"text": "No blockers."}
        if "risk" in q:
            if self.ms.risks:
                items = chr(10).join("- "+r.get("risk","")[:100] for r in self.ms.risks)
                return {"text": str(len(self.ms.risks))+" risks found."+chr(10)+items, "evidence": self.ms.risks[:5]}
            return {"text": "No risks."}
        if "decision" in q:
            return {"text": str(self.summary.get("decisions",0))+" decisions recorded.", "evidence": self.ms.decisions[:5]}
        if "task" in q or "progress" in q:
            return {"text": str(self.summary.get("tasks_done",0))+"/"+str(self.summary.get("tasks_total",0))+" tasks done."}
        if "question" in q:
            if self.ms.questions:
                items = chr(10).join("- "+x.get("question","")[:100] for x in self.ms.questions)
                return {"text": str(len(self.ms.questions))+" open questions."+chr(10)+items, "evidence": self.ms.questions[:5]}
            return {"text": "No open questions."}
        if "follow" in q or "next" in q:
            if self.ms.follow_ups:
                items = chr(10).join("- "+f.get("follow_up","")[:100] for f in self.ms.follow_ups)
                return {"text": str(len(self.ms.follow_ups))+" follow-ups."+chr(10)+items, "evidence": self.ms.follow_ups[:5]}
            return {"text": "No follow-ups."}
        if "status" in q or "summary" in q:
            s = self.summary
            return {"text": "Decisions: "+str(s["decisions"])+", Tasks: "+str(s["tasks_done"])+"/"+str(s["tasks_total"])+", Blockers: "+str(s["blockers"])+", Risks: "+str(s["risks"])}
        return {"text": "Project Memory summary: "+str(self.summary.get("decisions",0))+" decisions, "+str(self.summary.get("tasks_done",0))+"/"+str(self.summary.get("tasks_total",0))+" tasks."}
