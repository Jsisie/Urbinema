import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "app/src/main/assets/catalog/catalog.json"
V3 = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
I18N = ROOT / "tools/i18n_en"


def blank(value):
    text = (value or "").strip()
    return text or None


COUNTRIES = {
    "FRANCE": "France", "ITALY": "Italy", "JAPAN": "Japan", "USA": "United States",
    "UK": "United Kingdom", "GERMANY": "Germany", "RUSSIA": "Russia", "SWEDEN": "Sweden",
    "IRAN": "Iran", "SENEGAL": "Senegal", "SOUTH_KOREA": "South Korea", "INDIA": "India",
    "CHINA": "China", "BRAZIL": "Brazil", "MEXICO": "Mexico", "SPAIN": "Spain",
    "POLAND": "Poland", "DENMARK": "Denmark", "CZECH": "Czechia", "HUNGARY": "Hungary",
    "ARGENTINA": "Argentina", "EGYPT": "Egypt", "AUSTRALIA": "Australia", "CANADA": "Canada",
    "BELGIUM": "Belgium", "GREECE": "Greece", "TURKEY": "Turkey", "HONG_KONG": "Hong Kong",
    "TAIWAN": "Taiwan", "ALGERIA": "Algeria", "MALI": "Mali", "CUBA": "Cuba",
    "AUSTRIA": "Austria", "PORTUGAL": "Portugal", "CHILE": "Chile",
    "NEW_ZEALAND": "New Zealand", "UKRAINE": "Ukraine", "FINLAND": "Finland",
    "THAILAND": "Thailand", "PHILIPPINES": "Philippines", "BURKINA_FASO": "Burkina Faso",
    "ANGOLA": "Angola", "NIGERIA": "Nigeria", "PALESTINE": "Palestine", "LEBANON": "Lebanon",
    "SINGAPORE": "Singapore", "INDONESIA": "Indonesia", "BOLIVIA": "Bolivia",
    "ETHIOPIA": "Ethiopia", "MAURITANIA": "Mauritania", "CAMEROON": "Cameroon",
    "ZIMBABWE": "Zimbabwe", "CHAD": "Chad", "ESTONIA": "Estonia", "LITHUANIA": "Lithuania",
    "LATVIA": "Latvia", "NORWAY": "Norway", "TUNISIA": "Tunisia", "ISRAEL": "Israel",
    "GEORGIA": "Georgia", "ROMANIA": "Romania", "NETHERLANDS": "Netherlands",
    "VIETNAM": "Vietnam", "CAMBODIA": "Cambodia", "SOUTH_AFRICA": "South Africa",
    "YUGOSLAVIA": "Yugoslavia", "SWITZERLAND": "Switzerland",
}

CONTINENTS = {
    "EUROPE": "Europe", "ASIA": "Asia", "NORTH_AMERICA": "North America",
    "SOUTH_AMERICA": "South America", "AFRICA": "Africa", "OCEANIA": "Oceania",
}

GENRES = {
    "DRAME": "Drama", "GUERRE": "War", "HISTORIQUE": "Historical", "POLICIER": "Crime",
    "DOCUMENTAIRE": "Documentary", "COMEDIE": "Comedy", "WESTERN": "Western",
    "HORREUR": "Horror", "SCIENCE_FICTION": "Science fiction", "ROMANCE": "Romance",
    "THRILLER": "Thriller", "MUSICAL": "Musical", "ANIMATION": "Animation",
    "AVENTURE": "Adventure", "FILM_NOIR": "Film noir", "ACTION": "Action",
    "ARTS_MARTIAUX": "Martial arts", "BIOGRAPHIQUE": "Biographical",
    "CATASTROPHE": "Disaster", "COMEDIE_DRAMATIQUE": "Dramedy", "CRIME": "Crime",
    "ENQUETE": "Investigation", "EPOUVANTE": "Terror", "EROTIQUE": "Erotic",
    "ESPIONNAGE": "Spy", "FAMILLE": "Family", "FANTASTIQUE": "Fantasy",
    "GANGSTER": "Gangster", "MYSTERE": "Mystery", "PEPLUM": "Sword-and-sandal",
    "POLITIQUE": "Political", "SPORT": "Sport", "SUPER_HEROS": "Superhero",
}

