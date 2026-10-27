import json
import random
from collections import defaultdict
from config.settings import settings

def split_dataset(input_file: str = "dataset_cleaned.json", train_ratio: float = 0.70, val_ratio: float = 0.15):
    clean_path = settings.DATA_DIR / input_file
    if not clean_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {clean_path}")

    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Group by intent for stratified split
    intent_groups = defaultdict(list)
    for item in data:
        intent_groups[item["intent"]].append(item)

    train_data, val_data, test_data = [], [], []

    random.seed(42)
    for intent, items in intent_groups.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        train_data.extend(items[:n_train])
        val_data.extend(items[n_train:n_train + n_val])
        test_data.extend(items[n_train + n_val:])

    for name, dataset in [("train", train_data), ("val", val_data), ("test", test_data)]:
        path = settings.DATA_DIR / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2)
        print(f"[Dataset Splitter] {name.capitalize()} split: {len(dataset)} samples saved to {path}")

if __name__ == "__main__":
    split_dataset()
