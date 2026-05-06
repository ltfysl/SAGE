"""Neural training data generator for SAGE.

Generates sentence-level and story-level training data for the neural compiler.
Sentence format: "compile_sentence: {sentence}" → JSON array with 0 or 1 ops
Story format: "compile_story: {story}" → JSON array with all ops
"""

from __future__ import annotations
import json, random, re
from pathlib import Path
from sage.generator.synthetic_worlds import SyntheticWorldGenerator
from sage.generator.names import NAMES, OBJECT_TYPES, get_singular
from sage.compiler.rule_compiler import RuleCompiler


NUMBER_WORDS = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",
                8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",
                14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",
                19:"nineteen",20:"twenty"}


def generate_sentence_level_data(
    num_samples: int = 30000,
    include_ood: bool = True,
    include_adversarial: bool = True,
    seed: int = 42,
) -> list[dict]:
    """Generate sentence-level training examples.
    
    Each record: {"source": "compile_sentence: ...", "target": "[...]"}
    
    Distribution:
    - 40% in-domain sentences (from generated stories)
    - 20% OOD phrasing sentences
    - 15% OOD numbers (word numbers)
    - 15% adversarial/non-event sentences (target: [])
    - 10% noise/irrelevant sentences (target: [])
    """
    rng = random.Random(seed)
    gen = SyntheticWorldGenerator(seed=seed)
    rc = RuleCompiler()
    records = []
    
    # --- In-domain sentences (40%) ---
    for i in range(int(num_samples * 0.4)):
        gen.set_seed(seed + i)
        story = gen.generate_story(rng.randint(3, 10))
        sentences = rc._split_sentences(story.story_text)
        known_names, known_objects = set(), set()
        
        for sent in sentences:
            op = rc._parse_sentence(sent, story.story_text, known_names, known_objects)
            if op is not None:
                # Single-op target
                target = json.dumps([op], separators=(",", ":"))
                source = f"compile_sentence: {sent}"
                records.append({"source": source, "target": target})
                rc._track_names_objects(op, known_names, known_objects)
    
    # --- OOD phrasing (20%) ---
    if include_ood:
        OOD_PHRASING_TEMPLATES = [
            ("SET", "{person} starts with {amount} {obj}."),
            ("SET", "{person} begins with {amount} {obj}."),
            ("SET", "{person} is in possession of {amount} {obj}."),
            ("SET", "{person} currently has {amount} {obj}."),
            ("ADD", "{person} gains {amount} {obj}."),
            ("ADD", "{person} obtains {amount} {obj}."),
            ("ADD", "{person} acquires {amount} {obj}."),
            ("ADD", "{person} is given {amount} {obj}."),
            ("SUB", "{person} uses up {amount} {obj}."),
            ("SUB", "{person} gets rid of {amount} {obj}."),
            ("SUB", "{person} discards {amount} {obj}."),
            ("SUB", "{person} throws away {amount} {obj}."),
            ("TRANSFER", "{giver} hands {amount} {obj} over to {receiver}."),
            ("TRANSFER", "{giver} sends {amount} {obj} to {receiver}."),
            ("TRANSFER", "{receiver} takes {amount} {obj} from {giver}."),
            ("TRANSFER", "{receiver} accepts {amount} {obj} from {giver}."),
        ]
        for i in range(int(num_samples * 0.2)):
            op_type, tmpl = rng.choice(OOD_PHRASING_TEMPLATES)
            person = rng.choice(NAMES)
            obj = rng.choice(OBJECT_TYPES)
            singular = get_singular(obj)
            amt = rng.randint(1, 10)
            obj_form = singular if amt == 1 else obj
            
            if op_type == "TRANSFER":
                others = [n for n in NAMES if n != person]
                receiver = rng.choice(others)
                sent = tmpl.format(giver=person, receiver=receiver, amount=amt, obj=obj_form)
                op = {"op":"TRANSFER","from":f"{person}.{obj}","to":f"{receiver}.{obj}","value":amt}
            else:
                sent = tmpl.format(person=person, amount=amt, obj=obj_form)
                op = {"op":op_type,"target":f"{person}.{obj}","value":amt}
            
            target = json.dumps([op], separators=(",", ":"))
            source = f"compile_sentence: {sent}"
            records.append({"source": source, "target": target})
    
    # --- OOD numbers (15%) ---
    if include_ood:
        for i in range(int(num_samples * 0.15)):
            gen.set_seed(10000 + i)
            story = gen.generate_story(rng.randint(3, 8))
            sentences = rc._split_sentences(story.story_text)
            known_names, known_objects = set(), set()
            
            for sent in sentences:
                op = rc._parse_sentence(sent, story.story_text, known_names, known_objects)
                if op is not None:
                    rc._track_names_objects(op, known_names, known_objects)
                    # Replace digits with word numbers in source
                    word_sent = re.sub(r'\b(\d+)\b', lambda m: NUMBER_WORDS.get(int(m.group(1)), m.group(0)), sent)
                    target = json.dumps([op], separators=(",", ":"))
                    source = f"compile_sentence: {word_sent}"
                    records.append({"source": source, "target": target})
    
    # --- Adversarial non-events (15%) ---
    if include_adversarial:
        ADV_TEMPLATES = [
            "{person} almost gave {amount} {obj} to {other}, but changed his mind.",
            "{person} wanted to give {amount} {obj} to {other}, but did not.",
            "{person} planned to spend {amount} {obj}, but kept them.",
            "{person} says he has {amount} {obj}, but actually has {real_amount}.",
            "{person} claims to have {amount} {obj}, but really has {real_amount}.",
            "{person} tried to give {amount} {obj} to {other}, but couldn't.",
            "{person} thought about spending {amount} {obj}, but saved them instead.",
            "{person} nearly dropped {amount} {obj}, but caught them.",
            "{person} would have given {amount} {obj} to {other}, but changed his mind.",
        ]
        for i in range(int(num_samples * 0.15)):
            tmpl = rng.choice(ADV_TEMPLATES)
            person = rng.choice(NAMES)
            other = rng.choice([n for n in NAMES if n != person])
            obj = rng.choice(OBJECT_TYPES)
            singular = get_singular(obj)
            amt = rng.randint(1, 10)
            real_amt = rng.randint(1, 20)
            obj_form = singular if amt == 1 else obj
            sent = tmpl.format(person=person, amount=amt, obj=obj_form, other=other, real_amount=real_amt)
            # Target is empty array — no operation for non-events
            source = f"compile_sentence: {sent}"
            records.append({"source": source, "target": "[]"})
    
    # --- Noise sentences (10%) ---
    NOISE_SENTENCES = [
        "The weather is sunny today.",
        "A bird flies past the window.",
        "The clock strikes noon.",
        "Someone hums a quiet tune.",
        "Footsteps echo in the hallway.",
        "The curtains sway gently.",
        "A dog barks in the distance.",
        "The lamp flickers briefly.",
        "A book falls off the shelf.",
        "The radiator clicks on.",
        "A chair scrapes against the floor.",
        "The toaster pops.",
        "A light buzzes overhead.",
        "A shadow moves in the corner.",
        "The refrigerator hums.",
        "A cat stretches on the windowsill.",
        "The phone rings once.",
        "The kettle starts to whistle.",
        "The scent of coffee lingers.",
        "The door creaks open.",
    ]
    for i in range(int(num_samples * 0.1)):
        sent = rng.choice(NOISE_SENTENCES)
        source = f"compile_sentence: {sent}"
        records.append({"source": source, "target": "[]"})
    
    rng.shuffle(records)
    return records


