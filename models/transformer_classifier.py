import pickle
import numpy as np
from typing import List, Tuple
from sklearn.neural_network import MLPClassifier
from config.settings import settings

class TransformerEmbeddingClassifier:
    """
    Advanced ML Classifier: SentenceTransformers / Dense Embeddings + MLP Neural Classifier
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.encoder = None
        self.classifier = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=400, random_state=42)
        self.is_trained = False
        self._init_encoder()

    def _init_encoder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"[TransformerClassifier] SentenceTransformers load info: {e}. Using TF-IDF Dense Embedder fallback.")
            self.encoder = None

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        if self.encoder:
            return self.encoder.encode(texts, show_progress_bar=False)
        else:
            # Fallback embedding mechanism via dense TF-IDF
            from sklearn.feature_extraction.text import TfidfVectorizer
            if not hasattr(self, "_tfidf_fallback"):
                self._tfidf_fallback = TfidfVectorizer(max_features=512)
                return self._tfidf_fallback.fit_transform(texts).toarray()
            return self._tfidf_fallback.transform(texts).toarray()

    def train(self, texts: List[str], labels: List[str]):
        embeddings = self._get_embeddings(texts)
        self.classifier.fit(embeddings, labels)
        self.is_trained = True

    def predict(self, text: str) -> Tuple[str, float]:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        emb = self._get_embeddings([text])
        probs = self.classifier.predict_proba(emb)[0]
        max_idx = probs.argmax()
        intent = self.classifier.classes_[max_idx]
        confidence = float(probs[max_idx])
        return intent, confidence

    def predict_batch(self, texts: List[str]) -> List[str]:
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        embeddings = self._get_embeddings(texts)
        return self.classifier.predict(embeddings).tolist()

    def save(self, filepath: str = "advanced_model.pkl"):
        save_path = settings.MODELS_DIR / filepath
        with open(save_path, "wb") as f:
            pickle.dump({"classifier": self.classifier, "is_trained": self.is_trained}, f)
        print(f"[Advanced ML] Saved transformer/embedding classifier to {save_path}")

    def load(self, filepath: str = "advanced_model.pkl"):
        load_path = settings.MODELS_DIR / filepath
        with open(load_path, "rb") as f:
            data = pickle.load(f)
            self.classifier = data["classifier"]
            self.is_trained = data["is_trained"]
