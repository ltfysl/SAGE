"""Neural sentence compiler training.

Trains a seq2seq model to map individual sentences to operation JSON.
Input: "compile_sentence: {sentence}"
Target: "[{...}]" (single-op JSON array) or "[]" (NOOP)
"""

import json, torch, logging, time
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sage.training.device import resolve_device, describe_device, move_batch

logger = logging.getLogger(__name__)


class NeuralSentenceDataset(Dataset):
    """Dataset for neural sentence compiler training.
    
    Reads JSONL with {"source": "compile_sentence: ...", "target": "[...]"} format.
    """
    
    def __init__(self, jsonl_path: Path):
        self.records = []
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    self.records.append(json.loads(line))
    
    def __len__(self):
        return len(self.records)
    
    def __getitem__(self, idx):
        return {"source": self.records[idx]["source"], "target": self.records[idx]["target"]}


def get_collate_fn(tokenizer, max_input_length=256, max_output_length=256):
    """Collate function that tokenizes source and target."""
    def collate_fn(batch):
        sources = [item["source"] for item in batch]
        targets = [item["target"] for item in batch]
        
        model_inputs = tokenizer(sources, max_length=max_input_length,
                                 padding=True, truncation=True, return_tensors="pt")
        labels = tokenizer(targets, max_length=max_output_length,
                          padding=True, truncation=True, return_tensors="pt")
        labels_ids = labels["input_ids"]
        if tokenizer.pad_token_id is not None:
            labels_ids[labels_ids == tokenizer.pad_token_id] = -100
        model_inputs["labels"] = labels_ids
        return model_inputs
    return collate_fn


def train_neural_sentence_compiler(
    train_path: Path,
    dev_path: Path = None,
    model_name: str = "google/flan-t5-small",
    output_dir: str = "models/neural-sentence-compiler",
    num_epochs: int = 3,
    batch_size: int = 8,
    max_input_length: int = 256,
    max_output_length: int = 256,
    learning_rate: float = 5e-5,
    device: str = "auto",
):
    """Train a neural sentence compiler model."""
    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    dev = resolve_device(device)
    print(f"Device: {describe_device(dev)}")
    model.to(dev)
    
    train_dataset = NeuralSentenceDataset(train_path)
    collate = get_collate_fn(tokenizer, max_input_length, max_output_length)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                              collate_fn=collate, num_workers=0)
    
    dev_loader = None
    if dev_path:
        dev_dataset = NeuralSentenceDataset(dev_path)
        dev_loader = DataLoader(dev_dataset, batch_size=batch_size, shuffle=False,
                               collate_fn=collate, num_workers=0)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    
    model.train()
    global_step = 0
    t0 = time.time()
    
    for epoch in range(num_epochs):
        total_loss = 0.0
        for batch in train_loader:
            batch = move_batch(batch, dev)
            
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            global_step += 1
            
            if global_step % 100 == 0:
                elapsed = time.time() - t0
                print(f"  Step {global_step} | loss={total_loss/100:.4f} | {global_step/elapsed:.1f} steps/s")
                total_loss = 0.0
        
        if dev_loader:
            model.eval()
            dev_loss = 0.0
            with torch.no_grad():
                for batch in dev_loader:
                    batch = move_batch(batch, dev)
                    outputs = model(**batch)
                    dev_loss += outputs.loss.item()
            print(f"  Epoch {epoch+1} | dev_loss={dev_loss/len(dev_loader):.4f}")
            model.train()
        else:
            print(f"  Epoch {epoch+1} complete")
    
    # Save
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    print(f"Model saved to {out_dir}")
