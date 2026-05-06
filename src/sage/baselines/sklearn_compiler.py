"""Sklearn-based SAGE compiler — classifies sentences into operation types.

Uses TF-IDF + LogisticRegression to classify each sentence as:
SET, ADD, SUB, TRANSFER, QUERY, or NOOP (noise/non-event).
Then uses the shared EntityExtractor to fill entity fields.
"""

from __future__ import annotations
import json, joblib, logging
from pathlib import Path
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

from sage.extraction.entity_extractor import EntityExtractor
from sage.extraction.sentence_splitter import split_sentences


class SklearnCompiler:
    """Sentence-level op type classifier + entity extractor."""

    VALID_LABELS = ["SET", "ADD", "SUB", "TRANSFER", "QUERY", "NOOP"]

    def __init__(self):
        self.pipeline = None
        self.label_encoder = LabelEncoder()
        self.extractor = EntityExtractor()
        self._fitted = False

    def fit(self, sentences: list[str], labels: list[str]):
        self.label_encoder.fit(self.VALID_LABELS)
        y = self.label_encoder.transform(labels)
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 3), analyzer='char_wb', lowercase=True)),
            ('clf', LogisticRegression(max_iter=1000, solver='lbfgs', C=1.0, class_weight='balanced')),
        ])
        self.pipeline.fit(sentences, y)
        self._fitted = True
        return self

    def predict_label(self, sentence: str) -> str:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        idx = self.pipeline.predict([sentence])[0]
        return self.label_encoder.inverse_transform([idx])[0]

    def predict_labels(self, sentences: list[str]) -> list[str]:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        indices = self.pipeline.predict(sentences)
        return list(self.label_encoder.inverse_transform(indices))

    def compile(self, story_text: str) -> tuple[list[dict], bool]:
        """Compile a story into operations using predicted sentence labels + entity extraction."""
        sentences = split_sentences(story_text)
        labels = self.predict_labels(sentences)
        return self.extractor.compile_story(story_text, labels)

    def save(self, path: str | Path):
        joblib.dump({'pipeline': self.pipeline, 'label_encoder': self.label_encoder}, str(path))

    def load(self, path: str | Path):
        data = joblib.load(str(path))
        self.pipeline = data['pipeline']
        self.label_encoder = data['label_encoder']
        self._fitted = True
        return self


def train_sklearn_compiler(train_sentences_path: Path, output_path: Path):
    sentences, labels = [], []
    with open(train_sentences_path) as f:
        for line in f:
            rec = json.loads(line)
            sentences.append(rec["sentence"])
            labels.append(rec["label"])
    print(f"Training on {len(sentences)} sentences...")
    compiler = SklearnCompiler()
    compiler.fit(sentences, labels)
    compiler.save(output_path)
    from collections import Counter
    preds = compiler.predict_labels(sentences[:1000])
    correct = sum(1 for p, l in zip(preds, labels[:1000]) if p == l)
    print(f"  Train accuracy (first 1000): {correct/10:.1f}%")
    print(f"Model saved to {output_path}")


def load_sklearn_compiler(model_path: Path) -> SklearnCompiler:
    compiler = SklearnCompiler()
    compiler.load(model_path)
    return compiler
