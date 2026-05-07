"""SAGE CodeMap Cursor Integration — generates .cursor context and rule files."""

from __future__ import annotations
from pathlib import Path
from datetime import datetime


def generate_cursor_context(
    project_path: str | Path,
    task: str,
    map_path: str | Path | None = None,
    max_results: int = 20,
    force_scan: bool = False,
    write_rule: bool = True,
    output: str = ".cursor/sage-context.md",
) -> dict:
    """Generate .cursor/sage-context.md and optional .cursor/rules/sage-codemap.mdc.

    Returns dict with paths and status.
    """
    project_path = Path(project_path).resolve()
    if not project_path.is_dir():
        raise ValueError(f"Project path does not exist or is not a directory: {project_path}")

    # Determine codemap path
    if map_path:
        codemap_path = Path(map_path)
        if not codemap_path.exists():
            raise ValueError(f"Codemap not found: {codemap_path}")
    else:
        # Auto-generate or reuse
        safe_name = project_path.name.replace(" ", "_").replace("/", "_")
        codemap_path = Path("data/codemaps") / f"{safe_name}_codemap.json"

        if force_scan or not codemap_path.exists():
            from sage.domains.codemap.codemap_scan import run_codemap_scan
            run_codemap_scan(project_path, codemap_path)

    # Generate context
    from sage.domains.codemap.codemap_context import generate_context
    context = generate_context(str(codemap_path), task, max_results=max_results, format="markdown")

    # Build Cursor-friendly context file
    cursor_md = _build_cursor_md(task, context, project_path, codemap_path)

    # Write context file
    cursor_dir = project_path / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    context_file = project_path / output
    context_file.write_text(cursor_md)

    # Write rule file
    rule_written = False
    if write_rule:
        rules_dir = project_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rule_file = rules_dir / "sage-codemap.mdc"
        rule_file.write_text(CURSOR_RULE_CONTENT)
        rule_written = True

    return {
        "project": str(project_path),
        "context_file": str(context_file),
        "rule_file": str(project_path / ".cursor" / "rules" / "sage-codemap.mdc") if rule_written else None,
        "codemap": str(codemap_path),
        "task": task,
    }


def _build_cursor_md(task: str, context: str, project_path: Path, codemap_path: Path) -> str:
    """Wrap the context pack in Cursor-specific instructions."""
    ts = datetime.now().isoformat()
    return f"""# SAGE CodeMap Context

## Task
{task}

## How Cursor Should Use This
- Treat this as evidence-backed architecture context.
- Start with the listed files.
- Follow the runtime flow if present.
- Do not modify unrelated files.
- Verify assumptions in code before editing.
- Run suggested tests.

{context}

---
**Generated**: {ts}
**Project**: {project_path}
**Codemap**: {codemap_path}
**Parser mode**: deterministic — static analysis only. Evidence-bound.
"""


CURSOR_RULE_CONTENT = """---
description: Use SAGE CodeMap context for evidence-backed coding tasks
alwaysApply: false
---

When .cursor/sage-context.md exists:
- Use it as project context.
- Prefer files listed in the SAGE context.
- Follow evidence references.
- Do not modify unrelated files.
- Do not invent architecture facts.
- Inspect referenced files before editing.
- Preserve framework conventions.
- Run suggested tests when possible.
- If the SAGE context is incomplete, state what is missing and inspect the code.
"""
