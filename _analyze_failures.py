"""Analyze sklearn compiler extraction failures."""
import json, sys, re
sys.path.insert(0, "src")
from pathlib import Path
from collections import Counter
from sage.baselines.sklearn_compiler import load_sklearn_compiler
from sage.compiler.rule_compiler import RuleCompiler

sc = load_sklearn_compiler(Path("models/sklearn-op-classifier.joblib"))
rc = RuleCompiler()

# Load easy benchmark and compare extraction
bench_path = Path("data/benchmarks/easy.jsonl")
samples = []
with open(bench_path) as f:
    for line in f:
        samples.append(json.loads(line))

samples = samples[:50]

failure_categories = Counter()
extraction_failures = []

for sample in samples:
    story = sample["story"]
    gt_ops = sample["ops"]
    sentences = rc._split_sentences(story)
    labels = sc.predict_labels(sentences)
    
    known_names = set()
    known_objects = set()
    
    # Build sentence-to-GT-op mapping using evidence-like matching
    for sent_i, (sentence, label) in enumerate(zip(sentences, labels)):
        # Find the GT op that matches this sentence (by content overlap)
        matching_gt = None
        for gt_op in gt_ops:
            target = gt_op.get("target", "")
            from_t = gt_op.get("from", "")
            to_t = gt_op.get("to", "")
            val = str(gt_op.get("value", ""))
            # Check if persons/objects/values appear in sentence
            score = 0
            if target:
                parts = target.split(".")
                for p in parts:
                    if p.lower() in sentence.lower():
                        score += 1
            if from_t:
                parts = from_t.split(".")
                for p in parts:
                    if p.lower() in sentence.lower():
                        score += 1
            if to_t:
                parts = to_t.split(".")
                for p in parts:
                    if p.lower() in sentence.lower():
                        score += 1
            if val and val in sentence:
                score += 1
            if score >= 2:
                matching_gt = gt_op
                break
        
        if matching_gt is None and label == "NOOP":
            continue  # Correctly skipped noise
        
        # Get sklearn extraction
        sk_op = sc._extract_op_from_sentence(sentence, label, story, known_names, known_objects)
        
        if matching_gt and sk_op:
            # Compare entities
            reasons = []
            gt_target = matching_gt.get("target", "")
            sk_target = sk_op.get("target", "")
            
            if gt_target and sk_target:
                gt_parts = gt_target.split(".")
                sk_parts = sk_target.split(".")
                if len(gt_parts) == 2 and len(sk_parts) == 2:
                    if gt_parts[0].lower() != sk_parts[0].lower():
                        reasons.append("wrong_person")
                    if gt_parts[1].lower() != sk_parts[1].lower():
                        reasons.append("wrong_object")
            
            if matching_gt.get("op") in ("SET","ADD","SUB") and sk_op.get("op") in ("SET","ADD","SUB"):
                if matching_gt.get("value") != sk_op.get("value"):
                    reasons.append("wrong_value")
            
            if matching_gt.get("op") == "TRANSFER" and sk_op.get("op") == "TRANSFER":
                gt_from = matching_gt.get("from","")
                gt_to = matching_gt.get("to","")
                sk_from = sk_op.get("from","")
                sk_to = sk_op.get("to","")
                if not sk_from or not sk_to:
                    reasons.append("missing_transfer_direction")
                elif (gt_from and sk_from and gt_from.split(".")[0].lower() != sk_from.split(".")[0].lower()) or \
                     (gt_to and sk_to and gt_to.split(".")[0].lower() != sk_to.split(".")[0].lower()):
                    reasons.append("wrong_transfer_direction")
                if matching_gt.get("value") != sk_op.get("value"):
                    reasons.append("wrong_value")
            
            if not reasons:
                reasons.append("ok")
            
            for r in reasons:
                failure_categories[r] += 1
            
            if "ok" not in reasons:
                extraction_failures.append({
                    "sentence": sentence,
                    "predicted_label": label,
                    "gt_label": matching_gt.get("op",""),
                    "sk_extraction": sk_op,
                    "gt_extraction": matching_gt,
                    "reasons": reasons,
                })
        elif matching_gt and not sk_op:
            failure_categories["missing_op"] += 1
            extraction_failures.append({
                "sentence": sentence,
                "predicted_label": label,
                "gt_label": matching_gt.get("op",""),
                "sk_extraction": None,
                "gt_extraction": matching_gt,
                "reasons": ["missing_op"],
            })
        elif not matching_gt and sk_op and label != "NOOP":
            failure_categories["extra_op"] += 1

print("=== EXTRACTION FAILURE ANALYSIS ===")
print(f"Samples analyzed: {len(samples)}")
print(f"\nFailure categories:")
for cat, count in failure_categories.most_common():
    print(f"  {cat}: {count}")

print(f"\nSample failures:")
for ef in extraction_failures[:8]:
    print(f"  Sent: '{ef['sentence'][:80]}'")
    print(f"    Predicted: {ef['predicted_label']}  GT: {ef['gt_label']}")
    print(f"    Reasons: {ef['reasons']}")
    print(f"    GT entities: {ef.get('gt_extraction',{})}")
    print(f"    SK entities: {ef.get('sk_extraction',{})}")
    print()
