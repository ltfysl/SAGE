class Operation:
    def __init__(self, op, domain=None, payload=None, evidence=None,
                 confidence=1.0, tags=None, metadata=None):
        self.op = op
        self.domain = domain
        self.payload = payload or {}
        self.evidence = evidence
        self.confidence = float(confidence)
        self.tags = tags or []
        self.metadata = metadata or {}

    def to_dict(self):
        d = {'op': self.op}
        if self.domain: d['domain'] = self.domain
        d['payload'] = self.payload
        if self.evidence and hasattr(self.evidence, 'to_dict'):
            d['evidence'] = self.evidence.to_dict()
        elif isinstance(self.evidence, dict):
            d['evidence'] = self.evidence
        d['confidence'] = self.confidence
        if self.tags: d['tags'] = self.tags
        if self.metadata: d['metadata'] = self.metadata
        return d

    @classmethod
    def from_dict(cls, d):
        from sage.core.evidence import Evidence
        ev = d.get('evidence')
        if ev and isinstance(ev, dict):
            ev = Evidence.from_dict(ev)
        return cls(
            op=d['op'], domain=d.get('domain'), payload=d.get('payload', {}),
            evidence=ev, confidence=d.get('confidence', 1.0),
            tags=d.get('tags', []), metadata=d.get('metadata', {})
        )

    def validate_basic(self):
        return bool(self.op) and 0.0 <= self.confidence <= 1.0

    def __repr__(self):
        return f"Operation(op={self.op!r}, domain={self.domain!r}, confidence={self.confidence})"
