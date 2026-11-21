
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

    works_keywords = [
        "travaux",
        "construction",
        "rehabilitation",
        "amenagement",
        "renforcement",
        "extension du reseau",
        "realisation",
        "reparation",
        "renouvellement",
        "reconstruction",
        "transfert des coffrets",
        "installation de reseaux"
    ]

    supply_keywords = [
        "fourniture",
        "acquisition",
        "achat",
        "approvisionnement",
        "equipement",
        "materiel",
        "fournir",
        "telegestion",
        "livraison"
    ]

    service_keywords = [
        "prestation",
        "mise a disposition", 
        "interimaires", 
        "enquetes",
        "services",
        "maintenance",
        "gardiennage",
        "securite",
        "nettoyage",
        "formation",
        "restauration",
        "assistance",
        "etude",
        "conseil",
        "hebergement",
        "location",
        "transport",
        "entretien",
        "suivi",
        "mise a disposition",
        "interimaires",
        "enquetes",
        "controle",
        "organisation",
        "exploitation",
        "accueil",
        "secretariat",
        "assistance technique",
        "restauration collective",
        "service de restauration",
        "collecte",
        "traitement des dechets",
        "conduite d'engins",
        "organisation",
        "exploitation",
        "etudes",
        "suivi des travaux",
        "affermage"
    ]

    scores = {
        "travaux": sum(word in title for word in works_keywords),
        "fournitures": sum(word in title for word in supply_keywords),
        "services": sum(word in title for word in service_keywords)
    }

    best_type = max(scores, key=scores.get)

    if scores[best_type] == 0:
        return "non déterminé"

    return best_type




def classify_domain(tender):
    """Identify the business domain using the title and buyer."""

    title = get_tender_title(tender)
    buyer = normalize_text(tender.get("buyer", ""))

    domain_keywords = {
        "Météorologie": [
            "meteorologie", "radar meteorologique",
            "radiosondage", "station meteorologique"
        ],
        "Eau et assainissement": [
            "adduction d'eau", "eau potable",
            "assainissement", "traitement des eaux",
            "reseau d'eau", "canalisation",
            "pompage", "irrigation",
            "station d'epuration", "step",
            "traitement des lixiviats", "equipement d'un puits",
            "puits", "aep", "barrage", "telegestion","station d'epuration",
            "station d epuration"
        ],
        "Électricité": [
            "electricite", "electrique", "haute tension",
            "basse tension", "mise a la terre",
            "reseau electrique", "eclairage public",
            "compteurs bt", "coffrets des compteurs",
            "prepaiement"
        ],
        "Informatique": [
            "informatique", "ordinateur", "logiciel",
            "serveur", "reseau informatique",
            "cybersecurite", "developpement web",
            "application", "base de donnees",
            "materiel informatique", "imprimante",
            "solution digitale", "solutions digitales",
            "courtier de paquet de reseau",
            "reseau informatique", "telegestion"
        ],
        "Sécurité": [
            "gardiennage", "securite",
            "surveillance", "protection"
        ],
        "BTP": [
            "construction", "batiment", "route",
            "piste", "rehabilitation", "travaux publics",
            "genie civil", "voirie", "pont",
            "route", "mise a niveau", "gros oeuvre",
            "etancheite", "tremie", "amenagement urbain",
            "voirie urbaine","rn 23", "rr205", "route nationale",
            "route regionale"
        ],
        "Santé et médical": [
            "medicament", "hopital",
            "materiel medical", "laboratoire medical",
            "laboratoire d'analyses", "diagnostic",
            "dispositif medical", "dispositifs medicaux",
            "soins", "analyses medicales",
            "radiotherapie", "oncologie", "secretariat medical",
            "accelerateur lineaire", "equipements medicaux"
        ],
        "Nettoyage et restauration": [
            "nettoyage", "proprete", "restauration",
            "repas", "traiteur", "catering",
            "collecte des dechets", "dechets menagers",
            "nettoiement", "deep cleaning",
            "mise a niveau des surfaces"
        ],
        "Formation et conseil": [
            "formation", "conseil", "accompagnement",
            "etude", "expertise", "audit"
        ],
        "Agriculture": [
            "agriculture", "agricole", "elevage",
            "semence", "engrais", "irrigation"
        ],
        "Transport et logistique": [
            "transport", "autobus", "bus", "vehicule",
            "voiture", "camion", "carburant",
            "conduite d'engins", "poids lourd",
            "pieces de rechange automobile",
            "ferroviaire", "chemin de fer",
            "gare", "ascenseur", "escalator"
        ],

        "Audiovisuel et communication": [
            "audiovisuel", "camera", "microphone",
            "sonorisation", "eclairage",
            "communication", "publicite",
            "organisation des salons", "evenementiel",
            "forum", "organisation d'evenements"
        ],
        "Fournitures générales": [
            "fourniture de bureau", "fournitures de bureau",
            "papier", "chaussures", "vetements",
            "scelles cables", "equipements divers"
        ],

        "Géomatique et topographie": [
            "topographie", "topographique",
            "geometre", "geometrique",
            "leve topographique", "cartographie"
        ],

        "Agriculture et aquaculture": [
            "aquaculture", "piscicole", "pisciculture",
            "ferme aquacole", "equipements piscicoles"
        ],

        "Environnement et déchets": [
            "traitement des dechets", "gestion des dechets",
            "centre d'enfouissement", "enfouissement",
            "valorisation des dechets", "lixiviats",
            "dechets menagers"
        ],
        "Études et statistiques": [
            "statistique", "statistiques",
            "enquete statistique", "enquetes statistiques",
            "analyse statistique", "etude statistique",
            "collecte de donnees", "sondage"
        ],
    }

    scores = {}

    for domain, keywords in domain_keywords.items():
        scores[domain] = sum(
            keyword in title for keyword in keywords
        )

    # Use the buyer as additional evidence for water/electricity.
    if "branche eau" in buyer:
        scores["Eau et assainissement"] += 2

    if "branche electricite" in buyer:
        scores["Électricité"] += 2

    best_domain = max(scores, key=scores.get)

    if scores[best_domain] == 0:
        return "Autre"

    return best_domain




