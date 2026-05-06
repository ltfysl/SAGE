"""Simple CPU-friendly training for SAGE compiler and direct models.

Avoids HuggingFace Trainer API which can segfault on some CPU configs.
Uses a plain PyTorch training loop.
"""
import json, torch, logging, time
from pathlib import Path
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sage.training.data_module import SAGEDataset, get_collate_fn
from sage.config import TrainingConfig

logger = logging.getLogger(__name__)


def simple_train_compiler(config: TrainingConfig, train_path: Path, dev_path: Path = None):
    """Train compiler model with a simple PyTorch loop."""
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name)
    
    train_dataset = SAGEDataset(train_path, tokenizer, config.max_input_length, config.max_output_length, mode="compile")
    collate = get_collate_fn(tokenizer, config.max_input_length, config.max_output_length)
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True, collate_fn=collate, num_workers=0)
    
    if dev_path:
        dev_dataset = SAGEDataset(dev_path, tokenizer, config.max_input_length, config.max_output_length, mode="compile")
        dev_loader = DataLoader(dev_dataset, batch_size=config.batch_size, shuffle=False, collate_fn=collate, num_workers=0)
    else:
        dev_loader = None
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    
    model.train()
    global_step = 0
    t0 = time.time()
    
    for epoch in range(config.num_epochs):
        total_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            outputs = model(**{k: v for k, v in batch.items()})
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            global_step += 1
            
            if global_step % 100 == 0:
                elapsed = time.time() - t0
                steps_per_sec = global_step / elapsed if elapsed > 0 else 0
                print(f"  Step {global_step} | loss={total_loss/100:.4f} | {steps_per_sec:.1f} steps/s")
                total_loss = 0.0
        
        # Dev eval
        if dev_loader:
            model.eval()
            dev_loss = 0.0
            with torch.no_grad():
                for batch in dev_loader:
                    outputs = model(**{k: v for k, v in batch.items()})
                    dev_loss += outputs.loss.item()
            print(f"  Epoch {epoch+1} complete | dev_loss={dev_loss/len(dev_loader):.4f}")
            model.train()
    
    # Save
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    print(f"Model saved to {out_dir}")


def simple_train_direct(config: TrainingConfig, train_path: Path, dev_path: Path = None):
    """Train direct-answer model with a simple PyTorch loop."""
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name)
    
    train_dataset = SAGEDataset(train_path, tokenizer, config.max_input_length, config.max_output_length, mode="direct_answer")
    collate = get_collate_fn(tokenizer, config.max_input_length, config.max_output_length)
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True, collate_fn=collate, num_workers=0)
    
    if dev_path:
        dev_dataset = SAGEDataset(dev_path, tokenizer, config.max_input_length, config.max_output_length, mode="direct_answer")
        dev_loader = DataLoader(dev_dataset, batch_size=config.batch_size, shuffle=False, collate_fn=collate, num_workers=0)
    else:
        dev_loader = None
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    
    model.train()
    global_step = 0
    t0 = time.time()
    
    for epoch in range(config.num_epochs):
        total_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            outputs = model(**{k: v for k, v in batch.items()})
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            global_step += 1
            
            if global_step % 100 == 0:
                elapsed = time.time() - t0
                steps_per_sec = global_step / elapsed if elapsed > 0 else 0
                print(f"  Step {global_step} | loss={total_loss/100:.4f} | {steps_per_sec:.1f} steps/s")
                total_loss = 0.0
        
        if dev_loader:
            model.eval()
            dev_loss = 0.0
            with torch.no_grad():
                for batch in dev_loader:
                    outputs = model(**{k: v for k, v in batch.items()})
                    dev_loss += outputs.loss.item()
            print(f"  Epoch {epoch+1} complete | dev_loss={dev_loss/len(dev_loader):.4f}")
            model.train()
    
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    print(f"Model saved to {out_dir}")
