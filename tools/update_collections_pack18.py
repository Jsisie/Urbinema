#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pack 18 : Film noir / Western / Âge d'or japonais."""
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


def director_entry(code: str, first: str, last: str, chars: list[str] | None = None) -> dict:
    return {
        "code": code,
        "lastName": last,
        "displayName": f"{first} {last}".strip(),
        "firstName": first,
        "characteristicCodes": chars or [],
    }


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


def title_of(movie: dict) -> str:
    return (movie.get("frenchTitle") or movie.get("originalTitle") or "").casefold()


def collection_by_code(pack: dict, code: str) -> dict:
    for item in pack["collections"]:
        if item["code"] == code:
            return item
    raise SystemExit(f"Missing collection {code}")


def merge_movies(collection: dict, codes: list[str], available: set[str]) -> None:
    missing = [code for code in codes if code not in available]
    if missing:
        raise SystemExit(f"{collection['code']} unknown movies: {missing}")
    existing = [row["code"] for row in collection.get("movies") or []]
    for code in codes:
        if code not in existing:
            existing.append(code)
    collection["movies"] = [{"code": code, "displayOrder": index} for index, code in enumerate(existing, start=1)]


def sort_collection(collection: dict, by_code: dict[str, dict]) -> None:
    rows = list(collection.get("movies") or [])
    rows.sort(
        key=lambda row: (
            by_code[row["code"]]["releaseYear"],
            title_of(by_code[row["code"]]),
            row["code"],
        )
    )
    collection["movies"] = [
        {"code": row["code"], "displayOrder": index}
        for index, row in enumerate(rows, start=1)
    ]


NEW_DIRECTORS = [
    director_entry("JOSEPH_H_LEWIS", "Joseph H.", "Lewis", ["FILM_NOIR_STYLE", "HOLLYWOOD_CLASSIQUE"]),
    director_entry("ANDREW_DOMINIK", "Andrew", "Dominik", ["CINEMA_D_AUTEUR"]),
    director_entry("TOMU_UCHIDA", "Tomu", "Uchida", ["AGE_OR_CINEMA_JAPONAIS", "JIDAIGEKI"]),
    director_entry("KEISUKE_KINOSHITA", "Keisuke", "Kinoshita", ["AGE_OR_CINEMA_JAPONAIS", "CINEMA_D_AUTEUR"]),
]

