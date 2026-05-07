"""SAGE CodeMap scan — full pipeline: scan → detect → parse → build state → save."""
from __future__ import annotations
import json
from pathlib import Path
from sage.domains.codemap.project_scanner import scan_project
from sage.domains.codemap.language_detector import detect_languages
from sage.domains.codemap.framework_detector import detect_frameworks
from sage.domains.codemap.generic_symbol_parser import parse_symbols
from sage.domains.codemap.config_parser import parse_all as parse_configs
from sage.domains.codemap.codemap_engine import CodemapState


def run_codemap_scan(project_path: str | Path, output_path: str | Path = None, include_samples: bool = False) -> dict:
    """Run a full codemap scan on a project directory."""
    project_path = Path(project_path).resolve()

    files = scan_project(project_path, include_samples=include_samples)
    languages = detect_languages(files)
    frameworks = detect_frameworks(str(project_path))

    all_ops = []
    for f in files:
        file_path = project_path / f["path"]
        try:
            content = file_path.read_text(errors="replace")
        except Exception:
            continue

        ext = f["ext"].lower()

        # Generic parse for all files
        try:
            generic_ops = parse_symbols(str(file_path), content, f["language"])
            all_ops.extend(generic_ops)
        except Exception:
            pass

        # Language-specific parse
        try:
            if ext in (".php",):
                from sage.domains.codemap.php_parser import parse_php_file
                all_ops.extend(parse_php_file(str(file_path)))
            elif ext in (".js", ".jsx", ".ts", ".tsx", ".vue"):
                from sage.domains.codemap.js_ts_parser import parse_js_ts_file
                all_ops.extend(parse_js_ts_file(str(file_path)))
            elif ext in (".py",):
                from sage.domains.codemap.python_parser import parse_python_file
                all_ops.extend(parse_python_file(str(file_path)))
            elif ext in (".rs",):
                from sage.domains.codemap.rust_parser import parse_rust_file
                all_ops.extend(parse_rust_file(str(file_path)))
        except Exception:
            pass

    # Config files
    config_ops = parse_configs(str(project_path))
    all_ops.extend(config_ops)

    # Build dependency graph from operations
    from sage.domains.codemap.graph_builder import build_graph_from_ops
    graph = build_graph_from_ops(all_ops)

    # Build state
    state = CodemapState()
    for op in all_ops:
        state.apply(op)

    result = state.to_dict()
    result["graph"] = graph
    result["languages"] = sorted(languages)
    result["frameworks"] = sorted(frameworks)
    result["project_root"] = str(project_path)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    return result


def load_codemap(map_path: str | Path) -> dict:
    with open(map_path) as f:
        return json.load(f)
