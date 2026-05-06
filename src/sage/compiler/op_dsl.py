"""Compact operation DSL parser for SAGE.

Converts simple line-based DSL output from neural models into
evidence-bound JSON operation dictionaries.

DSL format (one operation per line):
    NOOP
    SET|<target>|<value>|span=<evidence_span>
    ADD|<target>|<value>|span=<evidence_span>
    SUB|<target>|<value>|span=<evidence_span>
    TRANSFER|<from_target>|<to_target>|<value>|span=<evidence_span>
    QUERY|<target>|span=<evidence_span>

Example:
    "ADD|Latif.coins|3|span=Latif gains three coins"
    → [{"op":"ADD","target":"Latif.coins","value":3,"evidence":{...}}]
"""

from __future__ import annotations


def parse_op_dsl(output: str, original_text: str) -> list[dict]:
    """Parse DSL model output into evidence-bound operation JSON.

    Args:
        output: Raw model output string (may contain multiple lines).
        original_text: Full story text used to resolve evidence spans.

    Returns:
        List of operation dicts with evidence.
    """
    ops = []
    lines = output.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.upper() == "NOOP":
            continue

        op = _parse_single_op(line, original_text)
        if op is not None:
            ops.append(op)

    return ops


def _parse_single_op(line: str, original_text: str) -> dict | None:
    """Parse a single DSL operation line."""
    parts = line.split("|")
    if len(parts) < 2:
        return None

    op_type = parts[0].strip().upper()
    if op_type not in ("SET", "ADD", "SUB", "TRANSFER", "QUERY"):
        return None

    # Extract span from the last field
    span = ""
    for part in parts:
        if part.strip().startswith("span="):
            span = part.strip()[5:]
            break

    if not span:
        return None  # Span is required for evidence

    # Find span in original text
    start = original_text.find(span)
    if start == -1:
        # Try case-insensitive
        import re
        escaped = re.escape(span)
        m = re.search(escaped, original_text, re.IGNORECASE)
        if m:
            start = m.start()
            span = original_text[start:start + len(span)]
        else:
            # Try replacing digits with word numbers in span for matching
            NW={0:'zero',1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',19:'nineteen',20:'twenty',30:'thirty',40:'forty',50:'fifty',60:'sixty',70:'seventy',80:'eighty',90:'ninety'}
            alt=span
            for d,w in sorted(NW.items(),reverse=True):
                alt=alt.replace(str(d),w)
            if alt!=span:
                start=original_text.find(alt)
                if start>=0:span=alt
            if start==-1:return None

    end = start + len(span)
    evidence = {"span": span, "start": start, "end": end, "confidence": 1.0}

    try:
        if op_type == "QUERY":
            if len(parts) < 3:
                return None
            target = parts[1].strip()
            return {"op": "QUERY", "target": target, "evidence": evidence}

        elif op_type == "TRANSFER":
            if len(parts) < 5:
                return None
            from_target = parts[1].strip()
            to_target = parts[2].strip()
            value = int(parts[3].strip())
            return {"op": "TRANSFER", "from": from_target, "to": to_target,
                    "value": value, "evidence": evidence}

        else:  # SET, ADD, SUB
            if len(parts) < 4:
                return None
            target = parts[1].strip()
            value = int(parts[2].strip())
            return {"op": op_type, "target": target, "value": value, "evidence": evidence}

    except (ValueError, IndexError):
        return None