NEW_MOVIES = [
    film(
        "THE_BIG_COMBO_1955", "The Big Combo", "Association criminelle", 1955, 89,
        "Un flic s'acharne sur un syndicate et sur la maîtresse du caïd.",
        "USA", "JOSEPH_H_LEWIS", ["FILM_NOIR", "POLICIER", "CRIME"],
        ["FILM_NOIR_STYLE", "HOLLYWOOD_CLASSIQUE"],
        bw=True, demand=0.7,
    ),
    film(
        "WINCHESTER_73_1950", "Winchester '73", "Winchester '73", 1950, 92,
        "Un fusil de compétition passe de main en main à travers la Frontière.",
        "USA", "ANTHONY_MANN", ["WESTERN"],
        ["WESTERN_CLASSIQUE", "HOLLYWOOD_CLASSIQUE"],
        bw=True, demand=0.68,
    ),
    film(
        "JOSEY_WALES_HORS_LA_LOI_1976", "The Outlaw Josey Wales", "Josey Wales hors-la-loi", 1976, 135,
        "Un fermier du Missouri, famille massacrée, devient hors-la-loi malgré lui.",
        "USA", "CLINT_EASTWOOD", ["WESTERN", "DRAME"],
        ["WESTERN_CLASSIQUE"],
        bw=False, demand=0.66,
    ),
    film(
        "L_ASSASSINAT_DE_JESSE_JAMES_2007",
        "The Assassination of Jesse James by the Coward Robert Ford",
        "L'Assassinat de Jesse James par le lâche Robert Ford",
        2007, 160,
        "Robert Ford s'approche de Jesse James jusqu'à le tuer, puis à n'être plus que ça.",
        "USA", "ANDREW_DOMINIK", ["WESTERN", "DRAME", "BIOGRAPHIQUE"],
        ["CINEMA_D_AUTEUR"],
        bw=False, demand=0.78,
    ),
    film(
        "L_ELEGIE_D_OSAKA_1936", "Naniwa erejii", "L'Élégie d'Osaka", 1936, 90,
        "Une jeune standardiste d'Osaka se ruine pour un homme et pour sa famille.",
        "JAPAN", "KENJI_MIZOGUCHI", ["DRAME"],
        ["AGE_OR_CINEMA_JAPONAIS", "MELODRAME"],
        bw=True, demand=0.8,
    ),
    film(
        "LA_TRAGEDIE_DU_JAPON_1953", "Nihon no higeki", "La Tragédie du Japon", 1953, 116,
        "Une mère d'après-guerre se sacrifie ; ses enfants la rejettent.",
        "JAPAN", "KEISUKE_KINOSHITA", ["DRAME"],
        ["AGE_OR_CINEMA_JAPONAIS"],
        bw=True, demand=0.76,
    ),
    film(
        "LE_GRONDEMENT_DE_LA_MONTAGNE_1954", "Yama no oto", "Le Grondement de la montagne", 1954, 95,
        "Un père de famille entend, trop tard, ce que sa belle-fille ne dit pas.",
        "JAPAN", "MIKIO_NARUSE", ["DRAME"],
        ["AGE_OR_CINEMA_JAPONAIS", "MELODRAME"],
        bw=True, demand=0.78,
    ),
    film(
        "VINGT_QUATRE_PRUNELLES_1954", "Nijushi no hitomi", "Vingt-quatre prunelles", 1954, 156,
        "Une institutrice de l'île de Shōdoshima suit douze élèves de 1928 à l'après-guerre.",
        "JAPAN", "KEISUKE_KINOSHITA", ["DRAME", "GUERRE"],
        ["AGE_OR_CINEMA_JAPONAIS"],
        bw=True, demand=0.74,
    ),
    film(
        "LA_HARPE_DE_BIRMANIE_1956", "Biruma no tategoto", "La Harpe de Birmanie", 1956, 116,
        "Un soldat japonais reste en Birmanie pour enterrer les morts de son armée.",
        "JAPAN", "KON_ICHIKAWA", ["GUERRE", "DRAME"],
        ["AGE_OR_CINEMA_JAPONAIS"],
        bw=True, demand=0.76,
    ),
    film(
        "LA_CONDITION_DE_L_HOMME_2_1959", "人間の條件 第2部",
        "La Condition de l'homme II : Le Chemin de l'éternité", 1959, 181,
        "Kaji est envoyé au front ; l'armée japonaise achève de le briser.",
        "JAPAN", "MASAKI_KOBAYASHI", ["GUERRE", "DRAME", "HISTORIQUE"],
        ["AGE_OR_CINEMA_JAPONAIS"],
        bw=True, demand=0.86,
    ),
    film(
        "LA_CONDITION_DE_L_HOMME_3_1961", "人間の條件 第3部",
        "La Condition de l'homme III : La Prière du soldat", 1961, 190,
        "Kaji traverse la Mandchourie en ruines, prisonnier puis fuyard.",
        "JAPAN", "MASAKI_KOBAYASHI", ["GUERRE", "DRAME", "HISTORIQUE"],
        ["AGE_OR_CINEMA_JAPONAIS"],
        bw=True, demand=0.86,
    ),
    film(
        "LA_COURTISANE_DE_NAKANO_1960", "Hana no Yoshiwara hyakunin giri",
        "La Courtisane de Nakano", 1960, 110,
        "Un marchand défiguré ruine sa vie pour une courtisane de Yoshiwara.",
        "JAPAN", "TOMU_UCHIDA", ["DRAME", "HISTORIQUE"],
        ["AGE_OR_CINEMA_JAPONAIS", "JIDAIGEKI"],
        bw=False, demand=0.74,
    ),
]

