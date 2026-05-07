class VerificationResult:
    def __init__(self, valid_ops=None, invalid_ops=None, warnings=None,
                 total_count=0, valid_count=0, invalid_count=0):
        self.valid_operations = valid_ops or []
        self.invalid_operations = invalid_ops or []
        self.warnings = warnings or []
        self.total_count = total_count
        self.valid_count = valid_count
        self.invalid_count = invalid_count

    @property
    def evidence_valid_rate(self):
        if self.total_count == 0:
            return 1.0
        return self.valid_count / self.total_count

    def to_dict(self):
        return {
            'valid_operations': [o.to_dict() for o in self.valid_operations if hasattr(o, 'to_dict')],
            'invalid_operations': [o.to_dict() for o in self.invalid_operations if hasattr(o, 'to_dict')],
            'warnings': self.warnings,
            'total_count': self.total_count,
            'valid_count': self.valid_count,
            'invalid_count': self.invalid_count,
        }


class BaseVerifier:
    def verify(self, operations, context=None):
        raise NotImplementedError


class DefaultVerifier(BaseVerifier):
    def verify(self, operations, context=None):
        valid, invalid, warnings = [], [], []
        for op in operations:
            if not hasattr(op, 'validate_basic') or not op.validate_basic():
                invalid.append(op)
                warnings.append(f"Invalid operation: {op}")
            else:
                valid.append(op)
        return VerificationResult(
            valid_ops=valid, invalid_ops=invalid, warnings=warnings,
            total_count=len(operations), valid_count=len(valid),
            invalid_count=len(invalid)
        )
