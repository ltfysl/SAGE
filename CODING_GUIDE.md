# SAGE Coding Guide

## Project Structure

```
SAGE/
├── src/sage/              # Main Python package
│   ├── compiler/          # Rule compiler, model compiler, op DSL
│   ├── engine/            # Deterministic state executor
│   ├── verifier/          # JSON/evidence validation
│   ├── renderer/          # Result rendering
│   ├── schemas/           # Pydantic operation models
│   ├── eval/              # Benchmarks, metrics, reports
│   ├── generator/         # Synthetic world/story generator
│   ├── extraction/        # Entity extraction (shared patterns)
│   ├── baselines/         # sklearn/heuristic baselines
│   ├── training/          # Neural training pipeline
│   └── domains/           # Domain-specific modules
│       ├── logs/          # Incident Lens (Laravel logs)
│       └── codemap/       # CodeMap (code architecture)
├── apps/                  # Web applications
│   └── sage-incident-lens-web/  # Next.js dashboard
├── data/
│   ├── benchmarks/        # Evaluation benchmarks
│   ├── generated/         # Training data
│   ├── samples/           # Sample inputs for testing
│   │   └── codebases/     # Sample codebases for CodeMap
│   └── reports/           # Generated reports (gitignored)
├── models/                # Trained model checkpoints
├── tests/                 # Pytest test suite
└── scripts/               # Standalone utility scripts
```

## Adding a New Domain

1. Create `src/sage/domains/YOUR_DOMAIN/__init__.py`
2. Define operation types (like `code_ops.py`)
3. Implement a parser → compiler → engine → renderer
4. Add CLI commands in `src/sage/cli.py`
5. Create sample data in `data/samples/`
6. Add tests in `tests/`

## Evaluation Pipeline

1. Generate benchmarks: `python3 -m sage.cli generate-data --benchmarks`
2. Run oracle: `python3 -m sage.cli eval-oracle --benchmark data/benchmarks/easy.jsonl`
3. Run rule compiler: `python3 -m sage.cli eval-rule --benchmark data/benchmarks/easy.jsonl`
4. Inspect failures: `python3 -m sage.cli inspect-failures --file data/reports/failures_easy.jsonl`

## Evidence Requirements

Every operation must include:
```python
"evidence": {
    "span": "exact source text",
    "start": 0,        # character offset
    "end": 200,        # character offset
    "confidence": 1.0  # 0.0–1.0
}
```
