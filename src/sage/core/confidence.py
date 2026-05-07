"""Evidence confidence scoring for SAGE operations."""

# Confidence labels ordered from strongest to weakest
VERIFIED = "verified"
STRONG = "strong"
INFERRED = "inferred"
WEAK = "weak"
UNCERTAIN = "uncertain"

LABELS = [VERIFIED, STRONG, INFERRED, WEAK, UNCERTAIN]


def score_evidence(op):
    """Score an operation on evidence quality. Returns (label, score 0.0-1.0)."""
    score = 0.0
    reasons = []
    ev = op.evidence if hasattr(op, "evidence") else op.get("evidence")
    if ev is None:
        return (UNCERTAIN, 0.0, ["No evidence attached"])
    if hasattr(ev, "has_location"):
        if ev.has_location():
            score += 0.20
            reasons.append("has location")
        if ev.span and len(ev.span) > 0:
            score += 0.20
            reasons.append("has span")
        if ev.file is not None:
            score += 0.15
            reasons.append("has file")
        if ev.line is not None:
            score += 0.15
            reasons.append("has line")
        if ev.parser is not None:
            score += 0.10
            reasons.append("has parser")
        if ev.start_offset is not None and ev.end_offset is not None:
            score += 0.10
            reasons.append("exact offsets")
        score += ev.confidence * 0.10
    if score >= 0.90:
        return (VERIFIED, score, reasons)
    elif score >= 0.70:
        return (STRONG, score, reasons)
    elif score >= 0.40:
        return (INFERRED, score, reasons)
    elif score >= 0.15:
        return (WEAK, score, reasons)
    return (UNCERTAIN, score, reasons)


def confidence_summary(ops):
    """Summarize confidence distribution across operations."""
    from collections import Counter
    dist = Counter()
    for op in ops:
        label, _, _ = score_evidence(op)
        dist[label] += 1
    total = len(ops)
    if total == 0:
        return {"total": 0, "distribution": {}, "strong_rate": 0.0}
    strong = dist.get(VERIFIED, 0) + dist.get(STRONG, 0)
    return {"total": total, "distribution": dict(dist), "strong_rate": strong / total}
