"""Detect frameworks from project root files."""

import json
import os
from pathlib import Path
from typing import Any


def _composer_has(path: str, package: str) -> bool:
    """Check if composer.json contains a require entry for *package*."""
    try:
        with open(path, encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    require = data.get("require", {})
    return package in require


def _package_has(path: str, dep: str) -> bool:
    """Check if package.json lists *dep* in dependencies or devDependencies."""
    try:
        with open(path, encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    return dep in deps or dep in dev_deps


def _any_file_has(path: str, needle: str) -> bool:
    """Return True if any line in *path* contains *needle*."""
    if not os.path.isfile(path):
        return False
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if needle in line:
                    return True
    except OSError:
        pass
    return False


def _file_exists(root: str, rel: str) -> bool:
    return os.path.isfile(os.path.join(root, rel))


def _dir_exists(root: str, rel: str) -> bool:
    return os.path.isdir(os.path.join(root, rel))


def _any_glob_match(root: str, pattern: str) -> bool:
    """True if any file/dir matches a simple glob (e.g. 'next.config.*')."""
    import glob

    matches = glob.glob(os.path.join(root, pattern))
    return len(matches) > 0


def detect_frameworks(root: str) -> list[str]:
    """Detect frameworks in root and immediate subdirectories."""
    import os
    frameworks = set()
    # Check root
    frameworks.update(_detect_at_path(root))
    # Check subdirectories up to 2 levels deep (for monorepos)
    try:
        for entry in os.listdir(root):
            sub = os.path.join(root, entry)
            if os.path.isdir(sub) and not entry.startswith('.') and entry not in ('node_modules', 'vendor', '__pycache__', 'data', 'models'):
                frameworks.update(_detect_at_path(sub))
                # Check one level deeper (e.g., apps/sage-incident-lens-web)
                try:
                    for sub_entry in os.listdir(sub):
                        sub2 = os.path.join(sub, sub_entry)
                        if os.path.isdir(sub2) and not sub_entry.startswith('.'):
                            frameworks.update(_detect_at_path(sub2))
                except OSError:
                    pass
    except OSError:
        pass
    return sorted(frameworks)

def _detect_at_path(root: str) -> list[str]:
    """Detect frameworks at a single path."""
    """Analyse *root* and return a deduplicated list of detected framework names.

    Supported frameworks:
        Laravel, Next.js, Vue, Express, FastAPI, Django, Rust (Cargo)
    """
    found: list[str] = []

    # ── Laravel ──────────────────────────────────────────────────────
    composer = os.path.join(root, "composer.json")
    artisan = os.path.join(root, "artisan")
    routes = os.path.join(root, "routes")

    if (
        _composer_has(composer, "laravel/framework")
        or (_file_exists(root, "artisan") and _dir_exists(root, "routes"))
    ):
        found.append("Laravel")

    # ── Next.js ──────────────────────────────────────────────────────
    pkg = os.path.join(root, "package.json")
    if _package_has(pkg, "next") or (
        (_dir_exists(root, "app") or _dir_exists(root, "pages"))
        and _any_glob_match(root, "next.config.*")
    ):
        found.append("Next.js")

    # ── Vue ──────────────────────────────────────────────────────────
    if _package_has(pkg, "vue"):
        found.append("Vue")
    else:
        # Fallback: check for .vue files at the top two levels.
        vue_files: list[str] = []
        try:
            for entry in os.scandir(root):
                if entry.is_file() and entry.name.endswith(".vue"):
                    vue_files.append(entry.name)
                elif entry.is_dir() and entry.name not in {
                    "node_modules", ".git", "__pycache__", ".venv", "dist",
                }:
                    for sub in os.scandir(entry.path):
                        if sub.is_file() and sub.name.endswith(".vue"):
                            vue_files.append(sub.name)
        except OSError:
            pass
        if vue_files:
            found.append("Vue")

    # ── Express ──────────────────────────────────────────────────────
    if _package_has(pkg, "express"):
        found.append("Express")

    # ── FastAPI ──────────────────────────────────────────────────────
    fastapi_found = False
    # Scan a few Python files in root and immediate subdirs.
    try:
        for entry in os.scandir(root):
            if not fastapi_found and entry.is_file() and entry.name.endswith(".py"):
                if _any_file_has(entry.path, "from fastapi import") or _any_file_has(
                    entry.path, "FastAPI()"
                ):
                    fastapi_found = True
    except OSError:
        pass
    if fastapi_found:
        found.append("FastAPI")

    # ── Django ───────────────────────────────────────────────────────
    manage = os.path.join(root, "manage.py")
    settings = os.path.join(root, "settings.py")
    urls = os.path.join(root, "urls.py")
    if (
        _file_exists(root, "manage.py")
        or _file_exists(root, "settings.py")
        or _file_exists(root, "urls.py")
    ):
        # Also check common subdir location
        found.append("Django")

    # ── Rust (Cargo) ─────────────────────────────────────────────────
    if _file_exists(root, "Cargo.toml"):
        found.append("Rust (Cargo)")

    return found
