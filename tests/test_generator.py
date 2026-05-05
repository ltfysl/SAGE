"""Tests for the SAGE data generator."""

import pytest
from sage.generator.synthetic_worlds import SyntheticWorldGenerator
from sage.generator.noise import NoiseInjector


class TestSyntheticWorldGenerator:
    """Test the synthetic world generator."""

    def test_basic_story(self):
        gen = SyntheticWorldGenerator(seed=42)
        story = gen.generate_story(num_events=3)
        assert len(story.sentences) > 0
        assert len(story.ops) > 0
        assert isinstance(story.answer, int)
        assert story.story_text  # non-empty

    def test_ops_contain_query(self):
        gen = SyntheticWorldGenerator(seed=42)
        story = gen.generate_story(num_events=5)
        op_types = [op["op"] for op in story.ops]
        assert "QUERY" in op_types

    def test_story_is_deterministic(self):
        gen1 = SyntheticWorldGenerator(seed=42)
        gen2 = SyntheticWorldGenerator(seed=42)
        s1 = gen1.generate_story(3)
        s2 = gen2.generate_story(3)
        assert s1.story_text == s2.story_text
        assert s1.answer == s2.answer

    def test_different_seeds_different(self):
        gen1 = SyntheticWorldGenerator(seed=1)
        gen2 = SyntheticWorldGenerator(seed=2)
        s1 = gen1.generate_story(10)
        s2 = gen2.generate_story(10)
        # Very unlikely to be identical with 10 events
        assert s1.story_text != s2.story_text

    def test_answer_matches_ops(self):
        """Execute ops and verify answer matches."""
        from sage.engine.executor import Executor
        from sage.schemas.ops import Operation, OpType

        gen = SyntheticWorldGenerator(seed=42)
        story = gen.generate_story(num_events=10)

        # Convert ops dicts to Operation objects
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


class TestNoiseInjector:
    """Test the noise injector."""

    def test_noise_injection(self):
        injector = NoiseInjector(seed=42)
        sentences = ["Alice has 5 coins.", "Bob gives 2 coins to Alice."]
        result = injector.inject_into_story(
            sentences, noise_count=3, distractor_people=["Charlie"], distractor_count=2
        )
        # Should have original sentences + noise
        assert len(result) > len(sentences)

    def test_no_noise(self):
        injector = NoiseInjector()
        sentences = ["Alice has 5 coins."]
        result = injector.inject_into_story(sentences, noise_count=0)
        assert result == sentences

    def test_shuffle_keeps_question(self):
        injector = NoiseInjector(seed=42)
        sentences = ["Alice has 5 coins.", "Bob gives 2 coins to Alice.",
                      "Question: How many coins does Alice have?"]
        result = injector.inject_into_story(sentences, shuffle=True)
        # Question should still be last
        assert result[-1].startswith("Question:")
