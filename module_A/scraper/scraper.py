
import json
import re
from pathlib import Path
from urllib.parse import urljoin
import argparse

from playwright.sync_api import sync_playwright


URL = (
    "https://www.marchespublics.gov.ma/"
    "index.php?page=entreprise.EntrepriseAdvancedSearch"
    "&AllCons&EnCours&searchAnnCons#2"
)
def save_tenders(tenders):
    output_path = (
        Path(__file__).resolve().parents[1]
        / "data" / "raw" / "live_tenders.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(tenders, file, ensure_ascii=False, indent=4)

    print(f"Progress saved: {len(tenders)} tenders")



def extract_field(text, pattern):
    """Extract a field using a regular expression."""
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def extract_between(text, start_label, end_label):
    """Extract text between two labeled fields."""
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


def parse_tender(card):
    """Extract structured information from one tender card."""

    text = card.inner_text()

    reference = extract_field(
        text,
        r"Référence\s*:\s*([^\r\n]+)"
    )

    title = extract_field(
        text,
        r"OBJET\s*:\s*(.*?)(?=\s*Estimation TTC|\s*ACHETEUR PUBLIC|"
        r"\s*DATE LIMITE DE REMISE DES PLIS|\s*LIEU D'EXÉCUTION|$)"
    )

    budget_text = extract_field(
        text,
        r"Estimation TTC \(en DH\)\s*:\s*([0-9\s.,]+)"
    )

    buyer = extract_field(
        text,
        r"ACHETEUR PUBLIC\s*:\s*([^\r\n]+)"
    )

    deadline = extract_field(
        text,
        r"DATE LIMITE DE REMISE DES PLIS\s*(.*?)"
        r"(?=\s*LIEU D'EXÉCUTION)"
    )

    location = extract_field(
        text,
        r"LIEU D'EXÉCUTION\s*([^\r\n]+)"
    )

    title = re.sub(r"\s+", " ", title).strip() if title else None
    deadline = re.sub(r"\s+", " ", deadline).strip() if deadline else None

    budget = None

    if budget_text:
        budget = float(
            budget_text.replace(" ", "").replace(".", "").replace(",", ".")
        )

    link = card.locator(
        'a[href*="EntrepriseDetailsConsultation"]'
    ).first

    tender_url = None

    if link.count() > 0:
        tender_url = urljoin(URL, link.get_attribute("href"))

    return {
        "reference": reference,
        "title": title,
        "estimated_budget": budget,
        "buyer": buyer,
        "deadline": deadline,
        "execution_location": location,
        "source": "marchespublics.gov.ma",
        "url": tender_url
    }


def enrich_tender(page, tender):
    """Visit a tender detail page and extract additional information."""

    if not tender.get("url"):
        print("No detail URL found. Skipping enrichment.")
        return tender

    try:
        page.goto(
            tender["url"],
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(1500)

        content = page.locator("body").inner_text()

        details = {
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

        dce_link = page.locator(
            'a[href*="EntrepriseDemandeTelechargementDce"]'
        )

        avis_link = page.locator(
            'a[href*="EntrepriseDownloadAvisJAL"]'
        )

        details["dce_url"] = (
            urljoin(page.url, dce_link.first.get_attribute("href"))
            if dce_link.count() > 0 else None
        )

        details["avis_url"] = (
            urljoin(page.url, avis_link.first.get_attribute("href"))
            if avis_link.count() > 0 else None
        )

        size_match = re.search(
            r"Dossier de consultation\s*-\s*([\d.,]+\s*Mo)",
            content,
            re.IGNORECASE
        )

        details["dce_size"] = (
            size_match.group(1) if size_match else None
        )

        # Keep the listing title if the detail-page title is unavailable.
        if not details["full_title"]:
            details["full_title"] = tender.get("title")

        tender.update(details)

    except Exception as error:
        print(f"Could not enrich tender {tender.get('reference')}: {error}")

    return tender

def scrape_tenders(max_pages=5, scrape_all=False):
    """Scrape multiple listing pages and enrich all collected tenders."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        output_path = (
            Path(__file__).resolve().parents[1]
            / "data" / "raw" / "live_tenders.json"
        )

        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as file:
                tenders = json.load(file)
            print(f"Loaded {len(tenders)} existing tenders.")
        else:
            tenders = []

        seen_urls = {
            tender.get("url") or tender.get("reference")
            for tender in tenders
            if tender.get("url") or tender.get("reference")
        }

        try:
            # STEP 1: Open the listing page.
            page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=90000
            )
            print("HTTP status:", page.url)
            print("Page title:", page.title())
            print("Page content:", page.locator("body").inner_text()[:2000])

            page.locator("div.item.tender_item").first.wait_for(
                timeout=30000
            )

            # STEP 2: Collect tenders from multiple pages.
            page_number = 1

            while True:

                print(f"\n===== LISTING PAGE {page_number} =====")

                cards = page.locator("div.item.tender_item")
                card_count = cards.count()

                print("Tenders found on this page:", card_count)

                first_card_text = cards.first.inner_text()

                for i in range(card_count):
                    tender = parse_tender(cards.nth(i))
                    unique_key = tender.get("url") or tender.get("reference")

                    if unique_key and unique_key not in seen_urls:
                        tenders.append(tender)
                        seen_urls.add(unique_key)


                print("Total unique tenders collected:", len(tenders))
                save_tenders(tenders)

                # Stop if we reached the configured page limit.
                # Stop if we reached the configured page limit.
                if not scrape_all and page_number >= max_pages:
                    break

                # STEP 3: Navigate to the next listing page.
                next_button = page.locator(
                    "#ctl0_CONTENU_PAGE_resultSearch_PagerTop_ctl2"
                )

                if next_button.count() == 0:
                    print("No next page available.")
                    break

                print("Moving to the next page...")

                next_button.click()

                try:
                    page.wait_for_function(
                        """oldText => {
                            const card = document.querySelector(
                                "div.item.tender_item"
                            );
                            return card && card.innerText !== oldText;
                        }""",
                        arg=first_card_text,
                        timeout=60000
                    )
                except Exception:
                    print("Warning: Page transition was not confirmed.")
                    print("Checking whether the listing page changed...")

                    page.wait_for_timeout(5000)

                    current_first_card = page.locator(
                        "div.item.tender_item"
                    ).first.inner_text()

                    if current_first_card == first_card_text:
                        print("Page did not change. Stopping safely.")
                        break

                page.wait_for_timeout(1500)
                page_number += 1

            # STEP 4: Enrich collected tenders using their detail pages.
            print("\n===== DETAIL PAGE ENRICHMENT =====")

            for i, tender in enumerate(tenders, start=1):
                print(
                    f"\nEnriching {i}/{len(tenders)}: "
                    f"{tender.get('reference')}"
                )

                enrich_tender(page, tender)
                save_tenders(tenders)
                page.wait_for_timeout(1000)
        finally:
            browser.close()

    # STEP 5: Save enriched records.
    output_path = (
        Path(__file__).resolve().parents[1]
        / "data" / "raw" / "live_tenders.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(tenders, file, ensure_ascii=False, indent=4)

    print("\n===== FINAL SCRAPING RESULTS =====")
    print("Total unique tenders scraped:", len(tenders))

    for tender in tenders:
        print("\nReference:", tender["reference"])
        print("Title:", tender.get("full_title") or tender["title"])
        print("Budget:", tender["estimated_budget"])
        print("Buyer:", tender["buyer"])
        print(
            "Deadline:",
            tender.get("submission_deadline") or tender["deadline"]
        )
        print("Provisional deposit:", tender.get("provisional_deposit"))
        print("DCE URL:", tender.get("dce_url"))

    print("\nEnriched data saved to:", output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Moroccan public tenders"
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Number of listing pages to scrape (default: 5)"
    )
    parser.add_argument(
    "--all",
    action="store_true",
    help="Scrape all available listing pages"
    )

    args = parser.parse_args()

    if args.pages < 1:
        parser.error("--pages must be at least 1")

    scrape_tenders(max_pages=args.pages, scrape_all=args.all)