# SAGE Project — Build Summary

**Date**: 2025-07-17

---

## Overview

SAGE (State-Aware Generative Engine) is an experimental alternative to direct next-token reasoning. Instead of asking a model to answer directly from long text, SAGE asks a small model to **compile** text into executable operations. A deterministic state engine executes those operations, verifies consistency, and renders the final answer.

**Core hypothesis**: As context grows, verified state transitions degrade slower than direct next-token answering.

## What Was Built

**39 Python files** across the full project structure, plus config files, benchmarks, and documentation.

### Project Structure

```
SAGE/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── data/
│   ├── generated/          # Train/dev/test JSONL splits
│   └── benchmarks/         # easy, medium, hard, long, noise_stress
├── src/sage/
│   ├── __init__.py
│   ├── config.py           # Pydantic config classes
│   ├── cli.py              # Typer CLI (7 commands)
│   ├── schemas/
│   │   ├── ops.py          # Operation, OpType, OperationSequence
│   │   ├── state.py        # StateStore, ExecutionResult, VerificationResult
│   │   └── dataset.py      # DatasetRecord, BenchmarkConfig
│   ├── engine/
│   │   ├── state_store.py  # Deterministic key-value state store
│   │   ├── executor.py     # Executes ops against state store
│   │   └── errors.py       # Engine exception hierarchy
│   ├── verifier/
│   │   └── verifier.py     # JSON parse + op schema validation
│   ├── renderer/
│   │   └── renderer.py     # Renders verified state → natural language
│   ├── generator/
│   │   ├── names.py        # People names + object types
│   │   ├── noise.py        # Noise injection + distractors
│   │   ├── synthetic_worlds.py  # Core story/ops generator
│   │   └── dataset_writer.py    # JSONL writer + benchmark generator
│   ├── compiler/
│   │   ├── rule_compiler.py     # Deterministic regex-based compiler
│   │   ├── model_compiler.py    # HuggingFace seq2seq compiler
│   │   └── postprocess.py       # Output cleaning + validation
│   ├── baselines/
│   │   ├── direct_answer_model.py  # Direct-answer baseline (flan-t5)
│   │   └── heuristic_baseline.py   # Simple regex heuristic
│   ├── training/
│   │   ├── data_module.py          # PyTorch Dataset + collate
│   │   ├── train_compiler.py       # Compiler training (story → ops)
│   │   └── train_direct_baseline.py # Direct baseline training
│   └── eval/
│       ├── metrics.py       # 6 metric functions
│       ├── run_benchmark.py # Full benchmark runner
│       └── report.py        # Rich table + JSON report
└── tests/
    ├── test_engine.py
    ├── test_generator.py
    ├── test_verifier.py
    └── test_end_to_end.py
```

## Verified Results

### Import Check
- **30/35 modules import cleanly** immediately after creation
- 5 failures are all `No module named 'torch'` — PyTorch not installed in test environment (expected)

### Core Smoke Tests (all passed)
- **StateStore**: SET, ADD, SUB, TRANSFER, GET — all deterministic
- **Executor**: Full pipeline with trace generation (5 ops → answer 4)
- **Verifier**: Catches invalid JSON, invalid op types, missing fields, JSON recovery from noisy output
- **Renderer**: Natural language output ("Latif has 4 coins.") + raw numeric extraction for eval
- **Rule Compiler**: Correctly compiles the canonical demo story
- **Data Generator**: Generated stories verified against their own ops via the engine
- **Noise Injector**: Injects noise while keeping question at end

### CLI Commands (all verified)

| Command | Status |
|---------|--------|
| `sage info` | Shows system overview |
| `sage version` | Prints v0.1.0 |
| `sage generate-data --samples 100 --benchmarks` | Generates data + 5 benchmarks |
| `sage demo` | Full pipeline on demo story |
| `sage demo --debug` | Full pipeline with trace |
| `sage eval-rule --benchmark data/benchmarks/easy.jsonl` | Runs rule compiler eval |

### Benchmark Data Generated

| Benchmark | Samples | Events | Noise |
|-----------|---------|--------|-------|
| easy | 1000 | 3–5 | 0% |
| medium | 1000 | 10–25 | 10% |
| hard | 1000 | 50–100 | 20% |
| long | 500 | 200–500 | 30% |
| noise_stress | 500 | 20–50 | 50% |

**All TRANSFER operations verified: 0 negative values across all benchmarks.**

### Rule Compiler Accuracy

- **easy benchmark (100 samples)**: 62.0% answer exact match
- **JSON validity**: 100%
- **Operation validity**: 100%
- **Execution success**: 100%
- **Average latency**: 0.2 ms per sample

## Key Design Decisions

1. **Operation schema uses `from_target`/`to_target`** internally (Python-friendly), with automatic JSON alias mapping for `from`/`to` keys
2. **Rule compiler returns `(list[dict], bool)` tuple** while model compiler returns `str` — the benchmark runner handles both
3. **Renderer has two output modes**: `render()` for human-readable text, `render_raw()` for numeric evaluation comparison
4. **Engine allows negative values by default** (configurable via `EngineConfig.allow_negative`)
5. **Unknown state keys default to 0** (configurable via `EngineConfig.default_value`)

## Bugs Fixed During Build

1. **Generator double-TRANSFER bug**: `generate_event_buys()` had leftover buggy code calling `self.transfer()` with wrong arguments before the correct inline implementation, producing duplicate TRANSFER ops with negative values
2. **Rule compiler singular-object detection**: `_extract_object()` only matched plural forms (`"stickers"`) but not singular forms (`"sticker"`) — added suffix-stripping and irregular plural mappings (`"berry"` → `"berries"`)
3. **Evaluation answer mismatch**: `_run_sage_pipeline()` used `renderer.render()` which produces `"Latif has 6 coins."` but ground truth is `"6"` — switched to `renderer.render_raw()` for evaluation

## What Would Count as Success

The critical benchmark result: **Does SAGE degrade slower than direct answering as event count and noise increase?**

Compare accuracy across difficulty levels:

| Difficulty | Events | Direct Answer Acc | SAGE Compiler Acc |
|-----------|--------|-------------------|-------------------|
| easy | 3–5 | ? | ? |
| medium | 10–25 | ? | ? |
| hard | 50–100 | ? | ? |
| long | 200–500 | ? | ? |

If SAGE accuracy falls off more slowly than direct answering, the hypothesis is supported.

## Next Steps

1. Install PyTorch + HuggingFace Transformers
2. Run `sage train-compiler` and `sage train-direct` on generated data
3. Run `sage eval` on all benchmark levels
4. Compare accuracy curves across difficulty levels
5. Generate plots (optional, matplotlib)

## Commands to Reproduce

```bash
cd /Users/lxxfysl/Projekte/SAGE
export PYTHONPATH=src

# Install deps
python3.11 -m pip install pydantic typer rich pandas scikit-learn numpy

# Generate all data
python3.11 -m sage.cli generate-data --samples 1000 --max-events 50 --benchmarks

# Quick demo
python3.11 -m sage.cli demo --debug

# Rule compiler eval
python3.11 -m sage.cli eval-rule --benchmark data/benchmarks/easy.jsonl

# Train (needs torch + transformers)
python3.11 -m sage.cli train-compiler --train data/generated/sage_train.jsonl --epochs 3
python3.11 -m sage.cli train-direct --train data/generated/sage_train.jsonl --epochs 3

# Full eval
python3.11 -m sage.cli eval --benchmark data/benchmarks/easy.jsonl
```
