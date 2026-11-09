
import json
from pathlib import Path
import re
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


# Load the scraped tender records
data_path = (
    Path(__file__).resolve().parents[1]
    / "data" / "raw" / "live_tenders.json"
)

with open(data_path, "r", encoding="utf-8") as file:
    tenders = json.load(file)


# Select the first tender
tender = tenders[0]

print("Tender reference:", tender["reference"])
print("Tender URL:", tender["url"])


if not tender.get("url"):
    raise ValueError("No detail-page URL found for this tender.")

def extract_between(text, start_label, end_label):
    pattern = (
        re.escape(start_label)
        + r"\s*:\s*(.*?)"
        + r"(?=\s*"
        + re.escape(end_label)
        + r"\s*:?)"
    )

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        return " ".join(match.group(1).split())

    return None
# Open its detail page
with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(
        tender["url"],
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    print("\n===== DETAIL PAGE TITLE =====")
    print(page.title())

    print("\n===== DETAIL PAGE CONTENT =====")

    content = page.locator("body").inner_text()
    # Extract structured information
    tender_details = {
        "full_title": extract_between(
            content, "Objet", "Date de mise en ligne"
        ),
        "publication_date": extract_between(
            content,
            "Date de mise en ligne",
            "Date et heure limite de remise des plis"
        ),
        "submission_deadline": extract_between(
            content,
            "Date et heure limite de remise des plis",
            "Modalités de réponse"
        ),
        "response_method": extract_between(
            content,
            "Modalités de réponse",
            "Caution provisoire"
        ),
        "provisional_deposit": extract_between(
            content,
            "Caution provisoire",
            "SE PREPARER A L'AVANCE A REPONDRE"
        )
    }

    # Extract document information
    dce_link = page.locator(
        'a[href*="EntrepriseDemandeTelechargementDce"]'
    )

    avis_link = page.locator(
        'a[href*="EntrepriseDownloadAvisJAL"]'
    )

    tender_details["dce_url"] = (
        urljoin(page.url, dce_link.first.get_attribute("href"))
        if dce_link.count() > 0 else None
    )

    tender_details["avis_url"] = (
        urljoin(page.url, avis_link.first.get_attribute("href"))
        if avis_link.count() > 0 else None
    )

    size_match = re.search(
        r"Dossier de consultation\s*-\s*([\d.,]+\s*Mo)",
        content,
        re.IGNORECASE
    )

    tender_details["dce_size"] = (
        size_match.group(1) if size_match else None
    )

    print("\n===== STRUCTURED TENDER DETAILS =====")

    for key, value in tender_details.items():
        print(f"{key}: {value}")

    print(content[:10000])

    print("\n===== DETAIL PAGE LINKS =====")

    links = page.locator("a").all()

    for link in links:
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if href:
            print(f"TEXT: {text}")
            print(f"URL: {href}")
            print("-" * 50)

    browser.close()
