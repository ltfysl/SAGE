"""Walk a project directory and yield file paths with metadata."""

import os
from pathlib import Path
from typing import Optional

from .language_detector import detect_language

IGNORED_DIRS: set[str] = {
    "node_modules",
    "vendor",
    ".git",
    "storage",
    "bootstrap/cache",
    "dist",
    "build",
    ".next",
    "target",
    "__pycache__",
    ".venv",
    "coverage",
    "data/private_logs",
    "data/reports",
    "models/hf_cache",
}


def _is_ignored(entry_path: str, root: str) -> bool:
    """Check whether a path should be skipped based on IGNORED_DIRS."""
    # Normalize separators.
    rel = entry_path.removeprefix(root).lstrip(os.sep).replace(os.sep, "/")
    if not rel:
        return False
    parts = Path(rel).parts
    # Check each prefix path segment
    for i in range(len(parts)):
        prefix = "/".join(parts[: i + 1])
        if prefix in IGNORED_DIRS:
            return True
    return False


def scan_project(
    root: str, *, max_files: Optional[int] = None, include_samples: bool = False
) -> list[dict]:
    """Walk *root* and return a list of file metadata dicts.

    Each dict has keys:
        path      – relative path from *root*
        ext       – file extension (lowercased, with dot, e.g. ".py")
        language  – detected language string (e.g. "Python")
        size_bytes – file size in bytes
    """
    root = os.path.abspath(root)
    results: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Prune ignored directories in-place so os.walk never descends.
        dirnames[:] = [
            d
            for d in dirnames
            if not _is_ignored(os.path.join(dirpath, d), root)
            and d not in IGNORED_DIRS  # simple name match for top-level
        ]

        # Also skip the current directory if it matches an ignored path.
        if _is_ignored(dirpath, root):
            continue

        for fname in filenames:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root)
            _, ext = os.path.splitext(fname)
            ext = ext.lower()

            try:
                size = os.path.getsize(full)
            except OSError:
                size = 0

            results.append(
                {
                    "path": rel,
                    "ext": ext,
                    "language": detect_language(fname),
                    "size_bytes": size,
                }
            )

            if max_files is not None and len(results) >= max_files:
                return results

    return results
