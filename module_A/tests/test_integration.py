
import json

from module_A.integration.schema import normalize_tender, normalize_tenders


def test_normalize_tender():
    tender = {
        "reference": "TEST-001",
        "title": "Fourniture de matériel informatique",
        "buyer": "Université Ibn Zohr",
        "estimated_budget": 450000,
        "deadline": "20 DEC 2026",
        "type": "fournitures",
        "domain": "Informatique",
        "region": ["Souss-Massa"],
        "source": "marchespublics.gov.ma",
        "url": "https://example.com/tender"
    }

    result = normalize_tender(tender)

    assert result["id"] == "TEST-001"
    assert result["reference"] == "TEST-001"
    assert result["currency"] == "MAD"
    assert result["submission_deadline"] == "20 DEC 2026"
    assert result["domain"] == "Informatique"


def test_normalize_tenders():
    tenders = [
        {"reference": "TEST-001", "title": "Tender 1"},
        {"reference": "TEST-002", "title": "Tender 2"}
    ]

    result = normalize_tenders(tenders)

    assert len(result) == 2
    assert result[0]["id"] == "TEST-001"
    assert result[1]["id"] == "TEST-002"


def test_exported_json_contains_ten_tenders():
    path = "module_A/data/processed/module_b_tenders.json"

    with open(path, "r", encoding="utf-8") as file:
        tenders = json.load(file)

    assert len(tenders) == 10
    assert len({tender["id"] for tender in tenders}) == 10
