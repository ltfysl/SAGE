class QueryResult:
    def __init__(self, answer="", evidence=None, confidence=1.0, limitations=None):
        self.answer = answer
        self.evidence = evidence or []
        self.confidence = float(confidence)
        self.limitations = limitations or []

    def to_dict(self):
        return {
            'answer': self.answer,
            'evidence': [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.evidence],
            'confidence': self.confidence,
            'limitations': self.limitations,
        }
