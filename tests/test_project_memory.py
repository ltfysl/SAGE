import sys;sys.path.insert(0,"src");from sage.domains.project_memory.domain import MemoryDomain;from sage.domains.project_memory.memory_engine import MemoryState
d=MemoryDomain()
def test_compile_parses_meeting():
    ops=d.compile("data/samples/project_memory/meetings")
    assert len(ops)>=5
    decisions=[o for o in ops if o.op=="DECISION"]
    assert len(decisions)==2
    assert decisions[0].payload["decision"]=="Use Postgres for event store"
def test_blockers_detected():
    ops=d.compile("data/samples/project_memory/meetings")
    blockers=[o for o in ops if o.op=="BLOCKER"]
    assert len(blockers)>=1
    assert blockers[0].payload["blocker"]=="Staging environment is down"
def test_risks_detected():
    ops=d.compile("data/samples/project_memory/meetings")
    risks=[o for o in ops if o.op=="RISK"]
    assert len(risks)>=1
def test_tasks_parsed():
    ops=d.compile("data/samples/project_memory/meetings")
    tasks=[o for o in ops if o.op in("TASK_CREATED","TASK_COMPLETED")]
    assert len(tasks)==3
def test_build_state():
    ops=d.compile("data/samples/project_memory/meetings")
    state=d.build_state(ops)
    assert len(state.operations)>=5
def test_render_markdown():
    ops=d.compile("data/samples/project_memory/meetings")
    state=d.build_state(ops)
    md=d.render(state,fmt="markdown")
    assert "Project Memory" in md
    assert "Staging" in md
