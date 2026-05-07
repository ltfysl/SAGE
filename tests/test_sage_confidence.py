import sys;sys.path.insert(0,"src");from sage.core.confidence import score_evidence,confidence_summary,VERIFIED,STRONG,INFERRED,WEAK,UNCERTAIN;from sage.core.evidence import Evidence;from sage.core.operation import Operation
def test_no_evidence_is_uncertain():
    op=Operation(op="TEST")
    label,score,reasons=score_evidence(op)
    assert label==UNCERTAIN
    assert score==0.0
def test_full_evidence_is_strong():
    ev=Evidence(span="hello",file="x.py",line=5,start_offset=0,end_offset=5,parser="test_parser",confidence=1.0)
    op=Operation(op="TEST",evidence=ev)
    label,score,reasons=score_evidence(op)
    assert label in(VERIFIED,STRONG)
    assert score>=0.90
def test_partial_evidence_is_inferred():
    ev=Evidence(span="hello",file="x.py",confidence=1.0)
    op=Operation(op="TEST",evidence=ev)
    label,score,reasons=score_evidence(op)
    assert label in(STRONG,INFERRED)
def test_confidence_summary():
    ops=[]
    ops.append(Operation(op="A",evidence=Evidence(span="x",file="f.py",line=1,start_offset=0,end_offset=1,parser="p",confidence=1.0)))
    ops.append(Operation(op="B"))
    ops.append(Operation(op="C",evidence=Evidence(span="y",file="g.py",confidence=1.0)))
    s=confidence_summary(ops)
    assert s["total"]==3
    assert sum(s["distribution"].values())==3
    assert s["strong_rate"]>=0.0
