"""Train the SAGE compiler model."""
import torch, sys
torch.set_num_threads(2)
sys.path.insert(0, "src")
from sage.training.simple_train import simple_train_compiler
from sage.config import TrainingConfig
from pathlib import Path

config = TrainingConfig(
    model_name='google/flan-t5-small',
    output_dir='models/sage-compiler-flan-t5-small',
    num_epochs=1,
    batch_size=2,
    use_cpu=True,
    max_input_length=128,
    max_target_length=128,
    learning_rate=5e-5,
    warmup_steps=0,
    weight_decay=0.01,
)
simple_train_compiler(config, Path('data/generated/train_easy_medium.jsonl'))
