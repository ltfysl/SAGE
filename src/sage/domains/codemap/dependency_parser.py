"""Build a dependency graph from imports/uses across all source files.

For each file we track:
  - what it imports (external packages and internal project files)
  - what it exports (symbols defined and exported)
  - adjacency: file A imports from file B ⇒ A depends on B
"""
from __future__ import annotations

import ast
import os
import re
from collections import defaultdict
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_graph(file_paths: list[str], project_root: str = ".") -> dict[str, Any]:
    """Build a full dependency graph from *file_paths*.

    Returns a dict with keys:
      - graph           : adjacency dict {file: [files it depends on]}
      - imports_by_file : {file: [{"name": ..., "source": ..., "external": bool}]}
      - exports_by_file : {file: [symbol_name]}
      - imported_by     : {file: [files that import it]}
    """
    graph: dict[str, list[str]] = defaultdict(list)
    imports_by_file: dict[str, list[dict[str, Any]]] = {}
    exports_by_file: dict[str, list[str]] = {}
    imported_by: dict[str, list[str]] = defaultdict(list)

    # Build a resolver map: short module name → relative path
    module_map = _build_module_map(file_paths, project_root)

    for fpath in file_paths:
        rel = os.path.relpath(fpath, project_root)
        ext = os.path.splitext(fpath)[1].lower()

        if ext == ".py":
            imps, exps = _parse_python(fpath)
        elif ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
            imps, exps = _parse_javascript(fpath)
        elif ext == ".rs":
            imps, exps = _parse_rust(fpath)
        elif ext == ".php":
            imps, exps = _parse_php(fpath)
        elif ext in (".vue", ".svelte"):
            imps, exps = _parse_javascript(fpath)
        else:
            imps, exps = [], []

        imports_by_file[rel] = imps
        exports_by_file[rel] = exps

        for imp in imps:
            if imp.get("source") and not imp.get("external"):
                resolved = _resolve_import(imp["source"], rel, module_map)
                if resolved:
                    graph[rel].append(resolved)
                    imported_by[resolved].append(rel)

        # Deduplicate
        graph[rel] = list(dict.fromkeys(graph[rel]))

    # Ensure every file has an entry even if it has no imports
    for fpath in file_paths:
        rel = os.path.relpath(fpath, project_root)
        if rel not in graph:
            graph[rel] = []

    return {
        "graph": dict(graph),
        "imports_by_file": imports_by_file,
        "exports_by_file": exports_by_file,
        "imported_by": dict(imported_by),
    }


# ---------------------------------------------------------------------------
# Language-specific parsers
# ---------------------------------------------------------------------------

def _parse_python(path: str) -> tuple[list[dict[str, Any]], list[str]]:
    imports: list[dict[str, Any]] = []
    exports: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
    except SyntaxError:
        return imports, exports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                external = name not in _STDLIB
                imports.append({"name": alias.name, "source": name, "external": external})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split(".")[0]
                external = name not in _STDLIB
                for alias in node.names:
                    imports.append({"name": alias.name, "source": node.module, "external": external})

        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                exports.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                exports.append(node.name)
        elif isinstance(node, ast.Assign):
            if isinstance(node.targets, (list, tuple)) and hasattr(node, 'value'):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.isupper():
                        exports.append(t.id)
                    elif isinstance(t, ast.Name) and not t.id.startswith("_"):
                        pass  # variable assignments are not typically "exports"

    return imports, exports