# Map Moroccan cities and provinces to their official regions

LOCATION_TO_REGION = {
    # Tanger-Tétouan-Al Hoceïma
    "tanger": "Tanger-Tétouan-Al Hoceïma",
    "tetouan": "Tanger-Tétouan-Al Hoceïma",
    "chefchaouen": "Tanger-Tétouan-Al Hoceïma",
    "larache": "Tanger-Tétouan-Al Hoceïma",
    "al hoceima": "Tanger-Tétouan-Al Hoceïma",
    "ouazzane": "Tanger-Tétouan-Al Hoceïma",
    "fnideq": "Tanger-Tétouan-Al Hoceïma",
    "martil": "Tanger-Tétouan-Al Hoceïma",
    "ksar sghir": "Tanger-Tétouan-Al Hoceïma",

    # Oriental
    "oujda": "Oriental",
    "nador": "Oriental",
    "berkane": "Oriental",
    "taourirt": "Oriental",
    "guercif": "Oriental",
    "jerada": "Oriental",
    "driouch": "Oriental",
    "figuig": "Oriental",

    # Fès-Meknès
    "fes": "Fès-Meknès",
    "meknes": "Fès-Meknès",
    "taza": "Fès-Meknès",
    "ifrane": "Fès-Meknès",
    "sefrou": "Fès-Meknès",
    "moulay yacoub": "Fès-Meknès",
    "boulemane": "Fès-Meknès",
    "el hajeb": "Fès-Meknès",

    # Rabat-Salé-Kénitra
    "kenitra": "Rabat-Salé-Kénitra",
    "rabat": "Rabat-Salé-Kénitra",
    "sale": "Rabat-Salé-Kénitra",
    "temara": "Rabat-Salé-Kénitra",
    "skhirat": "Rabat-Salé-Kénitra",
    "sidi kacem": "Rabat-Salé-Kénitra",
    "sidi slimane": "Rabat-Salé-Kénitra",
    "khémisset": "Rabat-Salé-Kénitra",

    # Béni Mellal-Khénifra
    "azilal": "Béni Mellal-Khénifra",
    "beni mellal": "Béni Mellal-Khénifra",
    "khenifra": "Béni Mellal-Khénifra",
    "khouribga": "Béni Mellal-Khénifra",
    "fquih ben salah": "Béni Mellal-Khénifra",
    "kasba tadla": "Béni Mellal-Khénifra",

    # Casablanca-Settat
    "casablanca": "Casablanca-Settat",
    "settat": "Casablanca-Settat",
    "berrechid": "Casablanca-Settat",
    "el jadida": "Casablanca-Settat",
    "mohammedia": "Casablanca-Settat",
    "benslimane": "Casablanca-Settat",
    "mediouna": "Casablanca-Settat",
    "nouaceur": "Casablanca-Settat",
    "sidi bennour": "Casablanca-Settat",

    # Marrakech-Safi
    "marrakech": "Marrakech-Safi",
    "safi": "Marrakech-Safi",
    "essaouira": "Marrakech-Safi",
    "chichaoua": "Marrakech-Safi",
    "el kelâa des sraghna": "Marrakech-Safi",
    "rehamna": "Marrakech-Safi",
    "youssoufia": "Marrakech-Safi",

    # Drâa-Tafilalet
    "ouarzazate": "Drâa-Tafilalet",
    "errachidia": "Drâa-Tafilalet",
    "zagora": "Drâa-Tafilalet",
    "tinghir": "Drâa-Tafilalet",
    "midelt": "Drâa-Tafilalet",

    # Souss-Massa
    "agadir": "Souss-Massa",
    "taroudant": "Souss-Massa",
    "tiznit": "Souss-Massa",
    "tata": "Souss-Massa",
    "chtouka ait baha": "Souss-Massa",
    "inezgane": "Souss-Massa",

    # Guelmim-Oued Noun
    "guelmim": "Guelmim-Oued Noun",
    "tan-tan": "Guelmim-Oued Noun",
    "sidi ifni": "Guelmim-Oued Noun",
    "assazag": "Guelmim-Oued Noun",

    # Laâyoune-Sakia El Hamra
    "laayoune": "Laâyoune-Sakia El Hamra",
    "boujdour": "Laâyoune-Sakia El Hamra",
    "tarfaya": "Laâyoune-Sakia El Hamra",
    "es-semara": "Laâyoune-Sakia El Hamra",

    # Dakhla-Oued Eddahab
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

        normalized_location = location.replace("-", " ").replace("_", " ")
        normalized_place = normalized_place.replace("-", " ").replace("_", " ")

        if normalized_place in normalized_location:
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
