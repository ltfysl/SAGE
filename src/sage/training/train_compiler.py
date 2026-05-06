"""Training script for the SAGE compiler model (story → operations).

Uses the HuggingFace Trainer API with a sequence-to-sequence model.
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from sage.config import TrainingConfig
from sage.training.data_module import SAGEDataset, get_collate_fn

logger = logging.getLogger(__name__)


def train_compiler(
    config: TrainingConfig,
    train_path: Path,
    dev_path: Path | None = None,
) -> None:
    """Train the SAGE compiler model that maps stories to executable operations.

    Args:
        config: Training hyper-parameters (see :class:`TrainingConfig`).
        train_path: Path to the training JSONL file.
        dev_path: Optional path to a development/validation JSONL file.
    """
    # ------------------------------------------------------------------
    # 1. Device / precision selection
    # ------------------------------------------------------------------
    device = "cpu" if config.use_cpu else "cuda"
    if not config.use_cpu and not torch.cuda.is_available():
        logger.warning("CUDA requested but not available – falling back to CPU.")
        device = "cpu"

    # ------------------------------------------------------------------
    # 2. Tokenizer & model
    # ------------------------------------------------------------------
    logger.info("Loading tokenizer and model: %s", config.model_name)
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)

    model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name)
    model.to(device)

    # ------------------------------------------------------------------
    # 3. Datasets
    # ------------------------------------------------------------------
    logger.info("Loading training data from %s", train_path)
    train_dataset = SAGEDataset(
        jsonl_path=train_path,
        tokenizer=tokenizer,
        max_input_length=config.max_input_length,
        max_output_length=config.max_output_length,
        mode="compile",
    )

    dev_dataset = None
    if dev_path is not None:
        logger.info("Loading dev data from %s", dev_path)
        dev_dataset = SAGEDataset(
            jsonl_path=dev_path,
            tokenizer=tokenizer,
            max_input_length=config.max_input_length,
            max_output_length=config.max_output_length,
            mode="compile",
        )

    # ------------------------------------------------------------------
    # 4. Data collator — use custom collate that handles lists properly
    # ------------------------------------------------------------------
    data_collator = get_collate_fn(
        tokenizer=tokenizer,
        max_input_length=config.max_input_length,
        max_output_length=config.max_output_length,
    )

    # ------------------------------------------------------------------
    # 5. Training arguments
    # ------------------------------------------------------------------
    training_args = Seq2SeqTrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_steps=config.warmup_steps,
        weight_decay=config.weight_decay,
        logging_steps=config.logging_steps,
        eval_steps=config.eval_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        load_best_model_at_end=(dev_dataset is not None),
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        evaluation_strategy="steps" if dev_dataset is not None else "no",
        save_strategy="steps",
        remove_unused_columns=False,
        predict_with_generate=False,
        fp16=torch.cuda.is_available() and not config.use_cpu,
        dataloader_num_workers=0,
        report_to=[],
        no_cuda=config.use_cpu,
    )

    # ------------------------------------------------------------------
    # 6. Trainer
    # ------------------------------------------------------------------
    callbacks = []
    if dev_dataset is not None:
        callbacks.append(
            EarlyStoppingCallback(early_stopping_patience=3)
        )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        tokenizer=tokenizer,
        callbacks=callbacks,
    )

    # ------------------------------------------------------------------
    # 7. Train
    # ------------------------------------------------------------------
    logger.info("Starting compiler training …")
    trainer.train()

    # ------------------------------------------------------------------
    # 8. Save final artefacts
    # ------------------------------------------------------------------
    logger.info("Saving model and tokenizer to %s", config.output_dir)
    trainer.save_model(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)

    logger.info("Compiler training complete.")
