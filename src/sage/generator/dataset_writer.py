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
                shuffle_surface=(noise > 0),
            )
            self.write_benchmark(records, name, benchmarks_dir)
