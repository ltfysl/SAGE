"""Synthetic event-world generator for SAGE.

Generates natural-language stories about people, objects, quantities,
transfers, gains, losses, and queries. Each story is paired with
its ground-truth operation sequence for supervised training.
"""

import random
from dataclasses import dataclass, field
from typing import Any

from sage.generator.names import NAMES, OBJECT_TYPES, get_singular


# ── Event types ──────────────────────────────────────────────────

class EventType:
    HAS = "HAS"           # Person has X amount
    GIVES = "GIVES"       # Person gives to another
    RECEIVES = "RECEIVES" # Person receives from another
    SPENDS = "SPENDS"     # Person spends/loses
    FINDS = "FINDS"       # Person finds/gains
    LOSES = "LOSES"       # Person loses
    BUYS = "BUYS"         # Person buys from another
    SELLS = "SELLS"       # Person sells to another


# ── Surface-form templates ───────────────────────────────────────

HAS_TEMPLATES = [
    "{person} has {amount} {obj}.",
    "{person} owns {amount} {obj}.",
    "{person} holds {amount} {obj}.",
    "{person} possesses {amount} {obj}.",
    "{person} has exactly {amount} {obj}.",
    "{person} is holding {amount} {obj}.",
]

GIVES_TEMPLATES = [
    "{giver} gives {amount} {obj} to {receiver}.",
    "{giver} hands {amount} {obj} to {receiver}.",
    "{giver} passes {amount} {obj} to {receiver}.",
    "{giver} gives {receiver} {amount} {obj}.",
    "{giver} offers {receiver} {amount} {obj}.",
    "{giver} transfers {amount} {obj} to {receiver}.",
]

RECEIVES_TEMPLATES = [
    "{receiver} receives {amount} {obj} from {giver}.",
    "{receiver} gets {amount} {obj} from {giver}.",
    "{receiver} takes {amount} {obj} from {giver}.",
    "{receiver} is given {amount} {obj} by {giver}.",
]

SPENDS_TEMPLATES = [
    "{person} spends {amount} {obj}.",
    "{person} uses {amount} {obj}.",
    "{person} consumes {amount} {obj}.",
    "{person} gives away {amount} {obj}.",
    "{person} parts with {amount} {obj}.",
]

FINDS_TEMPLATES = [
    "{person} finds {amount} {obj}.",
    "{person} discovers {amount} {obj}.",
    "{person} picks up {amount} {obj}.",
    "{person} gains {amount} {obj}.",
    "{person} collects {amount} {obj}.",
    "{person} earns {amount} {obj}.",
]

LOSES_TEMPLATES = [
    "{person} loses {amount} {obj}.",
    "{person} drops {amount} {obj}.",
    "{person} misplaces {amount} {obj}.",
    "{person} accidentally loses {amount} {obj}.",
]

BUYS_TEMPLATES = [
    "{buyer} buys {amount} {obj} from {seller}.",
    "{buyer} purchases {amount} {obj} from {seller}.",
    "{buyer} pays {seller} for {amount} {obj}.",
]

SELLS_TEMPLATES = [
    "{seller} sells {amount} {obj} to {buyer}.",
    "{seller} sells {buyer} {amount} {obj}.",
]

# Question templates
QUESTION_TEMPLATES = [
    "Question: How many {obj} does {person} have?",
    "Question: What is {person}'s {obj_singular} count?",
    "Question: How many {obj} is {person} holding?",
    "Question: How many {obj} does {person} possess now?",
    "Question: How many {obj} does {person} end up with?",
    "Question: How many {obj} remain with {person}?",
]


@dataclass
class SyntheticStory:
    """A complete synthetic story with ground-truth operations."""

    story_text: str
    sentences: list[str]
    ops: list[dict[str, Any]]
    answer: int
    query_target: str
    num_events: int
    num_people: int
    num_objects: int


