"""Noise injection for synthetic SAGE datasets.

Adds distractor sentences, irrelevant information, and
surface-form variation to test robustness.
"""

import random
from typing import List


# Irrelevant noise sentences that don't affect state
NOISE_SENTENCES = [
    "The weather is sunny today.",
    "A bird flies past the window.",
    "The clock strikes noon.",
    "Someone hums a quiet tune.",
    "The wind rustles the leaves.",
    "A dog barks in the distance.",
    "The lamp flickers briefly.",
    "A car drives by outside.",
    "The kettle starts to whistle.",
    "Someone sneezes loudly.",
    "The phone rings once.",
    "A cat stretches on the windowsill.",
    "The refrigerator hums.",
    "Raindrops tap against the glass.",
    "A book falls off the shelf.",
    "The door creaks open.",
    "Footsteps echo in the hallway.",
    "The radiator clicks on.",
    "A pen rolls across the desk.",
    "The curtains sway gently.",
    "Somewhere, a clock chimes.",
    "A shadow moves in the corner.",
    "The floorboards creak.",
    "A light buzzes overhead.",
    "The scent of coffee lingers.",
    "A magazine lies open on the table.",
    "The sky grows overcast.",
    "Someone coughs quietly.",
    "A chair scrapes against the floor.",
    "The toaster pops.",
]

# Distractor sentences that mention people but don't affect tracked state
DISTRACTOR_SENTENCE_TEMPLATES = [
    "{person} looks out the window.",
    "{person} hums a melody.",
    "{person} ties their shoelaces.",
    "{person} wonders what time it is.",
    "{person} yawns and stretches.",
    "{person} checks their watch.",
    "{person} adjusts their glasses.",
    "{person} remembers an old song.",
    "{person} thinks about lunch.",
    "{person} taps their fingers on the table.",
    "{person} glances at the clock.",
    "{person} smiles faintly.",
    "{person} scratches their head.",
    "{person} takes a deep breath.",
    "{person} notices a cloud in the sky.",
    "{person} folds their arms.",
    "{person} leans back in their chair.",
    "{person} flips through a book.",
    "{person} doodles on a napkin.",
    "{person} sips some water.",
]


class NoiseInjector:
    """Injects noise into synthetic stories.

    Supports:
    - Irrelevant sentences (ambient noise)
    - Distractor sentences about people
    - Shuffled surface phrasing
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate_noise_sentences(self, count: int) -> list[str]:
        """Generate a list of irrelevant noise sentences."""
        if count <= 0:
            return []
        return [self.rng.choice(NOISE_SENTENCES) for _ in range(count)]

    def generate_distractor_sentences(self, count: int, people: list[str]) -> list[str]:
        """Generate sentences about people that don't affect state."""
        if count <= 0 or not people:
            return []
        sentences = []
        for _ in range(count):
            person = self.rng.choice(people)
            template = self.rng.choice(DISTRACTOR_SENTENCE_TEMPLATES)
            sentences.append(template.format(person=person))
        return sentences

    def inject_into_story(self, story_sentences: list[str],
                          noise_count: int = 0,
                          distractor_people: list[str] = None,
                          distractor_count: int = 0,
                          shuffle: bool = False) -> list[str]:
        """Inject noise sentences into a story.

        Args:
            story_sentences: Core story sentences in order.
            noise_count: Number of irrelevant noise sentences.
            distractor_people: People to use in distractor sentences.
            distractor_count: Number of distractor sentences.
            shuffle: Whether to shuffle all sentences together.

        Returns:
            List of sentences with noise injected.
        """
        result = list(story_sentences)

        # Add noise sentences at random positions
        noise_sents = self.generate_noise_sentences(noise_count)
        for ns in noise_sents:
            pos = self.rng.randint(0, len(result))
            result.insert(pos, ns)

        # Add distractor sentences
        if distractor_people:
            distractor_sents = self.generate_distractor_sentences(
                distractor_count, distractor_people
            )
            for ds in distractor_sents:
                pos = self.rng.randint(0, len(result))
                result.insert(pos, ds)

        if shuffle:
            # Keep the question at the end
            question = result[-1] if result and result[-1].startswith("Question:") else None
            non_question = result[:-1] if question else result
            self.rng.shuffle(non_question)
            if question:
                result = non_question + [question]
            else:
                result = non_question

        return result

    def set_seed(self, seed: int):
        """Reset the random seed."""
        self.rng = random.Random(seed)
