"""Generic evidence model — links operations to source artifacts."""

class Evidence:
    def __init__(self, source=None, file=None, line=None, span=None,
                 start_offset=None, end_offset=None, confidence=1.0,
                 parser=None, metadata=None):
        self.source = source
        self.file = file
        self.line = line
        self.span = span
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.confidence = float(confidence)
        self.parser = parser
        self.metadata = metadata or {}

    def to_dict(self):
        d = {}
        if self.source is not None: d['source'] = self.source
        if self.file is not None: d['file'] = self.file
        if self.line is not None: d['line'] = self.line
        if self.span is not None: d['span'] = self.span
        if self.start_offset is not None: d['start_offset'] = self.start_offset
        if self.end_offset is not None: d['end_offset'] = self.end_offset
        d['confidence'] = self.confidence
        if self.parser: d['parser'] = self.parser
        if self.metadata: d['metadata'] = self.metadata
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            source=d.get('source'), file=d.get('file'), line=d.get('line'),
            span=d.get('span'), start_offset=d.get('start_offset'),
            end_offset=d.get('end_offset'), confidence=d.get('confidence', 1.0),
            parser=d.get('parser'), metadata=d.get('metadata', {})
        )

    def is_valid(self):
        return self.span is not None and self.confidence >= 0.0

    def short_span(self, max_chars=220):
        if not self.span:
            return ''
        if len(self.span) <= max_chars:
            return self.span
        return self.span[:max_chars] + '…'

    def has_location(self):
        return self.file is not None or self.line is not None

    def location_str(self):
        if self.file and self.line:
            return chr(123)+chr(125)+chr(58)+chr(123)+chr(125).format(self.file,self.line)
        if self.file:
            return self.file
        return chr(39)+chr(39)

    def __repr__(self):
        return f"Evidence(span={self.short_span(60)!r}, confidence={self.confidence})"