ERAS = {
    "CINEMA_MUET": "Silent cinema",
    "CINEMA_CLASSIQUE": "Classical cinema",
    "CINEMA_MODERNE": "Modern cinema",
    "CINEMA_CONTEMPORAIN": "Contemporary cinema",
}

CTYPES = {
    "MOVEMENT": "Movement", "CURRENT": "Current", "STYLE": "Style",
    "PERIOD": "Period", "SCHOOL": "School", "WAVE": "Wave",
}

BADGES = {
    "001": ("First Curtain", "Watch your first film."),
    "002": ("Second Screening", "Watch 20 films."),
    "003": ("Cinema Addict", "Watch 100 films."),
    "004": ("Collector", "Watch 300 films."),
    "005": ("Cinema Passport", "Explore 15 countries."),
    "006": ("Globe-Trotter", "Explore 30 countries."),
    "007": ("Cartographer of Cinema", "Explore 40 countries."),
    "008": ("Grand Tour of Europe", "Explore 10 European countries."),
    "009": ("Beyond Borders", "Watch five films on five continents."),
    "010": ("Dolce Vita", "Watch 20 Italian films."),
    "011": ("Made in USA", "Watch 50 American films."),
    "012": ("Rising Sun", "Watch 20 Japanese films."),
    "013": ("Light on France", "Watch 20 French films."),
    "014": ("Made in Asia", "Watch 50 Asian films."),
    "015": ("Beyond the Canon", "Watch 40 films released before 1950."),
    "016": ("Archaeologist of Cinema", "Watch 100 films released before 1960."),
    "017": ("Memory of the Seventh Art", "Watch 300 films released before 1980."),
    "018": ("Ghosts of Silence", "Watch 20 silent films."),
    "019": ("Back to the Sources", "Explore 5 decades."),
    "020": ("Across the Ages", "Watch one film from each decade, from 1890 to 2020."),
    "021": ("Child of the New Wave", "Watch 15 films by filmmakers associated with the New Wave."),
    "022": ("La Dolce Commedia", "Watch 15 films of Italian comedy."),
    "023": ("The Soviet Eye", "Watch 10 films of Soviet cinema."),
    "024": ("American Nights", "Watch 20 film noirs."),
    "025": ("Spaghetti Western", "Watch 15 Italian westerns."),
    "026": ("Form Before Content", "Watch 10 experimental films."),
    "027": ("Suspended Time", "Watch 20 films longer than three hours."),
    "028": ("The Great Crossing", "Watch 5 films longer than five hours."),
    "029": ("The Great Names", "Watch 10 films by 10 directors."),
    "030": ("Living Encyclopaedia", "Watch 10 films from 30 currents."),
    "031": ("World Map", "Watch at least one film from every country."),
    "032": ("Cabinet of Fears", "Watch 50 horror films."),
    "033": ("Silver Grain", "Watch 40 non-silent black-and-white films."),
    "034": ("In One Reel", "Watch 30 short films."),
    "035": ("The Real", "Watch 20 documentaries."),
    "036": ("Light of Africa", "Watch 20 films from the African continent."),
    "037": ("Our Century", "Watch 50 films released since 2000."),
    "038": ("Frame by Frame", "Watch 20 animated films."),
}

