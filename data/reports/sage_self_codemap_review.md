# SAGE CodeMap Self-Analysis Review

## Scan Summary

| Metric | Value |
|--------|-------|
| Files scanned | 102 |
| Operations emitted | 1,193 |
| Languages detected | JSON, Markdown, PHP, Python, Rust, TOML, TypeScript, Unknown |
| Frameworks detected | (none — framework detector needs improvement) |
| Routes/endpoints | 8 (4 from sample codebases, 4 from Next.js app) |
| Unique symbols | 410 |

## Ask Outputs

### "What endpoints exist?"
Found 8 endpoints. 4 are from sample codebases (data/samples/codebases/) and 4 from the actual Next.js app (apps/sage-incident-lens-web). This is correct but mixes sample data with real project data.

### "Where is CodemapState used?"
**FAILED** — No definitions found. Root cause: symbol search is case-sensitive. `CodemapState` exists in codemap_engine.py but the query `codemapstate` (lowercased) doesn't match.

### "What files are involved in codemap?"
**FAILED** — The `_search` method only searches routes and symbols, not file paths or all operations. Needs full-text search across the entire codemap.

### "What files are involved in Incident Lens?"
**FAILED** — Same issue: search scope too narrow. Should find `src/sage/domains/logs/` files.

### Impact: codemap_engine.py
**FAILED** — "No files depend on this." The dependency graph (`build_graph()`) was never called during the scan pipeline. Edges array is empty.

## What Worked

1. **File scanning**: 102 files correctly scanned, ignoring node_modules, models, data/codemaps, .next ✓
2. **Language detection**: Correctly identified 7 languages ✓
3. **Operation counts**: 1,193 ops with reasonable distribution ✓
4. **Python imports**: 620 IMPORTS_SYMBOL ops — good Python import detection ✓
5. **Next.js API detection**: Correctly found 4 API endpoints in the Next.js app ✓
6. **Symbol index**: 410 unique symbols tracked ✓
7. **Evidence references**: All ops include file:line evidence ✓
8. **No false positives from ignored dirs**: Models, caches, private logs correctly excluded ✓

## Top 5 Improvements Needed for CodeMap v0.1

1. **Case-insensitive symbol search** — `_find_usages` must lowercase both query and symbol keys
2. **Full-text search in `_search`** — Search file paths, operation names, and messages, not just routes/symbols
3. **Wire dependency graph into scan pipeline** — Call `build_graph()` during `codemap_scan` and include edges in state
4. **Better framework detection** — Detect Python projects (setup.py/pyproject.toml), Next.js in subdirectories, multi-framework repos
5. **Separate sample/project scanning** — Sample codebases in `data/samples/codebases/` should either be excluded from self-scan or flagged separately from real project code
