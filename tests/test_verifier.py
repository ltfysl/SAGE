"""Tests for the SAGE verifier."""

import json
import pytest
from sage.verifier.verifier import Verifier


class TestVerifier:
    """Test the operation verifier."""

    def test_valid_ops(self):
        verifier = Verifier()
        raw = json.dumps([
            {"op": "SET", "target": "Latif.coins", "value": 5},
            {"op": "QUERY", "target": "Latif.coins"},
        ])
        ops, result = verifier.verify(raw)
        assert ops is not None
        assert result.valid_json
        assert result.valid_ops
        assert len(ops) == 2

    def test_invalid_json(self):
        verifier = Verifier()
        ops, result = verifier.verify("not json at all")
        assert ops is None
        assert not result.valid_json

    def test_invalid_op_type(self):
        verifier = Verifier()
        raw = json.dumps([
            {"op": "INVALID", "target": "x", "value": 5},
        ])
        ops, result = verifier.verify(raw)
        assert ops is not None  # JSON is valid
        assert len(ops) == 0  # But no valid operations
        assert not result.valid_ops

    def test_missing_fields(self):
        verifier = Verifier()
        raw = json.dumps([
            {"op": "SET", "target": "x"},  # missing value
        ])
        ops, result = verifier.verify(raw)
        assert not result.valid_ops
        assert len(result.errors) > 0

    def test_transfer_fields(self):
        verifier = Verifier()
        raw = json.dumps([
            {"op": "TRANSFER", "from": "A.x", "to": "B.x", "value": 5},
        ])
        ops, result = verifier.verify(raw)
        assert result.valid_ops
        assert ops[0].from_target == "A.x"
        assert ops[0].to_target == "B.x"

    def test_json_recovery(self):
        verifier = Verifier()
        # Model might output extra text around JSON
        raw = 'Here is the output: [{"op":"SET","target":"x","value":5}] end'
        ops, result = verifier.verify(raw)
        assert ops is not None
        assert result.valid_json
        assert "recovered" in result.warnings[0].lower()

    def test_not_an_array(self):
        verifier = Verifier()
        raw = json.dumps({"op": "SET", "target": "x", "value": 5})
        ops, result = verifier.verify(raw)
        assert ops is None
        assert not result.valid_ops
