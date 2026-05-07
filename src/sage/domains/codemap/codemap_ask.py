"""SAGE CodeMap ask — deterministic question answering using structured codemap."""
from __future__ import annotations
import re


class CodemapAsk:
    """Answer fixed-scope questions using codemap state."""

    def __init__(self, state: dict):
        self.state = state
        # Build case-insensitive symbol index once
        self._lower_index: dict[str, list[dict]] = {}
        for sym_name, ops in state.get("symbols", {}).items():
            key = sym_name.lower()
            if key not in self._lower_index:
                self._lower_index[key] = []
            self._lower_index[key].extend(ops)

    def ask(self, question: str) -> dict:
        q = question.lower().strip()

        # What files are involved in X?  → full-text search
        if "files involved in" in q or "files are involved" in q:
            return self._search_fulltext(question)

        # What writes to <table>?
        if "write" in q or "writes" in q:
            return self._find_writers(q)

        # What reads <table>?
        if "read" in q or "reads" in q:
            return self._find_readers(q)

        # What endpoints/routes exist?
        if "endpoint" in q or "route" in q:
            return self._find_endpoints()

        # Where is <symbol> used?
        if "where is" in q or "used" in q:
            return self._find_usages(q)

        # What services?
        if "service" in q:
            return self._find_services()

        # What tests?
        if "test" in q:
            return self._find_tests()

        # Impact of file?
        if "impact" in q:
            return self._find_impact(q)

        return self._search(q)

    def _find_writers(self, q: str) -> dict:
        table = self._extract_table(q)
        writes = self.state.get("table_writes", {})
        ops = writes.get(table, [])
        if not ops:
            # Fuzzy match: search all table names
            for t, o in writes.items():
                if table.replace('_', '') in t.replace('_', '') or t.replace('_', '') in table.replace('_', ''):
                    ops.extend(o)
        return {
            "text": f"Found {len(ops)} operation(s) writing to {table}." if ops else f"No writes to {table} found.",
            "evidence": ops[:15],
            "notes": "Static analysis only. Dynamic writes may be missed.",
            "table": table,
        }

    def _find_readers(self, q: str) -> dict:
        table = self._extract_table(q)
        reads = self.state.get("table_reads", {})
        ops = reads.get(table, [])
        return {
            "text": f"Found {len(ops)} operation(s) reading from {table}." if ops else f"No reads from {table} found.",
            "evidence": ops[:15],
            "notes": "Static analysis only.",
            "table": table,
        }

    def _find_endpoints(self) -> dict:
        routes = self.state.get("routes", [])
        endpoints = self.state.get("endpoints", [])
        all_eps = routes + endpoints
        return {
            "text": f"Found {len(all_eps)} endpoint(s)/route(s).",
            "evidence": all_eps[:20],
            "count": len(all_eps),
        }

    def _find_usages(self, q: str) -> dict:
        symbol = self._extract_symbol(q)
        # Case-insensitive lookup via _lower_index; preserve original names in output
        ops = self._lower_index.get(symbol.lower(), [])
        return {
            "text": f"Found {len(ops)} definition(s) of {symbol}." if ops else f"No definitions of {symbol} found.",
            "evidence": ops[:15],
            "symbol": symbol,
        }

    def _find_services(self) -> dict:
        services = self.state.get("services", [])
        return {
            "text": f"Found {len(services)} service-related operation(s).",
            "evidence": services[:15],
        }

    def _find_tests(self) -> dict:
        # Tests are files that test something
        files = self.state.get("files", {})
        test_files = {k: v for k, v in files.items() if "test" in k.lower() or "spec" in k.lower()}
        ops = []
        for v in test_files.values():
            ops.extend(v)
        return {
            "text": f"Found {len(test_files)} test file(s)." if test_files else "No test files found.",
            "evidence": ops[:15],
        }

    def _find_impact(self, q: str) -> dict:
        file = self._extract_file(q)
        files = self.state.get("files", {})
        # Find matching file
        matching = {k: v for k, v in files.items() if file in k}
        ops = []
        for v in matching.values():
            ops.extend(v)
        # Find edges referencing this file
        edges = self.state.get("edges", [])
        related = [e for e in edges if file in e.get("from_file", "") or file in e.get("to_file", "")]
        return {
            "text": f"Found {len(ops)} operation(s) and {len(related)} edge(s) related to {file}.",
            "evidence": ops[:15] + [{"file": e.get("from_file", ""), "op": e.get("type", ""), "name": e.get("to_file", "")} for e in related[:10]],
            "file": file,
        }

    def _search(self, q: str) -> dict:
        keyword = q.strip().strip('"').strip("'")
        # Search in all structured data
        matches = []
        for route in self.state.get("routes", []):
            if keyword.lower() in str(route).lower():
                matches.append(route)
        for k, ops in self.state.get("symbols", {}).items():
            if keyword.lower() in k.lower():
                matches.extend(ops)
        return {
            "text": f"Found {len(matches)} match(es) for '{keyword}'." if matches else f"No matches for '{keyword}'.",
            "evidence": matches[:15],
        }

    def _search_fulltext(self, query: str) -> dict:
        """Full-text search across file paths, symbols, and operations with scoring."""
        keywords = query.lower().split()
        results = []
        for file_path, ops in self.state.get("files", {}).items():
            score = 0
            matches = []
            fp_lower = file_path.lower()
            for kw in keywords:
                if kw in fp_lower:
                    score += 5
                    matches.append(f"path contains '{kw}'")
            # Symbol matches via _lower_index
            for sym_name in self._lower_index:
                for kw in keywords:
                    if kw in sym_name:
                        # Only score once per keyword per file for symbol matches
                        if any(sym_name in fp_lower or fp_lower in sym_name for fp_lower in [file_path.lower()]):
                            score += 3
                            matches.append(f"symbol match: {sym_name}")
                            break
            for op in ops:
                op_str = str(op).lower()
                for kw in keywords:
                    if kw in op_str:
                        score += 2
                        matches.append(f"op: {op.get('op','?')} {op.get('name','?')}")
            if score > 0:
                results.append({"file": file_path, "score": score, "matches": matches[:5], "ops_count": len(ops)})
        results.sort(key=lambda r: -r["score"])
        return {
            "text": f"Found {len(results)} files matching '{query}'.",
            "evidence": [{"name": r["file"], "op": f"score={r['score']}", "evidence": {"file": r["file"], "line": 0}} for r in results[:20]],
            "notes": "Full-text search across file paths, symbols, and operations.",
        }

    @staticmethod
    def _extract_table(q: str) -> str:
        m = re.search(r'(?:writes?\s+to|reads?\s+from|(?:in|of)\s+)(\w+)', q)
        if m: return m.group(1)
        m = re.search(r'(\w+)\?', q)
        if m: return m.group(1)
        m = re.search(r'(?:table|resource)\s+(\w+)', q)
        if m: return m.group(1)
        words = q.replace("?", "").split()
        return words[-1] if words else ""

    @staticmethod
    def _extract_symbol(q: str) -> str:
        m = re.search(r'(?:where is|where\'s|used by|usages of|usage of)\s+(\w+)', q)
        if m: return m.group(1)
        words = q.replace("?", "").split()
        return words[-1] if words else ""

    @staticmethod
    def _extract_file(q: str) -> str:
        m = re.search(r'(?:change|modify|update|impact)\s+(\S+)', q)
        if m: return m.group(1).rstrip("?")
        words = q.replace("?", "").split()
        return words[-1] if words else ""