RANKINGS = {
    "RANK_01": (
        "Novice",
        "You are starting to draw your map of cinema.",
        "You enter the catalogue as one pushes a first theatre door. A few films are enough to put a point on the map, without yet drawing a territory. This rank records a first contact with film history, not a culture already formed. Each later screening simply widens the space you are beginning to inhabit.",
    ),
    "RANK_02": (
        "Amateur",
        "Your curiosity takes shape.",
        "Your curiosity is no longer an accident: you return to films by choice. Titles accumulate and the first echoes appear between eras. You do not yet have a method, but you have a taste that is beginning to take form. Cinema ceases to be isolated entertainment and becomes a habit of looking.",
    ),
    "RANK_03": (
        "Initiate",
        "You recognise the first territories.",
        "You now recognise a few territories: a country, a decade, an author's name. Films stop arriving one by one; they take their place in families. You can situate a work without yet being able to tell its whole genealogy. Initiation here is less encyclopaedic knowledge than the passage from a passive gaze to an oriented one.",
    ),
    "RANK_04": (
        "Enthusiast",
        "Cinema regularly accompanies your gaze.",
        "Cinema regularly accompanies your weeks, more as a practice than as a list. You accept difficult, long, old films because pleasure has shifted toward discovery. The conversations you could have about a shot, an actor or an era grow richer. This rank marks the moment when the catalogue is no longer a challenge: it becomes an appetite.",
    ),
    "RANK_05": (
        "Explorer",
        "You travel through varied cinematographies.",
        "You leave the most marked paths to travel through distant cinematographies. Asia, Africa, Latin America or silent film are no longer exceptions, but directions. To explore is to accept getting lost: a film can displace everything you thought settled. Your map grows less by accumulation than by gaps you seek on purpose.",
    ),
    "RANK_06": (
        "Connoisseur",
        "You connect works, authors and eras.",
        "You now connect works, authors and eras with an active memory. A Mizoguchi shot calls Renoir; an Italian crime film wakes Hollywood; a silent film lights a contemporary one. The connoisseur does not quote to shine: they compare in order to understand. Your path begins to have a coherence, even if it remains unfinished by nature.",
    ),
    "RANK_07": (
        "Scholar",
        "Your culture is broad and deep.",
        "Your culture has widened without thinning: you hold together the canon and its margins. Movements, schools and chronologies are no longer labels, but tools. Erudition, in Urbinema, is measured by the real diversity of what you have seen, not by the specialist's pose. You can cross a century of cinema and still point to what you lack.",
    ),
    "RANK_08": (
        "Specialist",
        "You master vast stretches of film history.",
        "You master vast stretches of film history, enough to discern lines of force in them. Some territories have become familiar enough that you can spot the exceptions. The specialist is not the one who shuts themselves in: it is the one who can go deep without losing the panorama. At this stage, each new film is read against an already dense inner library.",
    ),
    "RANK_09": (
        "Expert",
        "Your path covers almost the whole proposed territory.",
        "Your path covers almost the whole proposed territory, from the first silents to contemporary forms. You have crossed enough countries, formats and currents for catalogue accidents to become rare. Expertise shows less in speed than in accuracy: you know what you have seen and what it opens. There remain dark zones, but they are chosen more than suffered.",
    ),
    "RANK_10": (
        "Master",
        "You have travelled almost the whole Urbinema catalogue.",
        "You have travelled almost the whole Urbinema catalogue, not as a closed collection, but as an inhabited map. The title of master does not stop the gaze: it records a long, diverse, stubborn crossing. Films now answer one another of themselves, from one continent to another, from one decade to the next. Returning to a title already seen is then no longer a repetition: it is a rereading.",
    ),
}

