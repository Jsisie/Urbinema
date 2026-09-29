#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pack 16 : collections muet / NCA / Nouvel Hollywood / Âge d'or / Japon 70s / Hitchcock."""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_V2 = ROOT / "app/src/main/assets/catalog/catalog_v2.json"
CATALOG_LIVE = ROOT / "app/src/main/assets/catalog/catalog.json"
POSTERS_DIR = ROOT / "app/src/main/assets/media/posters"
INPUT_MOVIES = ROOT / "batchsData/batchPosters/input/input_movies.txt"

sys.path.insert(0, str(ROOT / "batchsData/batchPosters"))
from catalog_enrich import scores_for  # noqa: E402


def movie_format(minutes: int) -> str:
    if minutes < 40:
        return "SHORT"
    if minutes < 60:
        return "MEDIUM"
    if minutes >= 180:
        return "EXTENDED"
    return "FEATURE"


def pick(codes: list[str], available: set[str]) -> list[dict]:
    missing = [code for code in codes if code not in available]
    if missing:
        raise SystemExit(f"Unknown movie codes: {missing}")
    return [{"code": code, "displayOrder": index} for index, code in enumerate(codes, start=1)]


def director_entry(code: str, first: str, last: str, chars: list[str] | None = None) -> dict:
    entry = {
        "code": code,
        "lastName": last,
        "displayName": f"{first} {last}".strip(),
        "firstName": first,
        "characteristicCodes": chars or [],
    }
    return entry


def film(
    code: str,
    original: str,
    french: str,
    year: int,
    minutes: int,
    synopsis: str,
    country: str,
    director: str,
    genres: list[str],
    chars: list[str],
    *,
    silent: bool = False,
    bw: bool | None = None,
    experimental: bool = False,
    demand: float = 0.72,
) -> dict:
    hd, ad, hr, cr = scores_for(code, year, silent, experimental, demand)
    item = {
        "code": code,
        "originalTitle": original,
        "frenchTitle": french,
        "releaseYear": year,
        "durationMinutes": minutes,
        "format": movie_format(minutes),
        "synopsis": synopsis,
        "historicalDistance": round(hd, 4),
        "artisticDemand": round(ad, 4),
        "historicalRichness": round(hr, 4),
        "culturalRichness": round(cr, 4),
        "countries": [{"code": country, "isPrimary": True}],
        "directors": [{"code": director, "billingOrder": 0}],
        "genreCodes": genres,
        "characteristicCodes": chars,
    }
    if silent:
        item["isSilent"] = True
    if bw if bw is not None else year <= 1954:
        item["isBlackAndWhite"] = True
    if experimental:
        item["isExperimental"] = True
    return item