def generate_story_level_data(
    num_samples: int = 10000,
    include_ood: bool = True,
    seed: int = 99,
) -> list[dict]:
    """Generate story-level training examples.
    
    Each record: {"source": "compile_story: {story}", "target": "[...]"}
    """
    rng = random.Random(seed)
    gen = SyntheticWorldGenerator(seed=seed)
    rc = RuleCompiler()
    records = []
    
    for i in range(num_samples):
        gen.set_seed(seed + i * 137)
        num_events = rng.randint(3, 20)
        story = gen.generate_story(num_events)
        
        # Use rule compiler to get ops with evidence
        ops, success = rc.compile(story.story_text)
        if not success or not ops:
            continue
        
        target = json.dumps(ops, separators=(",", ":"))
        source = f"compile_story: {story.story_text}"
        records.append({"source": source, "target": target})
    
    rng.shuffle(records)
    return records


def write_neural_data(records: list[dict], output_path: Path):
    """Write records as JSONL."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def generate_all_neural_data(
    output_dir: Path = None,
    sentence_samples: int = 30000,
    story_samples: int = 10000,
    seed: int = 42,
):
    """Generate all neural training data (sentence + story level)."""
    if output_dir is None:
        output_dir = Path("data/generated")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating sentence-level data...")
    sent_records = generate_sentence_level_data(
        num_samples=sentence_samples, include_ood=True, include_adversarial=True, seed=seed
    )
    n = len(sent_records)
    split = int(n * 0.85)
    write_neural_data(sent_records[:split], output_dir / "neural_sentence_train.jsonl")
    write_neural_data(sent_records[split:], output_dir / "neural_sentence_dev.jsonl")
    print(f"  Sentence train: {split} samples")
    print(f"  Sentence dev: {n - split} samples")
    
    print("Generating story-level data...")
    story_records = generate_story_level_data(num_samples=story_samples, seed=seed + 1)
    n2 = len(story_records)
    split2 = int(n2 * 0.85)
    write_neural_data(story_records[:split2], output_dir / "neural_story_train.jsonl")
    write_neural_data(story_records[split2:], output_dir / "neural_story_dev.jsonl")
    print(f"  Story train: {split2} samples")
    print(f"  Story dev: {n2 - split2} samples")
    
    # Also create a mixed file with both sentence and story examples
    all_records = sent_records + story_records
    rng = random.Random(seed)
    rng.shuffle(all_records)
    write_neural_data(all_records, output_dir / "neural_mixed_train.jsonl")
    print(f"  Mixed: {len(all_records)} samples")
