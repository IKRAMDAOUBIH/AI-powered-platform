
import json
import os


def normalize_tender(tender):
    """
    Convert a tender into the standard format expected by Module B.
    Missing information is represented by None (JSON null).
    """

    return {
        "id": tender.get("id") or tender.get("reference"),
        "reference": tender.get("reference"),
        "title": tender.get("full_title") or tender.get("title"),
        "description": tender.get("description"),
        "buyer": tender.get("buyer"),
        "type": tender.get("type"),
        "domain": tender.get("domain"),
        "region": tender.get("region"),
        "execution_location": tender.get("execution_location"),
        "estimated_budget": tender.get("estimated_budget"),
        "currency": "MAD" if tender.get("estimated_budget") is not None else None,
        "publication_date": tender.get("publication_date"),
        "submission_deadline": (
            tender.get("submission_deadline") or tender.get("deadline")
        ),
        "response_method": tender.get("response_method"),
        "provisional_deposit": tender.get("provisional_deposit"),
        "source": tender.get("source"),
        "url": tender.get("url"),
        "dce_url": tender.get("dce_url"),
        "avis_url": tender.get("avis_url"),
        "dce_size": tender.get("dce_size"),
        "relevance_score": tender.get("relevance_score"),
        "status": tender.get("status"),
    }


def normalize_tenders(tenders):
    return [normalize_tender(tender) for tender in tenders]


def export_for_module_b(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as file:
        tenders = json.load(file)

    normalized = normalize_tenders(tenders)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=4)

    print("Module B export completed successfully!")
    print("Number of tenders exported:", len(normalized))
    print("Output file:", output_path)
