"""Rust parser for SAGE CodeMap.

Produces evidence-bound operations for .rs source files:
mod declarations, use imports, functions, structs, enums,
impl blocks, trait definitions, and pub visibility.
"""

from __future__ import annotations
import re
from pathlib import Path

# ── Regex patterns ──
# mod foo; or pub mod foo;
MOD_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?mod\s+(\w+)\s*[;{]'
)

# use crate::foo::bar / use std::collections::HashMap
USE_RE = re.compile(
    r'use\s+([\w:]+)(?:::\{([^}]+)\})?(?:\s+as\s+(\w+))?\s*;'
)

# fn function_name
FN_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+(?:\"[^\"]*\")\s+)?fn\s+(\w+)\s*[<(]'
)

# struct Foo / pub struct Foo
STRUCT_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?struct\s+(\w+)'
)

# enum Foo / pub enum Foo
ENUM_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?enum\s+(\w+)'
)

# impl Foo / impl Trait for Foo
IMPL_RE = re.compile(
    r'impl(?:\s*<\w+>)?\s+([\w:]+)(?:\s+for\s+([\w:]+))?'
)

# trait Foo / pub trait Foo
TRAIT_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?(?:unsafe\s+)?trait\s+(\w+)'
)

# type Foo = Bar;
TYPE_ALIAS_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?type\s+(\w+)'
)

# const / static
CONST_RE = re.compile(
    r'(?:pub(?:\s*\(\s*(?:crate|super|self)\s*\))?\s+)?(?:const|static\s+(?:mut\s+)?)\s+(\w+)'
)

# macro_rules!
MACRO_RE = re.compile(
    r'macro_rules!\s+(\w+)'
)

# #[derive(...)]
DERIVE_RE = re.compile(
    r'#\[derive\s*\(([^)]+)\)\]'
)

# #[test]
TEST_ATTR_RE = re.compile(
    r'#\[test\]'
)

# #[cfg(test)] / #[cfg(feature = "...")]
CFG_ATTR_RE = re.compile(
    r'#\[cfg\s*\(([^)]+)\)\]'
)

# Visibility detection helper
PUB_RE = re.compile(r'\bpub\b')


def parse_rust_file(file_path: str | Path) -> list[dict]:
    """Parse a Rust file into evidence-bound code operations."""
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    lines = text.split("\n")
    ops: list[dict] = []
    relative = str(file_path)

    def _emit(op: str, name: str, line: int, span: str, **extra) -> None:
        ops.append({
            "op": op,
            "name": name,
            "language": "rust",
            "file": relative,
            "line": line,
            "evidence": {
                "file": relative,
                "line": line,
                "span": span[:120],
                "confidence": 1.0,
                "parser": "rust_parser",
            },
            **extra,
        })

    pending_attrs: list[str] = []

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if not stripped:
            continue

        # ── Attribute accumulation ──
        if stripped.startswith("#[") and stripped.endswith("]"):
            pending_attrs.append(stripped)
            continue

        if stripped.startswith("#!["):
            if "feature" in stripped:
                m = re.search(r'feature\s*\(\s*([^)]+)\s*\)', stripped)
                if m:
                    _emit("DEFINE_CONFIG", f"feature: {m.group(1).strip()}", lineno, raw.strip())
            pending_attrs = []
            continue

        # ── mod ──
        m = MOD_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            op_type = "DEFINE_MODULE"
            _emit(op_type, m.group(1), lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            pending_attrs = []
            continue

        # ── use ──
        m = USE_RE.search(raw)
        if m:
            path = m.group(1)
            items = m.group(2)
            alias = m.group(3)
            if items:
                # use crate::foo::{Bar, Baz}
                for item in items.split(","):
                    item = item.strip()
                    if not item:
                        continue
                    if " as " in item:
                        item = item.split(" as ")[1].strip()
                    _emit("IMPORTS_SYMBOL", item, lineno, raw.strip())
            elif alias:
                _emit("IMPORTS_SYMBOL", alias, lineno, raw.strip())
            else:
                # import the last segment of the path
                leaf = path.split("::")[-1]
                _emit("IMPORTS_SYMBOL", leaf, lineno, raw.strip())
            pending_attrs = []
            continue

        # ── trait ──
        m = TRAIT_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            _emit("DEFINE_TRAIT", m.group(1), lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            pending_attrs = []
            continue

        # ── impl ──
        m = IMPL_RE.search(raw)
        if m:
            target = m.group(2) if m.group(2) else m.group(1)
            is_trait_impl = bool(m.group(2))
            _emit("DEFINE_MODULE" if is_trait_impl else "DEFINE_CLASS",
                  f"impl {target}",
                  lineno, raw.strip())
            pending_attrs = []
            continue

        # ── struct ──
        m = STRUCT_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            _emit("DEFINE_STRUCT", m.group(1), lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            # Check for derive
            if pending_attrs:
                for attr in pending_attrs:
                    dm = DERIVE_RE.search(attr)
                    if dm:
                        _emit("DEFINE_CONFIG", f"#[derive({dm.group(1)})]",
                              lineno, raw.strip())
            pending_attrs = []
            continue

        # ── enum ──
        m = ENUM_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            _emit("DEFINE_ENUM", m.group(1), lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            if pending_attrs:
                for attr in pending_attrs:
                    dm = DERIVE_RE.search(attr)
                    if dm:
                        _emit("DEFINE_CONFIG", f"#[derive({dm.group(1)})]",
                              lineno, raw.strip())
            pending_attrs = []
            continue

        # ── fn ──
        m = FN_RE.search(raw)
        if m:
            fn_name = m.group(1)
            is_pub = bool(PUB_RE.search(raw))
            is_test = any("test" in a for a in pending_attrs)

            if is_test or fn_name.startswith("test_"):
                _emit("TESTS_TARGET", fn_name, lineno, raw.strip())
            else:
                _emit("DEFINE_FUNCTION", fn_name, lineno, raw.strip(),
                      visibility="public" if is_pub else "private")
            pending_attrs = []
            continue

        # ── type alias ──
        m = TYPE_ALIAS_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            _emit("DEFINE_CONFIG", f"type {m.group(1)}", lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            pending_attrs = []
            continue

        # ── const / static ──
        m = CONST_RE.search(raw)
        if m:
            is_pub = bool(PUB_RE.search(raw))
            _emit("DEFINE_CONFIG", m.group(1), lineno, raw.strip(),
                  visibility="public" if is_pub else "private")
            pending_attrs = []
            continue

        # ── macro_rules! ──
        m = MACRO_RE.search(raw)
        if m:
            _emit("DEFINE_FUNCTION", f"{m.group(1)}!", lineno, raw.strip())
            pending_attrs = []
            continue

        pending_attrs = []

    return ops
