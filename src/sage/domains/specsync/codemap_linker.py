"""Link SpecSync requirements to CodeMap files and tests."""
import json,re
def load_codemap(mp):
 if isinstance(mp,str):mp=json.load(open(mp))
 return mp
def _get_payload(op):return op.payload if hasattr(op,"payload")else op.get("payload",{})
def _get_op(op):return op.op if hasattr(op,"op")else op.get("op","")
def _tokenize(t):return[w.lower()for w in re.findall(r"[A-Z][a-z]+|[a-z]+|[0-9]+",t)if len(w)>=2]
def build_coverage_report(ops,cm):
 files=cm.get("files",{})
 reqs=[o for o in ops if _get_op(o)=="DEFINE_REQUIREMENT"]
 acs=[o for o in ops if _get_op(o)=="DEFINE_ACCEPTANCE_CRITERION"]
 tasks=[o for o in ops if _get_op(o)=="DEFINE_TASK"]
 done=sum(1 for t in tasks if _get_payload(t).get("status")=="STATUS_IMPLEMENTED")
 miss=[]
 tfs={f:ops2 for f,ops2 in files.items() if"test"in f.lower()or"spec"in f.lower()}
 for ac in acs:
  p=_get_payload(ac);acid=p.get("id","");desc=p.get("description","")
  kw=_tokenize(acid+chr(32)+desc);found=False
  for fp in tfs:
   if any(k in fp.lower()for k in kw):found=True;break
  if not found:miss.append({"criterion_id":acid,"description":desc[:120]})
 return{"tasks_total":len(tasks),"tasks_done":done,"missing_test_coverage":miss,"recommendations":["Missing tests for "+str(len(miss))+" criteria"]if miss else["All covered"]}
