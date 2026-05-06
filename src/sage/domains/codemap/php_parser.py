"""Laravel/PHP parser for SAGE CodeMap.

Produces evidence-bound operations for PHP source files:
namespaces, imports, classes, methods, routes, models, migrations,
job dispatching, event emitting, and DB operations.
"""

from __future__ import annotations
import re
from pathlib import Path

# ── Regex patterns ──
NAMESPACE_RE = re.compile(r'namespace\s+([\w\\]+)\s*;')
USE_RE = re.compile(r'use\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;')
USE_FUNCTION_RE = re.compile(r'use\s+function\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;')
USE_CONST_RE = re.compile(r'use\s+const\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;')
CLASS_RE = re.compile(r'(?:abstract\s+)?(?:final\s+)?class\s+(\w+)')
TRAIT_RE = re.compile(r'trait\s+(\w+)')
INTERFACE_RE = re.compile(r'interface\s+(\w+)')
METHOD_RE = re.compile(r'(?:public|protected|private)\s+(?:static\s+)?function\s+(\w+)\s*\(')
CONSTRUCTOR_RE = re.compile(
    r'function\s+__construct\s*\(([^)]*)\)',
)
TYPE_HINT_RE = re.compile(r'(?:(\?)|(\w[\w\\]*))\s+\$(\w+)')
ROUTE_RE = re.compile(r"Route::(\w+)\(\s*['\"]([^'\"]+)['\"]")
ROUTE_CONTROLLER_RE = re.compile(r"([\w\\]+Controller)::class")
EXTENDS_MODEL_RE = re.compile(r'extends\s+Model\b')
TABLE_PROP_RE = re.compile(r'\$table\s*=\s*[\'"]([^\'\"]+)[\'\"]')
FILLABLE_RE = re.compile(r'\$fillable\s*=\s*\[([^\]]*)\]')
CASTS_RE = re.compile(r'\$casts\s*=\s*\[([^\]]*)\]')
RELATION_RE = re.compile(
    r'function\s+(\w+)\s*\([^)]*\)\s*\{?\s*\$this->(hasMany|belongsTo|hasOne|belongsToMany)\('
)
SCHEMA_CREATE_RE = re.compile(r"Schema::create\(\s*['\"]([^'\"]+)['\"]")
SCHEMA_TABLE_RE = re.compile(r"Schema::table\(\s*['\"]([^'\"]+)['\"]")
COLUMN_RE = re.compile(
    r'\$table->(\w+)\(\s*[\'"](\w+)[\'"]'
)
DB_READ_RE = re.compile(r"DB::table\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->\s*(get|first|find|pluck)")
DB_WRITE_RE = re.compile(
    r"DB::table\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->\s*(insert|update|delete|upsert)"
)
MODEL_CREATE_RE = re.compile(r'(\w+)::create\(')
MODEL_UPDATE_RE = re.compile(r'(\w+)::(?:updateOrCreate|update)\(')
MODEL_SAVE_RE = re.compile(r'(\$\w+)->save\(')
DISPATCH_RE = re.compile(r'dispatch\(\s*new\s+([^(]+)')
DISPATCH_STATIC_RE = re.compile(r'(\w+)::dispatch\(')
EVENT_EMIT_RE = re.compile(r'event\(\s*new\s+([^(]+)')


