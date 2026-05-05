"""Deterministic state store for SAGE.

The state store is a simple key-value mapping that tracks
creation time, modification time, and access count for each entry.
"""

from dataclasses import dataclass, field


@dataclass
class StateEntry:
    """Internal state entry tracking metadata."""

    value: int
    created_at: int = 0
    updated_at: int = 0
    access_count: int = 0


class StateStore:
    """Deterministic key-value state store.

    All operations are O(1) and deterministic.
    Unknown keys return the configured default value (default 0).
    """

    def __init__(self, default_value: int = 0, allow_negative: bool = True):
        self._data: dict[str, StateEntry] = {}
        self._step: int = 0
        self.default_value = default_value
        self.allow_negative = allow_negative

    @property
    def step(self) -> int:
        return self._step

    def advance_step(self) -> int:
        self._step += 1
        return self._step

    def get(self, key: str) -> int:
        """Get the value for a key, defaulting if not present."""
        if key in self._data:
            entry = self._data[key]
            entry.access_count += 1
            return entry.value
        return self.default_value

    def set(self, key: str, value: int) -> int:
        """Set a key to an exact value."""
        step = self.advance_step()
        if key in self._data:
            entry = self._data[key]
            entry.value = value
            entry.updated_at = step
        else:
            self._data[key] = StateEntry(value=value, created_at=step, updated_at=step)
        return value

    def add(self, key: str, delta: int) -> int:
        """Add a delta to a key's value (creating if needed)."""
        step = self.advance_step()
        if key in self._data:
            entry = self._data[key]
            entry.value += delta
            entry.updated_at = step
        else:
            self._data[key] = StateEntry(
                value=self.default_value + delta,
                created_at=step,
                updated_at=step,
            )
        return self._data[key].value

    def sub(self, key: str, delta: int) -> int:
        """Subtract a delta from a key's value (creating if needed)."""
        return self.add(key, -delta)

    def transfer(self, from_key: str, to_key: str, amount: int) -> tuple[int, int]:
        """Transfer an amount from one key to another."""
        step = self.advance_step()
        # Read current values
        from_val = self.get(from_key)
        to_val = self.get(to_key)

        new_from = from_val - amount
        new_to = to_val + amount

        # Write back
        if from_key in self._data:
            self._data[from_key].value = new_from
            self._data[from_key].updated_at = step
        else:
            self._data[from_key] = StateEntry(value=new_from, created_at=step, updated_at=step)

        if to_key in self._data:
            self._data[to_key].value = new_to
            self._data[to_key].updated_at = step
        else:
            self._data[to_key] = StateEntry(value=new_to, created_at=step, updated_at=step)

        return new_from, new_to

    def snapshot(self) -> dict[str, int]:
        """Return a snapshot of all current values."""
        return {k: e.value for k, e in self._data.items()}

    def reset(self):
        """Clear all state."""
        self._data.clear()
        self._step = 0
