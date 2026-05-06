"""Laravel log parser for SAGE Incident Lens.

Parses Laravel/PHP log files into structured log blocks.
Handles multiline stack traces and groups them with their parent log line.
"""

from __future__ import annotations
import re
from pathlib import Path


# Laravel log line pattern: [YYYY-MM-DD HH:MM:SS] environment.LEVEL: message
LOG_LINE_RE = re.compile(
    r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+'
    r'(\w+)\.(\w+):\s+(.*)'
)

# Stack trace frame pattern
STACK_FRAME_RE = re.compile(r'^#\d+\s+')
STACK_TRACE_HEADER_RE = re.compile(r'^\[stacktrace\]|^Stack trace:')
EXCEPTION_HEADER_RE = re.compile(r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+\w+\.\w+:')


def parse_log_file(file_path: str | Path) -> list[dict]:
    """Parse a Laravel log file into structured log blocks.

    Each block is a dict with:
        timestamp, environment, level, message, exception, file, line_number,
        raw_block (full multiline text), start_char, end_char

    Multiline stack traces are grouped with their parent log line.
    """
    file_path = Path(file_path)
    text = file_path.read_text(errors="replace")

    blocks = []
    current_block = None

    for line in text.split("\n"):
        # Check if this line starts a new log entry
        m = LOG_LINE_RE.match(line)
        if m:
            # Save previous block
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
            # Continuation line (stack trace, message continuation)
            current_block["raw_lines"].append(line)

    # Don't forget the last block
    if current_block is not None:
        _finalize_block(current_block)
        blocks.append(current_block)

    # Calculate character offsets
    _compute_offsets(blocks, text)

    return blocks


def _finalize_block(block: dict):
    """Extract exception and file info from a log block."""
    raw = "\n".join(block["raw_lines"])
    block["raw_block"] = raw

    # Extract exception class from message or stack trace
    exc_match = re.search(r'"exception":"([^"]+)"', raw)
    if exc_match:
        block["exception"] = exc_match.group(1).replace("\\\\", "\\")
    else:
        # Look for exception class in message
        exc_match = re.search(r'((?:[A-Z][a-z]*\\\\)+[A-Z][a-zA-Z]+)', raw)
        if exc_match:
            block["exception"] = exc_match.group(1)

    # Extract file from stack trace
    file_match = re.search(r'#\d+\s+(/[^:(]+)', raw)
    if file_match:
        block["file"] = file_match.group(1)

    # Extract line number
    line_match = re.search(r'#\d+\s+/[^(]+\((\d+)\)', raw)
    if line_match:
        block["line_number"] = int(line_match.group(1))


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
