import sys;sys.path.insert(0,"src");from sage.eval_suite.metrics import EvaluationMetric, EvaluationResult;from sage.eval_suite.runner import run_suite;from sage.eval_suite.renderer import render_results
import json

def test_metric_serialize():
    m=EvaluationMetric("test_metric",42,max_value=100,passed=True,details={"x":1})
    d=m.to_dict()
    assert d["name"]=="test_metric"
    assert d["value"]==42
    assert d["passed"]==True

def test_result_serialize():
    m=EvaluationMetric("t",5,passed=True)
    r=EvaluationResult("test",[m],passed=True,summary="all good")
    d=r.to_dict()
    assert d["suite"]=="test"
    assert d["passed"]==True

def test_codemap_eval_runs():
    r=run_suite("codemap")
    assert r.suite=="codemap"
    assert len(r.metrics)>0

def test_specsync_eval_runs():
    r=run_suite("specsync")
    assert r.suite=="specsync"
    assert len(r.metrics)>0

def test_memory_eval_runs():
    r=run_suite("project_memory")
    assert r.suite=="project_memory"
    assert len(r.metrics)>0

def test_all_eval_runs():
    r=run_suite("all")
    assert len(r)==3
    assert r[0].suite=="codemap"

def test_render_markdown():
    r=run_suite("specsync")
    md=render_results(r,"markdown")
    assert "SpecSync" in md or "specsync" in md

def test_render_json():
    r=run_suite("specsync")
    js=render_results(r,"json")
    parsed=json.loads(js)
    assert isinstance(parsed,list)
    assert parsed[0]["suite"]=="specsync"
