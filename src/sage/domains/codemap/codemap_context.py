"""CodeMap context generator — produces context packs for coding agents."""
from __future__ import annotations
from pathlib import Path
import json


def generate_context(map_path: str | Path, task: str) -> str:
    """Generate a context pack for a coding task."""
    from sage.domains.codemap.codemap_scan import load_codemap
    from sage.domains.codemap.codemap_ask import CodemapAsk

    data = load_codemap(map_path)
    ask = CodemapAsk(data)
    sr = ask._search_fulltext(task)
    files = sr.get("evidence", [])[:10]

    lines = []
    lines.append("=" * 60)
    lines.append("CodeMap Context Pack")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Task: {task}")
    lines.append("")
    lines.append("Relevant files:")
    for i, f in enumerate(files):
        fn = f.get("name") or f.get("evidence", {}).get("file", "?")
        sc = f.get("op", "").replace("score=", "")
        lines.append(f"  {i+1}. {fn} (score: {sc})")
    lines.append("")

    kw = task.lower().split()
    lines.append(f"Suggested tests: pytest tests/ -k \"{kw[0] if kw else 'codemap'}\"")
    lines.append("")
    lines.append("Note: Static analysis only. Some dynamic dependencies may be missed.")
    return "\n".join(lines)
