from module_A.scoring.relevance import calculate_relevance


company = {
    "domains": ["Informatique"],
    "preferred_types": ["fournitures", "services"],
    "regions": ["Souss-Massa", "Casablanca-Settat"],
    "min_budget": 100000,
    "max_budget": 1000000,
    "capital": 500000,
    "annual_turnover": 2000000,
    "qualifications": [
        "maintenance informatique",
        "fourniture matériel informatique"
    ]
}


def make_tender(title):
    return {
        "title": title,
        "domain": "Informatique",
        "type": "services",
        "region": ["Casablanca-Settat"],
        "estimated_budget": 300000
    }


def test_exact_qualification_match():
    tender = make_tender("Maintenance informatique")
    assert calculate_relevance(tender, company) == 100


def test_qualification_with_different_wording():
    tender = make_tender("Maintenance du système informatique")
    assert calculate_relevance(tender, company) == 100


def test_partial_qualification_match():
    tender = make_tender("Maintenance des équipements")
    score = calculate_relevance(tender, company)
    assert score > 75
    assert score < 100


def test_unrelated_title():
    tender = make_tender("Nettoyage des locaux administratifs")
    score = calculate_relevance(tender, company)
    assert score == 75