def _parse_javascript(path: str) -> tuple[list[dict[str, Any]], list[str]]:
    imports: list[dict[str, Any]] = []
    exports: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except Exception:
        return imports, exports

    # ES import: import { ... } from '...'  /  import X from '...'
    import_re = re.compile(
        r'''(?:import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s*(?:,\s*(?:\{[^}]*\}|\w+))?\s+from\s+)?['"]([^'"]+)['"])'''
    )
    # Dynamic import: import('...')
    dynamic_re = re.compile(r'''import\s*\(\s*['"]([^'"]+)['"]\s*\)''')
    # require('...')
    require_re = re.compile(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)''')

    for pattern in (import_re, dynamic_re, require_re):
        for m in pattern.finditer(source):
            source_path = m.group(1)
            name = source_path.rstrip("/").split("/")[-1]
            external = not source_path.startswith(".") and not source_path.startswith("@/")\
                and not source_path.startswith("~/")
            imports.append({"name": name, "source": source_path, "external": external})

    # Named exports: export const/function/class/let/var NAME
    export_re = re.compile(
        r'''(?:export\s+(?:const|function|class|let|var|default\s+(?:function|class)?))\s+(\w+)''',
        re.MULTILINE,
    )
    for m in export_re.finditer(source):
        exports.append(m.group(1))

    return imports, exports


def _parse_rust(path: str) -> tuple[list[dict[str, Any]], list[str]]:
    imports: list[dict[str, Any]] = []
    exports: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except Exception:
        return imports, exports

    # use crate::... ; use super::... ; use <external>::...
    use_re = re.compile(r'''use\s+([\w:]+)''')
    for m in use_re.finditer(source):
        full_path = m.group(1)
        crate_name = full_path.split("::")[0]
        external = crate_name not in ("crate", "self", "super")
        imports.append({"name": full_path, "source": crate_name, "external": external})

    # pub fn / pub struct / pub enum / pub trait / pub mod
    pub_re = re.compile(r'''pub\s+(?:fn|struct|enum|trait|mod|const|type|static)\s+(\w+)''')
    for m in pub_re.finditer(source):
        exports.append(m.group(1))

    return imports, exports


def _parse_php(path: str) -> tuple[list[dict[str, Any]], list[str]]:
    imports: list[dict[str, Any]] = []
    exports: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except Exception:
        return imports, exports

    # use Namespace\Class;
    use_re = re.compile(r'''use\s+([\w\\]+)''')
    for m in use_re.finditer(source):
        full = m.group(1)
        parts = full.split("\\")
        name = parts[-1]
        external = not any(p in full.lower() for p in ("app", "tests"))
        imports.append({"name": name, "source": full, "external": external})

    # class / interface / trait / enum
    class_re = re.compile(r'''(?:class|interface|trait|enum)\s+(\w+)''')
    for m in class_re.finditer(source):
        exports.append(m.group(1))

    return imports, exports


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_module_map(file_paths: list[str], project_root: str) -> dict[str, str]:
    """Map short module names to relative file paths."""
    mp: dict[str, str] = {}
    for fpath in file_paths:
        rel = os.path.relpath(fpath, project_root)
        stem = os.path.splitext(rel)[0].replace(os.sep, ".")
        basename = os.path.splitext(os.path.basename(rel))[0]
        mp[basename] = rel
        mp[stem] = rel
    return mp


def _resolve_import(source: str, from_file: str, module_map: dict[str, str]) -> str | None:
    """Resolve an import source to a relative file path, if internal."""
    # Direct match
    if source in module_map:
        return module_map[source]
    # Try common transforms
    normalized = source.replace("/", ".").replace("\\", ".")
    if normalized in module_map:
        return module_map[normalized]

    # Try relative to from_file
    from_dir = os.path.dirname(from_file)
    candidate = os.path.normpath(os.path.join(from_dir, source))
    for v in module_map.values():
        if os.path.normpath(v) == candidate:
            return v
        if os.path.normpath(v) == candidate + ".py":
            return v
        if os.path.normpath(v) == candidate + "/__init__.py":
            return v

    return None


# Python stdlib modules (3.11+)
_STDLIB: set[str] = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio", "asyncore",
    "atexit", "audioop", "base64", "bdb", "binascii", "binhex", "bisect", "builtins",
    "bz2", "calendar", "cgi", "cgitb", "chunk", "cmath", "cmd", "code", "codecs",
    "codeop", "collections", "colorsys", "compileall", "concurrent", "configparser",
    "contextlib", "contextvars", "copy", "copyreg", "cProfile", "crypt", "csv",
    "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal", "difflib",
    "dis", "distutils", "doctest", "email", "encodings", "enum", "errno",
    "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "formatter",
    "fractions", "ftplib", "functools", "gc", "getopt", "getpass", "gettext",
    "glob", "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac", "html", "http",
    "idlelib", "imaplib", "imghdr", "imp", "importlib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "lib2to3", "linecache", "locale", "logging",
    "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
    "modulefinder", "multiprocessing", "netrc", "nis", "nntplib", "numbers",
    "operator", "optparse", "os", "ossaudiodev", "pathlib", "pdb", "pickle",
    "pickletools", "pipes", "pkgutil", "platform", "plistlib", "poplib", "posix",
    "posixpath", "pprint", "profile", "pstats", "pty", "pwd", "py_compile",
    "pyclbr", "pydoc", "queue", "quopri", "random", "re", "readline", "reprlib",
    "resource", "rlcompleter", "runpy", "sched", "secrets", "select", "selectors",
    "shelve", "shlex", "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr",
    "socket", "socketserver", "sqlite3", "ssl", "stat", "statistics", "string",
    "stringprep", "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig",
    "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test",
    "textwrap", "threading", "time", "timeit", "tkinter", "token", "tokenize",
    "tomllib", "trace", "traceback", "tracemalloc", "tty", "turtle", "turtledemo",
    "types", "typing", "unicodedata", "unittest", "urllib", "uu", "uuid", "venv",
    "warnings", "wave", "weakref", "webbrowser", "winreg", "winsound", "wsgiref",
    "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
    # Additional common modules
    "__future__", "__main__",
}
