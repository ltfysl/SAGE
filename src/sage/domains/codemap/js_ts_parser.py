"""JavaScript / TypeScript parser for SAGE CodeMap.

Produces evidence-bound operations for .js/.jsx/.ts/.tsx source files:
imports, exports, functions, classes, React/Vue components,
API calls, server directives, and environment variable usage.
"""

from __future__ import annotations
import re
from pathlib import Path

# ── Regex patterns ──
# import { X, Y } from "Z"
IMPORT_NAMED_RE = re.compile(
    r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]'
)
# import X from "Z"
IMPORT_DEFAULT_RE = re.compile(
    r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
)
# import * as X from "Z"
IMPORT_STAR_RE = re.compile(
    r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
)
# import "Z" (side-effect import)
IMPORT_BARE_RE = re.compile(
    r'import\s+[\'"]([^\'"]+)[\'"]'
)

# Exports
EXPORT_DEFAULT_FN_RE = re.compile(
    r'export\s+default\s+(?:async\s+)?function\s+(\w+)'
)
EXPORT_FN_RE = re.compile(
    r'export\s+(?:async\s+)?function\s+(\w+)'
)
EXPORT_CONST_RE = re.compile(
    r'export\s+const\s+(\w+)'
)
EXPORT_DEFAULT_CLASS_RE = re.compile(
    r'export\s+default\s+class\s+(\w+)'
)
EXPORT_CLASS_RE = re.compile(
    r'export\s+class\s+(\w+)'
)

# Function declarations
FUNCTION_DECL_RE = re.compile(
    r'(?:async\s+)?function\s+(\w+)'
)

