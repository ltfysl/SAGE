"""Laravel/PHP parser for SAGE CodeMap v0.6.

Produces evidence-bound operations for PHP source files:
namespaces, imports, classes, methods, routes, models, migrations,
controller injection, service detection, job dispatching,
event emitting, and DB operations.
"""

from __future__ import annotations
import re
from pathlib import Path

# ── Module-level model-to-table mapping (persists across files) ──
_model_table_map: dict[str, str] = {}
_current_class: str | None = None
_current_namespace: str | None = None


def _model_to_table(class_or_var: str) -> str:
    """Resolve a model class name or variable to a table name."""
    clean = class_or_var.lstrip("$")
    if clean in _model_table_map:
        return _model_table_map[clean]
    # Fall back to snake_case
    return re.sub(r"(?<!^)(?=[A-Z])", "_", clean).lower()


# ── Regex patterns ──
NAMESPACE_RE = re.compile(r"namespace\s+([\w\\]+)\s*;")
USE_RE = re.compile(r"use\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;")
USE_FUNCTION_RE = re.compile(r"use\s+function\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;")
USE_CONST_RE = re.compile(r"use\s+const\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;")
CLASS_RE = re.compile(r"(?:abstract\s+)?(?:final\s+)?class\s+(\w+)")
TRAIT_RE = re.compile(r"trait\s+(\w+)")
INTERFACE_RE = re.compile(r"interface\s+(\w+)")
METHOD_RE = re.compile(
    r"(?:public|protected|private)\s+(?:static\s+)?function\s+(\w+)\s*\("
)
CONSTRUCTOR_RE = re.compile(r"function\s+__construct\s*\(([^)]*)\)")
TYPE_HINT_RE = re.compile(r"(?:(\?)|(\w[\w\\]*))\s+\$(\w+)")
ROUTE_RE = re.compile(r"Route::(\w+)\(\s*['\"]([^'\"]+)['\"]")
ROUTE_CONTROLLER_RE = re.compile(r"([\w\\]+Controller)::class")
EXTENDS_MODEL_RE = re.compile(r"extends\s+Model\b")
TABLE_PROP_RE = re.compile(r"\$table\s*=\s*['\"]([^'\"]+)['\"]")
FILLABLE_RE = re.compile(r"\$fillable\s*=\s*\[([^\]]*)\]")
CASTS_RE = re.compile(r"\$casts\s*=\s*\[([^\]]*)\]")
RELATION_RE = re.compile(
    r"function\s+(\w+)\s*\([^)]*\)\s*\{?\s*\$this->(hasMany|belongsTo|hasOne|belongsToMany)\("
)
SCHEMA_CREATE_RE = re.compile(r"Schema::create\(\s*['\"]([^'\"]+)['\"]")
SCHEMA_TABLE_RE = re.compile(r"Schema::table\(\s*['\"]([^'\"]+)['\"]")
COLUMN_RE = re.compile(r"\$table->(\w+)\(\s*['\"](\w+)['\"]")
DB_READ_RE = re.compile(
    r"DB::table\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->\s*(get|first|find|pluck)"
)
DB_WRITE_RE = re.compile(
    r"DB::table\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->\s*(insert|update|delete|upsert)"
)
# v0.6: broader DB::table detection – captures any method after ->table(...)
DB_TABLE_RE = re.compile(r"DB::table\(\s*['\"]([^'\"]+)['\"]\s*\)\s*->\s*(\w+)")
MODEL_CREATE_RE = re.compile(r"(\w+)::create\(")
MODEL_UPDATE_RE = re.compile(r"(\w+)::(?:updateOrCreate|update)\(")
MODEL_DELETE_RE = re.compile(r"(\$\w+)->delete\(")
CONSTRUCTOR_INJECTION_RE = re.compile(r'__construct\s*\(([^)]*)\)')
SERVICE_METHOD_CALL_RE = re.compile(r'\->(\w+)->(\w+)\(')
DISPATCH_CLASS_RE = re.compile(r'(\w+)::dispatch\(')
EVENT_NEW_RE = re.compile(r'event\(new\s+(\w+)')
MODEL_SAVE_RE = re.compile(r"(\$\w+)->save\(")
# v0.6: dispatch patterns
DISPATCH_NEW_RE = re.compile(r"dispatch\(\s*new\s+(\w+)")
DISPATCH_STATIC_RE = re.compile(r"(\w+)::dispatch\(")
EVENT_RE = re.compile(r"event\(\s*new\s+(\w+)")
# v0.6: constructor injection detection
CONSTRUCTOR_INJECTION_RE = re.compile(r"function\s+__construct\s*\(([^)]*)\)")
# v0.6: $this->serviceVar->method()
SERVICE_METHOD_CALL_RE = re.compile(r"\$this->(\w+)->(\w+)\(")

