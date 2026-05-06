"""Parse any text file for basic symbols using regex.

Kept intentionally generic — no framework-specific heuristics.
"""

import re
from typing import Optional

# ── Compiled patterns ────────────────────────────────────────────────

_RE_IMPORT = re.compile(
    r"""
    ^[\t ]*
    (?:
        # ES / TS: import X from 'Y'  |  import { X } from 'Y'  |  import 'Y'
        import[ \t]+
        (?:
            (?:type[ \t]+)?                            # import type (TS)
            (?:
                (?:\{[^}]*\})[ \t]*from[ \t]*['"][^'"]+['"]  # import { X } from 'Y'
                |
                ([\w.*,{} \t]+?)[ \t]*from[ \t]*['"][^'"]+['"]  # import X from 'Y'
                |
                ['"][^'"]+['"]                            # import 'Y' (side-effect)
                |
                ([\w.*,{} \t]+)                           # bare import X (no from)
            )
        )
        |
        # from X import Y  (Python)
        from[ \t]+\S+[ \t]+import[ \t]+([\w.*,{} \t]+)
        |
        # require('X') / require("X")
        (?:const|let|var)[ \t]+\w+[ \t]*=[ \t]*require[ \t]*\([ \t]*['"]([^'"]+)['"][ \t]*\)
        |
        # PHP use
        use[ \t]+([\w\\]+)[ \t]*;
        |
        # PHP include / require
        (?:include|include_once|require|require_once)[ \t]*['"]([^'"]+)['"]
        |
        # C include
        \#include[ \t]*["<]([^">]+)[">]
    )
    """,
    re.VERBOSE | re.MULTILINE,
)

_RE_FUNC = re.compile(
    r"""
    ^[\t ]*
    (?:
        (?:async\s+)?function\s+(\w+)        # function / async function (JS/TS)
        |fn\s+(\w+)                           # fn (Rust)
        |def\s+(\w+)                          # def (Python)
    )
    \s*\(
    """,
    re.VERBOSE | re.MULTILINE,
)

_RE_CLASS = re.compile(
    r"""
    ^[\t ]*
    (?:
        class\s+(\w+)                         # class
        |struct\s+(\w+)                       # struct
        |enum\s+(\w+)                         # enum
        |trait\s+(\w+)                        # trait
        |interface\s+(\w+)                    # interface
    )
    """,
    re.VERBOSE | re.MULTILINE,
)

_RE_EXPORT = re.compile(
    r"""
    (?:
        ^[\t ]*export\s+default\s+(?:class\s+|function\s+)?(\w+)      # export default X
        |^[\t ]*export\s+(?:const|let|var|function|class)\s+(\w+)     # export const/function/class X
        |^[\t ]*module\.exports\s*=\s*(\w+)                           # module.exports = X
    )
    """,
    re.VERBOSE | re.MULTILINE,
)

_RE_CALL = re.compile(
    r"""
    ([\w.]+)\s*\(
    """,
    re.VERBOSE,
)

_RE_CONFIG = re.compile(
    r"""
    (?:
        process\.env\.(\w+)               # process.env.X
        |env\(\s*['"]([^'"]+)['"]        # env('X')
        |config\(\s*['"]([^'"]+)['"]     # config('X')
        |\$_ENV\[['"]([^'"]+)['"]        # $_ENV['X']
    )
    """,
    re.VERBOSE,
)

# Lines that are obviously comments, definitions, or punctuation — skip call detection.
_SKIP_CALL_LINE = re.compile(
    r"^\s*("
    r"//|#|/\*|\*|<!--|-->"          # comments
    r"|import\s|from\s|export\s"      # import / export lines
    r"|def\s|fn\s|function\s|async\s" # function definitions
    r"|class\s|struct\s|enum\s|trait\s|interface\s|module\.exports"  # type definitions
    r")"
)

# Minimum call name length to reduce noise.
_MIN_CALL_LEN = 2

