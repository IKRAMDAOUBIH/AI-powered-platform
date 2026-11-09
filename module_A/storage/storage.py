import json
import os


def save_tenders(tenders, file_path):
    """Save enriched tenders to a JSON file."""

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            tenders,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"\n{len(tenders)} tenders saved successfully!")
    print("Output file:", file_path)