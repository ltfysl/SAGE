import sys,argparse,torch
sys.path.insert(0,"src")
from sage.training.device import resolve_device,describe_device
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
p=argparse.ArgumentParser()
p.add_argument("--device",default="auto")
p.add_argument("--model",default="google/flan-t5-small")
a=p.parse_args()
dev=resolve_device(a.device)
print(f"Device: {describe_device(dev)}")
print(f"Loading {a.model}...")
tok=AutoTokenizer.from_pretrained(a.model)
model=AutoModelForSeq2SeqLM.from_pretrained(a.model).to(dev)
model.eval()
text="compile_sentence: Latif gains three coins."
print(f"Input: {text}")
inputs=tok(text,return_tensors="pt",max_length=64,truncation=True)
inputs={k:v.to(dev)for k,v in inputs.items()}
with torch.no_grad():
    out=model(**inputs,labels=inputs["input_ids"])
    gen=model.generate(**inputs,max_new_tokens=64)
    r=tok.decode(gen[0],skip_special_tokens=True)
print(f"Forward loss: {out.loss.item():.4f}")
print(f"Generated: {r}")
print("OK")
