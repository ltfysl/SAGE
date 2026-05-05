"""SAGE engine errors."""


class EngineError(Exception):
    """Base exception for engine errors."""


class InvalidOperationError(EngineError):
    """Raised when an operation is invalid."""


class StateOverflowError(EngineError):
    """Raised when state size exceeds configured maximum."""


class MissingTargetError(EngineError):
    """Raised when a required target is missing."""


class ExecutionError(EngineError):
    """Raised when execution fails for any reason."""
