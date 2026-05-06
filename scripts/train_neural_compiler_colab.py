"""Standalone script to train SAGE neural compiler on Colab or any machine.

Usage:
    python scripts/train_neural_compiler_colab.py [--model flan-t5-small] [--epochs 3] [--batch-size 8]
"""

import sys
import os
import argparse
import subprocess


def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Train SAGE neural compiler end-to-end."
    )
    parser.add_argument("--model", default="google/flan-t5-small")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--sentence-samples", type=int, default=30000)
    parser.add_argument("--story-samples", type=int, default=5000)
    parser.add_argument("--max-input-length", type=int, default=256)
    parser.add_argument("--max-target-length", type=int, default=256)
    parser.add_argument("--use-gpu", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, "src")

    # 1. Setup
    run("pip install -q torch transformers datasets accelerate scikit-learn typer rich pydantic pandas 2>/dev/null || true")

    # 2. Generate data
    run(f"python -m sage.cli generate-neural-training-data --sentence-samples {args.sentence_samples} --story-samples {args.story_samples}")
    run(f"python -m sage.cli generate-data --samples 5000 --max-events 50 --benchmarks")

    # 3. Train sentence compiler
    gpu_flag = "--gpu" if args.use_gpu else "--cpu"
    run(f"python -m sage.cli train-neural-sentence-compiler "
        f"--train data/generated/neural_sentence_train.jsonl "
        f"--dev data/generated/neural_sentence_dev.jsonl "
        f"--model {args.model} --epochs {args.epochs} --batch-size {args.batch_size} "
        f"--max-input-length {args.max_input_length} --max-target-length {args.max_target_length} "
        f"--output-dir models/neural-sentence-compiler {gpu_flag}")

    # 4. Evaluate
    run("python -m sage.cli eval-neural-sentence-compiler --model models/neural-sentence-compiler --benchmarks all")

    # 5. Print results
    run("python -m sage.cli compare-full --max-samples 30")


if __name__ == "__main__":
    main()
