
import unicodedata
import re


def normalize_words(text):
    """Normalize text and extract meaningful keywords."""

    text = str(text or "").lower()

    # Remove accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    # Extract words
    words = re.findall(r"\b\w+\b", text)

    # Remove simple plural endings and common French stopwords
    stopwords = {"de", "des", "du", "la", "le", "les", "et", "en"}

    return {
        word[:-1] if word.endswith("s") else word
        for word in words
        if word not in stopwords
    }


def calculate_relevance(tender, company):

    score = 0

    # Use the complete title whenever available
    title = tender.get("full_title") or tender.get("title", "")

    # 1. Business domain (25 points)
    if tender["domain"] in company["domains"]:
        score += 25

    # 2. Tender type (15 points)
    if tender["type"] in company["preferred_types"]:
        score += 15

    # 3. Region (10 points)
    if any(
        region in company["regions"]
        for region in tender["region"]
    ):
        score += 10

    # 4. Budget compatibility and financial capacity
    budget = tender.get("estimated_budget")

    if budget is not None:

        # Budget compatibility (10 points)
        if company["min_budget"] <= budget <= company["max_budget"]:
            score += 10

        # Capital capacity (7.5 points)
        if budget <= company["capital"]:
            score += 7.5

        # Annual turnover capacity (7.5 points)
        if budget <= company["annual_turnover"]:
            score += 7.5

    # 5. Professional qualifications (25 points)
    title_words = normalize_words(title)

    for qualification in company["qualifications"]:

        qualification_words = normalize_words(qualification)

        if qualification_words and qualification_words.issubset(title_words):
            score += 25
            break

    return round(score, 2)
