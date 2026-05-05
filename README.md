# SAGE: State-Aware Generative Engine

SAGE is an experimental alternative to direct next-token-only reasoning.

Instead of asking a model to directly answer from long text, SAGE asks a model
to **compile** the text into executable operations. A deterministic state engine
executes those operations, verifies consistency, and renders the final answer.

**Core hypothesis**: As context grows, verified state transitions degrade slower
than direct next-token answering.

```
Input Text → Compiler → JSON Operations → Verifier → Engine → Verified Answer → Renderer
```

> SAGE is not a RAG system, not a memory system, and not a long-context attention trick.
> SAGE is based on the idea that the primitive unit of reasoning should not be the
> next token, but the next verified state transition.

## Project Status

- **Deterministic Engine**: Ready
- **Rule Compiler**: Ready
- **Synthetic Data Generator**: Ready
- **Model Compiler (Training)**: Ready
- **Baselines**: Ready
- **Evaluation**: Ready
- **Optimization / Scaling**: Pending

## Installation

```bash
# Clone and enter the project
cd SAGE

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install in dev mode
pip install -e .
```

For GPU support:
```bash
pip install -e ".[gpu]"
```

## Quick Start

```bash
# Show help
python -m sage.cli info

# Generate 1000 training samples
python -m sage.cli generate-data --samples 1000 --max-events 50

# Generate all benchmark files
python -m sage.cli generate-data --samples 100 --max-events 50 --benchmarks

# Demo the pipeline on a simple story
python -m sage.cli demo --text "Latif has 5 coins. Arno gives Latif 3 coins. Latif spends 2 coins. Question: How many coins does Latif have?"

# Demo with debug output
python -m sage.cli demo --debug

# Quick evaluation with rule compiler
python -m sage.cli eval-rule --benchmark data/benchmarks/easy.jsonl

# Train the compiler model
python -m sage.cli train-compiler --train data/generated/sage_train.jsonl --dev data/generated/sage_dev.jsonl --epochs 3

# Train the direct baseline
python -m sage.cli train-direct --train data/generated/sage_train.jsonl --dev data/generated/sage_dev.jsonl --epochs 3

# Full evaluation
python -m sage.cli eval --benchmark data/benchmarks/easy.jsonl --compiler checkpoints/compiler --direct checkpoints/direct
```

## Architecture

### Pipeline Components

| Stage | Component | Role |
|-------|-----------|------|
| 1 | **Compiler** | Converts NL story → JSON operation sequence |
| 2 | **Verifier** | Validates JSON syntax and operation schemas |
| 3 | **Engine** | Deterministically executes operations on state |
| 4 | **Renderer** | Converts verified state → human-readable answer |

### Operation Types

| Op | Description | Example |
|----|-------------|---------|
| `SET` | Set a state value | `{"op":"SET","target":"Latif.coins","value":5}` |
| `ADD` | Increase a state value | `{"op":"ADD","target":"Latif.coins","value":3}` |
| `SUB` | Decrease a state value | `{"op":"SUB","target":"Latif.coins","value":2}` |
| `TRANSFER` | Move value between targets | `{"op":"TRANSFER","from":"A.x","to":"B.x","value":5}` |
| `QUERY` | Read a state value | `{"op":"QUERY","target":"Latif.coins"}` |

### Compilers

1. **Rule Compiler** (`RuleCompiler`): Deterministic reference. Uses regex patterns to parse known sentence templates. Perfect accuracy on synthetic data (100% JSON validity).

2. **Model Compiler** (`ModelCompiler`): Seq2seq transformer (flan-t5-small) trained to map stories → JSON ops. The experimental target.

### Baselines

1. **Direct Answer Model**: Same small model trained to answer directly from text.
2. **Heuristic Baseline**: Simple regex-based answer extraction.

## Example

**Input:**
```
Latif has 5 coins. Arno gives Latif 3 coins. Latif spends 2 coins.
Question: How many coins does Latif have?
```

**Compiled Operations:**
```json
[
  {"op": "SET", "target": "Latif.coins", "value": 5},
  {"op": "ADD", "target": "Latif.coins", "value": 3},
  {"op": "SUB", "target": "Latif.coins", "value": 2},
  {"op": "QUERY", "target": "Latif.coins"}
]
```

**Execution Trace:**
```
Step 0: SET Latif.coins = 5       → {Latif.coins: 5}
Step 1: ADD Latif.coins + 3       → {Latif.coins: 8}
Step 2: SUB Latif.coins - 2       → {Latif.coins: 6}
Step 3: QUERY Latif.coins         → answer = 6
```

**Rendered Answer:**
```
Latif has 6 coins.
```

## Synthetic Data

The synthetic event world generates stories about people, objects, and quantities.

### Difficulty Levels

| Level | Events | Noise | Distractors |
|-------|--------|-------|-------------|
| easy | 3–5 | 0% | 0 |
| medium | 10–25 | 10% | 0–2 |
| hard | 50–100 | 20% | 2–5 |
| long | 200–500 | 30% | 5–10 |
| noise_stress | 20–50 | 50% | 5–15 |

### Event Types

- **HAS**: Person has X amount
- **GIVES**: Person gives to another
- **SPENDS**: Person spends/loses
- **FINDS**: Person finds/gains
- **LOSES**: Person loses
- **BUYS**: Person buys from another
- **SELLS**: Person sells to another

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| `answer_exact_match` | Predicted answer == ground truth |
| `compiled_json_valid_rate` | % of outputs that are valid JSON |
| `compiled_ops_valid_rate` | % of outputs with valid op schemas |
| `execution_success_rate` | % of outputs that execute without error |
| `accuracy_by_num_events` | Accuracy broken down by event count |
| `accuracy_by_noise_level` | Accuracy broken down by noise level |
| `latency_ms` | Wall-clock time per sample |

## Key Result to Watch

The critical benchmark result: **Does SAGE degrade slower than direct answering as event count and noise increase?**

If yes: verified state transitions are more robust than direct next-token reasoning for long structured contexts.

If no: the hypothesis needs revision.

## Future Work

- Multi-hop reasoning across multiple state domains
- Recursive compilation (nested state queries)
- Hybrid: compiler delegates to direct-answer for ambiguous cases
- Larger compiler models (flan-t5-base, flan-t5-large)
- Real-world datasets (bAbI, HotpotQA, etc.)
- Streaming compilation for very long documents
- Learned verifier that provides feedback to the compiler
- Integration with retrieval for fact verification
- Efficient attention variants specific to compiler tasks

## Limitations

- Synthetic data only (event-world domain)
- Small model capacity limits generalization
- Rule compiler is template-specific
- No handling of temporal reasoning
- No handling of negation or counterfactuals
- Single-turn only (no dialogue context)
- Currently English-only

## License

MIT