QUESTS = {
    "QUEST_BRONZE_SILENT": ("Silence is golden", "Watch 1 silent film"),
    "QUEST_BRONZE_FRANCE": ("A French screening", "Watch 1 French film"),
    "QUEST_BRONZE_BW": ("Shades of grey", "Watch 1 black-and-white film"),
    "QUEST_BRONZE_DRAMA": ("Drama first", "Watch 1 drama"),
    "QUEST_BRONZE_COMEDY": ("A burst of laughter", "Watch 1 comedy"),
    "QUEST_BRONZE_WESTERN": ("Dust and horizon", "Watch 1 western"),
    "QUEST_BRONZE_HORROR": ("A short scare", "Watch 1 horror film"),
    "QUEST_BRONZE_UK": ("A British evening", "Watch 1 British film"),
    "QUEST_BRONZE_GERMANY": ("A German screening", "Watch 1 German film"),
    "QUEST_BRONZE_EXPERIMENTAL": ("Off the story", "Watch 1 experimental film"),
    "QUEST_BRONZE_1930S": ("Back to 1930", "Watch 1 film released in the 1930s"),
    "QUEST_BRONZE_FROM_1980": ("After 1980", "Watch 1 film released in 1980 or later"),
    "QUEST_BRONZE_NEW_WAVE": ("A breath of Wave", "Watch 1 film of the French New Wave"),
    "QUEST_BRONZE_NOIR": ("A dark alley", "Watch 1 film noir"),
    "QUEST_BRONZE_ANIMATION": ("A drawing that moves", "Watch 1 animated film"),
    "QUEST_BRONZE_DOCUMENTARY": ("A look at the real", "Watch 1 documentary"),
    "QUEST_SILVER_ASIA": ("Three Asian gazes", "Watch 3 Asian films"),
    "QUEST_SILVER_ITALY": ("Journey to Italy", "Watch 3 Italian films"),
    "QUEST_SILVER_JAPAN": ("Three gazes from Japan", "Watch 3 Japanese films"),
    "QUEST_SILVER_1960S": ("The 1960s", "Watch 3 films released in the 1960s"),
    "QUEST_SILVER_DRAMA_2": ("Two dramas", "Watch 2 dramas"),
    "QUEST_SILVER_COMEDY": ("Two comedies", "Watch 2 comedies"),
    "QUEST_SILVER_GERMANY": ("Three Germanys", "Watch 3 German films"),
    "QUEST_SILVER_UK": ("Three Albions", "Watch 3 British films"),
    "QUEST_SILVER_1950S": ("The 1950s", "Watch 3 films released in the 1950s"),
    "QUEST_SILVER_1970S": ("The 1970s", "Watch 3 films released in the 1970s"),
    "QUEST_SILVER_1930S": ("The 1930s", "Watch 3 films released in the 1930s"),
    "QUEST_SILVER_NEW_HOLLYWOOD": ("New Hollywood", "Watch 3 New Hollywood films"),
    "QUEST_SILVER_NOIR": ("Three dark nights", "Watch 3 film noirs"),
    "QUEST_SILVER_WESTERN": ("Three frontiers", "Watch 3 westerns"),
    "QUEST_SILVER_BW": ("Three greys", "Watch 3 black-and-white films"),
    "QUEST_SILVER_SOUTH_AMERICA": ("Three South Americas", "Watch 3 South American films"),
    "QUEST_SILVER_AUTEUR": ("Three signatures", "Watch 3 art-house films"),
    "QUEST_GOLD_BEFORE_1950": ("Before 1950", "Watch 5 films released before 1950"),
    "QUEST_GOLD_USA": ("Five Americas", "Watch 5 American films"),
    "QUEST_GOLD_EUROPE": ("Grand tour of Europe", "Watch 5 European films"),
    "QUEST_GOLD_DIRECTORS": ("Five authors", "Watch 5 films by 5 different directors"),
    "QUEST_GOLD_FRANCE": ("Five French screenings", "Watch 5 French films"),
    "QUEST_GOLD_1960S": ("Full 1960s", "Watch 5 films released in the 1960s"),
    "QUEST_GOLD_FROM_1980": ("Five contemporary gazes", "Watch 5 films released in 1980 or later"),
    "QUEST_GOLD_COUNTRIES": ("Five flags", "Watch films from 5 different countries"),
    "QUEST_GOLD_GENRES": ("Four genres", "Watch films from 4 different genres"),
    "QUEST_GOLD_DECADES": ("Four decades", "Watch films from 4 different decades"),
    "QUEST_GOLD_NOIR": ("Five dark nights", "Watch 5 film noirs"),
    "QUEST_GOLD_AUTEUR": ("Five signatures", "Watch 5 art-house films"),
    "QUEST_GOLD_HOLLYWOOD": ("Five studios", "Watch 5 films of classical Hollywood"),
    "QUEST_GOLD_RUNTIME": ("Five long screenings", "Watch 5 films longer than 2 hours"),
    "QUEST_GOLD_WESTERN": ("Five rides", "Watch 5 westerns"),
    "QUEST_GOLD_COMEDY": ("Five bursts", "Watch 5 comedies"),
    "QUEST_GOLD_NEW_WAVE": ("Five Waves", "Watch 5 films of the French New Wave"),
    "QUEST_BRONZE_GIALLO": ("A red blade", "Watch 1 giallo"),
    "QUEST_BRONZE_DOGME": ("The vow of chastity", "Watch 1 Dogme 95 film"),
    "QUEST_BRONZE_JIDAIGEKI": ("Blade and era", "Watch 1 jidai-geki"),
    "QUEST_SILVER_NEOREALISM": ("The postwar streets", "Watch 3 films of Italian neorealism"),
    "QUEST_SILVER_EXPRESSIONISM": ("Tilted shadows", "Watch 3 films of German expressionism"),
    "QUEST_SILVER_SPAGHETTI": ("Three duels in the sun", "Watch 3 spaghetti westerns"),
    "QUEST_GOLD_SURREALISM": ("Logic of the dream", "Watch 5 surrealist films"),
    "QUEST_GOLD_JAPAN_GOLDEN": ("Five golden screens", "Watch 5 films of the Japanese golden age"),
    "QUEST_GOLD_SOVIET": ("Five montages", "Watch 5 films of Soviet cinema"),
}