NEW_DIRECTORS = [
    director_entry("DENNIS_HOPPER", "Dennis", "Hopper", ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR"]),
    director_entry("KOICHI_SAITO", "Kōichi", "Saitō", ["CINEMA_D_AUTEUR"]),
    director_entry("SHUJI_TERAYAMA", "Shūji", "Terayama", ["CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR"]),
    director_entry("KINJI_FUKASAKU", "Kinji", "Fukasaku", ["CINEMA_D_AUTEUR"]),
    director_entry("NOBUHIKO_OBAYASHI", "Nobuhiko", "Obayashi", ["CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR"]),
]

NEW_MOVIES = [
    film(
        "SOUPCONS_1941", "Suspicion", "Soupçons", 1941, 99,
        "Un officier britannique commence à croire que son mari veut l'empoisonner.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "MYSTERE", "ROMANCE"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
    ),
    film(
        "L_OMBRE_D_UN_DOUTE_1943", "Shadow of a Doubt", "L'Ombre d'un doute", 1943, 108,
        "Une adolescente de Santa Rosa soupçonne son oncle adoré d'être un tueur.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "DRAME", "FILM_NOIR"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"],
    ),
    film(
        "CANOT_DE_SAUVETAGE_1944", "Lifeboat", "Canot de sauvetage", 1944, 97,
        "Rescapés d'un torpillage, civils alliés et un marin allemand partagent un canot.",
        "USA", "ALFRED_HITCHCOCK", ["DRAME", "GUERRE", "THRILLER"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
    ),
    film(
        "LA_MAISON_DU_DOCTEUR_EDWARDES_1945", "Spellbound", "La Maison du docteur Edwardes", 1945, 111,
        "Une psychiatre tombe amoureuse d'un amnésique qu'on accuse de meurtre.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "MYSTERE", "ROMANCE"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
    ),
    film(
        "LA_CORDE_1948", "Rope", "La Corde", 1948, 80,
        "Deux étudiants cachent un cadavre dans un coffre et donnent un dîner autour.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "CRIME", "DRAME"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
        bw=True,
    ),
    film(
        "L_INCONNU_DU_NORD_EXPRESS_1951", "Strangers on a Train", "L'Inconnu du Nord-Express", 1951, 101,
        "Dans un train, un inconnu propose d'échanger deux meurtres.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "CRIME", "FILM_NOIR"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"],
    ),
    film(
        "LE_CRIME_ETAIT_PRESQUE_PARFAIT_1954", "Dial M for Murder", "Le Crime était presque parfait", 1954, 105,
        "Un tenniseman monte le meurtre de sa femme ; le plan dérape.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "CRIME", "MYSTERE"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
        bw=False,
    ),
    film(
        "LA_MAIN_AU_COLLET_1955", "To Catch a Thief", "La Main au collet", 1955, 106,
        "Un ancien cambrioleur de la Côte d'Azur doit prouver qu'il n'a pas repris du service.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "ROMANCE", "COMEDIE"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
        bw=False,
    ),
    film(
        "L_HOMME_QUI_EN_SAVAIT_TROP_1956", "The Man Who Knew Too Much", "L'Homme qui en savait trop", 1956, 120,
        "À Marrakech, un couple américain voit son fils enlevé après un assassinat.",
        "USA", "ALFRED_HITCHCOCK", ["THRILLER", "AVENTURE"],
        ["CINEMA_D_AUTEUR", "HOLLYWOOD_CLASSIQUE"],
        bw=False,
    ),
    film(
        "FRENZY_1972", "Frenzy", "Frenzy", 1972, 116,
        "Un cravatier londonien est accusé d'être le tueur à la cravate.",
        "UK", "ALFRED_HITCHCOCK", ["THRILLER", "CRIME", "HORREUR"],
        ["CINEMA_D_AUTEUR"],
        bw=False, demand=0.7,
    ),
    film(
        "EASY_RIDER_1969", "Easy Rider", "Easy Rider", 1969, 95,
        "Deux motards traversent l'Amérique avec l'argent d'un deal, vers une fête qui n'arrive pas.",
        "USA", "DENNIS_HOPPER", ["DRAME", "AVENTURE"],
        ["NEW_HOLLYWOOD", "ROAD_MOVIE", "CINEMA_D_AUTEUR"],
        bw=False, demand=0.62,
    ),
    film(
        "CONVERSATION_SECRETE_1974", "The Conversation", "Conversation secrète", 1974, 113,
        "Un spécialiste de la surveillance se prend dans l'enregistrement qu'il a lui-même fabriqué.",
        "USA", "FRANCIS_FORD_COPPOLA", ["THRILLER", "DRAME", "MYSTERE"],
        ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR"],
        bw=False, demand=0.78,
    ),
    film(
        "LA_SORCIERE_ROUGE_1968", "Yabu no Naka no Kuroneko", "La Sorcière rouge", 1968, 99,
        "Deux femmes assassinées par des samouraïs reviennent en chats-fantômes dans le Japon médiéval.",
        "JAPAN", "KANETO_SHINDO", ["HORREUR", "FANTASTIQUE", "DRAME"],
        ["CINEMA_D_AUTEUR", "JIDAIGEKI"],
        bw=True, demand=0.8,
    ),
    film(
        "LA_BALLADE_DE_TSUGARU_1973", "Tsugaru jongara bushi", "La Ballade de Tsugaru", 1973, 114,
        "Un homme revient dans le Tsugaru natal et se heurte aux chants, à la neige et aux morts.",
        "JAPAN", "KOICHI_SAITO", ["DRAME"],
        ["CINEMA_D_AUTEUR"],
        bw=False, demand=0.76,
    ),
    film(
        "PASTORAL_MOURIR_A_LA_CAMPAGNE_1974", "Den-en ni shisu", "Pastoral : mourir à la campagne", 1974, 115,
        "Un poète revisite son enfance dans un village où mémoire, théâtre et magie se mélangent.",
        "JAPAN", "SHUJI_TERAYAMA", ["DRAME", "FANTASTIQUE"],
        ["CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR"],
        bw=False, experimental=True, demand=0.88,
    ),
    film(
        "LE_CIMETIERE_DE_LA_MORALE_1975", "Jingi no hakaba", "Le Cimetière de la morale", 1975, 94,
        "Un yakuza sort de prison et découvre que le code d'honneur de son clan n'existe plus.",
        "JAPAN", "KINJI_FUKASAKU", ["CRIME", "DRAME", "ACTION"],
        ["CINEMA_D_AUTEUR"],
        bw=False, demand=0.74,
    ),
    film(
        "HOUSE_1977", "Hausu", "House", 1977, 88,
        "Sept lycéennes passent l'été dans une maison de campagne qui se met à les dévorer.",
        "JAPAN", "NOBUHIKO_OBAYASHI", ["HORREUR", "FANTASTIQUE", "COMEDIE"],
        ["CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR"],
        bw=False, experimental=True, demand=0.7,
    ),
]

