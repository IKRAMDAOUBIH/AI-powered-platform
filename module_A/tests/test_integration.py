
import json

from module_A.integration.schema import (
    export_for_module_b,
    normalize_tender,
    normalize_tenders
)


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


def test_export_for_module_b(tmp_path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"

    source_tenders = [
        {
            "reference": "TEST-001",
            "title": "IT maintenance",
            "relevance_score": 100
        },
        {
            "reference": "TEST-002",
            "title": "Computer equipment",
            "relevance_score": 85
        }
    ]

    with open(input_path, "w", encoding="utf-8") as file:
        json.dump(source_tenders, file)

    export_for_module_b(str(input_path), str(output_path))

    with open(output_path, "r", encoding="utf-8") as file:
        exported = json.load(file)

    assert len(exported) == 2
    assert exported[0]["id"] == "TEST-001"
    assert exported[1]["id"] == "TEST-002"
    assert exported[0]["relevance_score"] == 100
