"""Merge the horror TMDB batch into catalog_v3. Characteristics only if they already exist."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
BATCH = ROOT / "batchsData/batchPosters/output/catalog/movies.json"
POSTERS_SRC = ROOT / "batchsData/batchPosters/output/posters"
POSTERS_DST = ROOT / "app/src/main/assets/media/posters"
INPUT_DIRS = ROOT / "batchsData/batchReals/input/input_directors.txt"
NEW_DIRS = ROOT / "tools/output/_horror_new_directors.txt"

TAGS = {
    "L_OISEAU_AU_PLUMAGE_DE_CRISTAL_1970": ["GIALLO"],
    "TENEBRES_1982": ["GIALLO"],
    "PHENOMENES_1985": [],
    "LE_MASQUE_DU_DEMON_1960": [],
    "LA_DANSE_DES_VAMPIRES_1967": ["CINEMA_D_AUTEUR"],
    "LA_MARQUE_DU_DIABLE_1970": ["CINEMA_EXPLOITATION"],
    "LES_LEVRES_DE_SANG_1975": ["SURREALISME"],
    "LA_MERE_JEANNE_DES_ANGES_1961": ["ECOLE_POLONAISE"],
    "VIY_1967": ["CINEMA_SOVIETIQUE"],
    "LE_DIABLE_1972": ["CINEMA_TRANSGRESSION"],
    "SZAMANKA_1996": ["CINEMA_TRANSGRESSION"],
    "CARNIVAL_OF_SOULS_1962": ["CINEMA_INDEPENDANT_AMERICAIN"],
    "GANJA_AND_HESS_1973": ["LA_REBELLION"],
    "DERANGED_1974": ["CINEMA_INDEPENDANT_AMERICAIN"],
    "MARTIN_1977": ["NEW_HOLLYWOOD", "CINEMA_INDEPENDANT_AMERICAIN"],
    "ANGOISSE_1987": [],
    "INUGAMI_2001": [],
    "TROIS_HISTOIRES_DE_L_AU_DELA_2002": [],
    "SPIDER_FOREST_2004": ["KOREAN_NEW_WAVE"],
    "LA_NUIT_DES_MALEFICES_1971": [],
    "PENDAS_FEN_1974": [],
    "A_FIELD_IN_ENGLAND_2013": ["CINEMA_EXPERIMENTAL"],
    "THE_WITCH_2015": [],
    "HAGAZUSSA_2017": [],
    "TETSUO_1989": ["CINEMA_EXPERIMENTAL"],
    "EXISTENZ_1999": [],
    "TAXIDERMIE_2006": ["SURREALISME"],
    "TITANE_2021": ["CINEMA_TRANSGRESSION", "NEW_FRENCH_EXTREMITY"],
    "LA_SENTINELLE_DES_MAUDITS_1977": [],
    "INNOCENCE_2004": [],
    "BEYOND_THE_BLACK_RAINBOW_2010": [],
    "THE_LIGHTHOUSE_2019": [],
    "FRANKENSTEIN_S_EST_ECHAPPE_1957": [],
    "LE_CAUCHEMAR_DE_DRACULA_1958": [],
    "LE_GRAND_INQUISITEUR_1968": [],
    "LA_DERNIERE_MAISON_SUR_LA_GAUCHE_1972": ["CINEMA_EXPLOITATION"],
    "VENDREDI_13_1980": [],
    "LES_GRIFFES_DE_LA_NUIT_1984": [],
    "SCREAM_1996": [],
    "RING_1998": [],
    "AUDITION_1999": [],
    "KAIRO_2001": [],
    "JU_ON_2002": [],
    "THE_EYE_2002": [],
    "LA_RESIDENCE_1969": [],
    "LES_REVOLTES_DE_L_AN_2000_1976": [],
    "LES_AUTRES_2001": [],
    "L_ECHINE_DU_DIABLE_2001": ["NUEVO_CINE_MEXICANO"],
    "L_ORPHELINAT_2007": ["MELODRAME"],
    "LA_CHOSE_D_UN_AUTRE_MONDE_1951": ["AGE_OR_HOLLYWOOD"],
    "L_HOMME_QUI_RETRECIT_1957": ["AGE_OR_HOLLYWOOD"],
    "IT_FOLLOWS_2014": ["CINEMA_INDEPENDANT_AMERICAIN"],
    "HEREDITE_2018": [],
    "US_2019": [],
    "NOPE_2022": [],
    "POLTERGEIST_1982": [],
    "EVIL_DEAD_1981": ["CINEMA_INDEPENDANT_AMERICAIN", "CINEMA_GORE"],
    "MISERY_1990": [],
    "VINGT_HUIT_JOURS_PLUS_TARD_2002": [],
    "MIDSOMMAR_2019": [],
}
ALREADY = {
    "LA_FEMME_DES_SABLES_1964": ["NOUVELLE_VAGUE_JAPONAISE"],
    "L_EMPIRE_DES_SENS_1976": ["NOUVELLE_VAGUE_JAPONAISE"],
    "LA_DERNIERE_VAGUE_1977": ["AUSTRALIAN_NEW_WAVE"],
    "THE_CRIMINAL_LIFE_OF_ARCHIBALDO_DE_LA_CRUZ_1955": ["SURREALISME"],
}
CONTINENT = {
    "AT": ("AUSTRIA", "EUROPE"),
    "HU": ("HUNGARY", "EUROPE"),
    "PL": ("POLAND", "EUROPE"),
    "ES": ("SPAIN", "EUROPE"),
    "MX": ("MEXICO", "NORTH_AMERICA"),
    "TH": ("THAILAND", "ASIA"),
    "KR": ("SOUTH_KOREA", "ASIA"),
    "HK": ("HONG_KONG", "ASIA"),
    "SU": ("RUSSIA", "EUROPE"),
    "RU": ("RUSSIA", "EUROPE"),
}


def add_unique(codes: list, extra: list) -> list:
    for code in extra:
        if code not in codes:
            codes.append(code)
    return codes


def main() -> None:
    payload = json.loads(BATCH.read_text(encoding="utf-8"))
    movies = payload["movies"]
    got = {movie["code"] for movie in movies}
    missing = sorted(set(TAGS) - got)
    if missing:
        raise SystemExit("missing from batch: " + ", ".join(missing))
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    known_chars = {item["code"] for item in pack["characteristics"]}
    known_movies = {item["code"] for item in pack["movies"]}
    known_dirs = {item["code"] for item in pack["directors"]}
    known_countries = {item["code"] for item in pack["countries"]}
    for code, tags in TAGS.items():
        unknown = [tag for tag in tags if tag not in known_chars]
        if unknown:
            raise SystemExit(f"unknown characteristic {unknown} on {code}")
        if code in known_movies:
            raise SystemExit(f"movie already in catalog {code}")

    for movie in movies:
        movie["characteristicCodes"] = list(TAGS[movie["code"]])
        if movie["code"] == "INNOCENCE_2004":
            movie["releaseYear"] = 2004
        if movie["code"] == "THE_WITCH_2015":
            movie["countries"] = [
                {"code": "USA", "isPrimary": True},
                {"code": "CANADA", "isPrimary": False},
            ]
        genres = list(movie.get("genreCodes") or [])
        if "HORREUR" not in genres and movie["code"] in {"INNOCENCE_2004", "THE_LIGHTHOUSE_2019"}:
            genres.append("HORREUR")
            movie["genreCodes"] = genres
        if not movie.get("synopsis"):
            movie["synopsis"] = movie.get("frenchTitle") or movie["originalTitle"]
        if movie.get("durationMinutes", 0) <= 0:
            movie["durationMinutes"] = 90
        if any(item["code"] == "DIRECTOR" for item in movie["directors"]):
            raise SystemExit(f"unnamed director on {movie['code']}")
        pack["movies"].append(movie)

    for movie in pack["movies"]:
        extra = ALREADY.get(movie["code"])
        if extra:
            movie["characteristicCodes"] = add_unique(list(movie.get("characteristicCodes") or []), extra)

    added_directors = []
    for director in payload.get("newDirectors") or []:
        if director["code"] in known_dirs:
            continue
        director.setdefault("characteristicCodes", [])
        pack["directors"].append(director)
        known_dirs.add(director["code"])
        added_directors.append(director)

    for country in payload.get("newCountries") or []:
        if country["code"] in known_countries:
            continue
        if not country.get("continentCodes"):
            iso = str(country.get("isoCode") or "")
            hinted = CONTINENT.get(iso)
            if hinted:
                country["continentCodes"] = [hinted[1]]
        pack["countries"].append(country)
        known_countries.add(country["code"])

    referenced = {item["code"] for item in pack["directors"]}
    for movie in movies:
        for director in movie["directors"]:
            if director["code"] not in referenced:
                raise SystemExit(f"dangling director {director['code']} on {movie['code']}")

    copied = 0
    for movie in movies:
        source = None
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = POSTERS_SRC / f"{movie['code']}{ext}"
            if candidate.is_file() and candidate.stat().st_size > 0:
                source = candidate
                break
        if source is None:
            raise SystemExit(f"missing poster {movie['code']}")
        shutil.copyfile(source, POSTERS_DST / f"{movie['code']}{source.suffix.lower()}")
        copied += 1

    pack["version"] = 37
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY)

    lines = INPUT_DIRS.read_text(encoding="utf-8").splitlines()
    fresh = []
    for director in added_directors:
        row = ";".join([
            director["code"],
            director.get("firstName") or "",
            director.get("lastName") or "",
            director.get("displayName") or director["code"],
        ])
        if row not in lines:
            lines.append(row)
        fresh.append(row)
    INPUT_DIRS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    NEW_DIRS.write_text("\n".join(fresh) + "\n", encoding="utf-8")
    print("movies", len(pack["movies"]), "new", len(movies), "directors", len(added_directors), "posters", copied)


if __name__ == "__main__":
    main()
