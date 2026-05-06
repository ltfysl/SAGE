import json,time,torch,sys;sys.path.insert(0,"src");from pathlib import Path
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from sage.training.device import resolve_device,describe_device
from sage.eval.run_benchmark import _load_benchmark
from sage.engine.executor import Executor
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.config import EngineConfig
from sage.extraction.sentence_splitter import split_sentences
from sage.compiler.op_dsl import parse_op_dsl
from sage.eval.metrics import compute_all_metrics

dev=resolve_device("auto")
print(f"Device: {describe_device(dev)}")
tok=AutoTokenizer.from_pretrained("models/neural-sentence-compiler-dsl")
model=AutoModelForSeq2SeqLM.from_pretrained("models/neural-sentence-compiler-dsl").to(dev)
model.eval()

engine_cfg=EngineConfig();verifier=Verifier(engine_cfg);executor=Executor(engine_cfg);renderer=Renderer()

for name in ["easy","medium","hard","long","adversarial","ood_numbers","ood_phrasing","ood_mixed","ood_names"]:
    path=Path(f"data/benchmarks/{name}.jsonl")
    if not path.exists():continue
    samples=_load_benchmark(path)[:50]
    t0=time.perf_counter()
    all_sents=[];s2s=[]
    for si,s in enumerate(samples):
        sents=split_sentences(s["story"])[:200]
        for sent in sents:
            all_sents.append(f"compile_sentence: {sent}");s2s.append(si)
    print(f"{name}: {len(samples)} stories, {len(all_sents)} sents",end=" ",flush=True)

    all_raw=[]
    for bs in range(0,len(all_sents),32):
        batch=all_sents[bs:bs+32]
        inp=tok(batch,return_tensors="pt",max_length=256,truncation=True,padding=True).to(dev)
        with torch.no_grad():out=model.generate(**inp,max_new_tokens=128,num_beams=1,do_sample=False)
        for o in out:all_raw.append(tok.decode(o,skip_special_tokens=True).strip())

    story_ops={si:[]for si in range(len(samples))}
    for si,raw in enumerate(all_raw):
        story_ops[s2s[si]].extend(parse_op_dsl(raw,samples[s2s[si]]["story"]))

    results=[]
    for si,s in enumerate(samples):
        ops=story_ops[si]
        for op in ops:
            if op.get("op")=="TRANSFER":
                if"from"in op:op["from_target"]=op.pop("from")
                if"to"in op:op["to_target"]=op.pop("to")
        comp_json=json.dumps(ops)
        ops_obj,vr=verifier.verify(comp_json,story_text=s["story"])
        er=executor.execute(ops_obj)if ops_obj else None
        pred=renderer.render_raw(er)if er and er.valid else""
        match=str(pred).strip()==str(s["answer"]).strip()
        results.append({"id":s.get("id",""),"system":"neural","ground_truth_answer":str(s["answer"]),"predicted_answer":pred,"answer_match":match,"execution_success":er.valid if er else False,"valid_json":vr.valid_json,"valid_ops":vr.valid_ops,"evidence_valid":vr.execution_success,"num_events":s.get("metadata",{}).get("num_events",0),"latency_ms":0,"ground_truth_ops":s.get("ops",[]),"compiled_ops_raw":ops,"missing_ops":[],"extra_ops":[],"failure_reason":""if match else"answer_mismatch"})

    m=compute_all_metrics(results)
    acc=m["neural"]["accuracy"];elapsed=time.perf_counter()-t0
    print(f"-> {acc*100:.1f}% ({elapsed:.1f}s)",flush=True)

print("DONE")
