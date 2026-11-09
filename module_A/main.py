
import os

from module_A.preprocessing.cleaning import load_tenders, clean_tenders
from module_A.classification.classifier import classify_tenders
from module_A.scoring.relevance import calculate_relevance
from module_A.storage.storage import save_tenders


# File paths
tenders_path = "module_A/data/raw/live_tenders.json"
company_path = "module_A/data/company_profile.json"
output_path = "module_A/data/processed/live_enriched_tenders.json"


# 1. Load company profile
company = load_tenders(company_path)

print("Company profile loaded:", company["name"])


# 2. Load real tender data
tenders = load_tenders(tenders_path)

print("Original number of tenders:", len(tenders))


# 3. Adapt live data to our pipeline
for tender in tenders:
    tender["id"] = tender["reference"]


# 4. Clean data
cleaned_tenders = clean_tenders(tenders)

print("Number of tenders after cleaning:", len(cleaned_tenders))


# 5. Classify tenders
classified_tenders = classify_tenders(cleaned_tenders)

print("\n===== CLASSIFICATION RESULTS =====")

for tender in classified_tenders:
    display_title = tender.get("full_title") or tender.get("title", "N/A")

    print("\nID:", tender["id"])
    print("Title:", display_title)
    print("Type:", tender["type"])
    print("Domain:", tender["domain"])
    print("Execution location:", tender.get("execution_location"))
    print("Region:", tender["region"])


# 6. Calculate relevance scores
print("\n===== RELEVANCE SCORING =====")

for tender in classified_tenders:
    score = calculate_relevance(tender, company)

    tender["relevance_score"] = score
    tender["status"] = (
        "Relevant" if score >= 70
        else "Not sufficiently relevant"
    )

    print("\nTender ID:", tender["id"])
    print("Company:", company["name"])
    print("Relevance score:", str(score) + "%")
    print("Status:", tender["status"])


# 7. Save enriched tenders
save_tenders(classified_tenders, output_path)
