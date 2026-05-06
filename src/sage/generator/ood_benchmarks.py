"""Out-of-distribution benchmark generator for SAGE.

Creates benchmarks that test generalization beyond training templates:
- ood_names: Unseen person names
- ood_phrasing: Unseen surface forms
- ood_numbers: Word numbers instead of digits
- ood_mixed: All of the above combined
"""

from __future__ import annotations
import json, random, re
from pathlib import Path
from sage.generator.synthetic_worlds import SyntheticWorldGenerator
from sage.generator.names import NAMES, OBJECT_TYPES, get_singular


# OOD names not in training set
OOD_NAMES = ["Nora","Yusuf","Selin","Omar","Elena","Malik","Derya","Milan",
             "Anika","Bjorn","Cem","Dalal","Emre","Farah","Gunnar","Helin",
             "Ibrahim","Jana","Kamil","Lale","Mert","Nisa","Osman","Pelin",
             "Rami","Suna","Tarik","Ulya","Veli","Walid","Xena","Yonca","Zeki"]

# OOD phrasing templates
OOD_PHRASING = {
    "SET": [
        "{person} starts with {amount} {obj}.",
        "{person} begins with {amount} {obj}.",
        "{person} is in possession of {amount} {obj}.",
        "{person} currently has {amount} {obj}.",
    ],
    "ADD": [
        "{person} gains {amount} {obj}.",
        "{person} is given {amount} {obj}.",
        "{person} obtains {amount} {obj}.",
        "{person} acquires {amount} {obj}.",
        "{person} receives a gift of {amount} {obj}.",
    ],
    "SUB": [
        "{person} uses up {amount} {obj}.",
        "{person} gets rid of {amount} {obj}.",
        "{person} throws away {amount} {obj}.",
        "{person} wastes {amount} {obj}.",
        "{person} discards {amount} {obj}.",
    ],
    "TRANSFER": [
        "{giver} hands {amount} {obj} over to {receiver}.",
        "{giver} sends {amount} {obj} to {receiver}.",
        "{receiver} takes {amount} {obj} from {giver}.",
        "{receiver} accepts {amount} {obj} from {giver}.",
        "{receiver} gets given {amount} {obj} by {giver}.",
        "{giver} provides {receiver} with {amount} {obj}.",
    ],
    "QUESTION": [
        "Question: How many {obj} does {person} end up with?",
        "Question: How many {obj} is {person} left with?",
        "Question: What is the total number of {obj} that {person} has?",
        "Question: After everything, how many {obj} does {person} have?",
    ],
}

# Number word mapping
NUMBER_WORDS = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",
                8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",
                14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",
                19:"nineteen",20:"twenty"}


def generate_ood_names_benchmark(num_samples: int = 500, output_path: Path = None) -> Path:
    """Generate benchmark with unseen person names."""
    if output_path is None:
        output_path = Path("data/benchmarks/ood_names.jsonl")
    
    rng = random.Random(42)
    gen = SyntheticWorldGenerator(seed=42)
    records = []
    
    for i in range(num_samples):
        gen.reset()
        gen.set_seed(1000 + i)
        
        # Override NAMES with OOD names (mutate in-place so all refs see it)
        import sage.generator.names as nm
        original_names = list(nm.NAMES)
        nm.NAMES[:] = OOD_NAMES
        story_obj = gen.generate_story(rng.randint(3, 8))
        nm.NAMES[:] = original_names
        
        records.append({
            "id": f"ood_names_{i:06d}",
            "story": story_obj.story_text,
            "ops": story_obj.ops,
            "answer": str(story_obj.answer),
            "metadata": {"num_events": story_obj.num_events, "difficulty": "ood_names"}
        })
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return output_path


