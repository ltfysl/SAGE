"""Python parser for SAGE CodeMap.

Produces evidence-bound operations for .py source files:
imports, functions, classes, FastAPI routes, Django URL patterns,
Celery tasks, and Django model detection.
"""

from __future__ import annotations
import re
from pathlib import Path

# ── Regex patterns ──
# import X / import X, Y
IMPORT_MODULE_RE = re.compile(
    r'^import\s+([\w.]+)(?:\s+as\s+(\w+))?'
)
# from X import Y
FROM_IMPORT_RE = re.compile(
    r'^from\s+([\w.]+)\s+import\s+(.+)$'
)

# Function definition
FUNC_DEF_RE = re.compile(
    r'(?:async\s+)?def\s+(\w+)\s*\('
)

# Class definition
CLASS_DEF_RE = re.compile(
    r'class\s+(\w+)\s*(?:\(([^)]*)\))?'
)

# FastAPI route decorators
FASTAPI_ROUTE_RE = re.compile(
    r'@(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]*)[\'"]'
)

# Django URL patterns
DJANGO_PATH_RE = re.compile(
    r'(?:path|re_path)\s*\(\s*[\'"]([^\'"]*)[\'"]'
)
DJANGO_URL_NAME_RE = re.compile(
    r'name\s*=\s*[\'"]([^\'"]+)[\'"]'
)

# Celery task decorators
CELERY_TASK_RE = re.compile(
    r'@(?:app|shared)_task\b'
)

# Django Model detection
DJANGO_MODEL_RE = re.compile(
    r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\)'
)

# Serializer / DRF detection
DRF_SERIALIZER_RE = re.compile(
    r'class\s+(\w+)\s*\([^)]*serializers\.\w*Serializer[^)]*\)'
)

# pytest test detection
PYTEST_FUNC_RE = re.compile(
    r'(?:async\s+)?def\s+(test_\w+)\s*\('
)
PYTEST_CLASS_RE = re.compile(
    r'class\s+(Test\w+)\s*'
)

# FastAPI app/router creation
FASTAPI_APP_RE = re.compile(
    r'(\w+)\s*=\s*(?:FastAPI|APIRouter)\s*\('
)

# Pydantic model
PYDANTIC_MODEL_RE = re.compile(
    r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\)'
)

# SQLAlchemy model
SQLA_MODEL_RE = re.compile(
    r'class\s+(\w+)\s*\([^)]*Base[^)]*\)'
)

# Flask route decorator
FLASK_ROUTE_RE = re.compile(
    r'@(\w+)\.route\s*\(\s*[\'"]([^\'"]*)[\'"]'
)

# Django include
DJANGO_INCLUDE_RE = re.compile(
    r'include\s*\(\s*[\'"]([^\'"]+)[\'"]'
)


def parse_python_file(file_path: str | Path) -> list[dict]:
    """Parse a Python file into evidence-bound code operations."""
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    lines = text.split("\n")
    ops: list[dict] = []
    relative = str(file_path)

    def _emit(op: str, name: str, line: int, span: str, **extra) -> None:
        ops.append({
            "op": op,
            "name": name,
            "language": "python",
            "file": relative,
            "line": line,
            "evidence": {
                "file": relative,
                "line": line,
                "span": span[:120],
                "confidence": 1.0,
                "parser": "python_parser",
            },
            **extra,
        })

    pending_decorator: str | None = None

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            continue

        # ── Imports ──
        m = FROM_IMPORT_RE.match(stripped)
        if m:
            module = m.group(1)
            imports = m.group(2)
            # Extract individual symbols
            symbols = _split_import_list(imports)
            for sym in symbols:
                _emit("IMPORTS_SYMBOL", sym, lineno, raw.strip())
            continue

        m = IMPORT_MODULE_RE.match(stripped)
        if m:
            alias = m.group(2) if m.group(2) else m.group(1)
            _emit("IMPORTS_SYMBOL", alias, lineno, raw.strip())
            continue

        # ── Decorator tracking ──
        if stripped.startswith("@"):
            pending_decorator = stripped
            continue

        # ── Function definitions ──
        m = FUNC_DEF_RE.search(stripped)
        if m:
            func_name = m.group(1)
            if pending_decorator:
                if "app." in pending_decorator or "router." in pending_decorator:
                    # FastAPI/Flask route
                    route_match = FASTAPI_ROUTE_RE.search(pending_decorator)
                    if route_match:
                        _emit("DEFINE_ROUTE",
                              f"{route_match.group(1).upper()} {route_match.group(2)}",
                              lineno, raw.strip())
                    else:
                        route_match = FLASK_ROUTE_RE.search(pending_decorator)
                        if route_match:
                            _emit("DEFINE_ROUTE",
                                  f"FLASK {route_match.group(2)}",
                                  lineno, raw.strip())
                elif "task" in pending_decorator:
                    _emit("DEFINE_JOB", func_name, lineno, raw.strip())
                elif "property" in pending_decorator:
                    _emit("DEFINE_METHOD", func_name, lineno, raw.strip())
                elif "staticmethod" in pending_decorator or "classmethod" in pending_decorator:
                    _emit("DEFINE_METHOD", func_name, lineno, raw.strip())

            # Detect pytest tests
            if func_name.startswith("test_"):
                _emit("TESTS_TARGET", func_name, lineno, raw.strip())
            else:
                _emit("DEFINE_FUNCTION", func_name, lineno, raw.strip())

            pending_decorator = None
            continue

        # ── Class definitions ──
        m = CLASS_DEF_RE.search(stripped)
        if m:
            class_name = m.group(1)
            bases = m.group(2) or ""

            if "models.Model" in bases or (
                    "Model" in bases and "pydantic" not in bases.lower()):
                _emit("DEFINE_MODEL", class_name, lineno, raw.strip())
            elif "BaseModel" in bases:
                _emit("DEFINE_MODEL", class_name, lineno, raw.strip())
            elif "Serializer" in bases:
                _emit("DEFINE_CLASS", class_name, lineno, raw.strip())
            elif class_name.startswith("Test"):
                _emit("TESTS_TARGET", class_name, lineno, raw.strip())
            else:
                _emit("DEFINE_CLASS", class_name, lineno, raw.strip())

            pending_decorator = None
            continue

        # ── FastAPI app/router creation ──
        m = FASTAPI_APP_RE.search(stripped)
        if m:
            _emit("DEFINE_SERVICE", m.group(1), lineno, raw.strip())
            continue

        # ── Django path() / re_path() ──
        m = DJANGO_PATH_RE.search(stripped)
        if m:
            # Try to get the name= parameter from the same line
            name_match = DJANGO_URL_NAME_RE.search(stripped)
            route_name = name_match.group(1) if name_match else m.group(1)
            _emit("DEFINE_ROUTE", f"DJANGO {route_name}", lineno, raw.strip())
            continue

        # ── Django include ──
        m = DJANGO_INCLUDE_RE.search(stripped)
        if m:
            _emit("INCLUDES_FILE", m.group(1), lineno, raw.strip())
            continue

        pending_decorator = None

    return ops


def _split_import_list(imports_str: str) -> list[str]:
    """Split 'X, Y, Z as W' into individual symbols."""
    symbols = []
    # Handle parenthesized multiline (single-line with parens not likely at this point)
    for part in imports_str.split(","):
        part = part.strip()
        if not part:
            continue
        # Handle 'X as Y'
        if " as " in part:
            alias = part.split(" as ")[1].strip()
            symbols.append(alias)
        else:
            symbols.append(part)
    return symbols
