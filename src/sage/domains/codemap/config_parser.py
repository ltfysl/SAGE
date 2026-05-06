"""Parse configuration files into SAGE CodeMap operations.

Supported config files:
  - composer.json, package.json, pyproject.toml, Cargo.toml
  - requirements.txt
  - docker-compose.yml
  - .env.example
  - vite.config.*, next.config.*, tsconfig.json (presence detection)
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from sage.domains.codemap.code_ops import (
    DEFINE_CONFIG,
    DEFINE_PACKAGE,
    DEFINE_SERVICE,
    USES_ENV,
)


def parse_all(root: str) -> list[dict[str, Any]]:
    """Parse all recognised config files under *root* and return a flat list of ops."""
    ops: list[dict[str, Any]] = []
    for entry in os.scandir(root):
        if not entry.is_file():
            continue
        name = entry.name.lower()
        path = entry.path

        if name == "composer.json":
            ops.extend(_parse_composer(path))
        elif name == "package.json":
            ops.extend(_parse_package(path))
        elif name == "pyproject.toml":
            ops.extend(_parse_pyproject(path))
        elif name == "requirements.txt":
            ops.extend(_parse_requirements(path))
        elif name == "cargo.toml":
            ops.extend(_parse_cargo(path))
        elif name == "docker-compose.yml" or name == "docker-compose.yaml":
            ops.extend(_parse_docker_compose(path))
        elif name == ".env.example":
            ops.extend(_parse_env_example(path))
        elif name.startswith("vite.config"):
            ops.extend(_make_config_op(path, "vite"))
        elif name.startswith("next.config"):
            ops.extend(_make_config_op(path, "next"))
        elif name == "tsconfig.json":
            ops.extend(_make_config_op(path, "typescript"))
    return ops


# ---------------------------------------------------------------------------
# Per-file helpers
# ---------------------------------------------------------------------------

def _make_config_op(path: str, kind: str) -> list[dict[str, Any]]:
    rel = _rel_path(path, os.path.dirname(path))
    return [
        {
            "op": DEFINE_CONFIG,
            "file": rel,
            "kind": kind,
            "path": rel,
        }
    ]


def _parse_composer(path: str) -> list[dict[str, Any]]:
    data = _read_json(path)
    if not data:
        return []
    root_dir = os.path.dirname(path)
    ops: list[dict[str, Any]] = []
    file = _rel_path(path, root_dir)

    for name, version in data.get("require", {}).items():
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "prod"})
    for name, version in data.get("require-dev", {}).items():
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "dev"})
    for name, _meta in data.get("autoload", {}).get("psr-4", {}).items():
        ops.append({"op": DEFINE_CONFIG, "file": file, "kind": "autoload", "namespace": name.rstrip("\\"), "value": _meta})
    for name, _meta in data.get("autoload-dev", {}).get("psr-4", {}).items():
        ops.append({"op": DEFINE_CONFIG, "file": file, "kind": "autoload-dev", "namespace": name.rstrip("\\"), "value": _meta})
    for script_name, _cmd in data.get("scripts", {}).items():
        ops.append({"op": DEFINE_CONFIG, "file": file, "kind": "script", "name": script_name, "command": _cmd})
    return ops


def _parse_package(path: str) -> list[dict[str, Any]]:
    data = _read_json(path)
    if not data:
        return []
    root_dir = os.path.dirname(path)
    ops: list[dict[str, Any]] = []
    file = _rel_path(path, root_dir)

    for name, version in data.get("dependencies", {}).items():
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "prod"})
    for name, version in data.get("devDependencies", {}).items():
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "dev"})
    for script_name, _cmd in data.get("scripts", {}).items():
        ops.append({"op": DEFINE_CONFIG, "file": file, "kind": "script", "name": script_name, "command": _cmd})
    return ops


def _parse_pyproject(path: str) -> list[dict[str, Any]]:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return []
    root_dir = os.path.dirname(path)
    ops: list[dict[str, Any]] = []
    file = _rel_path(path, root_dir)

    deps = data.get("project", {}).get("dependencies", [])
    for dep in deps:
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": dep, "version": None, "scope": "prod"})
    opt_deps = data.get("project", {}).get("optional-dependencies", {})
    for group, pkgs in opt_deps.items():
        for pkg in pkgs:
            ops.append({"op": DEFINE_PACKAGE, "file": file, "name": pkg, "version": None, "scope": f"optional:{group}"})
    return ops


def _parse_requirements(path: str) -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = []
    root_dir = os.path.dirname(path)
    file = _rel_path(path, root_dir)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ops.append({"op": DEFINE_PACKAGE, "file": file, "name": line, "version": None, "scope": "prod"})
    except Exception:
        pass
    return ops


def _parse_cargo(path: str) -> list[dict[str, Any]]:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return []
    root_dir = os.path.dirname(path)
    ops: list[dict[str, Any]] = []
    file = _rel_path(path, root_dir)

    for name, _meta in data.get("dependencies", {}).items():
        version = _meta if isinstance(_meta, str) else _meta.get("version")
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "prod"})
    for name, _meta in data.get("dev-dependencies", {}).items():
        version = _meta if isinstance(_meta, str) else _meta.get("version")
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "dev"})
    for name, _meta in data.get("build-dependencies", {}).items():
        version = _meta if isinstance(_meta, str) else _meta.get("version")
        ops.append({"op": DEFINE_PACKAGE, "file": file, "name": name, "version": version, "scope": "build"})
    return ops


def _parse_docker_compose(path: str) -> list[dict[str, Any]]:
    try:
        import yaml
    except ImportError:
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception:
        return []
    if not data:
        return []
    root_dir = os.path.dirname(path)
    ops: list[dict[str, Any]] = []
    file = _rel_path(path, root_dir)

    services = data.get("services", {})
    for svc_name, svc in services.items():
        op: dict[str, Any] = {"op": DEFINE_SERVICE, "file": file, "name": svc_name}
        if isinstance(svc.get("ports"), list):
            op["ports"] = svc["ports"]
        if isinstance(svc.get("depends_on"), list):
            op["depends_on"] = svc["depends_on"]
        if isinstance(svc.get("environment"), dict):
            op["environment"] = list(svc["environment"].keys())
        elif isinstance(svc.get("environment"), list):
            env_keys = []
            for item in svc["environment"]:
                if isinstance(item, str):
                    env_keys.append(item.split("=", 1)[0])
                elif isinstance(item, dict):
                    env_keys.extend(item.keys())
            op["environment"] = env_keys
        if isinstance(svc.get("image"), str):
            op["image"] = svc["image"]
        if isinstance(svc.get("build"), (str, dict)):
            op["build"] = svc["build"] if isinstance(svc["build"], str) else svc["build"].get("context")
        ops.append(op)

        # Emit USES_ENV for each environment variable
        for key in op.get("environment", []):
            ops.append({"op": USES_ENV, "file": file, "key": key, "service": svc_name})

    return ops


def _parse_env_example(path: str) -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = []
    root_dir = os.path.dirname(path)
    file = _rel_path(path, root_dir)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key = line.split("=", 1)[0].strip()
                if key:
                    ops.append({"op": USES_ENV, "file": file, "key": key})
    except Exception:
        pass
    return ops


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_json(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _rel_path(path: str, base: str) -> str:
    """Return *path* relative to *base* (which is usually the dirname)."""
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(base)
    return os.path.relpath(abs_path, abs_base)
