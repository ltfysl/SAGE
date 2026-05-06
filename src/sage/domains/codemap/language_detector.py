"""Map file extensions to languages."""

import os
from typing import Optional

# Primary extension → language mapping.
EXT_TO_LANG: dict[str, str] = {
    ".php": "PHP",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".py": "Python",
    ".rs": "Rust",
    ".vue": "Vue",
    ".json": "JSON",
    ".sql": "SQL",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".md": "Markdown",
    ".env.example": "Env",
}


def detect_language(file_path: str) -> str:
    """Return the language string for a single file path.

    Handles special filename cases (.env.example) and falls back to
    extension-based lookup.
    """
    fname = os.path.basename(file_path)

    # Special-case .env.example (exact match).
    if fname == ".env.example":
        return "Env"

    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    return EXT_TO_LANG.get(ext, "Unknown")


def detect_languages(files: list[dict]) -> set[str]:
    """Return the set of languages present across a list of file metadata.

    Each dict in *files* must have a "language" key (as produced by
    `project_scanner.scan_project`).
    """
    langs: set[str] = set()
    for f in files:
        lang = f.get("language")
        if lang:
            langs.add(lang)
    return langs
