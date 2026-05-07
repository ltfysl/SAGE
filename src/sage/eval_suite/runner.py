"""SAGE evaluation runner."""
from sage.eval_suite.codemap_eval import evaluate_codemap
from sage.eval_suite.specsync_eval import evaluate_specsync
from sage.eval_suite.memory_eval import evaluate_memory

def run_suite(name):
    if name == "codemap": return evaluate_codemap()
    if name == "specsync": return evaluate_specsync()
    if name == "project_memory": return evaluate_memory()
    if name == "all": return list(filter(None, [evaluate_codemap(), evaluate_specsync(), evaluate_memory()]))
    raise ValueError(f"Unknown suite: {name}")