def parse_php_file(file_path: str | Path) -> list[dict]:
    """Parse a PHP file into evidence-bound code operations."""
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    lines = text.split("\n")
    ops: list[dict] = []
    relative = str(file_path)

    def _emit(op: str, name: str, line: int, span: str, **extra) -> None:
        ops.append({
            "op": op,
            "name": name,
            "language": "php",
            "file": relative,
            "line": line,
            "evidence": {
                "file": relative,
                "line": line,
                "span": span[:120],
                "confidence": 1.0,
                "parser": "php_parser",
            },
            **extra,
        })

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("//") or stripped.startswith("#"):
            continue

        # ── Namespace ──
        m = NAMESPACE_RE.search(raw)
        if m:
            _emit("DEFINE_MODULE", m.group(1), lineno, raw.strip())
            continue

        # ── Use statements ──
        m = USE_FUNCTION_RE.search(raw)
        if m:
            name = m.group(2) if m.group(2) else m.group(1)
            _emit("IMPORTS_SYMBOL", name, lineno, raw.strip())
            continue
        m = USE_CONST_RE.search(raw)
        if m:
            name = m.group(2) if m.group(2) else m.group(1)
            _emit("IMPORTS_SYMBOL", name, lineno, raw.strip())
            continue
        m = USE_RE.search(raw)
        if m:
            name = m.group(2) if m.group(2) else m.group(1)
            _emit("IMPORTS_SYMBOL", name, lineno, raw.strip())
            continue

        # ── Trait ──
        m = TRAIT_RE.search(raw)
        if m:
            _emit("DEFINE_TRAIT", m.group(1), lineno, raw.strip())
            continue

        # ── Interface ──
        m = INTERFACE_RE.search(raw)
        if m:
            _emit("DEFINE_INTERFACE", m.group(1), lineno, raw.strip())
            continue

        # ── Class ──
        m = CLASS_RE.search(raw)
        if m:
            class_name = m.group(1)
            op_type = "DEFINE_CLASS"

            # Model detection
            if EXTENDS_MODEL_RE.search(raw):
                op_type = "DEFINE_MODEL"

            _emit(op_type, class_name, lineno, raw.strip())

            # Check for extends Model for model classes that may span lines
            # The simple case is single-line `class X extends Model`
            continue

        # ── Methods ──
        m = METHOD_RE.search(raw)
        if m:
            _emit("DEFINE_METHOD", m.group(1), lineno, raw.strip())
            continue

        # ── Constructor parameter injection ──
        m = CONSTRUCTOR_RE.search(raw)
        if m:
            params = m.group(1)
            if params.strip():
                # Extract type-hinted constructor params
                for tm in TYPE_HINT_RE.finditer(params):
                    param_name = tm.group(3)
                    _emit("DEFINE_FUNCTION", f"__construct(${param_name})", lineno, raw.strip())
            continue

        # ── Route definitions ──
        m = ROUTE_RE.search(raw)
        if m:
            verb = m.group(1)
            path_ = m.group(2)
            _emit("DEFINE_ROUTE", f"{verb.upper()} {path_}", lineno, raw.strip())
            continue

        # ── Controller::class references in routes ──
        m = ROUTE_CONTROLLER_RE.search(raw)
        if m:
            _emit("ROUTE_TO_HANDLER", m.group(1), lineno, raw.strip())
            continue

        # ── $table property ──
        m = TABLE_PROP_RE.search(raw)
        if m:
            _emit("MODEL_USES_TABLE", m.group(1), lineno, raw.strip())
            continue

        # ── $fillable ──
        m = FILLABLE_RE.search(raw)
        if m:
            _emit("DEFINE_CONFIG", "$fillable", lineno, raw.strip())
            continue

        # ── $casts ──
        m = CASTS_RE.search(raw)
        if m:
            _emit("DEFINE_CONFIG", "$casts", lineno, raw.strip())
            continue

        # ── Eloquent relationships ──
        m = RELATION_RE.search(raw)
        if m:
            rel_type = m.group(2)
            _emit("CALLS_METHOD", f"$this->{rel_type}()", lineno, raw.strip())
            continue

        # ── Schema::create ──
        m = SCHEMA_CREATE_RE.search(raw)
        if m:
            _emit("DEFINE_TABLE", m.group(1), lineno, raw.strip())
            continue

        # ── Schema::table ──
        m = SCHEMA_TABLE_RE.search(raw)
        if m:
            _emit("WRITES_TABLE", m.group(1), lineno, raw.strip())
            continue

        # ── Column definitions ──
        m = COLUMN_RE.search(raw)
        if m:
            _emit("DEFINE_COLUMN", m.group(2), lineno, raw.strip())
            continue

        # ── DB reads ──
        m = DB_READ_RE.search(raw)
        if m:
            _emit("READS_TABLE", m.group(1), lineno, raw.strip())
            continue

        # ── DB writes ──
        m = DB_WRITE_RE.search(raw)
        if m:
            _emit("WRITES_TABLE", m.group(1), lineno, raw.strip())
            continue

        # ── Model create ──
        m = MODEL_CREATE_RE.search(raw)
        if m and m.group(1)[0].isupper():
            _emit("CALLS_METHOD", f"{m.group(1)}::create()", lineno, raw.strip())
            _emit("WRITES_TABLE", m.group(1).lower(), lineno, raw.strip())
            continue

        # ── Model update/updateOrCreate ──
        m = MODEL_UPDATE_RE.search(raw)
        if m and m.group(1)[0].isupper():
            _emit("CALLS_METHOD", f"{m.group(1)}::update()", lineno, raw.strip())
            _emit("WRITES_TABLE", m.group(1).lower(), lineno, raw.strip())
            continue

        # ── $model->save() ──
        m = MODEL_SAVE_RE.search(raw)
        if m:
            _emit("CALLS_METHOD", f"{m.group(1)}->save()", lineno, raw.strip())
            _emit("WRITES_TABLE", m.group(1).lower(), lineno, raw.strip())
            continue

        # ── Job dispatching ──
        m = DISPATCH_RE.search(raw)
        if m:
            _emit("DISPATCHES_JOB", m.group(1).strip(), lineno, raw.strip())
            continue
        m = DISPATCH_STATIC_RE.search(raw)
        if m:
            _emit("DISPATCHES_JOB", m.group(1), lineno, raw.strip())
            continue

        # ── Event emitting ──
        m = EVENT_EMIT_RE.search(raw)
        if m:
            _emit("EMITS_EVENT", m.group(1).strip(), lineno, raw.strip())
            continue

    return ops
