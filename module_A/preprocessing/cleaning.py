
import json


def load_tenders(file_path):
    """
    Load tender announcements from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        tenders = json.load(file)

    return tenders


def clean_tenders(tenders):
    """
    Normalize tender data and remove duplicate announcements.
    """
    cleaned_tenders = []
    seen_ids = set()

    for tender in tenders:

        # Normalize text fields
        tender = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in tender.items()
        }

        # Skip records without an ID
        tender_id = tender.get("id")

        if not tender_id:
            continue

        # Remove duplicates
        if tender_id in seen_ids:
            continue

        seen_ids.add(tender_id)
        cleaned_tenders.append(tender)

    return cleaned_tenders