BATCH_ROWS = [
    ('Soupçons', 1941, 'Alfred Hitchcock', 'SOUPCONS_1941', 'Suspicion'),
    ("L'Ombre d'un doute", 1943, 'Alfred Hitchcock', 'L_OMBRE_D_UN_DOUTE_1943', 'Shadow of a Doubt'),
    ('Canot de sauvetage', 1944, 'Alfred Hitchcock', 'CANOT_DE_SAUVETAGE_1944', 'Lifeboat'),
    ('La Maison du docteur Edwardes', 1945, 'Alfred Hitchcock', 'LA_MAISON_DU_DOCTEUR_EDWARDES_1945', 'Spellbound'),
    ('La Corde', 1948, 'Alfred Hitchcock', 'LA_CORDE_1948', 'Rope'),
    ("L'Inconnu du Nord-Express", 1951, 'Alfred Hitchcock', 'L_INCONNU_DU_NORD_EXPRESS_1951', 'Strangers on a Train'),
    ('Le Crime était presque parfait', 1954, 'Alfred Hitchcock', 'LE_CRIME_ETAIT_PRESQUE_PARFAIT_1954', 'Dial M for Murder'),
    ('La Main au collet', 1955, 'Alfred Hitchcock', 'LA_MAIN_AU_COLLET_1955', 'To Catch a Thief'),
    ("L'Homme qui en savait trop", 1956, 'Alfred Hitchcock', 'L_HOMME_QUI_EN_SAVAIT_TROP_1956', 'The Man Who Knew Too Much'),
    ('Frenzy', 1972, 'Alfred Hitchcock', 'FRENZY_1972', 'Frenzy'),
    ('Easy Rider', 1969, 'Dennis Hopper', 'EASY_RIDER_1969', 'Easy Rider'),
    ('Conversation secrète', 1974, 'Francis Ford Coppola', 'CONVERSATION_SECRETE_1974', 'The Conversation'),
    ('La Sorcière rouge', 1968, 'Kaneto Shindo', 'LA_SORCIERE_ROUGE_1968', 'Yabu no Naka no Kuroneko'),
    ('La Ballade de Tsugaru', 1973, 'Koichi Saito', 'LA_BALLADE_DE_TSUGARU_1973', 'Tsugaru jongara bushi'),
    ('Pastoral : mourir à la campagne', 1974, 'Shuji Terayama', 'PASTORAL_MOURIR_A_LA_CAMPAGNE_1974', 'Den-en ni shisu'),
    ('Le Cimetière de la morale', 1975, 'Kinji Fukasaku', 'LE_CIMETIERE_DE_LA_MORALE_1975', 'Jingi no hakaba'),
    ('House', 1977, 'Nobuhiko Obayashi', 'HOUSE_1977', 'Hausu'),
]


def collection_by_code(pack: dict, code: str) -> dict:
    for item in pack["collections"]:
        if item["code"] == code:
            return item
    raise SystemExit(f"Missing collection {code}")


def hitchcock_codes(pack: dict) -> set[str]:
    return {
        movie["code"]
        for movie in pack["movies"]
        if any(item["code"] == "ALFRED_HITCHCOCK" for item in movie.get("directors") or [])
    }