# ── Write-classification methods (for DB_TABLE_RE fallback) ──
_WRITE_METHODS = frozenset({
    "insert", "update", "delete", "upsert", "truncate", "increment",
    "decrement", "updateOrInsert", "insertOrIgnore", "insertGetId",
})
_READ_METHODS = frozenset({
    "get", "first", "find", "pluck", "value", "count", "exists",
    "doesntExist", "paginate", "chunk", "cursor",
})


def _classify_table_op(method: str) -> str | None:
    """Return 'WRITES_TABLE', 'READS_TABLE', or None for a given DB method."""
    if method in _WRITE_METHODS:
        return "WRITES_TABLE"
    if method in _READ_METHODS:
        return "READS_TABLE"
    return None


def parse_php_file(file_path: str | Path) -> list[dict]:
    """Parse a PHP file into evidence-bound code operations."""
    global _current_class, _current_namespace

    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    lines = text.split("\n")
    ops: list[dict] = []
    relative = str(file_path)

    # Reset per-file class tracking
    _current_class = None
    _current_namespace = None

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
            _current_namespace = m.group(1)
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
            _current_class = class_name
            op_type = "DEFINE_CLASS"

            # Model detection
            if EXTENDS_MODEL_RE.search(raw):
                op_type = "DEFINE_MODEL"
            # v0.6: Service detection (class name ends with "Service")
            elif class_name.endswith("Service"):
                op_type = "DEFINE_SERVICE"

            _emit(op_type, class_name, lineno, raw.strip())
            continue

        # ── Methods ──
        m = METHOD_RE.search(raw)
        if m:
            _emit("DEFINE_METHOD", m.group(1), lineno, raw.strip())
            continue

        # ── v0.6: Constructor injection ──
        m = CONSTRUCTOR_INJECTION_RE.search(raw)
        if m:
            params = m.group(1)
            if params.strip():
                for tm in TYPE_HINT_RE.finditer(params):
                    type_name = tm.group(2)
                    param_name = tm.group(3)
                    if type_name:
                        # If type-hinted type is a Service, emit CONTROLLER_USES_SERVICE
                        if type_name.endswith("Service"):
                            _emit("CONTROLLER_USES_SERVICE", type_name, lineno, raw.strip())
                        # Always emit the constructor param as DEFINE_FUNCTION
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
            table_name = m.group(1)
            _emit("MODEL_USES_TABLE", table_name, lineno, raw.strip())
            # v0.6: populate model-to-table mapping
            if _current_class:
                _model_table_map[_current_class] = table_name
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

        # ── v0.6: $this->serviceVar->method() calls ──
        m = SERVICE_METHOD_CALL_RE.search(raw)
        if m:
            var_name = m.group(1)
            method_name = m.group(2)
            _emit("CALLS_METHOD", f"$this->{var_name}->{method_name}()", lineno, raw.strip())
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

        # ── v0.6: Broader DB::table detection (any method) ──
        m = DB_TABLE_RE.search(raw)
        if m:
            table = m.group(1)
            method = m.group(2)
            op_type = _classify_table_op(method)
            if op_type:
                _emit(op_type, table, lineno, raw.strip())
            continue

        # ── Constructor injection detection ──
        m = CONSTRUCTOR_INJECTION_RE.search(raw)
        if m:
            params = m.group(1)
            for cls in re.findall(r'(\w+Service|\w+Repository)\s+\$', params):
                _emit("CONTROLLER_USES_SERVICE", cls, lineno, raw.strip())
            for cls in re.findall(r'(?:private|protected|public)\s+(\w+Service|\w+Repository)\s+\$', params):
                _emit("CONTROLLER_USES_SERVICE", cls, lineno, raw.strip())

        # ── ->service->method() calls ──
        m = SERVICE_METHOD_CALL_RE.search(raw)
        if m:
            _emit("CALLS_METHOD", f"{m.group(1)}->{m.group(2)}()", lineno, raw.strip())

        # ── Job dispatch ──
        m = DISPATCH_CLASS_RE.search(raw)
        if m:
            _emit("DISPATCHES_JOB", m.group(1), lineno, raw.strip())

        # ── Event dispatch ──
        m = EVENT_NEW_RE.search(raw)
        if m:
            _emit("EMITS_EVENT", m.group(1), lineno, raw.strip())

        # ── Model create/firstOrCreate ──
        m = MODEL_CREATE_RE.search(raw)
        if m and m.group(1)[0].isupper():
            model = m.group(1)
            _emit("CALLS_METHOD", f"{model}::create()", lineno, raw.strip())
            table = _model_to_table(model)
            _emit("WRITES_TABLE", table, lineno, raw.strip())
            # v0.6: also emit SERVICE_USES_MODEL
            _emit("SERVICE_USES_MODEL", model, lineno, raw.strip())
            continue

        # ── Model update/updateOrCreate/firstOrCreate ──
        m = MODEL_UPDATE_RE.search(raw)
        if m and m.group(1)[0].isupper():
            model = m.group(1)
            _emit("CALLS_METHOD", f"{model}::update()", lineno, raw.strip())
            table = _model_to_table(model)
            _emit("WRITES_TABLE", table, lineno, raw.strip())
            _emit("SERVICE_USES_MODEL", model, lineno, raw.strip())
            continue

        # ── Model query/where/find/all → READS_TABLE ──
        m = re.search(r'(\w+)::(?:query|where|find|all)\s*\(', raw)
        if m and m.group(1)[0].isupper():
            model = m.group(1)
            table = _model_to_table(model)
            _emit("READS_TABLE", table, lineno, raw.strip())
        m = re.search(r'(\w+)::where\([^)]+\)\s*->\s*update\s*\(', raw)
        if m and m.group(1)[0].isupper():
            model = m.group(1)
            table = _model_to_table(model)
            _emit("WRITES_TABLE", table, lineno, raw.strip())

        # ── $model->save() / $model->delete() ──
        m = MODEL_SAVE_RE.search(raw)
        if m:
            var = m.group(1)
            _emit("CALLS_METHOD", f"{var}->save()", lineno, raw.strip())
            table = _model_to_table(var)
            _emit("WRITES_TABLE", table, lineno, raw.strip())
        m = MODEL_DELETE_RE.search(raw)
        if m:
            var = m.group(1)
            _emit("CALLS_METHOD", f"{var}->delete()", lineno, raw.strip())
            table = _model_to_table(var)
            _emit("WRITES_TABLE", table, lineno, raw.strip())
            continue

        # ── Job dispatching (dispatch(new X)) ──
        m = DISPATCH_NEW_RE.search(raw)
        if m:
            _emit("DISPATCHES_JOB", m.group(1).strip(), lineno, raw.strip())
            continue
        # ── Job dispatching (X::dispatch()) ──
        m = DISPATCH_STATIC_RE.search(raw)
        if m:
            _emit("DISPATCHES_JOB", m.group(1), lineno, raw.strip())
            continue

        # ── Event emitting ──
        m = EVENT_RE.search(raw)
        if m:
            _emit("EMITS_EVENT", m.group(1).strip(), lineno, raw.strip())
            continue

    return ops


# ── Public API ──
def get_model_table_map() -> dict[str, str]:
    """Return the accumulated model→table mapping (for inspection)."""
    return dict(_model_table_map)


def clear_model_table_map() -> None:
    """Reset the model→table mapping."""
    global _model_table_map
    _model_table_map.clear()
