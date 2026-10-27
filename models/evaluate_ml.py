import json
from config.settings import settings
from models.baseline_classifier import BaselineIntentClassifier
from models.transformer_classifier import TransformerEmbeddingClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

def evaluate_models() -> dict:
    test_path = settings.DATA_DIR / "test.json"
    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset not found at {test_path}")

    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    X_test = [d["user_prompt"] for d in test_data]
    y_test = [d["intent"] for d in test_data]

    # Load Baseline
    baseline = BaselineIntentClassifier()
    baseline.load("baseline_model.pkl")
    base_preds = baseline.predict_batch(X_test)

    # Load Advanced
    advanced = TransformerEmbeddingClassifier()
    advanced.load("advanced_model.pkl")
    adv_preds = advanced.predict_batch(X_test)

    # Calculate metrics
    base_acc = accuracy_score(y_test, base_preds)
    base_p, base_r, base_f1, _ = precision_recall_fscore_support(y_test, base_preds, average="macro")

    adv_acc = accuracy_score(y_test, adv_preds)
    adv_p, adv_r, adv_f1, _ = precision_recall_fscore_support(y_test, adv_preds, average="macro")

    results = {
        "baseline": {
            "accuracy": round(float(base_acc), 4),
            "precision": round(float(base_p), 4),
            "recall": round(float(base_r), 4),
            "f1_score": round(float(base_f1), 4)
        },
        "advanced": {
            "accuracy": round(float(adv_acc), 4),
            "precision": round(float(adv_p), 4),
            "recall": round(float(adv_r), 4),
            "f1_score": round(float(adv_f1), 4)
        }
    }

    print("==================================================")
    print("           ML INTENT CLASSIFICATION EVALUATION   ")
    print("==================================================")
    print(f"Baseline (TF-IDF + LogReg):    Acc={base_acc:.4f} | Prec={base_p:.4f} | Rec={base_r:.4f} | F1={base_f1:.4f}")
    print(f"Advanced (Embedding + MLP):    Acc={adv_acc:.4f} | Prec={adv_p:.4f} | Rec={adv_r:.4f} | F1={adv_f1:.4f}")
    print("==================================================\n")

    # Save metrics JSON to evaluation folder
    eval_file = settings.EVALUATION_DIR / "ml_evaluation_results.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    evaluate_models()
