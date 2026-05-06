"""CodemapState — the central index for SAGE CodeMap.

Receives operations (dicts) via ``apply()``, indexes them, and exposes
declarative query methods for impact analysis, route discovery, and
dependency traversal.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from sage.domains.codemap.code_ops import (
    CALLS_FUNCTION,
    CALLS_METHOD,
    DEFINE_API_ENDPOINT,
    DEFINE_CLASS,
    DEFINE_COMPONENT,
    DEFINE_CONFIG,
    DEFINE_ENUM,
    DEFINE_EVENT,
    DEFINE_FILE,
    DEFINE_FUNCTION,
    DEFINE_INTERFACE,
    DEFINE_JOB,
    DEFINE_METHOD,
    DEFINE_MIDDLEWARE,
    DEFINE_MODEL,
    DEFINE_MODULE,
    DEFINE_PACKAGE,
    DEFINE_POLICY,
    DEFINE_ROUTE,
    DEFINE_SERVICE,
    DEFINE_STRUCT,
    DEFINE_TABLE,
    DEFINE_TRAIT,
    IMPORTS_SYMBOL,
    EXPORTS_SYMBOL,
    READS_TABLE,
    REQUIRES_FILE,
    ROUTE_TO_HANDLER,
    USES_CLASS,
    USES_CONFIG,
    USES_ENV,
    USES_FUNCTION,
    USES_SERVICE,
    WRITES_TABLE,
)

# Ops that "define" something (their presence creates a symbol)
_DEFINE_OPS = frozenset({
    DEFINE_FILE, DEFINE_MODULE, DEFINE_CLASS, DEFINE_FUNCTION,
    DEFINE_METHOD, DEFINE_COMPONENT, DEFINE_ROUTE, DEFINE_API_ENDPOINT,
    DEFINE_MODEL, DEFINE_SERVICE, DEFINE_JOB, DEFINE_EVENT,
    DEFINE_MIDDLEWARE, DEFINE_POLICY, DEFINE_CONFIG, DEFINE_PACKAGE,
    DEFINE_TABLE, DEFINE_STRUCT, DEFINE_ENUM, DEFINE_TRAIT, DEFINE_INTERFACE,
})

# Ops that represent a "read" on a table
_READ_TABLE_OPS = frozenset({READS_TABLE})

# Ops that represent a "write" on a table
_WRITE_TABLE_OPS = frozenset({WRITES_TABLE})

# Ops that signal a relationship edge
_EDGE_OPS = frozenset({
    CALLS_FUNCTION, CALLS_METHOD, IMPORTS_SYMBOL, EXPORTS_SYMBOL,
    USES_CLASS, USES_FUNCTION, USES_SERVICE, USES_CONFIG, USES_ENV,
    REQUIRES_FILE, ROUTE_TO_HANDLER,
})


class CodemapState:
    """Mutable index of every operation applied to the codemap."""

    def __init__(self) -> None:
        self._ops: list[dict[str, Any]] = []

        # file → list of op dicts
        self._files: dict[str, list[dict[str, Any]]] = defaultdict(list)

        # symbol name → list of op dicts that define it
        self._symbols: dict[str, list[dict[str, Any]]] = defaultdict(list)

        # route/endpoint detail
        self._routes: list[dict[str, Any]] = []
        self._endpoints: list[dict[str, Any]] = []

        # tables accessed: {table_name: [op dicts]}
        self._table_reads: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._table_writes: dict[str, list[dict[str, Any]]] = defaultdict(list)

        # services
        self._services: list[dict[str, Any]] = []

        # relationship edges: list of (source_op, target_op, rel_type)
        self._edges: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def apply(self, op: dict[str, Any]) -> None:
        """Apply a single operation to the index."""
        self._ops.append(op)
        op_type = op.get("op", "")
        file = op.get("file", "")

        # File index
        if file:
            self._files[file].append(op)

        # Symbol index
        if op_type in _DEFINE_OPS:
            name = op.get("name") or op.get("path") or op.get("kind")
            if name:
                self._symbols[name].append(op)

        # Routes / Endpoints
        if op_type == DEFINE_ROUTE:
            self._routes.append(op)
        if op_type == DEFINE_API_ENDPOINT:
            self._endpoints.append(op)

        # Tables
        if op_type in _READ_TABLE_OPS:
            table = op.get("table") or op.get("name", "")
            if table:
                self._table_reads[table].append(op)
        if op_type in _WRITE_TABLE_OPS:
            table = op.get("table") or op.get("name", "")
            if table:
                self._table_writes[table].append(op)

        # Services
        if op_type == DEFINE_SERVICE:
            self._services.append(op)

        # Edges
        if op_type in _EDGE_OPS:
            target = op.get("target") or op.get("name") or op.get("symbol") or ""
            self._edges.append({
                "source_file": file,
                "op": op_type,
                "target": target,
                "detail": {k: v for k, v in op.items() if k not in ("op", "file")},
            })

    def bulk_apply(self, ops: list[dict[str, Any]]) -> None:
        """Apply a list of operations."""
        for op in ops:
            self.apply(op)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def find_writers(self, table: str) -> list[dict[str, Any]]:
        """Return all ops that write to *table*."""
        return list(self._table_writes.get(table, []))

    def find_readers(self, table: str) -> list[dict[str, Any]]:
        """Return all ops that read from *table*."""
        return list(self._table_reads.get(table, []))

    def find_usages(self, symbol: str) -> list[dict[str, Any]]:
        """Return every op that references *symbol* (edges targeting it)."""
        results: list[dict[str, Any]] = []
        for edge in self._edges:
            if edge.get("target") == symbol:
                results.append(edge)
        return results

    def find_endpoints(self) -> list[dict[str, Any]]:
        """Return all API endpoint ops."""
        return list(self._endpoints)

    def find_routes(self) -> list[dict[str, Any]]:
        """Return all route ops."""
        return list(self._routes)

    def impact_for_file(self, file: str) -> dict[str, Any]:
        """Compute an impact report for *file*.

        Returns a dict with:
          - defines   : symbols defined by this file
          - reads     : tables read
          - writes    : tables written
          - calls     : functions/services called
          - used_by   : files that depend on this file (edges targeting this file's symbols)
          - depends_on: files this file references
        """
        file_ops = self._files.get(file, [])
        symbols_defined = [
            op.get("name") or op.get("path") or op.get("kind")
            for op in file_ops if op.get("op") in _DEFINE_OPS
        ]
        symbols_defined = [s for s in symbols_defined if s]

        tables_read: list[str] = []
        tables_written: list[str] = []
        calls: list[str] = []

        for op in file_ops:
            ot = op.get("op", "")
            if ot == READS_TABLE:
                t = op.get("table") or op.get("name", "")
                if t:
                    tables_read.append(t)
            elif ot == WRITES_TABLE:
                t = op.get("table") or op.get("name", "")
                if t:
                    tables_written.append(t)
            elif ot in (CALLS_FUNCTION, CALLS_METHOD, USES_FUNCTION, USES_SERVICE):
                t = op.get("target") or op.get("name") or op.get("symbol", "")
                if t:
                    calls.append(t)

        # Who uses us? Any edge that targets one of our defined symbols
        used_by: set[str] = set()
        for sym in symbols_defined:
            for edge in self._edges:
                if edge.get("target") == sym and edge.get("source_file") != file:
                    used_by.add(edge["source_file"])

        # Who do we depend on? Any edge we emit
        depends_on: set[str] = set()
        for edge in self._edges:
            if edge.get("source_file") == file:
                tgt_file = edge.get("detail", {}).get("file") or ""
                if tgt_file:
                    depends_on.add(tgt_file)

        return {
            "file": file,
            "defines": list(dict.fromkeys(symbols_defined)),
            "reads": list(dict.fromkeys(tables_read)),
            "writes": list(dict.fromkeys(tables_written)),
            "calls": list(dict.fromkeys(calls)),
            "used_by": sorted(used_by),
            "depends_on": sorted(depends_on),
        }

    def dependencies_of(self, file: str) -> list[dict[str, Any]]:
        """Return ops in files that *file* depends on (edges emitted by *file*)."""
        results: list[dict[str, Any]] = []
        seen: set[int] = set()
        for i, edge in enumerate(self._edges):
            if edge.get("source_file") == file and i not in seen:
                results.append(edge)
                seen.add(i)
        return results

    def dependents_of(self, file: str) -> list[dict[str, Any]]:
        """Return edges from other files that target symbols defined in *file*."""
        symbols_defined = {
            op.get("name") or op.get("path") or op.get("kind")
            for op in self._files.get(file, [])
            if op.get("op") in _DEFINE_OPS
        }
        results: list[dict[str, Any]] = []
        seen: set[int] = set()
        for i, edge in enumerate(self._edges):
            if edge.get("target") in symbols_defined and i not in seen:
                results.append(edge)
                seen.add(i)
        return results

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full state to a plain dict (JSON-safe)."""
        return {
            "ops_count": len(self._ops),
            "files": dict(self._files),
            "symbols": dict(self._symbols),
            "routes": self._routes,
            "endpoints": self._endpoints,
            "table_reads": dict(self._table_reads),
            "table_writes": dict(self._table_writes),
            "services": self._services,
            "edges": self._edges,
        }
