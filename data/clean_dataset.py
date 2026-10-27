import json
from config.settings import settings

def clean_dataset(input_file: str = "dataset_raw.json", output_file: str = "dataset_cleaned.json"):
    raw_path = settings.DATA_DIR / input_file
    clean_path = settings.DATA_DIR / output_file

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset file not found: {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen_prompts = set()
    cleaned_data = []

    for item in data:
        prompt = item.get("user_prompt", "").strip()
        intent = item.get("intent", "").strip()
        
        # Validation checks
        if not prompt or not intent:
            continue
        if prompt.lower() in seen_prompts:
            continue
        
        seen_prompts.add(prompt.lower())
        cleaned_data.append(item)

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2)

    print(f"[Dataset Cleaner] Raw samples: {len(data)} | Cleaned unique samples: {len(cleaned_data)}")
    print(f"[Dataset Cleaner] Cleaned dataset saved to: {clean_path}")

if __name__ == "__main__":
    clean_dataset()
