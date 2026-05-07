"""CodeMap changed-files analysis."""
import json, subprocess
from pathlib import Path

def analyze_changes(project_path, map_path=None, base="main", max_results=20):
    p = Path(project_path).resolve()
    if not (p / ".git").exists():
        return {"error": f"Not a git repo: {p}"}
    changed = _git_changed(p, base)
    ds = _git_diff_stat(p, base)
    return {"changed_files": changed[:max_results], "diff_stat": ds, "limitations": ["Static analysis only."]}

def _git_changed(p, base):
    try:
        r = subprocess.run(["git", "diff", "--name-only", base], capture_output=True, text=True, cwd=str(p), timeout=15)
        return [f.strip() for f in r.stdout.split(chr(10)) if f.strip()]
    except: return []

def _git_diff_stat(p, base):
    try:
        r = subprocess.run(["git", "diff", "--stat", base], capture_output=True, text=True, cwd=str(p), timeout=15)
        return r.stdout.strip()
    except: return ""
