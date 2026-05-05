"""Tests for the SAGE deterministic engine."""

import pytest
from sage.config import EngineConfig
from sage.engine.executor import Executor
from sage.engine.state_store import StateStore
from sage.engine.errors import ExecutionError
from sage.schemas.ops import Operation, OpType


class TestStateStore:
    """Test the deterministic state store."""

    def test_default_value(self):
        store = StateStore(default_value=0)
        assert store.get("unknown") == 0

    def test_set_and_get(self):
        store = StateStore()
        store.set("Latif.coins", 5)
        assert store.get("Latif.coins") == 5

    def test_add(self):
        store = StateStore()
        store.add("Latif.coins", 3)
        assert store.get("Latif.coins") == 3  # default 0 + 3
        store.add("Latif.coins", 2)
        assert store.get("Latif.coins") == 5

    def test_sub(self):
        store = StateStore()
        store.set("Latif.coins", 10)
        store.sub("Latif.coins", 3)
        assert store.get("Latif.coins") == 7

    def test_transfer(self):
        store = StateStore()
        store.set("Arno.coins", 10)
        store.transfer("Arno.coins", "Latif.coins", 4)
        assert store.get("Arno.coins") == 6
        assert store.get("Latif.coins") == 4

    def test_snapshot(self):
        store = StateStore()
        store.set("a.x", 1)
        store.set("b.y", 2)
        snap = store.snapshot()
        assert snap == {"a.x": 1, "b.y": 2}

    def test_reset(self):
        store = StateStore()
        store.set("a.x", 5)
        store.reset()
        assert store.get("a.x") == 0
        assert store.snapshot() == {}


class TestExecutor:
    """Test the deterministic executor."""

    def test_basic_execution(self):
        ops = [
            Operation(op=OpType.SET, target="Latif.coins", value=5),
            Operation(op=OpType.SET, target="Arno.coins", value=4),
            Operation(op=OpType.TRANSFER, from_target="Arno.coins", to_target="Latif.coins", value=2),
            Operation(op=OpType.SUB, target="Latif.coins", value=3),
            Operation(op=OpType.QUERY, target="Latif.coins"),
        ]
        executor = Executor()
        result = executor.execute(ops)

        assert result.valid
        assert result.answer == 4
        assert result.target == "Latif.coins"

    def test_missing_query(self):
        ops = [
            Operation(op=OpType.SET, target="Latif.coins", value=5),
        ]
        executor = Executor()
        result = executor.execute(ops)
        assert result.valid
        assert result.answer is None  # No QUERY op

    def test_trace_generation(self):
        ops = [
            Operation(op=OpType.SET, target="x", value=10),
            Operation(op=OpType.ADD, target="x", value=5),
            Operation(op=OpType.QUERY, target="x"),
        ]
        executor = Executor()
        result = executor.execute(ops)
        assert len(result.trace) == 3
        assert result.trace[0].state_before == {}
        assert result.trace[0].state_after == {"x": 10}

    def test_complex_story(self):
        """Latif has 5 coins. Arno has 4 coins. Arno gives 2 coins to Latif.
        Latif spends 3 coins. Question: How many coins does Latif have?
        Answer: 4"""
        ops = [
            Operation(op=OpType.SET, target="Latif.coins", value=5),
            Operation(op=OpType.SET, target="Arno.coins", value=4),
            Operation(op=OpType.TRANSFER, from_target="Arno.coins", to_target="Latif.coins", value=2),
            Operation(op=OpType.SUB, target="Latif.coins", value=3),
            Operation(op=OpType.QUERY, target="Latif.coins"),
        ]
        executor = Executor()
        result = executor.execute(ops)
        assert result.answer == 4

    def test_batch_execution(self):
        ops1 = [
            Operation(op=OpType.SET, target="a", value=1),
            Operation(op=OpType.QUERY, target="a"),
        ]
        ops2 = [
            Operation(op=OpType.SET, target="b", value=2),
            Operation(op=OpType.QUERY, target="b"),
        ]
        executor = Executor()
        results = executor.execute_batch([ops1, ops2])
        assert results[0].answer == 1
        assert results[1].answer == 2
