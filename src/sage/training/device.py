"""Device handling utilities."""
import torch

def resolve_device(device="auto"):
    d=device.lower()
    if d=="auto":
        if torch.cuda.is_available():return torch.device("cuda")
        if hasattr(torch.backends,"mps")and torch.backends.mps.is_available():return torch.device("mps")
        return torch.device("cpu")
    if d=="cuda":
        if not torch.cuda.is_available():raise RuntimeError("CUDA not available")
        return torch.device("cuda")
    if d=="mps":
        if not hasattr(torch.backends,"mps")or not torch.backends.mps.is_available():raise RuntimeError("MPS not available")
        return torch.device("mps")
    if d=="cpu":return torch.device("cpu")
    raise ValueError(f"Unknown device {d}")

def describe_device(dev):
    if dev.type=="cuda":return f"cuda ({torch.cuda.get_device_name(0)})"
    if dev.type=="mps":return "mps (Apple Silicon)"
    return "cpu"

def move_batch(batch,dev):
    return {k:v.to(dev)if isinstance(v,torch.Tensor)else v for k,v in batch.items()}
