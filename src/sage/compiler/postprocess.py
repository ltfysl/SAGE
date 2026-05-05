"""Post-processing utilities for compiler output.

Cleans up raw model output, extracts JSON arrays,
and performs basic validation.
"""

from __future__ import annotations

import json
import re
from typing import Any


def clean_model_output(raw: str) -> str:
    """Extract and clean a JSON array from raw model output.

    Handles common formatting issues:
    - Extra text before/after the JSON array
    - Trailing commas
    - Single quotes instead of double quotes
    - Missing brackets

    Args:
        raw: Raw string output from the model.

    Returns:
        Cleaned JSON array string (or empty string if unrecoverable).
    """
    raw = raw.strip()

    # Find the outermost JSON array
    start = raw.find("[")
    end = raw.rfind("]")

    if start == -1 or end == -1 or end <= start:
        # Try to find a JSON object instead
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end > start:
            # Wrap single object in array
            inner = raw[start:end + 1]
            return f"[{inner}]"
        return ""

    json_str = raw[start:end + 1]

    # Fix common issues
    # Replace single quotes with double quotes (careful with apostrophes)
    # This is a simplistic approach
    if '"' not in json_str and "'" in json_str:
        json_str = json_str.replace("'", '"')

    # Remove trailing commas before ] or }
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    # Try to parse and re-serialize for canonical form
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed)
    except json.JSONDecodeError:
        return json_str


def validate_ops_json(raw: str) -> tuple[list[dict[str, Any]] | None, bool]:
    """Parse and basic validate JSON operation sequence.

    Args:
        raw: Raw compiler output string.

    Returns:
        Tuple of (parsed ops list or None, is_valid).
    """
    cleaned = clean_model_output(raw)
    if not cleaned:
        return None, False

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None, False

    if not isinstance(parsed, list):
        return None, False

    # Basic validation: each element must be a dict with "op" key
    for item in parsed:
        if not isinstance(item, dict):
            return None, False
        if "op" not in item:
            return None, False
        op_type = item["op"].upper()
        if op_type not in {"SET", "ADD", "SUB", "TRANSFER", "QUERY"}:
            return None, False

    return parsed, True


def extract_answer_from_output(raw: str) -> str | None:
    """Extract just the answer from model output.

    For direct baseline: the model outputs a number or short answer.

    Args:
        raw: Raw model output.

    Returns:
        Extracted answer string or None.
    """
    raw = raw.strip()

    # Try to extract just digits
    num_match = re.search(r'\b(\d+)\b', raw)
    if num_match:
        return num_match.group(1)

    # Return the full output trimmed
    if raw:
        return raw
    return None
