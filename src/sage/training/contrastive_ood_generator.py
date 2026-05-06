"""Contrastive OOD data generator for neural SAGE compiler.

Generates paired positive/negative examples where the model must learn
to distinguish real events from non-event variants with similar wording.
"""

import json,random,re
from pathlib import Path
from sage.generator.names import NAMES,OBJECT_TYPES,get_singular
from sage.compiler.rule_compiler import RuleCompiler

NUMBER_WORDS={1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty"}

CONTRASTIVE_ADD=[("ADD","{person} gains {amount} {obj}.","{person} almost gains {amount} {obj}."),("ADD","{person} gains {amount} {obj}.","{person} wanted to gain {amount} {obj} but did not."),("ADD","{person} obtains {amount} {obj}.","{person} almost obtains {amount} {obj}."),("ADD","{person} obtains {amount} {obj}.","{person} planned to obtain {amount} {obj} but never did."),("ADD","{person} acquires {amount} {obj}.","{person} says they acquired {amount} {obj}."),("ADD","{person} receives {amount} {obj}.","{person} hoped to receive {amount} {obj} but did not."),("ADD","{person} is given {amount} {obj}.","{person} claims to have been given {amount} {obj}."),("ADD","{person} picks up {amount} {obj}.","{person} nearly picked up {amount} {obj}.")]

CONTRASTIVE_SUB=[("SUB","{person} spends {amount} {obj}.","{person} almost spends {amount} {obj}."),("SUB","{person} spends {amount} {obj}.","{person} wanted to spend {amount} {obj} but did not."),("SUB","{person} uses up {amount} {obj}.","{person} almost uses up {amount} {obj}."),("SUB","{person} loses {amount} {obj}.","{person} planned to lose {amount} {obj} but never did."),("SUB","{person} discards {amount} {obj}.","{person} says they discarded {amount} {obj}."),("SUB","{person} gives away {amount} {obj}.","{person} thought about giving away {amount} {obj} but kept them."),("SUB","{person} loses {amount} {obj}.","{person} claims to have lost {amount} {obj}.")]

CONTRASTIVE_TRANSFER=[("TRANSFER","{giver} hands {receiver} {amount} {obj}.","{giver} almost hands {receiver} {amount} {obj}."),("TRANSFER","{giver} hands {amount} {obj} to {receiver}.","{giver} wanted to hand {amount} {obj} to {receiver} but did not."),("TRANSFER","{receiver} takes {amount} {obj} from {giver}.","{receiver} almost took {amount} {obj} from {giver}."),("TRANSFER","{giver} passes {receiver} {amount} {obj}.","{giver} planned to pass {receiver} {amount} {obj} but never did."),("TRANSFER","{giver} gives {receiver} {amount} {obj}.","{giver} says they gave {receiver} {amount} {obj}."),("TRANSFER","{receiver} takes {amount} {obj} from {giver}.","{receiver} claims to have taken {amount} {obj} from {giver}."),("TRANSFER","{giver} hands {receiver} {amount} {obj}.","{giver} would have handed {receiver} {amount} {obj}.")]

CONTRASTIVE_SET=[("SET","{person} starts with {amount} {obj}.","{person} says they started with {amount} {obj}."),("SET","{person} begins with {amount} {obj}.","{person} claims to have begun with {amount} {obj}."),("SET","{person} has {amount} {obj}.","{person} claims to have {amount} {obj}."),("SET","{person} ends up with {amount} {obj}.","{person} would have ended up with {amount} {obj}."),("SET","{person} is left with {amount} {obj}.","{person} says they are left with {amount} {obj}.")]

ALL_CONTRASTIVE={"ADD":CONTRASTIVE_ADD,"SUB":CONTRASTIVE_SUB,"TRANSFER":CONTRASTIVE_TRANSFER,"SET":CONTRASTIVE_SET}

def _op_to_dsl(op,sentence=""):
    span=op.get("evidence",{}).get("span","")
    if not span and sentence:span=sentence.rstrip(".")
    ot=op["op"]
    if ot=="QUERY":return "QUERY|"+op.get("target","")+"|span="+span
    if ot=="TRANSFER":return "TRANSFER|"+op.get("from","")+"|"+op.get("to","")+"|"+str(op.get("value",0))+"|span="+span
    return ot+"|"+op.get("target","")+"|"+str(op.get("value",0))+"|span="+span

def generate_contrastive_ood_data(num_samples=60000,seed=42,target_format="dsl"):
    rng=random.Random(seed);rc=RuleCompiler();records=[]
    from sage.training.neural_data_generator import generate_sentence_level_data as gid
    records.extend(gid(int(num_samples*0.30),include_ood=False,include_adversarial=False,seed=seed,target_format=target_format))
    nc=int(num_samples*0.25)
    for _ in range(nc*2):
        fam=rng.choice(list(ALL_CONTRASTIVE.keys()));tmpls=ALL_CONTRASTIVE[fam];ot,pt,nt=rng.choice(tmpls)
        p=rng.choice(NAMES);obj=rng.choice(OBJECT_TYPES);sg=get_singular(obj);amt=rng.randint(1,10);of=sg if amt==1 else obj
        if fam=="TRANSFER":
            others=[n for n in NAMES if n!=p];recv=rng.choice(others)
            ps=pt.format(giver=p,receiver=recv,amount=amt,obj=of);ns=nt.format(giver=p,receiver=recv,amount=amt,obj=of)
            op={"op":ot,"from":f"{p}.{obj}","to":f"{recv}.{obj}","value":amt}
        else:
            ps=pt.format(person=p,amount=amt,obj=of);ns=nt.format(person=p,amount=amt,obj=of)
            op={"op":ot,"target":f"{p}.{obj}","value":amt}
        if target_format=="dsl":pos_tgt=_op_to_dsl(op,ps);neg_tgt="NOOP"
        else:pos_tgt=json.dumps([op]);neg_tgt="[]"
        records.append({"source":f"compile_sentence: {ps}","target":pos_tgt,"metadata":{"category":"contrastive_pos","op_type":ot}})
        records.append({"source":f"compile_sentence: {ns}","target":neg_tgt,"metadata":{"category":"contrastive_neg","op_type":"NOOP"}})
    from sage.generator.synthetic_worlds import SyntheticWorldGenerator
    gen=SyntheticWorldGenerator(seed=seed+1000)
    for i in range(int(num_samples*0.10)):
        gen.set_seed(10000+i);story=gen.generate_story(rng.randint(3,8))
        sents=rc._split_sentences(story.story_text);kn,ko=set(),set()
        for sent in sents:
            op=rc._parse_sentence(sent,story.story_text,kn,ko)
            if op is not None:
                rc._track_names_objects(op,kn,ko)
                ws=re.sub(r"\b(\d+)\b",lambda m:NUMBER_WORDS.get(int(m.group(1)),m.group(0)),sent)
                target=_op_to_dsl(op,sent)if target_format=="dsl"else json.dumps([op])
                records.append({"source":f"compile_sentence: {ws}","target":target,"metadata":{"category":"ood_numbers"}})
    OOD_NAMES=["Nora","Yusuf","Selin","Omar","Elena","Malik","Derya","Milan"]
    for i in range(int(num_samples*0.05)):
        p=rng.choice(OOD_NAMES);obj=rng.choice(OBJECT_TYPES);sg=get_singular(obj);amt=rng.randint(1,10);of=sg if amt==1 else obj
        v=rng.choice(["has","owns","gains","spends","finds","loses"]);om={"has":"SET","owns":"SET","gains":"ADD","spends":"SUB","finds":"ADD","loses":"SUB"}
        sent=f"{p} {v} {amt} {of}.";op={"op":om[v],"target":f"{p}.{obj}","value":amt}
        target=_op_to_dsl(op,sent)if target_format=="dsl"else json.dumps([op])
        records.append({"source":f"compile_sentence: {sent}","target":target,"metadata":{"category":"ood_names"}})
    NOISE=["The weather is sunny today.","A bird flies past the window.","The clock strikes noon.","Someone hums a quiet tune.","Footsteps echo in the hallway."]
    for i in range(int(num_samples*0.05)):
        records.append({"source":f"compile_sentence: {rng.choice(NOISE)}","target":"NOOP","metadata":{"category":"noise","op_type":"NOOP"}})
    rng.shuffle(records);return records

def write_contrastive_data(records,output_path):
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    with open(output_path,"w")as f:
        for r in records:f.write(json.dumps(r,ensure_ascii=False)+"\n")

def generate_contrastive_split(num_samples=60000,output_dir="data/generated",seed=42):
    records=generate_contrastive_ood_data(num_samples,seed);n=len(records);s=int(n*0.85)
    rng=random.Random(seed);rng.shuffle(records)
    write_contrastive_data(records[:s],Path(output_dir)/"neural_sentence_train_contrastive.jsonl")
    write_contrastive_data(records[s:],Path(output_dir)/"neural_sentence_dev_contrastive.jsonl")
    print(f"Contrastive: train={s} dev={n-s}")