def main() -> None:
    pack = json.loads(CATALOG_V2.read_text(encoding="utf-8"))
    directors = pack["directors"]
    director_codes = {item["code"] for item in directors}
    for entry in NEW_DIRECTORS:
        if entry["code"] not in director_codes:
            directors.append(entry)
            director_codes.add(entry["code"])

    movie_codes = {movie["code"] for movie in pack["movies"]}
    added_movies: list[str] = []
    for movie in NEW_MOVIES:
        if movie["code"] in movie_codes:
            continue
        pack["movies"].append(movie)
        movie_codes.add(movie["code"])
        added_movies.append(movie["code"])

    hitch = hitchcock_codes(pack)
    for collection in pack["collections"]:
        if collection["code"] == "COLLECTION_017":
            continue
        kept = [row for row in collection.get("movies") or [] if row["code"] not in hitch]
        if len(kept) != len(collection.get("movies") or []):
            collection["movies"] = [
                {"code": row["code"], "displayOrder": index}
                for index, row in enumerate(kept, start=1)
            ]

    silent = collection_by_code(pack, "COLLECTION_012")
    silent["track"] = "DARKROOM"
    silent["movies"] = pick([
        "LA_SORTIE_DES_USINES_LUMIERE_1895",
        "L_ARRIVEE_D_UN_TRAIN_1896",
        "LA_FEE_AUX_CHOUX_1896",
        "VOYAGE_DANS_LA_LUNE_1902",
        "LE_VOL_DU_GRAND_RAPIDE_1903",
        "INTOLERANCE_1916",
        "LE_LYS_BRISE_1919",
        "CABINET_DU_DOCTEUR_CALIGARI_1920",
        "LE_KID_1921",
        "LA_CHARRETTE_FANTOME_1921",
        "NOSFERATU_1922",
        "HAXAN_1922",
        "NANOUK_L_ESQUIMAU_1922",
        "MONTEUR_DE_SECURITE_1923",
        "LE_DERNIER_DES_HOMMES_1924",
        "SHERLOCK_JUNIOR_1924",
        "LA_RUEE_VERS_LOR_1925",
        "LE_CUIRASSE_POTEMKINE_1925",
        "LE_MECANICIEN_DE_LA_GENERAL_1926",
        "L_AURORE_1927",
        "METROPOLIS_1927",
        "NAPOLEON_1927",
        "LA_PASSION_DE_JEANNE_DARC_1928",
        "LA_FOULE_1928",
        "L_HOMME_A_LA_CAMERA_1929",
        "LA_BOITE_DE_PANDORE_1929",
        "UN_CHIEN_ANDALOU_1929",
        "LES_LUMIERES_DE_LA_VILLE_1931",
    ], movie_codes)
    silent["longDescription"] = (
        "Avant 1930, le cinéma invente presque tous ses langages. Méliès truque la Lune, "
        "Griffith monumentalisé le récit, Keaton, Chaplin et Lloyd font du corps une grammaire. "
        "L'Allemagne expressionniste, Flaherty, Murnau, l'URSS du montage et Dreyer prouvent "
        "que le silence n'est pas un manque. La Passion de Jeanne d'Arc colle aux visages, "
        "L'Aurore invente une caméra lyrique, Napoléon déborde l'écran. Le parlant n'efface "
        "pas cet âge : il le recouvre. Revenir au muet, c'est réapprendre à voir avant d'écouter."
    )

    nca = collection_by_code(pack, "COLLECTION_010")
    nca["track"] = "OFFSCREEN"

    hollywood = collection_by_code(pack, "COLLECTION_005")
    hollywood["name"] = "Âge d'or d'Hollywood"
    hollywood["track"] = "CLUB"
    hollywood["description"] = "Le système des studios, ses genres et sa continuité invisible."
    hollywood["longDescription"] = (
        "De 1930 à 1960, Hollywood fabrique un langage que le monde entier apprend. "
        "John Ford sculpte le western, Howard Hawks passe du polar à la comédie, "
        "Billy Wilder aiguise le dialogue, Welles ouvre une brèche d'auteur à l'intérieur "
        "même du système. Le code Hays bride, les stars portent, la continuité invisible "
        "coud les plans. Autant en emporte le vent et Le Magicien d'Oz saturent le mythe ; "
        "Citizen Kane et Casablanca le fissurent. Cette période n'est pas un âge d'or innocent : "
        "elle est une industrie, une censure et une invention permanente."
    )
    hollywood["characteristicCodes"] = ["HOLLYWOOD_CLASSIQUE", "AGE_OR_HOLLYWOOD"]
    hollywood["movies"] = pick([
        "SHANGHAI_EXPRESS_1932",
        "HAUTE_PEGRE_1932",
        "KING_KONG_1933",
        "NEW_YORK_MIAMI_1934",
        "LA_CHEVAUCHEE_FANTASTIQUE_1939",
        "AUTANT_EN_EMPORTE_LE_VENT_1939",
        "LE_MAGICIEN_D_OZ_1939",
        "CITIZEN_KANE_1941",
        "CASABLANCA_1942",
        "ASSURANCE_SUR_LA_MORT_1944",
        "LES_MEILLEURES_ANNEES_DE_NOTRE_VIE_1946",
        "LA_VIE_EST_BELLE_1946",
        "CHANTONS_SOUS_LA_PLUIE_1952",
        "LA_PRISONNIERE_DU_DESERT_1956",
        "CERTAINS_L_AIMENT_CHAUD_1959",
    ], movie_codes)

    existing_codes = {item["code"] for item in pack["collections"]}
    if "COLLECTION_015" not in existing_codes:
        pack["collections"].append({
            "code": "COLLECTION_015",
            "displayOrder": 15,
            "name": "Nouvel Hollywood",
            "description": "Les années 1967–1979, quand les studios laissent les auteurs casser le jouet.",
            "longDescription": (
                "Après Bonnie and Clyde et Le Lauréat, Hollywood bascule. Easy Rider, Taxi Driver, "
                "Le Parrain, Apocalypse Now, Massacre à la tronçonneuse : une génération filme "
                "la guerre, la paranoïa, le sexe et l'horreur sans le vernis du code Hays. "
                "Coppola, Scorsese, Hopper, Friedkin, Hooper, Spielberg encore jeune : le studio "
                "finance des films qui le dévorent. Cette collection n'est pas tout le cinéma "
                "américain des années 1970, c'est la porte d'entrée de ce basculement."
            ),
            "isPublished": True,
            "movies": pick([
                "BONNIE_AND_CLYDE_1967",
                "LE_LAUREAT_1967",
                "2001_L_ODYSSEE_DE_L_ESPACE_1968",
                "ROSEMARY_S_BABY_1968",
                "EASY_RIDER_1969",
                "MACADAM_COWBOY_1969",
                "CINQ_PIECES_FACILES_1970",
                "ORANGE_MECANIQUE_1971",
                "THE_FRENCH_CONNECTION_1971",
                "LA_DERNIERE_SEANCE_1971",
                "LE_PARRAIN_1972",
                "L_EXORCISTE_1973",
                "MEAN_STREETS_1973",
                "LE_PARRAIN_2_1974",
                "CHINATOWN_1974",
                "MASSACRE_A_LA_TRONCONNEUSE_1974",
                "CONVERSATION_SECRETE_1974",
                "LES_DENTS_DE_LA_MER_1975",
                "VOL_AU_DESSUS_D_UN_NID_DE_COUCOU_1975",
                "TAXI_DRIVER_1976",
                "NETWORK_1976",
                "CARRIE_AU_BAL_DU_DIABLE_1976",
                "LA_GUERRE_DES_ETOILES_1977",
                "ANNIE_HALL_1977",
                "HALLOWEEN_1978",
                "VOYAGE_AU_BOUT_DE_L_ENFER_1978",
                "APOCALYPSE_NOW_1979",
                "ALIEN_1979",
            ], movie_codes),
            "characteristicCodes": ["NEW_HOLLYWOOD"],
            "countryCodes": ["USA"],
            "eraCodes": ["CINEMA_MODERNE"],
            "track": "GATEWAY",
        })
    if "COLLECTION_016" not in existing_codes:
        pack["collections"].append({
            "code": "COLLECTION_016",
            "displayOrder": 16,
            "name": "Japon — années 70",
            "description": "Après l'âge d'or des studios : yakuza, fantômes, expérimental et pop.",
            "longDescription": (
                "Quand les grands studios japonais vacillent, une autre décennie s'ouvre. "
                "Shindō fait revenir les mortes en chats, Saitō filme le Tsugaru natal, "
                "Terayama transforme l'enfance en théâtre, Fukasaku enterre le code yakuza, "
                "Ōshima pousse le désir jusqu'au scandale, Obayashi laisse une maison dévorer "
                "des lycéennes. Autour, Kurosawa en couleur, Yoshida, Matsumoto, Imamura. "
                "Ce n'est pas une école : c'est le Japon des années 1970, hors des tatamis classiques."
            ),
            "isPublished": True,
            "movies": pick([
                "EROS_MASSACRE_1969",
                "FUNERAL_PARADE_OF_ROSES_1969",
                "LA_SORCIERE_ROUGE_1968",
                "DODES_KA_DEN_1970",
                "LA_BALLADE_DE_TSUGARU_1973",
                "PASTORAL_MOURIR_A_LA_CAMPAGNE_1974",
                "LE_CIMETIERE_DE_LA_MORALE_1975",
                "L_EMPIRE_DES_SENS_1976",
                "HOUSE_1977",
                "VENGEANCE_IS_MINE_1979",
            ], movie_codes),
            "countryCodes": ["JAPAN"],
            "track": "CINEMATHEQUE",
        })
    if "COLLECTION_017" not in existing_codes:
        pack["collections"].append({
            "code": "COLLECTION_017",
            "displayOrder": 17,
            "name": "Hitchcockiens",
            "description": "Vingt films où le suspense devient une forme, de Londres à Hollywood.",
            "longDescription": (
                "Alfred Hitchcock passe du thriller britannique des années 1930 au studio "
                "américain, puis revient à Londres pour Frenzy. Les 39 Marches, Rebecca, "
                "Fenêtre sur cour, Sueurs froides, Psychose, Les Oiseaux : le regard, la blonde, "
                "l'escalier, le train. Cette collection rassemble vingt films majeurs, retirés "
                "des autres parcours pour qu'on les voie comme une œuvre, pas comme un genre "
                "Hollywood de plus."
            ),
            "isPublished": True,
            "movies": pick([
                "LES_39_MARCHES_1935",
                "UNE_FEMME_DISPARAIT_1938",
                "REBECCA_1940",
                "SOUPCONS_1941",
                "L_OMBRE_D_UN_DOUTE_1943",
                "CANOT_DE_SAUVETAGE_1944",
                "LA_MAISON_DU_DOCTEUR_EDWARDES_1945",
                "LES_ENCHAINES_1946",
                "LA_CORDE_1948",
                "L_INCONNU_DU_NORD_EXPRESS_1951",
                "FENETRE_SUR_COUR_1954",
                "LE_CRIME_ETAIT_PRESQUE_PARFAIT_1954",
                "LA_MAIN_AU_COLLET_1955",
                "L_HOMME_QUI_EN_SAVAIT_TROP_1956",
                "SUEURS_FROIDES_1958",
                "LA_MORT_AUX_TROUSSES_1959",
                "PSYCHOSE_1960",
                "LES_OISEAUX_1963",
                "PAS_DE_PRINTEMPS_POUR_MARNIE_1964",
                "FRENZY_1972",
            ], movie_codes),
            "countryCodes": ["USA", "UK"],
            "track": "DARKROOM",
        })

    orders = [item["displayOrder"] for item in pack["collections"]]
    if len(orders) != len(set(orders)):
        raise SystemExit(f"Duplicate collection displayOrder: {orders}")

    pack["version"] = 16
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
    CATALOG_V2.write_text(text, encoding="utf-8")
    shutil.copyfile(CATALOG_V2, CATALOG_LIVE)

    existing_input = INPUT_MOVIES.read_text(encoding="utf-8") if INPUT_MOVIES.exists() else ""
    to_append: list[str] = []
    for french, year, director, code, original in BATCH_ROWS:
        if code not in added_movies:
            continue
        poster = POSTERS_DIR / f"{code}.jpg"
        if poster.is_file():
            continue
        if f";{code};" in existing_input:
            continue
        to_append.append(
            f'"{french}";{year};"{director}";{code};"{original}"'
        )
    if to_append:
        with INPUT_MOVIES.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n")
            handle.write("# Nouveaux films pack 16 (Hitchcock / Japon 70s / Nouvel Hollywood).\n")
            handle.write("\n".join(to_append))
            handle.write("\n")

    print(f"pack {pack['version']} movies={len(pack['movies'])} collections={len(pack['collections'])}")
    print(f"added movies: {added_movies}")
    print(f"batch posters appended: {len(to_append)}")
    for item in pack["collections"]:
        print(f"  {item['displayOrder']:2} {item['code']} {item['track']:12} {item['name']} ({len(item['movies'])})")


if __name__ == "__main__":
    main()