BATCH_ROWS = [
    ("Association criminelle", 1955, "Joseph H. Lewis", "THE_BIG_COMBO_1955", "The Big Combo"),
    ("Winchester '73", 1950, "Anthony Mann", "WINCHESTER_73_1950", "Winchester '73"),
    ("Josey Wales hors-la-loi", 1976, "Clint Eastwood", "JOSEY_WALES_HORS_LA_LOI_1976", "The Outlaw Josey Wales"),
    (
        "L'Assassinat de Jesse James par le lâche Robert Ford",
        2007,
        "Andrew Dominik",
        "L_ASSASSINAT_DE_JESSE_JAMES_2007",
        "The Assassination of Jesse James by the Coward Robert Ford",
    ),
    ("L'Élégie d'Osaka", 1936, "Kenji Mizoguchi", "L_ELEGIE_D_OSAKA_1936", "Naniwa erejii"),
    ("La Tragédie du Japon", 1953, "Keisuke Kinoshita", "LA_TRAGEDIE_DU_JAPON_1953", "Nihon no higeki"),
    ("Le Grondement de la montagne", 1954, "Mikio Naruse", "LE_GRONDEMENT_DE_LA_MONTAGNE_1954", "Yama no oto"),
    ("Vingt-quatre prunelles", 1954, "Keisuke Kinoshita", "VINGT_QUATRE_PRUNELLES_1954", "Nijushi no hitomi"),
    ("La Harpe de Birmanie", 1956, "Kon Ichikawa", "LA_HARPE_DE_BIRMANIE_1956", "Biruma no tategoto"),
    (
        "La Condition de l'homme II : Le Chemin de l'éternité",
        1959,
        "Masaki Kobayashi",
        "LA_CONDITION_DE_L_HOMME_2_1959",
        "Ningen no joken II",
    ),
    (
        "La Condition de l'homme III : La Prière du soldat",
        1961,
        "Masaki Kobayashi",
        "LA_CONDITION_DE_L_HOMME_3_1961",
        "Ningen no joken III",
    ),
    (
        "La Courtisane de Nakano",
        1960,
        "Tomu Uchida",
        "LA_COURTISANE_DE_NAKANO_1960",
        "Hana no Yoshiwara hyakunin giri",
    ),
]


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

    noir = collection_by_code(pack, "COLLECTION_008")
    merge_movies(noir, [
        "DETOUR_1945",
        "LE_GRAND_SOMMEIL_1946",
        "SORTILEGES_1947",
        "LA_DAME_DE_SHANGHAI_1947",
        "THE_BIG_COMBO_1955",
        "LE_SAMOURAI_1967",
        "THE_LONG_GOODBYE_1973",
    ], movie_codes)

    western = collection_by_code(pack, "COLLECTION_009")
    merge_movies(western, [
        "WINCHESTER_73_1950",
        "JOHNNY_GUITAR_1954",
        "MCCABE_AND_MRS_MILLER_1971",
        "JOSEY_WALES_HORS_LA_LOI_1976",
        "IMPITOYABLE_1992",
        "L_ASSASSINAT_DE_JESSE_JAMES_2007",
    ], movie_codes)

    japon = collection_by_code(pack, "COLLECTION_003")
    japon["name"] = "Âge d'or japonais"
    japon["description"] = "Quelques portes d'entrée vers l'âge d'or du cinéma japonais."
    merge_movies(japon, [
        "JE_SUIS_NE_MAIS_1932",
        "L_ELEGIE_D_OSAKA_1936",
        "PRINTEMPS_TARDIF_1949",
        "LA_TRAGEDIE_DU_JAPON_1953",
        "LE_GRONDEMENT_DE_LA_MONTAGNE_1954",
        "VINGT_QUATRE_PRUNELLES_1954",
        "LA_HARPE_DE_BIRMANIE_1956",
        "LA_CONDITION_DE_L_HOMME_1959",
        "LA_CONDITION_DE_L_HOMME_2_1959",
        "LA_COURTISANE_DE_NAKANO_1960",
        "LA_CONDITION_DE_L_HOMME_3_1961",
    ], movie_codes)

    by_code = {movie["code"]: movie for movie in pack["movies"]}
    for collection in pack["collections"]:
        sort_collection(collection, by_code)

    pack["version"] = 18
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
        to_append.append(f'"{french}";{year};"{director}";{code};"{original}"')
    if to_append:
        with INPUT_MOVIES.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n")
            handle.write("# Nouveaux films pack 18 (Film noir / Western / Âge d'or japonais).\n")
            handle.write("\n".join(to_append))
            handle.write("\n")

    print(f"pack {pack['version']} movies={len(pack['movies'])}")
    print(f"added movies: {added_movies}")
    print(f"batch posters appended: {len(to_append)}")
    for code in ("COLLECTION_003", "COLLECTION_008", "COLLECTION_009"):
        item = collection_by_code(pack, code)
        print(f"  {item['name']} ({len(item['movies'])})")


if __name__ == "__main__":
    main()
