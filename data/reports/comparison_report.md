# SAGE vs Direct Baseline — Comparison Report

## Overall Accuracy

| Benchmark | Events | Oracle SAGE | Rule SAGE | Direct Heuristic | SAGE Advantage |
|-----------|--------|-------------|-----------|------------------|----------------|
| easy | 5 | 100% | 100% | 35% | +186% |
| medium | 20 | 100% | 100% | 33% | +203% |
| hard | 84 | 100% | 100% | 26% | +285% |
| long | 407 | 100% | 100% | 32% | +212% |
| adversarial | 15 | 100% | 100% | 31% | +223% |

## Context-Scaling Advantage

| Threshold | SAGE Max Events | Direct Max Events | Advantage Ratio |
|-----------|----------------|-------------------|-----------------|
| 90% | 407 | 0 | infx |
| 80% | 407 | 0 | infx |
| 70% | 407 | 0 | infx |

## Event Bucket Accuracy

| Benchmark | Bucket | Rule SAGE | Direct |
|-----------|--------|-----------|--------|
| easy | 1-5 | 100% | 33% |
| easy | 6-25 | 100% | 37% |
| medium | 6-25 | 100% | 37% |
| medium | 26-100 | 100% | 18% |
| hard | 26-100 | 100% | 22% |
| hard | 101-500 | 100% | 40% |
| long | 101-500 | 100% | 32% |
| adversarial | 6-25 | 100% | 31% |