def load_json(name):
    path = I18N / name
    return json.loads(path.read_text(encoding="utf-8"))


def apply_pair(items, table, name_key="nameEn", extra_key=None):
    missing = []
    for item in items:
        code = item.get("code") or item.get("typeCode")
        row = table.get(code)
        if row is None:
            missing.append(code)
            continue
        if isinstance(row, tuple):
            item[name_key] = row[0]
            if extra_key and len(row) > 1:
                item[extra_key] = row[1]
            if extra_key == "descriptionEn" and len(row) > 2:
                item["longDescriptionEn"] = row[2]
        elif isinstance(row, str):
            item[name_key] = row
        else:
            item.update({k: v for k, v in row.items() if v})
    return missing


def apply_chars(pack, overlay):
    missing = []
    for item in pack["characteristics"]:
        row = overlay.get(item["code"])
        if not row:
            missing.append(item["code"])
            continue
        item["nameEn"] = row["nameEn"]
        if row.get("descriptionEn"):
            item["descriptionEn"] = row["descriptionEn"]
    return missing


def apply_path(pack, overlay):
    path = pack["paths"][0]
    path["nameEn"] = overlay["nameEn"]
    path["summaryEn"] = overlay["summaryEn"]
    path["descriptionEn"] = overlay["descriptionEn"]
    path["periodLabelEn"] = overlay["periodLabelEn"]
    steps = overlay["steps"]
    for step in path["steps"]:
        en = steps[step["code"]]
        step["nameEn"] = en["nameEn"]
        step["descriptionEn"] = en["descriptionEn"]
        if en.get("periodLabelEn"):
            step["periodLabelEn"] = en["periodLabelEn"]
        if en.get("transitionEn"):
            step["transitionEn"] = en["transitionEn"]
        for fact, fact_en in zip(step["facts"], en["facts"]):
            fact["titleEn"] = fact_en["titleEn"]
            fact["bodyEn"] = fact_en["bodyEn"]
        for figure, role_en in zip(step["figures"], en["figures"]):
            figure["roleEn"] = role_en


def main():
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    chars = load_json("characteristics.json")
    collections = load_json("collections.json")
    path = load_json("path.json")

    missing = []
    missing += apply_pair(pack["countries"], COUNTRIES)
    missing += apply_pair(pack["continents"], CONTINENTS)
    missing += apply_pair(pack["genres"], GENRES)
    missing += apply_pair(pack["eras"], ERAS)
    missing += apply_pair(pack["characteristicTypes"], CTYPES)
    missing += apply_pair(pack["badges"], BADGES, extra_key="descriptionEn")
    missing += apply_pair(pack["rankings"], RANKINGS, extra_key="descriptionEn")
    missing += apply_pair(pack["quests"], QUESTS, extra_key="descriptionEn")
    missing += apply_chars(pack, chars)
    missing += apply_pair(pack["collections"], collections)
    apply_path(pack, path)

    missing = [code for code in missing if code]
    if missing:
        raise SystemExit("missing translations: " + ", ".join(missing[:40]))

    pack["version"] = 46
    text = json.dumps(pack, ensure_ascii=False, indent=2)
    CATALOG.write_text(text + "\n", encoding="utf-8")
    V3.write_text(text + "\n", encoding="utf-8")
    print("ok pack", pack["version"])


if __name__ == "__main__":
    main()
