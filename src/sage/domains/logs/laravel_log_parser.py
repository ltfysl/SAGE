"""Laravel log parser for SAGE Incident Lens.

Parses Laravel/PHP log files into structured log blocks.
Handles multiline stack traces, multiline messages, and [object] exception format.
"""

from __future__ import annotations
import re
from pathlib import Path


# Laravel log line pattern: [YYYY-MM-DD HH:MM:SS] environment.LEVEL: message
LOG_LINE_RE = re.compile(
    r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+'
    r'(\w+)\.(\w+):\s+(.*)'
)


def parse_log_file(file_path: str | Path) -> list[dict]:
    """Parse a Laravel log file into structured log blocks."""
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")
    blocks = []
    current_block = None

    for line in text.split("\n"):
        m = LOG_LINE_RE.match(line)
        if m:
            if current_block is not None:
                _finalize_block(current_block)
                blocks.append(current_block)

            timestamp, env, level, message = m.groups()
            current_block = {
                "timestamp": timestamp,
                "environment": env,
                "level": level.upper(),
                "message": message.strip(),
                "exception": None,
                "file": str(file_path),
                "line_number": 0,
                "raw_lines": [line],
                "start_char": 0,
                "end_char": len(line),
            }
        elif current_block is not None:
            current_block["raw_lines"].append(line)

    if current_block is not None:
        _finalize_block(current_block)
        blocks.append(current_block)

    _compute_offsets(blocks, text)
    return blocks


def _finalize_block(block: dict):
    """Extract exception, file, and line from a log block."""
    raw = "\n".join(block["raw_lines"])
    block["raw_block"] = raw

    # ── Exception extraction ──
    # Format 1: {"exception":"[object] (ClassName(code: N): message...)"}
    # Format 2: {"exception":"ClassName\\..."}  (simple JSON string)
    # Format 3: exception class embedded in the message itself

    exc_match = re.search(r'"exception":"([^"]*)"', raw)
    if exc_match:
        raw_exc = exc_match.group(1)
        # Strip [object] prefix and extract class name
        exc_class = _extract_exception_class(raw_exc)
        block["exception"] = exc_class
    else:
        # Look for exception class in the raw block
        exc_class = _extract_exception_class_from_raw(raw)
        block["exception"] = exc_class

    # ── File extraction from stacktrace ──
    file_match = re.search(r'#\d+\s+(/[^:(]+\.[a-z]+)', raw)
    if file_match:
        block["file"] = file_match.group(1)

    # ── Line number ──
    line_match = re.search(r'#\d+\s+/[^(]+\((\d+)\)', raw)
    if line_match:
        block["line_number"] = int(line_match.group(1))


def _extract_exception_class(raw_exc: str) -> str | None:
    """Extract exception class name from [object] (ClassName(...)) or simple string."""
    if not raw_exc:
        return None
    # Try [object] (ClassName(code: ...)) format
    m = re.match(r'\[object\]\s*\(([^(]+)', raw_exc)
    if m:
        cls = m.group(1).strip()
        # Normalize backslashes
        cls = cls.replace('\\', '\\\\')  # store with double-backslashes for consistency
        return cls
    # Try simple class name
    m = re.match(r'([A-Z][\w\\]+(?:Exception|Error))', raw_exc)
    if m:
        return m.group(1).replace('\\', '\\\\')
    # Try to find any Exception/Error class
    m = re.search(r'([A-Z][\w\\]*(?:Exception|Error))', raw_exc)
    if m:
        return m.group(1).replace('\\', '\\\\')
    return None


def _extract_exception_class_from_raw(raw: str) -> str | None:
    """Fallback: extract exception class from any location in the raw block."""
    # Look for [object] (ClassName pattern
    m = re.search(r'\[object\]\s*\(([^(]+)', raw)
    if m:
        return m.group(1).strip().replace('\\', '\\\\')
    # Look for common Laravel exception namespaces
    m = re.search(r'((?:Illuminate|Symfony|App)\\\\(?:[A-Z][a-z]*\\\\)*[A-Z][a-zA-Z]+)', raw)
    if m:
        return m.group(1)
    return None


def _compute_offsets(blocks: list[dict], full_text: str):
    """Compute character offsets for each block."""
    pos = 0
    for block in blocks:
        raw = block["raw_block"]
        start = full_text.find(raw, pos)
        if start >= 0:
            block["start_char"] = start
            block["end_char"] = start + len(raw)
            block["evidence"] = {
                "span": raw,
                "start": start,
                "end": start + len(raw),
                "confidence": 1.0,
            }
            pos = start + len(raw)
        else:
            block["start_char"] = 0
            block["end_char"] = len(raw)
            block["evidence"] = {
                "span": raw,
                "start": 0,
                "end": len(raw),
                "confidence": 1.0,
            }
