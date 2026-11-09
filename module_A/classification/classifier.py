
import unicodedata


VALID_TYPES = ["travaux", "fournitures", "services"]


def normalize_text(text):
    """Convert text to lowercase and remove accents."""

    text = str(text or "").lower()

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text

def get_tender_title(tender):
    """Use the complete title when available."""

    return normalize_text(
        tender.get("full_title") or tender.get("title", "")
    )


def classify_type(tender):
    """Identify the type of public procurement."""

    title = get_tender_title(tender)

    # Works
    works_keywords = [
        "construction",
        "travaux",
        "rehabilitation",
        "amenagement",
        "renforcement des reseaux",
        "construction de la route"
    ]

    # Supplies
    supply_keywords = [
        "fourniture",
        "acquisition",
        "achat",
        "materiel",
        "serveurs",
        "equipement"
    ]

    # Services
    service_keywords = [
        "maintenance",
        "gardiennage",
        "securite",
        "nettoyage",
        "formation",
        "prestations de service"
    ]

    if any(word in title for word in works_keywords):
        return "travaux"

    if any(word in title for word in supply_keywords):
        return "fournitures"

    if any(word in title for word in service_keywords):
        return "services"

    return "non déterminé"



def classify_domain(tender):
    """Identify the business domain using the title and buyer."""

    title = get_tender_title(tender)
    buyer = normalize_text(tender.get("buyer", ""))

    # Meteorology
    if any(word in title for word in [
        "radar meteorologique",
        "meteorologie",
        "radiosondage",
        "station meteorologique",
        "prevision meteorologique"
    ]):
        return "Météorologie"

    # Water and sanitation
    if any(word in title for word in [
        "adduction d'eau",
        "approvisionnement en eau",
        "eau potable",
        "assainissement",
        "traitement des eaux",
        "production d'eau"
    ]) or "branche eau" in buyer:
        return "Eau et assainissement"

    # Electricity
    if any(word in title for word in [
        "electricite",
        "electrique",
        "tension",
        "mise a la terre",
        "alimentation electrique",
        "reseaux electriques",
        "reseaux d'electricite"
    ]) or "branche electricite" in buyer:
        return "Électricité"

    # Information technology
    if any(word in title for word in [
        "informatique",
        "ordinateur",
        "logiciel",
        "serveur",
        "stockage",
        "videosurveillance"
    ]):
        return "Informatique"

    # Security
    if any(word in title for word in [
        "gardiennage",
        "securite"
    ]):
        return "Sécurité"

    # Construction and public works
    if any(word in title for word in [
        "construction",
        "batiment",
        "route",
        "pistes",
        "rehabilitation",
        "travaux"
    ]):
        return "BTP"

    return "Autre"



# Map Moroccan cities and provinces to their official regions
LOCATION_TO_REGION = {
    "tanger": "Tanger-Tétouan-Al Hoceïma",
    "tetouan": "Tanger-Tétouan-Al Hoceïma",
    "chefchaouen": "Tanger-Tétouan-Al Hoceïma",
    "larache": "Tanger-Tétouan-Al Hoceïma",
    "al hoceima": "Tanger-Tétouan-Al Hoceïma",

    "oujda": "Oriental",
    "nador": "Oriental",
    "berkane": "Oriental",
    "taourirt": "Oriental",

    "fes": "Fès-Meknès",
    "meknes": "Fès-Meknès",
    "taza": "Fès-Meknès",
    "ifrane": "Fès-Meknès",

    "kenitra": "Rabat-Salé-Kénitra",
    "rabat": "Rabat-Salé-Kénitra",
    "sale": "Rabat-Salé-Kénitra",
    "temara": "Rabat-Salé-Kénitra",

    "azilal": "Béni Mellal-Khénifra",
    "beni mellal": "Béni Mellal-Khénifra",
    "khenifra": "Béni Mellal-Khénifra",
    "khouribga": "Béni Mellal-Khénifra",

    "casablanca": "Casablanca-Settat",
    "settat": "Casablanca-Settat",
    "berrechid": "Casablanca-Settat",
    "el jadida": "Casablanca-Settat",
    "mohammedia": "Casablanca-Settat",

    "marrakech": "Marrakech-Safi",
    "safi": "Marrakech-Safi",
    "essaouira": "Marrakech-Safi",

    "ouarzazate": "Drâa-Tafilalet",
    "errachidia": "Drâa-Tafilalet",
    "zagora": "Drâa-Tafilalet",

    "agadir": "Souss-Massa",
    "taroudant": "Souss-Massa",
    "tiznit": "Souss-Massa",
    "tata": "Souss-Massa",

    "guelmim": "Guelmim-Oued Noun",
    "tan-tan": "Guelmim-Oued Noun",
    "sidi ifni": "Guelmim-Oued Noun",

    "laayoune": "Laâyoune-Sakia El Hamra",
    "boujdour": "Laâyoune-Sakia El Hamra",

    "dakhla": "Dakhla-Oued Eddahab",
    "aousserd": "Dakhla-Oued Eddahab"
}


def classify_region(tender):
    """Identify all Moroccan regions covered by a tender."""

    location = normalize_text(
        tender.get("execution_location", "")
    )

    detected_regions = set()

    for place, region in LOCATION_TO_REGION.items():

        normalized_place = normalize_text(place)

        if normalized_place in location:
            detected_regions.add(region)

    if detected_regions:
        return sorted(detected_regions)

    return ["Région non identifiée"]



def classify_tenders(tenders):
    """Classify all tender announcements."""

    classified_tenders = []

    for tender in tenders:

        tender["type"] = classify_type(tender)
        tender["domain"] = classify_domain(tender)
        tender["region"] = classify_region(tender)

        classified_tenders.append(tender)

    return classified_tenders
