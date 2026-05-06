"""Dataset writer for SAGE.

Writes synthetic stories as JSONL files with train/dev/test splits.
Also generates benchmark files at different difficulty levels.
"""

import json
import random
from pathlib import Path
from typing import Optional

from sage.generator.synthetic_worlds import SyntheticWorldGenerator
from sage.generator.noise import NoiseInjector


class DatasetWriter:
    """Writes synthetic SAGE datasets to JSONL files.

    Supports train/dev/test splits, benchmark generation by difficulty,
    and metadata tracking.
    """

    def __init__(self, output_dir: Path, seed: int = 42):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generator = SyntheticWorldGenerator(seed=seed)
        self.noise = NoiseInjector(seed=seed + 1)
        self.rng = random.Random(seed)

    def generate_samples(self, num_samples: int,
                         min_events: int = 3,
                         max_events: int = 50,
                         noise_level: float = 0.0,
                         distractor_people: int = 0,
                         distractor_objects: int = 0,
                         irrelevant_sentences: int = 0,
                         shuffle_surface: bool = False) -> list[dict]:
        """Generate a list of dataset records.

        Args:
            num_samples: Number of samples to generate.
            min_events: Minimum events per story.
            max_events: Maximum events per story.
            noise_level: Fraction of events that are noise (0.0-1.0).
            distractor_people: Number of distractor people to add.
            distractor_objects: Number of distractor objects to add.
            irrelevant_sentences: Number of irrelevant sentences.
            shuffle_surface: Whether to shuffle sentences.

        Returns:
            List of dataset record dicts.
        """
        records = []
        for i in range(num_samples):
            seed = 42 + i * 137
            self.generator.set_seed(seed)
            self.noise.set_seed(seed + 1)

            num_events = self.rng.randint(min_events, max_events)
            story = self.generator.generate_story(num_events)

            # Inject noise
            noise_count = max(0, int(num_events * noise_level)) + irrelevant_sentences
            distractor_count = max(0, int(num_events * noise_level * 0.5))

            noise_people = []
            if distractor_people > 0:
                from sage.generator.names import NAMES
                used_names = set(story.sentences)
                noise_people = [n for n in NAMES if n not in str(used_names)][:distractor_people]

            noisy_sentences = self.noise.inject_into_story(
                story.sentences,
                noise_count=noise_count,
                distractor_people=noise_people,
                distractor_count=distractor_count,
                shuffle=shuffle_surface,
            )

            # Remove question from shuffle consideration
            question = noisy_sentences[-1] if noisy_sentences[-1].startswith("Question:") else None
            story_body = noisy_sentences[:-1] if question else noisy_sentences
            full_text = " ".join(story_body + ([question] if question else []))

            difficulty = self._classify_difficulty(num_events, noise_level)

            record = {
                "id": f"sample_{i:06d}",
                "story": full_text,
                "ops": story.ops,
                "answer": str(story.answer),
                "metadata": {
                    "num_events": story.num_events,
                    "num_people": story.num_people,
                    "num_objects": story.num_objects,
                    "noise_level": noise_level,
                    "difficulty": difficulty,
                },
            }
            records.append(record)

        return records

    def write_splits(self, records: list[dict],
                     train_ratio: float = 0.8,
                     dev_ratio: float = 0.1,
                     test_ratio: float = 0.1,
                     prefix: str = "sage") -> dict[str, Path]:
        """Write records to train/dev/test JSONL files.

        Returns:
            Dict mapping split name to file path.
        """
        self.rng.shuffle(records)
        n = len(records)
        train_end = int(n * train_ratio)
        dev_end = train_end + int(n * dev_ratio)

        splits = {
            "train": records[:train_end],
            "dev": records[train_end:dev_end],
            "test": records[dev_end:],
        }

        paths = {}
        for split_name, split_records in splits.items():
            path = self.output_dir / f"{prefix}_{split_name}.jsonl"
            self._write_jsonl(path, split_records)
            paths[split_name] = path

        return paths

    def write_benchmark(self, records: list[dict], name: str,
                        benchmarks_dir: Path | None = None) -> Path:
        """Write a benchmark file."""
        if benchmarks_dir is None:
            benchmarks_dir = self.output_dir / "benchmarks"
        benchmarks_dir = Path(benchmarks_dir)
        benchmarks_dir.mkdir(parents=True, exist_ok=True)

        path = benchmarks_dir / f"{name}.jsonl"
        self._write_jsonl(path, records)
        return path

    @staticmethod
    def _write_jsonl(path: Path, records: list[dict]):
        """Write records as JSONL."""
        with open(path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _classify_difficulty(num_events: int, noise_level: float) -> str:
        """Classify difficulty based on events and noise."""
        if num_events <= 5 and noise_level == 0.0:
            return "easy"
        elif num_events <= 25 and noise_level <= 0.2:
            return "medium"
        elif num_events <= 100:
            return "hard"
        else:
            return "long"

    def generate_adversarial_benchmark(self, num_samples: int = 500,
                                        output_path: Path | None = None) -> Path:
        """Generate an adversarial benchmark with misleading non-event sentences.

        Interleaves real state-changing events (~70%) with misleading non-events (~30%)
        that the rule compiler must ignore. The ground-truth ops only include real events.
        """
        import random as _random
        from sage.generator.names import NAMES, OBJECT_TYPES, get_singular

        rng = _random.Random(42)

        pronouns = {"male": "his", "female": "her"}
        default_pronoun = "their"

        ADVERSARIAL_TEMPLATES = [
            "{person} almost gives {amount} {obj} to {other}, but changes {pronoun} mind.",
            "{person} wanted to give {amount} {obj} to {other}, but did not.",
            "{person} planned to give {amount} {obj} to {other}, but never did.",
            "{person} intended to spend {amount} {obj}, but kept them.",
            "{person} almost lost {amount} {obj}, but found them again.",
            "{person} hoped to find {amount} {obj}, but didn't.",
            "{person} says {pronoun} has {amount} {obj}, but actually has {real_amount}.",
            "{person} claims to have {amount} {obj}, but really has {real_amount}.",
            "{person} tried to give {amount} {obj} to {other}, but couldn't.",
            "{person} gives {amount} {obj} to {other}, not to {third_person}.",
            "{person} thought about spending {amount} {obj}, but saved them instead.",
            "{person} nearly dropped {amount} {obj}, but caught them.",
            "{person} wished {pronoun} had {amount} {obj}, but didn't get any.",
        ]

        if output_path is None:
            output_path = Path("data/benchmarks/adversarial.jsonl")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = []
        gen = self.generator
        gen.set_seed(99)

        for i in range(num_samples):
            # Generate a real story with 5-15 events
            num_real_events = rng.randint(5, 15)
            story = gen.generate_story(num_real_events)

            # Extract people names from sentences (capitalized words)
            import re as _re
            all_text = " ".join(story.sentences)
            story_people = list(set(_re.findall(r'\b([A-Z][a-z]+)\b', all_text)))
            if not story_people:
                story_people = rng.sample(NAMES, min(3, len(NAMES)))

            real_sentences = list(story.sentences)
            question = real_sentences[-1]  # Question is last
            real_body = real_sentences[:-1]

            # Generate ~30% misleading sentences
            num_misleading = max(1, int(len(real_body) * 0.3))
            misleading_sents = []
            for _ in range(num_misleading):
                tmpl = rng.choice(ADVERSARIAL_TEMPLATES)
                person = rng.choice(story_people)
                others = [p for p in story_people if p != person]
                other = rng.choice(others) if others else rng.choice(NAMES)
                third_candidates = [p for p in story_people if p not in (person, other)]
                third = rng.choice(third_candidates) if third_candidates else rng.choice(NAMES)
                amount = rng.randint(1, 10)
                real_amount = rng.randint(1, 20)
                # Extract objects from ops targets
                story_objs = list(set(
                    op["target"].split(".", 1)[1] if "target" in op and "." in op.get("target", "") else ""
                    for op in story.ops
                ))
                story_objs = [o for o in story_objs if o]
                obj = rng.choice(story_objs) if story_objs else rng.choice(OBJECT_TYPES)
                singular = get_singular(obj)
                obj_form = singular if amount == 1 else obj
                pronoun = default_pronoun

                sent = tmpl.format(person=person, amount=amount, obj=obj_form,
                                   other=other, third_person=third,
                                   real_amount=real_amount, pronoun=pronoun)
                misleading_sents.append(sent)

            # Interleave: insert misleading sentences at random positions
            all_body = list(real_body)
            for ms in misleading_sents:
                pos = rng.randint(0, len(all_body))
                all_body.insert(pos, ms)

            full_text = " ".join(all_body + [question])

            difficulty = "adversarial"
            record = {
                "id": f"adv_{i:06d}",
                "story": full_text,
                "ops": story.ops,
                "answer": str(story.answer),
                "metadata": {
                    "num_events": story.num_events + num_misleading,
                    "num_people": story.num_people,
                    "num_objects": story.num_objects,
                    "noise_level": 0.3,
                    "difficulty": difficulty,
                    "misleading_count": num_misleading,
                },
            }
            records.append(record)

        self._write_jsonl(output_path, records)
        return output_path

    def generate_benchmarks(self, benchmarks_dir: Path):
        """Generate all standard benchmark files."""
        configs = [
            ("easy", 1000, 3, 5, 0.0, 0, 0, 0),
            ("medium", 1000, 10, 25, 0.1, 0, 0, 2),
            ("hard", 1000, 50, 100, 0.2, 2, 1, 5),
            ("long", 500, 200, 500, 0.3, 5, 3, 10),
            ("noise_stress", 500, 20, 50, 0.5, 5, 2, 15),
        ]

        benchmarks_dir = Path(benchmarks_dir)
        benchmarks_dir.mkdir(parents=True, exist_ok=True)

        for name, n, min_e, max_e, noise, dp, do, irr in configs:
            records = self.generate_samples(
                num_samples=n,
                min_events=min_e,
                max_events=max_e,
                noise_level=noise,
                distractor_people=dp,
                distractor_objects=do,
                irrelevant_sentences=irr,
                shuffle_surface=False,  # Don't shuffle benchmarks — ops must match text order
            )
            self.write_benchmark(records, name, benchmarks_dir)
