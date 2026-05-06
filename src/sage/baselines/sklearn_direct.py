"""Sklearn-based direct answer baseline.

Uses TF-IDF + Ridge regression to predict numeric answers directly from story text.
Since answers are integers, we round the regression output.
"""

from __future__ import annotations
import json, re, joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline


class SklearnDirectModel:
    """Direct answer prediction using TF-IDF + Ridge regression.
    
    Trained to map: story text → numeric answer
    """
    
    def __init__(self):
        self.pipeline = None
        self._fitted = False
    
    def fit(self, stories: list[str], answers: list[float]):
        """Train the direct answer model."""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000, ngram_range=(1, 3),
                analyzer='char_wb', lowercase=True,
            )),
            ('reg', Ridge(alpha=1.0)),
        ])
        self.pipeline.fit(stories, answers)
        self._fitted = True
        return self
    
    def predict(self, story: str) -> float:
        """Predict answer for a story."""
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        return self.pipeline.predict([story])[0]
    
    def answer(self, story: str) -> str:
        """Return string answer (rounded integer)."""
        pred = self.predict(story)
        return str(int(round(pred)))
    
    def save(self, path: str | Path):
        joblib.dump({'pipeline': self.pipeline}, str(path))
    
    def load(self, path: str | Path):
        data = joblib.load(str(path))
        self.pipeline = data['pipeline']
        self._fitted = True
        return self


def train_sklearn_direct(train_jsonl_path: Path, output_path: Path):
    """Train sklearn direct model on story-level data."""
    stories = []
    answers = []
    with open(train_jsonl_path) as f:
        for line in f:
            rec = json.loads(line)
            stories.append(rec["story"])
            answers.append(float(rec["answer"]))
    
    print(f"Training on {len(stories)} stories...")
    model = SklearnDirectModel()
    model.fit(stories, answers)
    model.save(output_path)
    
    # Quick check
    preds = [model.predict(s) for s in stories[:100]]
    mae = sum(abs(p - a) for p, a in zip(preds, answers[:100])) / 100
    print(f"  MAE (first 100): {mae:.2f}")
    print(f"Model saved to {output_path}")
