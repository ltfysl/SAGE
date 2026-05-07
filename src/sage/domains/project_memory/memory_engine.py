"""Project Memory state engine — tracks decisions, tasks, blockers, owners."""
from collections import defaultdict

class MemoryState:
    def __init__(self):
        self.decisions = []
        self.tasks = []
        self.blockers = []
        self.owners = []
        self.questions = []
        self.deadlines = []
        self.risks = []
        self.follow_ups = []
        self.notes = []
        self.status_changes = []

    def apply(self, op):
        p = op.payload if hasattr(op,"payload") else op.get("payload",{})
        ot = op.op if hasattr(op,"op") else op.get("op","")
        if ot == "DECISION": self.decisions.append(p)
        elif ot in ("TASK_CREATED","TASK_COMPLETED"): self.tasks.append(p)
        elif ot == "BLOCKER": self.blockers.append(p)
        elif ot == "OWNER_ASSIGNED": self.owners.append(p)
        elif ot == "OPEN_QUESTION": self.questions.append(p)
        elif ot == "DEADLINE": self.deadlines.append(p)
        elif ot == "RISK": self.risks.append(p)
        elif ot == "FOLLOW_UP": self.follow_ups.append(p)
        elif ot == "NOTE": self.notes.append(p)
        elif ot == "STATUS_CHANGE": self.status_changes.append(p)

    def summary(self):
        tasks_done = sum(1 for t in self.tasks if t.get("status")=="TASK_COMPLETED" or t.get("description","").startswith("[x]"))
        return {"decisions":len(self.decisions),"tasks_total":len(self.tasks),"tasks_done":tasks_done,"blockers":len(self.blockers),"open_questions":len(self.questions),"risks":len(self.risks)}

    def to_dict(self):
        return {"decisions":self.decisions,"tasks":self.tasks,"blockers":self.blockers,"owners":self.owners,"questions":self.questions,"deadlines":self.deadlines,"risks":self.risks,"follow_ups":self.follow_ups,"notes":self.notes,"status_changes":self.status_changes}
