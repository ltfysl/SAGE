# SAGE — State-Aware Generative Engine

Evidence-bound compilation for code, logs, and synthetic event worlds.

## Architecture

SAGE compiles unstructured input into **verified state operations** with **evidence links** back to source text. No black-box AI — every operation has a source span, line number, and confidence marker.

```
Input → Compiler → Operations (with evidence) → Verifier → Engine → Answer
```

## Modules

### 1. SAGE Core (synthetic CoinWorld)
Deterministic rule compiler + neural DSL compiler for synthetic event-world stories.

```bash
export PYTHONPATH=src
python3 -m sage.cli generate-data --samples 5000 --max-events 50 --benchmarks
python3 -m sage.cli eval-rule --benchmark data/benchmarks/easy.jsonl
python3 -m sage.cli eval-neural-fast --model models/neural-sentence-compiler-dsl --device auto
```

### 2. SAGE Incident Lens (Laravel log analysis)
Local-first log analyzer. Turn messy Laravel logs into verified incident timelines.

```bash
python3 -m sage.cli logs-report --file data/samples/laravel_realistic_mixed_incident.log
python3 -m sage.cli logs-analyze --file data/samples/laravel_realistic_mixed_incident.log --format json
python3 -m sage.cli logs-ask --file data/samples/laravel_realistic_mixed_incident.log --question "top exception"
```

### 3. SAGE CodeMap (framework-agnostic code mapping)
Static-analysis architecture maps for any codebase. Supports PHP/Laravel, JS/TS/Next.js/Vue, Python/FastAPI/Django, Rust/Cargo.

```bash
python3 -m sage.cli codemap-scan --path /path/to/project --output data/codemaps/map.json
python3 -m sage.cli codemap-ask --map data/codemaps/map.json --question "What writes to course_progresses?"
python3 -m sage.cli codemap-summary --map data/codemaps/map.json
```

### 4. SAGE Incident Lens Web (Next.js dashboard)
Premium dark-themed web UI for log analysis.

```bash
cd apps/sage-incident-lens-web
npm install
npm run dev
# Open http://localhost:3000
```

## Neural Training

Train a sentence-level compiler for CoinWorld:

```bash
export PYTHONPATH=src
export HF_HOME=$(pwd)/models/hf_cache
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Generate training data
python3 -m sage.cli generate-neural-training-data --sentence-samples 30000 --target-format dsl

# Train (flan-t5-small, ~60 min on MPS, ~30 min on T4 GPU)
python3 -m sage.cli train-neural-sentence-compiler \
  --train data/generated/neural_sentence_train.jsonl \
  --dev data/generated/neural_sentence_dev.jsonl \
  --model google/flan-t5-small --epochs 3 --batch-size 4 \
  --device auto --target-format dsl

# Evaluate
python3 -m sage.cli eval-neural-fast --model models/neural-sentence-compiler-dsl --device auto
```

## Key Principle

**No operation executes unless the event is strongly evidence-supported.**
