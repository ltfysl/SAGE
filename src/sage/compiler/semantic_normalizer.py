"""Semantic phrase normalizer — maps unseen phrasing to canonical operation intents.

Uses TF-IDF cosine similarity against canonical example sentences.
Does NOT require neural models or sentence-transformers.
"""

from __future__ import annotations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Canonical operation examples
CANONICAL_EXAMPLES = {
    "ADD": [
        "Latif gets 3 coins.",
        "Latif receives 3 coins.",
        "Latif finds 3 coins.",
        "Latif earns 3 coins.",
        "Latif gains 3 coins.",
        "Latif obtains 3 coins.",
        "Latif is given 3 coins.",
        "Latif discovers 3 coins.",
        "Latif collects 3 coins.",
        "Latif picks up 3 coins.",
        "Latif acquires 3 coins.",
        "Latif takes 3 coins.",
    ],
    "SUB": [
        "Latif spends 2 coins.",
        "Latif loses 2 coins.",
        "Latif uses 2 coins.",
        "Latif uses up 2 coins.",
        "Latif gives away 2 coins.",
        "Latif gets rid of 2 coins.",
        "Latif consumes 2 coins.",
        "Latif drops 2 coins.",
        "Latif misplaces 2 coins.",
        "Latif parts with 2 coins.",
        "Latif discards 2 coins.",
        "Latif wastes 2 coins.",
        "Latif throws away 2 coins.",
    ],
    "TRANSFER": [
        "Arno gives Latif 3 coins.",
        "Arno gives 3 coins to Latif.",
        "Arno hands Latif 3 coins.",
        "Arno hands 3 coins over to Latif.",
        "Latif receives 3 coins from Arno.",
        "Latif takes 3 coins from Arno.",
        "Arno passes 3 coins to Latif.",
        "Arno sends 3 coins to Latif.",
        "Arno transfers 3 coins to Latif.",
        "Arno offers Latif 3 coins.",
        "Latif gets given 3 coins by Arno.",
        "Arno provides Latif with 3 coins.",
        "Latif accepts 3 coins from Arno.",
    ],
    "SET": [
        "Latif has 5 coins.",
        "Latif starts with 5 coins.",
        "Latif owns 5 coins.",
        "Latif begins with 5 coins.",
        "Latif ends up with 5 coins.",
        "Latif is left with 5 coins.",
        "Latif holds 5 coins.",
        "Latif possesses 5 coins.",
        "Latif is holding 5 coins.",
        "Latif currently has 5 coins.",
        "Latif is in possession of 5 coins.",
    ],
    "QUERY": [
        "Question: How many coins does Latif have?",
        "Question: How many coins is Latif holding?",
        "Question: How many coins does Latif end up with?",
        "Question: How many coins is Latif left with?",
        "Question: What is Latif's coin count?",
    ],
    "NOOP": [
        "The weather is sunny today.",
        "A bird flies past the window.",
        "The clock strikes noon.",
        "Someone hums a quiet tune.",
        "Footsteps echo in the hallway.",
    ],
}


class SemanticNormalizer:
    """Maps unseen sentences to canonical operation intents via TF-IDF similarity."""

    def __init__(self):
        self.vectorizer = None
        self.intent_vectors = None
        self.intent_labels = None
        self.all_texts = None
        self._fitted = False

    def fit(self):
        """Build TF-IDF vectors from canonical examples."""
        all_examples = []
        all_labels = []
        for intent, examples in CANONICAL_EXAMPLES.items():
            for ex in examples:
                all_examples.append(ex)
                all_labels.append(intent)

        self.all_texts = all_examples
        self.intent_labels = all_labels

        self.vectorizer = TfidfVectorizer(
            max_features=2000, ngram_range=(1, 3),
            analyzer='char_wb', lowercase=True,
        )
        self.intent_vectors = self.vectorizer.fit_transform(all_examples)
        self._fitted = True
        return self

    def normalize(self, sentence: str, top_k: int = 3) -> list[tuple[str, float, str]]:
        """Normalize a sentence to the top-k most similar canonical intents.

        Returns list of (intent, similarity_score, matched_canonical) sorted by score descending.
        """
        if not self._fitted:
            self.fit()

        sent_vec = self.vectorizer.transform([sentence])
        similarities = cosine_similarity(sent_vec, self.intent_vectors)[0]

        # Get top-k indices, sorted by similarity descending
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            results.append((
                self.intent_labels[idx],
                float(similarities[idx]),
                self.all_texts[idx],
            ))
        return results

    def predict_intent(self, sentence: str, threshold: float = 0.3) -> tuple[str, float]:
        """Predict the best operation intent for a sentence.

        Returns (intent, confidence).
        If the best similarity score is below *threshold*, returns ("NOOP", score).
        """
        if not self._fitted:
            self.fit()

        sent_vec = self.vectorizer.transform([sentence])
        similarities = cosine_similarity(sent_vec, self.intent_vectors)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])
        best_intent = self.intent_labels[best_idx]

        if best_score < threshold:
            return ("NOOP", best_score)

        return (best_intent, best_score)