class SyntheticWorldGenerator:
    """Generates synthetic event-world stories with ground-truth operations.

    The generator builds stories programmatically: it maintains an internal
    state, generates natural-language sentences, and simultaneously records
    the corresponding SET/ADD/SUB/TRANSFER/QUERY operations.

    This ensures perfect ground truth for training and evaluation.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.person_objects: dict[str, dict[str, int]] = {}  # person -> {obj_type: count}
        self.ops: list[dict[str, Any]] = []
        self.sentences: list[str] = []
        self.people: list[str] = []
        self.object_types: list[str] = []
        self._person_counter: int = 0

    def reset(self):
        """Reset internal state for a new story."""
        self.person_objects = {}
        self.ops = []
        self.sentences = []
        self.people = []
        self.object_types = []
        self._person_counter = 0

    def pick_person(self, existing: bool = True) -> str:
        """Pick a person from the story."""
        if existing and self.people:
            return self.rng.choice(self.people)
        name = self.rng.choice(NAMES)
        if name not in self.people:
            self.people.append(name)
        return name

    def pick_object(self) -> str:
        """Pick an object type."""
        if self.object_types and self.rng.random() < 0.7:
            return self.rng.choice(self.object_types)
        obj = self.rng.choice(OBJECT_TYPES)
        if obj not in self.object_types:
            self.object_types.append(obj)
        return obj

    def get_count(self, person: str, obj: str) -> int:
        """Get current count for a person-object pair."""
        return self.person_objects.get(person, {}).get(obj, 0)

    def set_count(self, person: str, obj: str, value: int):
        """Set count and record op."""
        if person not in self.person_objects:
            self.person_objects[person] = {}
        self.person_objects[person][obj] = value
        self.ops.append({
            "op": "SET",
            "target": f"{person}.{obj}",
            "value": value,
        })

    def add_count(self, person: str, obj: str, delta: int):
        """Add to count and record op."""
        current = self.get_count(person, obj)
        new_value = current + delta
        if person not in self.person_objects:
            self.person_objects[person] = {}
        self.person_objects[person][obj] = new_value
        self.ops.append({
            "op": "ADD",
            "target": f"{person}.{obj}",
            "value": delta,
        })

    def sub_count(self, person: str, obj: str, delta: int):
        """Subtract from count and record op."""
        current = self.get_count(person, obj)
        new_value = current - delta
        if person not in self.person_objects:
            self.person_objects[person] = {}
        self.person_objects[person][obj] = new_value
        self.ops.append({
            "op": "SUB",
            "target": f"{person}.{obj}",
            "value": delta,
        })

    def transfer(self, from_person: str, to_person: str, obj: str, amount: int):
        """Transfer between people and record op."""
        self.sub_count(from_person, obj, amount)
        self.add_count(to_person, obj, amount)

        # Replace the last two ops (ADD/SUB) with a single TRANSFER op
        # Actually, keep them as explicit ADD/SUB for clarity,
        # OR add a TRANSFER op. Let's use TRANSFER for gives/buys/sells.
        # We already added ADD and SUB. Let's restructure:
        # Actually, the cleaner approach: remove the ADD/SUB and insert TRANSFER.
        self.ops.pop()  # Remove ADD
        self.ops.pop()  # Remove SUB
        self.ops.append({
            "op": "TRANSFER",
            "from": f"{from_person}.{obj}",
            "to": f"{to_person}.{obj}",
            "value": amount,
        })

    def generate_event_has(self) -> str:
        """Generate a 'Person has X' sentence."""
        person = self.pick_person(existing=False)
        obj = self.pick_object()
        amount = self.rng.randint(1, 20)
        self.set_count(person, obj, amount)

        template = self.rng.choice(HAS_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(person=person, amount=amount, obj=obj_form)

    def generate_event_gives(self) -> str:
        """Generate a 'Person gives to Person' sentence."""
        giver = self.pick_person(existing=True)
        receiver = self.pick_person(existing=True)
        if giver == receiver:
            # Pick a different receiver
            others = [p for p in self.people if p != giver]
            if not others:
                receiver = self.pick_person(existing=False)
            else:
                receiver = self.rng.choice(others)

        obj = self.pick_object()
        giver_count = self.get_count(giver, obj)
        max_give = max(1, giver_count)
        amount = self.rng.randint(1, min(max_give, 10))

        self.transfer(giver, receiver, obj, amount)

        template = self.rng.choice(GIVES_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(giver=giver, amount=amount, obj=obj_form, receiver=receiver)

    def generate_event_spends(self) -> str:
        """Generate a 'Person spends X' sentence."""
        person = self.pick_person(existing=True)
        obj = self.pick_object()
        current = self.get_count(person, obj)
        max_spend = max(1, current)
        amount = self.rng.randint(1, min(max_spend, 10))

        self.sub_count(person, obj, amount)

        template = self.rng.choice(SPENDS_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(person=person, amount=amount, obj=obj_form)

    def generate_event_finds(self) -> str:
        """Generate a 'Person finds X' sentence."""
        person = self.pick_person(existing=True)
        obj = self.pick_object()
        amount = self.rng.randint(1, 10)
        self.add_count(person, obj, amount)

        template = self.rng.choice(FINDS_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(person=person, amount=amount, obj=obj_form)

    def generate_event_loses(self) -> str:
        """Generate a 'Person loses X' sentence."""
        person = self.pick_person(existing=True)
        obj = self.pick_object()
        current = self.get_count(person, obj)
        max_lose = max(1, current)
        amount = self.rng.randint(1, min(max_lose, 5))

        self.sub_count(person, obj, amount)

        template = self.rng.choice(LOSES_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(person=person, amount=amount, obj=obj_form)

    def generate_event_buys(self) -> str:
        """Generate a 'Person buys from Person' sentence."""
        buyer = self.pick_person(existing=True)
        seller = self.pick_person(existing=True)
        if buyer == seller:
            others = [p for p in self.people if p != buyer]
            seller = self.rng.choice(others) if others else self.pick_person(existing=False)

        obj = self.pick_object()
        amount = self.rng.randint(1, 5)
        seller_count = self.get_count(seller, obj)
        actual_amount = min(amount, seller_count)
        if actual_amount <= 0:
            actual_amount = 1

        self.sub_count(seller, obj, actual_amount)
        self.add_count(buyer, obj, actual_amount)
        self.ops.pop()
        self.ops.pop()
        self.ops.append({
            "op": "TRANSFER",
            "from": f"{seller}.{obj}",
            "to": f"{buyer}.{obj}",
            "value": actual_amount,
        })

        template = self.rng.choice(BUYS_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if actual_amount == 1 else obj
        return template.format(buyer=buyer, amount=actual_amount, obj=obj_form, seller=seller)

    def generate_event_sells(self) -> str:
        """Generate a 'Person sells to Person' sentence."""
        seller = self.pick_person(existing=True)
        buyer = self.pick_person(existing=True)
        if buyer == seller:
            others = [p for p in self.people if p != seller]
            buyer = self.rng.choice(others) if others else self.pick_person(existing=False)

        obj = self.pick_object()
        seller_count = self.get_count(seller, obj)
        amount = self.rng.randint(1, min(max(1, seller_count), 5))

        self.sub_count(seller, obj, amount)
        self.add_count(buyer, obj, amount)
        self.ops.pop()
        self.ops.pop()
        self.ops.append({
            "op": "TRANSFER",
            "from": f"{seller}.{obj}",
            "to": f"{buyer}.{obj}",
            "value": amount,
        })

        template = self.rng.choice(SELLS_TEMPLATES)
        singular = get_singular(obj)
        obj_form = singular if amount == 1 else obj
        return template.format(seller=seller, amount=amount, obj=obj_form, buyer=buyer)

    def generate_question(self, person: str, obj: str) -> str:
        """Generate a question sentence."""
        self.ops.append({
            "op": "QUERY",
            "target": f"{person}.{obj}",
        })
        template = self.rng.choice(QUESTION_TEMPLATES)
        singular = get_singular(obj)
        return template.format(person=person, obj=obj, obj_singular=singular)

    def generate_story(self, num_events: int,
                       num_people: int | None = None,
                       num_objects: int | None = None) -> SyntheticStory:
        """Generate a complete synthetic story.

        Args:
            num_events: Number of events (excluding initial HAS and query).
            num_people: Target number of people (auto if None).
            num_objects: Target number of object types (auto if None).

        Returns:
            SyntheticStory with text, ops, answer, and metadata.
        """
        self.reset()

        num_people = num_people or max(2, num_events // 5 + 1)
        num_objects = num_objects or max(1, num_events // 10 + 1)

        # Pre-seed some people
        for _ in range(num_people):
            self.pick_person(existing=False)

        # Pre-seed some initial HAS events for variety
        init_count = min(num_people, self.rng.randint(1, num_people + 1))
        for _ in range(init_count):
            sent = self.generate_event_has()
            self.sentences.append(sent)

        # Event type weights (favors certain types)
        event_generators = [
            (self.generate_event_has, 0.05),      # less frequent after init
            (self.generate_event_gives, 0.25),
            (self.generate_event_spends, 0.20),
            (self.generate_event_finds, 0.20),
            (self.generate_event_loses, 0.10),
            (self.generate_event_buys, 0.10),
            (self.generate_event_sells, 0.10),
        ]

        events_generated = 0
        # Force some variety: ensure we have enough events
        actual_events = max(num_events, 1)

        while events_generated < actual_events:
            gen = self.rng.choices(
                [g for g, _ in event_generators],
                weights=[w for _, w in event_generators],
                k=1
            )[0]
            try:
                sent = gen()
                self.sentences.append(sent)
                events_generated += 1
            except Exception:
                # If something fails, try a different event type
                fallback = self.generate_event_has if gen != self.generate_event_has else self.generate_event_finds
                try:
                    sent = fallback()
                    self.sentences.append(sent)
                    events_generated += 1
                except Exception:
                    continue

        # Pick a query target: someone who has at least one tracked object
        tracked_people = list(self.person_objects.keys())
        if not tracked_people:
            # Fallback: add a person with something
            person = self.people[0] if self.people else "Latif"
            obj = self.object_types[0] if self.object_types else "coins"
            sent = self.generate_event_has()
            self.sentences.append(sent)
            tracked_people = [person]

        query_person = self.rng.choice(tracked_people)
        person_objs = self.person_objects.get(query_person, {})
        if person_objs:
            query_obj = self.rng.choice(list(person_objs.keys()))
        else:
            query_obj = self.object_types[0] if self.object_types else "coins"
            # Set something so we have a state
            self.set_count(query_person, query_obj, self.rng.randint(1, 10))
            sent = self.generate_event_has()
            self.sentences.append(sent)

        question = self.generate_question(query_person, query_obj)
        self.sentences.append(question)

        answer = self.get_count(query_person, query_obj)

        story_text = " ".join(self.sentences)

        return SyntheticStory(
            story_text=story_text,
            sentences=self.sentences,
            ops=self.ops,
            answer=answer,
            query_target=f"{query_person}.{query_obj}",
            num_events=len(self.sentences) - 1,  # minus the question
            num_people=len(self.people),
            num_objects=len(self.object_types),
        )

    def set_seed(self, seed: int):
        """Reset the random seed."""
        self.rng = random.Random(seed)
