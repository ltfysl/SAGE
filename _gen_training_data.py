"""Generate sentence-level training data for sklearn baselines.

Each record: {"sentence": str, "label": "SET"|"ADD"|"SUB"|"TRANSFER"|"QUERY"|"NOOP"}
Labels come from the rule compiler to ensure perfect ground truth on training data.
"""
import sys, json, re
sys.path.insert(0, "src")
from pathlib import Path
from sage.compiler.rule_compiler import RuleCompiler

compiler = RuleCompiler()
output_dir = Path("data/generated")
output_dir.mkdir(parents=True, exist_ok=True)

# Load training data
input_paths = [
    ("train_mixed.jsonl", "train_sentences.jsonl"),
    ("dev_mixed.jsonl", "dev_sentences.jsonl"),
]

for input_name, output_name in input_paths:
    input_path = output_dir / input_name
    output_path = output_dir / output_name
    if not input_path.exists():
        print(f"  SKIP: {input_name} not found")
        continue

    records = []
    with open(input_path) as f:
        for line in f:
            rec = json.loads(line)
            story = rec["story"]
            sentences = compiler._split_sentences(story)
            known_names = set()
            known_objects = set()

            for sent in sentences:
                s = sent.strip()
                op = compiler._parse_sentence(s, story, known_names, known_objects)
                if op is not None:
                    label = op["op"]
                    # Track names/objects from parsed ops
                    compiler._track_names_objects(op, known_names, known_objects)
                else:
                    label = "NOOP"
                records.append({"sentence": s, "label": label})

    with open(output_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Count labels
    from collections import Counter
    counts = Counter(r["label"] for r in records)
    print(f"  {output_name}: {len(records)} sentences, labels={dict(counts)}")

print("Done.")
