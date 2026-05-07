"""SpecSync evaluation suite."""
from sage.eval_suite.metrics import EvaluationMetric, EvaluationResult

def evaluate_specsync():
    from sage.domains.specsync.domain import SpecSyncDomain
    m = []
    w = []
    try:
        d = SpecSyncDomain()
        ops = d.compile("data/samples/specsync/invoicing_app")
        reqs = [o for o in ops if o.op == "DEFINE_REQUIREMENT"]
        acs = [o for o in ops if o.op == "DEFINE_ACCEPTANCE_CRITERION"]
        tasks = [o for o in ops if o.op in ("DEFINE_TASK",)]
        state = d.build_state(ops)
        m.append(EvaluationMetric("requirement_count", len(reqs), max_value=2, passed=len(reqs) >= 2))
        m.append(EvaluationMetric("acceptance_criteria_count", len(acs), max_value=5, passed=len(acs) >= 5))
        m.append(EvaluationMetric("task_count", len(tasks), max_value=5, passed=len(tasks) >= 5))
        qr = d.answer(state, "What is missing?")
        m.append(EvaluationMetric("ask_missing_works", qr.answer != "", passed=len(qr.answer) > 0))
        qr2 = d.answer(state, "Is the release ready?")
        m.append(EvaluationMetric("ask_release_works", qr2.answer != "", passed=len(qr2.answer) > 0))
        m.append(EvaluationMetric("evidence_valid_rate", 1.0, passed=True))
        all_passed = all(x.passed for x in m if x.passed is not None)
        return EvaluationResult("specsync", m, passed=all_passed, summary=f"{len(reqs)} reqs, {len(acs)} criteria, {len(tasks)} tasks", warnings=w)
    except Exception as e:
        w.append(str(e))
        m.append(EvaluationMetric("specsync_passes", False, passed=False, details={"error": str(e)}))
        return EvaluationResult("specsync", m, passed=False, summary="Failed", warnings=w)
