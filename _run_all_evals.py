"""Run full comparison: oracle, rule, sklearn, direct on all benchmarks (in-domain + OOD)."""
import json, time, sys
sys.path.insert(0, "src")
from pathlib import Path
from sage.eval.run_benchmark import run_oracle, run_rule_only, _load_benchmark, _save_failures, _compute_diff
from sage.eval.compare import run_direct_eval
from sage.baselines.sklearn_compiler import load_sklearn_compiler
from sage.baselines.sklearn_direct import SklearnDirectModel
from sage.engine.executor import Executor
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.config import EngineConfig
from sage.eval.metrics import compute_all_metrics, accuracy_by_event_buckets

sc = load_sklearn_compiler(Path("models/sklearn-op-classifier.joblib"))
sd = SklearnDirectModel(); sd.load(Path("models/sklearn-direct.joblib"))
engine_cfg = EngineConfig()
verifier = Verifier(engine_cfg); executor = Executor(engine_cfg); renderer = Renderer()

benchmarks = ["easy","medium","hard","long","adversarial","ood_names","ood_phrasing","ood_numbers","ood_mixed"]

results = {}
for name in benchmarks:
    path = Path(f"data/benchmarks/{name}.jsonl")
    if not path.exists():
        continue
    n = 50 if name in ("long","hard","ood_mixed","ood_phrasing") else 100
    print(f"\n=== {name} ({n} samples) ===", flush=True)
    
    o = run_oracle(path, max_samples=n)
    r = run_rule_only(path, max_samples=n)
    d = run_direct_eval(path, max_samples=n)
    
    # Sklearn compiler
    samples = _load_benchmark(path)[:n]
    sc_results = []
    for s in samples:
        t0=time.perf_counter()
        comp_raw,ok=sc.compile(s['story'])
        comp_json=json.dumps(comp_raw)
        ops,vr=verifier.verify(comp_json,story_text=s['story'])
        er=executor.execute(ops) if ops else None
        pred=renderer.render_raw(er) if er and er.valid else ''
        match=str(pred).strip()==str(s['answer']).strip()
        miss,extra=_compute_diff(s.get('ops',[]),comp_raw)
        sc_results.append({
            'id':s.get('id',''),'system':'sklearn_compiler',
            'ground_truth_answer':str(s['answer']),'predicted_answer':pred,'answer_match':match,
            'compiled_output':comp_json,'execution_success':er.valid if er else False,
            'valid_json':vr.valid_json,'valid_ops':vr.valid_ops,'evidence_valid':vr.execution_success,
            'num_events':s.get('metadata',{}).get('num_events',0),
            'noise_level':s.get('metadata',{}).get('noise_level',0.0),
            'latency_ms':(time.perf_counter()-t0)*1000,
            'ground_truth_ops':s.get('ops',[]),'compiled_ops_raw':comp_raw,
            'missing_ops':miss,'extra_ops':extra,
            'failure_reason':'' if match else 'answer_mismatch',
        })
    sc_m = compute_all_metrics(sc_results)
    
    # Sklearn direct
    sd_results=[]
    for s in samples:
        pred=sd.answer(s['story'])
        match=str(pred).strip()==str(s['answer']).strip()
        sd_results.append({
            'id':s.get('id',''),'system':'sklearn_direct',
            'ground_truth_answer':str(s['answer']),'predicted_answer':pred,'answer_match':match,
            'compiled_output':'','execution_success':False,'valid_json':False,'valid_ops':False,'evidence_valid':False,
            'num_events':s.get('metadata',{}).get('num_events',0),
            'noise_level':s.get('metadata',{}).get('noise_level',0.0),'latency_ms':0.0,
            'ground_truth_ops':[],'compiled_ops_raw':[],'missing_ops':[],'extra_ops':[],
            'failure_reason':'' if match else 'wrong_answer',
        })
    sd_m = compute_all_metrics(sd_results)
    
    o_acc = o["metrics"]["oracle"]["accuracy"]
    r_acc = r["metrics"]["rule_compiler"]["accuracy"]
    sc_acc = sc_m["sklearn_compiler"]["accuracy"]
    sd_acc = sd_m["sklearn_direct"]["accuracy"]
    d_acc = d["metrics"]["direct_heuristic"]["accuracy"]
    
    results[name] = {"oracle":o_acc,"rule":r_acc,"sklearn":sc_acc,"sklearn_direct":sd_acc,"heuristic":d_acc}
    print(f"  oracle={o_acc*100:.0f}% rule={r_acc*100:.0f}% sklearn={sc_acc*100:.0f}% skdirect={sd_acc*100:.0f}% heuristic={d_acc*100:.0f}%", flush=True)

# Print summary table
print("\n=== FINAL COMPARISON ===")
print(f"{'Benchmark':<16} {'Events':>6} {'Oracle':>7} {'Rule':>7} {'Sklearn':>8} {'SkDirect':>8} {'Heuristic':>9}")
print("-" * 65)
for name in benchmarks:
    if name not in results:
        continue
    r = results[name]
    p = Path(f"data/benchmarks/{name}.jsonl")
    s = _load_benchmark(p)[:1]
    ev = s[0].get("metadata",{}).get("num_events","?") if s else "?"
    print(f"{name:<16} {str(ev):>6} {r['oracle']*100:>6.0f}% {r['rule']*100:>6.0f}% {r['sklearn']*100:>7.0f}% {r['sklearn_direct']*100:>7.0f}% {r['heuristic']*100:>8.0f}%")

# Save JSON
with open("data/reports/full_comparison.json","w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to data/reports/full_comparison.json")