def generate_ood_phrasing_benchmark(num_samples: int = 500, output_path: Path = None) -> Path:
    """Generate benchmark with unseen phrasing templates."""
    if output_path is None:
        output_path = Path("data/benchmarks/ood_phrasing.jsonl")
    
    rng = random.Random(42)
    records = []
    
    for i in range(num_samples):
        # Generate a story manually with OOD phrasing
        people = rng.sample(NAMES, min(rng.randint(3, 6), len(NAMES)))
        obj_type = rng.choice(OBJECT_TYPES)
        singular = get_singular(obj_type)
        
        sentences = []
        state = {}
        ops = []  # Track operations alongside state during generation
        for p in people:
            amt = rng.randint(1, 15)
            tmpl = rng.choice(OOD_PHRASING["SET"])
            sent = tmpl.format(person=p, amount=amt, obj=singular if amt==1 else obj_type)
            sentences.append(sent)
            state[f"{p}.{obj_type}"] = amt
            ops.append({"op":"SET","target":f"{p}.{obj_type}","value":amt})
        
        num_events = rng.randint(3, 10)
        
        for _ in range(num_events):
            evt = rng.choice(["ADD","SUB","TRANSFER"])
            p = rng.choice(people)
            
            if evt == "ADD":
                amt = rng.randint(1, 10)
                tmpl = rng.choice(OOD_PHRASING["ADD"])
                sent = tmpl.format(person=p, amount=amt, obj=singular if amt==1 else obj_type)
                sentences.append(sent)
                state[f"{p}.{obj_type}"] = state.get(f"{p}.{obj_type}", 0) + amt
                ops.append({"op":"ADD","target":f"{p}.{obj_type}","value":amt})
            elif evt == "SUB":
                current = state.get(f"{p}.{obj_type}", 0)
                amt = rng.randint(1, max(1, current))
                tmpl = rng.choice(OOD_PHRASING["SUB"])
                sent = tmpl.format(person=p, amount=amt, obj=singular if amt==1 else obj_type)
                sentences.append(sent)
                state[f"{p}.{obj_type}"] = state.get(f"{p}.{obj_type}", 0) - amt
                ops.append({"op":"SUB","target":f"{p}.{obj_type}","value":amt})
            elif evt == "TRANSFER":
                others = [x for x in people if x != p]
                if not others:
                    continue
                receiver = rng.choice(others)
                current = state.get(f"{p}.{obj_type}", 0)
                amt = rng.randint(1, max(1, current))
                tmpl = rng.choice(OOD_PHRASING["TRANSFER"])
                sent = tmpl.format(giver=p, receiver=receiver, amount=amt, obj=singular if amt==1 else obj_type)
                sentences.append(sent)
                state[f"{p}.{obj_type}"] = state.get(f"{p}.{obj_type}", 0) - amt
                state[f"{receiver}.{obj_type}"] = state.get(f"{receiver}.{obj_type}", 0) + amt
                ops.append({"op":"TRANSFER","from":f"{p}.{obj_type}","to":f"{receiver}.{obj_type}","value":amt})
        
        # Question
        query_person = rng.choice(people)
        answer = state.get(f"{query_person}.{obj_type}", 0)
        tmpl = rng.choice(OOD_PHRASING["QUESTION"])
        question = tmpl.format(person=query_person, obj=obj_type, obj_singular=singular)
        sentences.append(question)
        ops.append({"op":"QUERY","target":f"{query_person}.{obj_type}"})
        
        full_text = " ".join(sentences)
        
        records.append({
            "id": f"ood_phrasing_{i:06d}",
            "story": full_text,
            "ops": ops,
            "answer": str(answer),
            "metadata": {"num_events": len(sentences), "difficulty": "ood_phrasing"}
        })
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return output_path


def generate_ood_numbers_benchmark(num_samples: int = 500, output_path: Path = None) -> Path:
    """Generate benchmark with word numbers instead of digit numbers."""
    if output_path is None:
        output_path = Path("data/benchmarks/ood_numbers.jsonl")
    
    rng = random.Random(42)
    gen = SyntheticWorldGenerator(seed=42)
    records = []
    
    for i in range(num_samples):
        gen.reset()
        gen.set_seed(2000 + i)
        story_obj = gen.generate_story(rng.randint(3, 8))
        
        # Replace digit numbers with word numbers
        story_text = story_obj.story_text
        def replace_num(m):
            d = int(m.group(1))
            if d in NUMBER_WORDS:
                return NUMBER_WORDS[d]
            return m.group(0)
        story_text = re.sub(r'\b(\d+)\b', replace_num, story_text)
        
        records.append({
            "id": f"ood_numbers_{i:06d}",
            "story": story_text,
            "ops": story_obj.ops,  # ops still have digit values (ground truth)
            "answer": str(story_obj.answer),
            "metadata": {"num_events": story_obj.num_events, "difficulty": "ood_numbers"}
        })
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return output_path


