"""SAGE configuration."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class EngineConfig(BaseModel):
    """Configuration for the deterministic state engine."""

    default_value: int = Field(default=0, description="Default value for unknown targets.")
    allow_negative: bool = Field(default=True, description="Allow negative state values.")
    max_state_size: int = Field(default=10_000, description="Maximum number of distinct state entries.")


class CompilerConfig(BaseModel):
    """Configuration for the model compiler."""

    model_name: str = Field(default="google/flan-t5-small", description="HuggingFace model name.")
    max_input_length: int = Field(default=2048, description="Maximum input token length.")
    max_output_length: int = Field(default=1024, description="Maximum output token length.")
    use_rule_compiler: bool = Field(default=False, description="Use rule-based compiler instead of model.")


class TrainingConfig(BaseModel):
    """Configuration for training."""

    model_name: str = Field(default="google/flan-t5-small")
    output_dir: str = Field(default="checkpoints/compiler")
    num_epochs: int = Field(default=3)
    batch_size: int = Field(default=8)
    learning_rate: float = Field(default=5e-5)
    warmup_steps: int = Field(default=500)
    weight_decay: float = Field(default=0.01)
    max_input_length: int = Field(default=2048)
    max_output_length: int = Field(default=1024)
    gradient_accumulation_steps: int = Field(default=1)
    eval_steps: int = Field(default=500)
    save_steps: int = Field(default=1000)
    logging_steps: int = Field(default=100)
    use_cpu: bool = Field(default=True)


class GeneratorConfig(BaseModel):
    """Configuration for synthetic data generation."""

    output_dir: Path = Field(default=Path("data/generated"))
    benchmarks_dir: Path = Field(default=Path("data/benchmarks"))
    seed: int = Field(default=42)

    # People configuration
    min_people: int = Field(default=2)
    max_people: int = Field(default=10)
    people_names_file: Optional[Path] = Field(default=None)

    # Object configuration
    min_object_types: int = Field(default=1)
    max_object_types: int = Field(default=5)

    # Event configuration
    min_events: int = Field(default=3)
    max_events: int = Field(default=500)

    # Noise configuration
    noise_level: float = Field(default=0.0, description="0.0 = no noise, 1.0 = max noise.")
    distractor_people: int = Field(default=0)
    distractor_objects: int = Field(default=0)
    shuffle_surface: bool = Field(default=False)
    irrelevant_sentences: int = Field(default=0)

    # Dataset splits
    train_ratio: float = Field(default=0.8)
    dev_ratio: float = Field(default=0.1)
    test_ratio: float = Field(default=0.1)


class EvalConfig(BaseModel):
    """Configuration for evaluation."""

    benchmark_path: Path = Field(default=Path("data/benchmarks/easy.jsonl"))
    compiler_checkpoint: Optional[Path] = Field(default=None)
    direct_baseline_checkpoint: Optional[Path] = Field(default=None)
    output_dir: Path = Field(default=Path("outputs"))
    use_cpu: bool = Field(default=True)
