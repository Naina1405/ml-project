import pickle
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from config.settings import settings

class BaselineIntentClassifier:
    """
    Baseline ML Classifier: TF-IDF + Logistic Regression
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=500, C=1.0)
        self.is_trained = False

    def train(self, texts: List[str], labels: List[str]):
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.is_trained = True

    def predict(self, text: str) -> Tuple[str, float]:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        max_idx = probs.argmax()
        intent = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        return intent, confidence

    def predict_batch(self, texts: List[str]) -> List[str]:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform(texts)
        return self.model.predict(X).tolist()

    def save(self, filepath: str = "baseline_model.pkl"):
        save_path = settings.MODELS_DIR / filepath
        with open(save_path, "wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "model": self.model}, f)
        print(f"[Baseline ML] Saved baseline model to {save_path}")

    def load(self, filepath: str = "baseline_model.pkl"):
        load_path = settings.MODELS_DIR / filepath
        with open(load_path, "rb") as f:
            data = pickle.load(f)
            self.vectorizer = data["vectorizer"]
            self.model = data["model"]
            self.is_trained = True
