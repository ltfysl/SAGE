import sys;sys.path.insert(0,"src");from sage.domains.specsync.domain import SpecSyncDomain;from sage.domains.specsync.coverage_engine import CoverageState
d=SpecSyncDomain()
def test_compile_parses_prd():
    ops=d.compile("data/samples/specsync/invoicing_app")
    assert len(ops)>=10
    reqs=[o for o in ops if o.op=="DEFINE_REQUIREMENT"]
    assert len(reqs)>=2
    assert reqs[0].payload["id"]=="REQ-001"
def test_tasks_parsed():
    ops=d.compile("data/samples/specsync/invoicing_app")
    tasks=[o for o in ops if o.op=="DEFINE_TASK"]
    assert len(tasks)>=5
    done=[t for t in tasks if t.payload.get("status")=="STATUS_IMPLEMENTED"]
    assert len(done)==2
    pending=[t for t in tasks if t.payload.get("status")=="STATUS_MISSING"]
    assert len(pending)>=3
def test_coverage_summary():
    ops=d.compile("data/samples/specsync/invoicing_app")
    cov=CoverageState()
    for op in ops:cov.apply(op)
    s=cov.summary()
    assert s["requirements"]>=2
    assert s["tasks_total"]>=5
    assert s["tasks_done"]>=1
    assert s["tasks_pending"]>=3
def test_build_state():
    ops=d.compile("data/samples/specsync/invoicing_app")
    state=d.build_state(ops)
    assert state is not None
    assert hasattr(state,"operations")
    assert len(state.operations)>=10
def test_render_markdown():
    ops=d.compile("data/samples/specsync/invoicing_app")
    state=d.build_state(ops)
    md=d.render(state,fmt="markdown")
    assert "SpecSync" in md
    assert "REQ-001" in md
def test_render_json():
    ops=d.compile("data/samples/specsync/invoicing_app")
    state=d.build_state(ops)
    js=d.render(state,fmt="json")
    import json
    parsed=json.loads(js)
    assert "ops_count" in parsed
    assert parsed["ops_count"]>=10
