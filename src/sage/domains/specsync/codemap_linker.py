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
 return{"tasks_total":len(tasks),"tasks_done":done,"tasks_pending":len(tasks)-done,"requirements":len(reqs),"acceptance_criteria":len(acs),"missing_test_coverage":miss,"recommendations":["Missing tests for "+str(len(miss))+" criteria"]if miss else["All covered"]}
def render_coverage_markdown(r):
 nl=chr(10);lines=["# SpecSync + CodeMap Coverage","","| Metric | Value |","|---|---|"]
 for k in["requirements","acceptance_criteria","tasks_total","tasks_done","tasks_pending"]:
  lines.append("| "+k.replace(chr(95),chr(32)).title()+" | "+str(r.get(k,0))+" |")
 lines.append("")
 miss=r.get("missing_test_coverage",[])
 if miss:lines.append("## Missing ("+str(len(miss))+")");[lines.append("- **"+m.get("criterion_id","?")+"**: "+m.get("description",""))for m in miss]
 else:lines.append("All criteria covered.")
 recs=r.get("recommendations",[])
 if recs:lines.append("");lines.append("## Recommendations");[lines.append("- "+rec)for rec in recs]
 return nl.join(lines)
def build_specsync_cursor_context(ops,cm,task=""):
 nl=chr(10);r=build_coverage_report(ops,cm)
 lines=["# SpecSync Context","","**Task:** "+task,"","## Requirements"]
 reqs=[_get_payload(o)for o in ops if _get_op(o)=="DEFINE_REQUIREMENT"]
 for req in reqs:lines.append("- **"+req.get("id","?")+"**: "+req.get("description","")[:120])
 miss=r.get("missing_test_coverage",[])
 if miss:
  lines.append("");lines.append("## Missing / Incomplete")
  for m in miss:lines.append("- **"+m.get("criterion_id","?")+"**: "+m.get("description",""))
 lines.append("");lines.append("## Limitations");lines.append("- Static analysis only.")
 return nl.join(lines)