# Known keywords that look like calls but aren't.
_CALL_BLACKLIST: set[str] = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "throw",
    "typeof",
    "instanceof",
    "new",
    "delete",
    "void",
    "yield",
    "await",
    "else",
    "try",
    "finally",
    "case",
    "default",
    "break",
    "continue",
    "do",
    "in",
    "of",
    "not",
    "and",
    "or",
    "is",
    "print",
    "echo",
}


# ── Public API ───────────────────────────────────────────────────────

def parse_symbols(
    path: str,
    content: Optional[str] = None,
    *,
    max_lines: Optional[int] = None,
) -> list[dict]:
    """Parse a text file and return a flat list of symbol dicts.

    Each dict:
        op       – symbol kind ("import", "function", "class", "export", "call", "config")
        name     – extracted name / identifier
        line     – 1-based line number
        evidence – { "file": path, "line": N, "span": [start, end] }
    """
    if content is None:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            return []

    lines = content.splitlines()
    symbols: list[dict] = []

    # ── Imports ──────────────────────────────────────────────────
    for m in _RE_IMPORT.finditer(content):
        name = next((g for g in m.groups() if g is not None), "")
        line_no = content[: m.start()].count("\n") + 1
        symbols.append(
            {
                "op": "import",
                "name": name.strip(),
                "line": line_no,
                "evidence": {
                    "file": path,
                    "line": line_no,
                    "span": [m.start(), m.end()],
                },
            }
        )

    # ── Functions ────────────────────────────────────────────────
    for m in _RE_FUNC.finditer(content):
        name = next((g for g in m.groups() if g is not None), "")
        line_no = content[: m.start()].count("\n") + 1
        symbols.append(
            {
                "op": "function",
                "name": name,
                "line": line_no,
                "evidence": {
                    "file": path,
                    "line": line_no,
                    "span": [m.start(), m.end()],
                },
            }
        )

    # ── Classes ──────────────────────────────────────────────────
    for m in _RE_CLASS.finditer(content):
        name = next((g for g in m.groups() if g is not None), "")
        line_no = content[: m.start()].count("\n") + 1
        symbols.append(
            {
                "op": "class",
                "name": name,
                "line": line_no,
                "evidence": {
                    "file": path,
                    "line": line_no,
                    "span": [m.start(), m.end()],
                },
            }
        )

    # ── Exports ──────────────────────────────────────────────────
    for m in _RE_EXPORT.finditer(content):
        name = next((g for g in m.groups() if g is not None), "")
        line_no = content[: m.start()].count("\n") + 1
        symbols.append(
            {
                "op": "export",
                "name": name,
                "line": line_no,
                "evidence": {
                    "file": path,
                    "line": line_no,
                    "span": [m.start(), m.end()],
                },
            }
        )

    # ── Obvious function calls ───────────────────────────────────
    for lineno, raw_line in enumerate(lines, start=1):
        if max_lines is not None and lineno > max_lines:
            break
        if _SKIP_CALL_LINE.match(raw_line):
            continue
        for cm in _RE_CALL.finditer(raw_line):
            call_name = cm.group(1)
            # Skip blacklisted keywords and very short names.
            if call_name in _CALL_BLACKLIST or len(call_name) < _MIN_CALL_LEN:
                continue
            # Skip if the match is inside a string literal (rough heuristic).
            col = cm.start()
            prefix = raw_line[:col]
            if prefix.count('"') % 2 != 0 or prefix.count("'") % 2 != 0:
                continue
            symbols.append(
                {
                    "op": "call",
                    "name": call_name,
                    "line": lineno,
                    "evidence": {
                        "file": path,
                        "line": lineno,
                        "span": [cm.start(), cm.end()],
                    },
                }
            )

    # ── Config references ────────────────────────────────────────
    for m in _RE_CONFIG.finditer(content):
        name = next((g for g in m.groups() if g is not None), "")
        line_no = content[: m.start()].count("\n") + 1
        symbols.append(
            {
                "op": "config",
                "name": name,
                "line": line_no,
                "evidence": {
                    "file": path,
                    "line": line_no,
                    "span": [m.start(), m.end()],
                },
            }
        )

    return symbols
