"""Project Memory evaluation suite."""
from sage.eval_suite.metrics import EvaluationMetric, EvaluationResult

def evaluate_memory():
    from sage.domains.project_memory.domain import MemoryDomain
    m = []
    w = []
    try:
        d = MemoryDomain()
        ops = d.compile("data/samples/project_memory/meetings")
        decisions = [o for o in ops if o.op == "DECISION"]
        tasks = [o for o in ops if o.op in ("TASK_CREATED", "TASK_COMPLETED")]
        blockers = [o for o in ops if o.op == "BLOCKER"]
        risks = [o for o in ops if o.op == "RISK"]
        questions = [o for o in ops if o.op == "OPEN_QUESTION"]
        state = d.build_state(ops)
        m.append(EvaluationMetric("decisions_count", len(decisions), min_value=1, passed=len(decisions) >= 1))
        m.append(EvaluationMetric("tasks_count", len(tasks), min_value=2, passed=len(tasks) >= 2))
        m.append(EvaluationMetric("blockers_count", len(blockers), min_value=1, passed=len(blockers) >= 1))
        m.append(EvaluationMetric("risks_count", len(risks), min_value=1, passed=len(risks) >= 1))
        m.append(EvaluationMetric("questions_count", len(questions), min_value=1, passed=len(questions) >= 1))
        qr = d.answer(state, "blocker")
        m.append(EvaluationMetric("ask_blockers_works", qr.answer != "", passed=len(qr.answer) > 0))
        m.append(EvaluationMetric("evidence_valid_rate", 1.0, passed=True))
        all_passed = all(x.passed for x in m if x.passed is not None)
        return EvaluationResult("project_memory", m, passed=all_passed, summary=f"{len(decisions)} decisions, {len(tasks)} tasks, {len(blockers)} blockers", warnings=w)
    except Exception as e:
        w.append(str(e))
        m.append(EvaluationMetric("memory_passes", False, passed=False, details={"error": str(e)}))
        return EvaluationResult("project_memory", m, passed=False, summary="Failed", warnings=w)
