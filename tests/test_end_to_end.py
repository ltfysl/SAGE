"""End-to-end tests for the SAGE pipeline."""

import json
import pytest
from sage.engine.executor import Executor
from sage.verifier.verifier import Verifier
from sage.renderer.renderer import Renderer
from sage.generator.synthetic_worlds import SyntheticWorldGenerator
from sage.schemas.ops import Operation, OpType
from sage.config import EngineConfig


class TestEndToEnd:
    """Full pipeline tests: compile → verify → execute → render."""

    def test_full_pipeline_rule_compiler(self):
        """Test the rule compiler through the full pipeline."""
        from sage.compiler.rule_compiler import RuleCompiler

        story = (
            "Latif has 5 coins. "
            "Arno has 4 coins. "
            "Arno gives 2 coins to Latif. "
            "Latif spends 3 coins. "
            "Question: How many coins does Latif have?"
        )

        # Compile
        compiler = RuleCompiler()
        ops_raw, success = compiler.compile(story)
        assert success
        assert len(ops_raw) > 0

        # Verify
        verifier = Verifier()
        ops, ver_result = verifier.verify(json.dumps(ops_raw))
        assert ver_result.valid_json
        assert ver_result.valid_ops

        # Execute
        executor = Executor()
        result = executor.execute(ops)
        assert result.valid
        assert result.answer == 4

        # Render
        renderer = Renderer()
        answer = renderer.render(result)
        assert "Latif" in answer
        assert "4" in answer

    def test_full_pipeline_generated(self):
        """Test pipeline on generated stories."""
        gen = SyntheticWorldGenerator(seed=42)
        story = gen.generate_story(num_events=5)

        # Convert ops to Operation objects
        ops = []
        for op_dict in story.ops:
            d = dict(op_dict)
            if "from" in d:
                d["from_target"] = d.pop("from")
            if "to" in d:
                d["to_target"] = d.pop("to")
            ops.append(Operation(**d))

        executor = Executor()
        result = executor.execute(ops)
        assert result.valid
        assert result.answer == story.answer

        renderer = Renderer()
        answer = renderer.render(result)
        assert len(answer) > 0

    def test_debug_output(self):
        """Test debug rendering."""
        ops = [
            Operation(op=OpType.SET, target="x", value=10),
            Operation(op=OpType.QUERY, target="x"),
        ]
        executor = Executor()
        result = executor.execute(ops)

        renderer = Renderer()
        debug = renderer.render_debug(result, input_text="test", compiled_ops=[{"op": "SET", "target": "x", "value": 10}])
        assert debug["answer"] == 10
        assert len(debug["state_trace"]) == 2
        assert debug["verification"]["execution_success"]

    def test_error_handling(self):
        """Test that invalid ops produce proper errors."""
        # Missing QUERY
        ops = [
            Operation(op=OpType.SET, target="x", value=5),
        ]
        executor = Executor()
        result = executor.execute(ops)
        assert result.valid
        assert result.answer is None

        renderer = Renderer()
        answer = renderer.render(result)
        assert "Error" in answer

    def test_multiple_people_objects(self):
        """Test complex story with multiple people and objects."""
        ops = [
            Operation(op=OpType.SET, target="Alice.coins", value=10),
            Operation(op=OpType.SET, target="Bob.apples", value=5),
            Operation(op=OpType.TRANSFER, from_target="Alice.coins", to_target="Bob.coins", value=3),
            Operation(op=OpType.ADD, target="Bob.apples", value=2),
            Operation(op=OpType.SUB, target="Alice.coins", value=1),
            Operation(op=OpType.QUERY, target="Alice.coins"),
        ]
        executor = Executor()
        result = executor.execute(ops)
        # Alice: 10 - 3 - 1 = 6 coins
        assert result.answer == 6
        assert result.state_snapshot["Bob.coins"] == 3
        assert result.state_snapshot["Bob.apples"] == 7
