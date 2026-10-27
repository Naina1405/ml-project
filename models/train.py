import json
from config.settings import settings
from models.baseline_classifier import BaselineIntentClassifier
from models.transformer_classifier import TransformerEmbeddingClassifier
from sklearn.metrics import accuracy_score, f1_score

def train_models():
    train_path = settings.DATA_DIR / "train.json"
    val_path = settings.DATA_DIR / "val.json"

    if not train_path.exists() or not val_path.exists():
        print("[Train] Dataset splits not found. Generating now...")
        from data.dataset_generator import generate_dataset
        from data.clean_dataset import clean_dataset
        from data.split_dataset import split_dataset
        generate_dataset()
        clean_dataset()
        split_dataset()

    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(val_path, "r", encoding="utf-8") as f:
        val_data = json.load(f)

    X_train = [d["user_prompt"] for d in train_data]
    y_train = [d["intent"] for d in train_data]

    X_val = [d["user_prompt"] for d in val_data]
    y_val = [d["intent"] for d in val_data]

    print(f"[Train] Training samples: {len(X_train)} | Validation samples: {len(X_val)}")

    # 1. Train Baseline
    print("\n--- Training Baseline (TF-IDF + Logistic Regression) ---")
    baseline = BaselineIntentClassifier()
    baseline.train(X_train, y_train)
    val_preds_base = baseline.predict_batch(X_val)
    acc_base = accuracy_score(y_val, val_preds_base)
    f1_base = f1_score(y_val, val_preds_base, average="macro")
    print(f"[Baseline Val] Accuracy: {acc_base:.4f} | Macro F1: {f1_base:.4f}")
    baseline.save("baseline_model.pkl")

    # 2. Train Advanced
    print("\n--- Training Advanced (Embedding + MLP Classifier) ---")
    advanced = TransformerEmbeddingClassifier()
    advanced.train(X_train, y_train)
    val_preds_adv = advanced.predict_batch(X_val)
    acc_adv = accuracy_score(y_val, val_preds_adv)
    f1_adv = f1_score(y_val, val_preds_adv, average="macro")
    print(f"[Advanced Val] Accuracy: {acc_adv:.4f} | Macro F1: {f1_adv:.4f}")
    advanced.save("advanced_model.pkl")

    print("\n[Train] Model training and validation complete.")

if __name__ == "__main__":
    train_models()
