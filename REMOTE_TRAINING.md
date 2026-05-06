## Google Colab (Recommended)

The fastest way to train a neural SAGE compiler:

1. Open [SAGE_Neural_Compiler_Colab.ipynb](notebooks/SAGE_Neural_Compiler_Colab.ipynb) in Colab
2. Runtime → Change runtime type → T4 GPU
3. Run all cells

**Expected results on T4 (free GPU)**:
- Data generation: ~5 minutes
- Sentence compiler training (30K samples, 3 epochs): ~15-20 minutes
- Evaluation: ~10 minutes
- Total: ~30-35 minutes, 8GB RAM, 4GB VRAM

**Or use the standalone script**:
```bash
python scripts/train_neural_compiler_colab.py --use-gpu --epochs 3 --batch-size 8
```

---

# Remote Training Guide for SAGE Neural Models

Train the SAGE compiler and direct baseline models on a machine with working PyTorch.

## Prerequisites

- Python 3.11+
- 8+ GB RAM (CPU training)
- 4+ GB GPU VRAM (GPU training, recommended)
- Linux, macOS, or WSL2
- Google Colab (free GPU), RunPod, Vast.ai, or Lambda Labs

## Quick Start (Any Machine)

```bash
# Clone
git clone <repo-url> SAGE
cd SAGE

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install torch transformers datasets accelerate sentencepiece
export PYTHONPATH=src
```

## Google Colab

```python
# Cell 1: Setup
!git clone <repo-url> /content/SAGE
%cd /content/SAGE
!pip install -q typer rich pydantic pandas scikit-learn datasets transformers accelerate
import sys; sys.path.insert(0, 'src')

# Cell 2: Generate data
!python -m sage.cli generate-data --samples 10000 --max-events 100 --benchmarks

# Cell 3: Train compiler
!python -m sage.cli train-compiler \
  --train data/generated/train_mixed.jsonl \
  --dev data/generated/dev_mixed.jsonl \
  --model google/flan-t5-small \
  --epochs 3 --batch-size 8 --cpu/--gpu \
  --max-input-length 1024 --max-target-length 1024 \
  --output-dir models/sage-compiler-flan-t5-small

# Cell 4: Train direct baseline
!python -m sage.cli train-direct \
  --train data/generated/train_mixed.jsonl \
  --dev data/generated/dev_mixed.jsonl \
  --model google/flan-t5-small \
  --epochs 3 --batch-size 8 --cpu/--gpu \
  --max-input-length 1024 --max-target-length 32 \
  --output-dir models/direct-flan-t5-small

# Cell 5: Evaluate
!python -m sage.cli eval-models \
  --compiler-model models/sage-compiler-flan-t5-small \
  --direct-model models/direct-flan-t5-small

# Cell 6: Download models (optional)
from google.colab import files
!zip -r models.zip models/
files.download('models.zip')
```

## RunPod / Vast.ai

```bash
# After SSH into instance
apt update && apt install -y python3.11 python3.11-venv git
git clone <repo-url> SAGE
cd SAGE
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install torch transformers datasets accelerate

export PYTHONPATH=src

# Generate data
python -m sage.cli generate-data --samples 10000 --max-events 100 --benchmarks

# Train (GPU)
python -m sage.cli train-compiler \
  --train data/generated/train_mixed.jsonl \
  --dev data/generated/dev_mixed.jsonl \
  --model google/flan-t5-small \
  --epochs 3 --batch-size 16 --gpu \
  --output-dir models/sage-compiler-flan-t5-small

python -m sage.cli train-direct \
  --train data/generated/train_mixed.jsonl \
  --dev data/generated/dev_mixed.jsonl \
  --model google/flan-t5-small \
  --epochs 3 --batch-size 16 --gpu \
  --output-dir models/direct-flan-t5-small

# Compare
python -m sage.cli eval-models \
  --compiler-model models/sage-compiler-flan-t5-small \
  --direct-model models/direct-flan-t5-small
```

## Linux CPU (slower but works)

```bash
# Same as above but reduce batch size and epochs
python -m sage.cli train-compiler \
  --train data/generated/train_easy_medium.jsonl \
  --model google/flan-t5-small \
  --epochs 1 --batch-size 2 --cpu \
  --max-input-length 256 --max-target-length 256 \
  --output-dir models/sage-compiler-flan-t5-small

# Expected: ~1-2 hours for 1 epoch on 7500 samples
```

## Model Sizes

| Model | Parameters | Disk Size | Min RAM |
|-------|-----------|-----------|---------|
| google/flan-t5-small | 77M | ~300MB | 4GB |
| google/flan-t5-base | 248M | ~1GB | 8GB |
| google/flan-t5-large | 783M | ~3GB | 16GB |

## Expected Results

After training on 10K samples, expect:

| System | easy | medium | hard | long |
|--------|------|--------|------|------|
| Oracle SAGE | 100% | 100% | 100% | 100% |
| Rule SAGE | 100% | 100% | 100% | 100% |
| Neural SAGE | ? | ? | ? | ? |
| Neural Direct | ? | ? | ? | ? |

First training run may produce low accuracy — the model needs to learn JSON syntax
from scratch. If JSON validity is low, consider:
- More epochs (5-10)
- Larger model (flan-t5-base)
- Pre-training on easier examples
- Adding constrained decoding

## Troubleshooting

### JSON validity is 0%
The model outputs invalid JSON. Try:
- Increase `--max-target-length` to 2048
- Train on easy data only first (train_easy_medium.jsonl)
- Check raw model output in `data/reports/neural_compiler_failures_*.jsonl`

### Out of memory
- Reduce `--batch-size` to 2 or 1
- Reduce `--max-input-length` to 512 or 256
- Use gradient accumulation: add `--gradient-accumulation-steps 4` to the training config

### Training too slow on CPU
- Use `train_easy_medium.jsonl` instead of `train_mixed.jsonl`
- Reduce `--epochs` to 1
- Reduce `--max-input-length` to 128
- Consider GPU rental ($0.30-0.50/hour on RunPod/Vast.ai)