# Arrow functions assigned to const
ARROW_FN_RE = re.compile(
    r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\('
)

# Class definitions (non-export)
CLASS_DECL_RE = re.compile(
    r'class\s+(\w+)'
)

# React/Vue component detection
JSX_RETURN_RE = re.compile(r'return\s*[\(\<]')
VUE_EXT_RE = re.compile(r'\.vue$')

# API calls
FETCH_RE = re.compile(r'fetch\(\s*[\'"]([^\'"]+)[\'"]')
AXIOS_GET_RE = re.compile(
    r'axios\.(get|post|put|patch|delete)\(\s*[\'"]([^\'"]+)[\'"]'
)

# "use server" directive
USE_SERVER_RE = re.compile(r'[\'"`]use\s+server[\'"`]')

# process.env.X
ENV_RE = re.compile(r'process\.env\.(\w+)')

# React component patterns (function component returning JSX)
REACT_COMPONENT_RE = re.compile(
    r'(?:export\s+(?:default\s+)?)?(?:function|const)\s+([A-Z]\w*)'
)

# Next.js route handlers
NEXT_ROUTE_RE = re.compile(
    r'export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)'
)



def _is_api_route(file_path, name: str) -> bool:
    """Check if this is a Next.js API route handler."""
    return (
        "app/api/" in str(file_path) or "pages/api/" in str(file_path)
    ) and name.upper() in ("GET", "POST", "PUT", "PATCH", "DELETE")

def _api_path(file_path) -> str:
    """Extract API path from file path."""
    import re
    m = re.search(r'(?:app|pages)/api/(.+?)(?:/route)?\.[jt]sx?$', str(file_path))
    if m:
        return "/api/" + m.group(1)
    return file_path
def parse_js_ts_file(file_path: str | Path) -> list[dict]:
    """Parse a JS/TS file into evidence-bound code operations."""
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    lines = text.split("\n")
    ops: list[dict] = []
    relative = str(file_path)

    # Detect language variant from extension
    ext = file_path.suffix.lower()
    lang_map = {".js": "javascript", ".jsx": "javascript",
                ".ts": "typescript", ".tsx": "typescript",
                ".mjs": "javascript", ".cjs": "javascript",
                ".mts": "typescript", ".cts": "typescript",
                ".vue": "vue"}
    language = lang_map.get(ext, "javascript")

    def _emit(op: str, name: str, line: int, span: str, **extra) -> None:
        ops.append({
            "op": op,
            "name": name,
            "language": language,
            "file": relative,
            "line": line,
            "evidence": {
                "file": relative,
                "line": line,
                "span": span[:120],
                "confidence": 1.0,
                "parser": "js_ts_parser",
            },
            **extra,
        })

    # Track whether current scope is a React component (heuristic)
    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if not stripped or stripped.startswith("//"):
            continue

        # ── Imports ──
        m = IMPORT_NAMED_RE.search(raw)
        if m:
            names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            for name in names:
                _emit("IMPORTS_SYMBOL", name, lineno, raw.strip())
            continue

        m = IMPORT_STAR_RE.search(raw)
        if m:
            _emit("IMPORTS_SYMBOL", m.group(1), lineno, raw.strip())
            continue

        m = IMPORT_DEFAULT_RE.search(raw)
        if m:
            _emit("IMPORTS_SYMBOL", m.group(1), lineno, raw.strip())
            continue

        m = IMPORT_BARE_RE.search(raw)
        if m:
            _emit("REQUIRES_FILE", m.group(1), lineno, raw.strip())
            continue

        # ── Exports ──
        m = EXPORT_DEFAULT_FN_RE.search(raw)
        if m:
            name = m.group(1)
            # Component detection: capitalized function name returning JSX
            _emit("EXPORTS_SYMBOL", name, lineno, raw.strip())
            if _is_component_line(raw, name):
                _emit("DEFINE_COMPONENT", name, lineno, raw.strip())
            else:
                _emit("DEFINE_FUNCTION", name, lineno, raw.strip())
            continue

        m = EXPORT_FN_RE.search(raw)
        if m:
            name = m.group(1)
            _emit("EXPORTS_SYMBOL", name, lineno, raw.strip())
            _emit("DEFINE_FUNCTION", name, lineno, raw.strip())
            # Next.js API route detection
            if _is_api_route(file_path, name):
                _emit("DEFINE_API_ENDPOINT", f"{name} {_api_path(file_path)}", lineno, raw.strip())
            continue

        m = EXPORT_CONST_RE.search(raw)
        if m:
            _emit("EXPORTS_SYMBOL", m.group(1), lineno, raw.strip())
            continue

        m = EXPORT_DEFAULT_CLASS_RE.search(raw)
        if m:
            _emit("EXPORTS_SYMBOL", m.group(1), lineno, raw.strip())
            _emit("DEFINE_CLASS", m.group(1), lineno, raw.strip())
            continue

        m = EXPORT_CLASS_RE.search(raw)
        if m:
            _emit("EXPORTS_SYMBOL", m.group(1), lineno, raw.strip())
            _emit("DEFINE_CLASS", m.group(1), lineno, raw.strip())
            continue

        # ── Function declarations ──
        m = FUNCTION_DECL_RE.search(raw)
        if m and not raw.strip().startswith("export"):
            name = m.group(1)
            if _is_component_line(raw, name):
                _emit("DEFINE_COMPONENT", name, lineno, raw.strip())
            else:
                _emit("DEFINE_FUNCTION", name, lineno, raw.strip())
            continue

        # ── Arrow function assignments ──
        m = ARROW_FN_RE.search(raw)
        if m and not raw.strip().startswith("export"):
            name = m.group(1)
            if _is_component_line(raw, name):
                _emit("DEFINE_COMPONENT", name, lineno, raw.strip())
            else:
                _emit("DEFINE_FUNCTION", name, lineno, raw.strip())
            continue

        # ── Class declarations ──
        m = CLASS_DECL_RE.search(raw)
        if m and "export" not in raw:
            _emit("DEFINE_CLASS", m.group(1), lineno, raw.strip())
            continue

        # ── Next.js route handlers ──
        m = NEXT_ROUTE_RE.search(raw)
        if m:
            _emit("DEFINE_ROUTE", f"{m.group(1)} (Next.js)", lineno, raw.strip())
            continue

        # ── API calls ──
        m = FETCH_RE.search(raw)
        if m:
            _emit("PAGE_USES_API", m.group(1), lineno, raw.strip())
            continue

        m = AXIOS_GET_RE.search(raw)
        if m:
            _emit("PAGE_USES_API", f"{m.group(1).upper()} {m.group(2)}", lineno, raw.strip())
            continue

        # ── "use server" ──
        m = USE_SERVER_RE.search(raw)
        if m:
            _emit("DEFINE_CONFIG", "use server", lineno, raw.strip())
            continue

        # ── process.env.X ──
        m = ENV_RE.search(raw)
        if m:
            _emit("USES_ENV", m.group(1), lineno, raw.strip())
            continue

    # ── Vue SFC detection ──
    if VUE_EXT_RE.search(relative):
        _emit("DEFINE_COMPONENT", file_path.stem, 1, lines[0].strip() if lines else "")

    return ops


def _is_component_line(line: str, name: str) -> bool:
    """Heuristic: does this look like a React/Vue component definition?"""
    # Components start with uppercase by convention
    if not name or not name[0].isupper():
        return False
    # Arrow functions with JSX-like returns
    if "<" in line or "JSX" in line:
        return True
    # function declaration with (props) or ({ ... })
    if re.search(r'\(\s*\{?\s*\}?\s*\)', line):
        return True
    # If it's a capitalized arrow function assigned to const, likely a component
    if re.match(r'(?:const|let|var)\s+[A-Z]', line):
        return True
    return False