def generate_ood_mixed_benchmark(num_samples: int = 500, output_path: Path = None) -> Path:
    """Generate benchmark with all OOD variations combined."""
    if output_path is None:
        output_path = Path("data/benchmarks/ood_mixed.jsonl")
    
    rng = random.Random(42)
    records = []
    
    for i in range(num_samples):
        # Alternate between OOD approaches
        if i % 3 == 0:
            # OOD names + word numbers
            gen = SyntheticWorldGenerator(seed=3000 + i)
            import sage.generator.names as nm
            orig = list(nm.NAMES)
            nm.NAMES[:] = OOD_NAMES
            story_obj = gen.generate_story(rng.randint(3, 10))
            nm.NAMES[:] = orig
            story_text = re.sub(r'\b(\d+)\b', lambda m: NUMBER_WORDS.get(int(m.group(1)), m.group(0)), story_obj.story_text)
        elif i % 3 == 1:
            # OOD phrasing + word numbers
            people = rng.sample(NAMES, min(rng.randint(3, 5), len(NAMES)))
            obj_type = rng.choice(OBJECT_TYPES)
            singular = get_singular(obj_type)
            sentences = []
            state = {}
            for p in people:
                amt = rng.randint(1, 15)
                sent = f"{p} starts with {NUMBER_WORDS.get(amt, str(amt))} {singular if amt==1 else obj_type}."
                sentences.append(sent)
                state[f"{p}.{obj_type}"] = amt
            
            for _ in range(rng.randint(3, 8)):
                p = rng.choice(people)
                amt = rng.randint(1, 10)
                current = state.get(f"{p}.{obj_type}", 0)
                if rng.random() < 0.3 and current > 0:
                    sent = f"{p} uses up {NUMBER_WORDS.get(amt, str(amt))} {singular if amt==1 else obj_type}."
                    state[f"{p}.{obj_type}"] = current - amt
                elif rng.random() < 0.6:
                    sent = f"{p} obtains {NUMBER_WORDS.get(amt, str(amt))} {singular if amt==1 else obj_type}."
                    state[f"{p}.{obj_type}"] = current + amt
                else:
                    others = [x for x in people if x != p]
                    if others:
                        r = rng.choice(others)
                        sent = f"{p} hands {NUMBER_WORDS.get(amt, str(amt))} {singular if amt==1 else obj_type} over to {r}."
                        state[f"{p}.{obj_type}"] = current - amt
                        state[f"{r}.{obj_type}"] = state.get(f"{r}.{obj_type}", 0) + amt
                    else:
                        continue
                sentences.append(sent)
            
            query_p = rng.choice(people)
            answer = state.get(f"{query_p}.{obj_type}", 0)
            sentences.append(f"Question: How many {obj_type} does {query_p} end up with?")
            full_text = " ".join(sentences)
            from sage.compiler.rule_compiler import RuleCompiler
            ops, _ = RuleCompiler().compile(full_text)
            story_obj = type('obj', (object,), {'story_text': full_text, 'ops': ops, 'answer': answer, 'num_events': len(sentences)})()
        else:
            # OOD names + OOD phrasing
            gen = SyntheticWorldGenerator(seed=4000 + i)
            import sage.generator.names as nm
            orig = list(nm.NAMES)
            nm.NAMES[:] = OOD_NAMES
            story_obj = gen.generate_story(rng.randint(3, 8))
            nm.NAMES[:] = orig
        
        records.append({
            "id": f"ood_mixed_{i:06d}",
            "story": story_obj.story_text,
            "ops": story_obj.ops,
            "answer": str(story_obj.answer),
            "metadata": {"num_events": story_obj.num_events, "difficulty": "ood_mixed"}
        })
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return output_path


def generate_all_ood_benchmarks(benchmarks_dir: Path = None, num_samples: int = 200):
    """Generate all four OOD benchmarks."""
    if benchmarks_dir is None:
        benchmarks_dir = Path("data/benchmarks")
    benchmarks_dir = Path(benchmarks_dir)
    benchmarks_dir.mkdir(parents=True, exist_ok=True)
    
    generate_ood_names_benchmark(num_samples, benchmarks_dir / "ood_names.jsonl")
    generate_ood_phrasing_benchmark(num_samples, benchmarks_dir / "ood_phrasing.jsonl")
    generate_ood_numbers_benchmark(num_samples, benchmarks_dir / "ood_numbers.jsonl")
    generate_ood_mixed_benchmark(num_samples, benchmarks_dir / "ood_mixed.jsonl")
    
    print("OOD benchmarks generated:")
    for p in sorted(benchmarks_dir.glob("ood_*.jsonl")):
        count = sum(1 for _ in open(p))
        print(f"  {p.name}: {count} samples")
