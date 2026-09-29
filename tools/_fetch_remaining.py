"""Récupère les films de collections encore absents, avec contrôle réalisateur."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "batchPosters"))

from catalog_enrich import build_movie  # noqa: E402
from posters_batch import TmdbClient, load_env, pick_poster_path  # noqa: E402

CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
BATCH = ROOT / "batchPosters/output/catalog/movies_collections.json"
POSTER_SRC = ROOT / "batchPosters/output/posters"
POSTER_DST = ROOT / "app/src/main/assets/media/posters"
INPUT = ROOT / "batchPosters/input/input_movies.txt"
REPORT = ROOT / "tools/output/_remaining_fetch.txt"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w780"
FOUND_IDS = {
    "THE_SPOOKY_BUNCH_1980": 104681,
    "THE_SECRET_1979": 176219,
    "THE_CLUB_1981": 170319,
    "NOMAD_1982": 157229,
    "L_INCIDENT_DU_CANON_NOIR_1985": 176643,
    "EMPIRE_WARHOL_1964": 108419,
}

# code, year, director, french title, queries, collections, force country, characteristics
TARGETS = [
    (
        "BULLET_IN_THE_HEAD_1990",
        1990,
        "John Woo",
        "Bullet in the Head",
        [],
        ["COLLECTION_019"],
        "HONG_KONG",
        ["HONG_KONG_NEW_WAVE"],
    ),
    (
        "THE_SPOOKY_BUNCH_1980",
        1980,
        "Ann Hui",
        "The Spooky Bunch",
        ["The Spooky Bunch", "撞到正"],
        ["COLLECTION_019"],
        "HONG_KONG",
        ["HONG_KONG_NEW_WAVE"],
    ),
    (
        "THE_SECRET_1979",
        1979,
        "Ann Hui",
        "The Secret",
        ["瘋劫", "Feng jie", "The Secret"],
        ["COLLECTION_019"],
        "HONG_KONG",
        ["HONG_KONG_NEW_WAVE"],
    ),
    (
        "THE_CLUB_1981",
        1981,
        "Kirk Wong",
        "The Club",
        ["舞廳", "The Club"],
        ["COLLECTION_019"],
        "HONG_KONG",
        ["HONG_KONG_NEW_WAVE"],
    ),
    (
        "NOMAD_1982",
        1982,
        "Patrick Tam",
        "Nomad",
        ["烈火青春", "Nomad"],
        ["COLLECTION_019"],
        "HONG_KONG",
        ["HONG_KONG_NEW_WAVE"],
    ),
    (
        "VALERIE_ET_LA_SEMAINE_DES_MERVEILLES_1970",
        1970,
        "Jaromil Jireš",
        "Valérie et la Semaine des merveilles",
        ["Valerie and Her Week of Wonders", "Valerie a týden divů"],
        ["COLLECTION_021", "COLLECTION_023"],
        "CZECH",
        ["SURREALISME", "NOUVELLE_VAGUE_TCHEQUE"],
    ),
    (
        "LE_SOLEIL_DANS_UN_FILET_1962",
        1962,
        "Štefan Uher",
        "Le Soleil dans un filet",
        ["The Sun in a Net", "Slnko v sieti"],
        ["COLLECTION_023"],
        "CZECH",
        ["NOUVELLE_VAGUE_TCHEQUE"],
    ),
    (
        "LE_CR_MATEUR_1969",
        1969,
        "Juraj Herz",
        "Le Crémateur",
        ["The Cremator", "Spalovač mrtvol"],
        ["COLLECTION_023"],
        "CZECH",
        ["NOUVELLE_VAGUE_TCHEQUE"],
    ),
    (
        "UN_ET_HUIT_1983",
        1983,
        "Zhang Junzhao",
        "Un et Huit",
        ["One and Eight", "一个和八个"],
        ["COLLECTION_024"],
        "CHINA",
        ["CINQUIEME_GENERATION_CHINOISE"],
    ),
    (
        "L_INCIDENT_DU_CANON_NOIR_1985",
        1985,
        "Huang Jianxin",
        "L'Incident du canon noir",
        ["The Black Cannon Incident", "黑炮事件"],
        ["COLLECTION_024"],
        "CHINA",
        ["CINQUIEME_GENERATION_CHINOISE"],
    ),
    (
        "LE_VIEUX_PUITS_1987",
        1987,
        "Wu Tianming",
        "Le Vieux Puits",
        ["Old Well", "老井"],
        ["COLLECTION_024"],
        "CHINA",
        ["CINQUIEME_GENERATION_CHINOISE"],
    ),
    (
        "LA_LUNE_TENTATRICE_1996",
        1996,
        "Chen Kaige",
        "La Lune tentatrice",
        ["Temptress Moon", "风月"],
        ["COLLECTION_024"],
        "CHINA",
        ["CINQUIEME_GENERATION_CHINOISE"],
    ),
    (
        "EMPIRE_WARHOL_1964",
        1964,
        "Andy Warhol",
        "Empire",
        ["Empire Warhol", "Andy Warhol Empire", "Empire"],
        ["COLLECTION_026"],
        "USA",
        ["CINEMA_EXPERIMENTAL"],
    ),
]


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def slug_name(display: str) -> str:
    normalized = unicodedata.normalize("NFKD", display)
    ascii_name = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ascii_name).strip("_").upper()
    return slug


def covers(name: str, blob: str) -> bool:
    parts = [part for part in fold(name).split() if len(part) >= 3]
    tokens = set(fold(blob).split())
    return bool(parts) and all(part in tokens for part in parts)


def director_blob(details: dict) -> str:
    crew = (details.get("credits") or {}).get("crew") or []
    jobs = {"director", "realisateur"}
    names = []
    for person in crew:
        job = fold(str(person.get("job") or ""))
        if job in jobs or job.startswith("director"):
            names.append(str(person.get("name") or ""))
    return " ".join(names)


def acceptable(code: str, year: int, director: str, details: dict) -> bool:
    blob = director_blob(details)
    if not covers(director, blob):
        return False
    title = fold(str(details.get("title") or ""))
    original = fold(str(details.get("original_title") or ""))
    if code == "EMPIRE_WARHOL_1964":
        return "warhol" in fold(blob) and (title == "empire" or original == "empire") and "roman" not in title and "fall" not in title
    release = str(details.get("release_date") or "")
    tmdb_year = int(release[:4]) if len(release) >= 4 and release[:4].isdigit() else 0
    if tmdb_year and abs(tmdb_year - year) > 2:
        return False
    return True


def person_record(display: str, taken: set[str]) -> dict:
    parts = display.split()
    first = " ".join(parts[:-1]) if len(parts) > 1 else ""
    last = parts[-1] if parts else display
    code = slug_name(display) or "DIRECTOR"
    base = code
    suffix = 2
    while code in taken:
        code = f"{base}_{suffix}"
        suffix += 1
    return {
        "code": code,
        "firstName": first,
        "lastName": last,
        "displayName": display,
        "characteristicCodes": [],
    }


def resort(collection: dict, movies_by_code: dict) -> None:
    ranked = []
    for ref in collection["movies"]:
        movie = movies_by_code[ref["code"]]
        ranked.append((int(movie.get("releaseYear") or 0), ref["code"]))
    ranked.sort()
    seen = set()
    movies = []
    for year, code in ranked:
        if code in seen:
            continue
        seen.add(code)
        movies.append({"code": code, "displayOrder": len(movies) + 1})
    collection["movies"] = movies


def search(client: TmdbClient, queries: list[str], year: int) -> list[dict]:
    seen: set[int] = set()
    found: list[dict] = []
    for query in queries:
        for language in ("en-US", "fr-FR"):
            for item in client.search_movie(query, year, language):
                movie_id = item.get("id")
                if not isinstance(movie_id, int) or movie_id in seen:
                    continue
                seen.add(movie_id)
                found.append(item)
                if len(found) >= 8:
                    return found
    return found


def save_poster(client: TmdbClient, details: dict, code: str) -> bool:
    poster_path = pick_poster_path(details, ["fr", "xx", "en"])
    if not poster_path:
        return False
    data, _content_type = client.download(f"{TMDB_IMAGE}{poster_path}")
    if not data:
        return False
    destination = POSTER_DST / f"{code}.jpg"
    if destination.exists():
        return False
    destination.write_bytes(data)
    return True


def main() -> None:
    load_env(ROOT / "batchPosters" / ".env")
    token = (os.environ.get("TMDB_ACCESS_TOKEN") or os.environ.get("TMDB_API_KEY") or "").strip()
    api_key = (os.environ.get("TMDB_API_KEY") or "").strip()
    if not token and not api_key:
        raise SystemExit("TMDB manquant")
    client = TmdbClient(api_key, os.environ.get("TMDB_ACCESS_TOKEN") or "", 0.2)
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    batch_movies = {item["code"]: item for item in batch["movies"]}
    movies_by_code = {item["code"]: item for item in pack["movies"]}
    collections = {item["code"]: item for item in pack["collections"]}
    known_countries = {item["code"] for item in pack["countries"]}
    known_genres = {item["code"] for item in pack["genres"]}
    known_chars = {item["code"] for item in pack["characteristics"]}
    taken_directors = {item["code"] for item in pack["directors"]}
    lines: list[str] = []
    added: list[str] = []
    failed: list[tuple[str, int, str, str]] = []

    for code, year, director, french, queries, collection_codes, forced, chars in TARGETS:
        if code in movies_by_code:
            lines.append(f"SKIP_EXISTS {code}")
            continue
        movie = None
        details = None
        if code == "BULLET_IN_THE_HEAD_1990":
            movie = json.loads(json.dumps(batch_movies[code]))
        elif code in FOUND_IDS:
            identity = client.movie_details(FOUND_IDS[code], "en-US")
            if not acceptable(code, year, director, identity):
                lines.append(f"REJECT_ID {code}")
                failed.append((french, year, director, code))
                continue
            details = client.movie_details(FOUND_IDS[code], "fr-FR")
            movie, _new_directors, _new_countries, _warnings = build_movie(
                code=code,
                csv_title=french,
                csv_original=french,
                csv_year=year,
                csv_director=director,
                demand=0.72,
                details=details,
                catalog=pack,
            )
        else:
            chosen = None
            for item in search(client, queries, year):
                details = client.movie_details(int(item["id"]), "fr-FR")
                if acceptable(code, year, director, details):
                    chosen = details
                    break
            if chosen is None:
                lines.append(f"NOT_FOUND {code}")
                failed.append((french, year, director, code))
                continue
            movie, _new_directors, _new_countries, _warnings = build_movie(
                code=code,
                csv_title=french,
                csv_original=french,
                csv_year=year,
                csv_director=director,
                demand=0.72,
                details=chosen,
                catalog=pack,
            )
            details = chosen
        existing = next((item for item in pack["directors"] if fold(item.get("displayName") or "") == fold(director)), None)
        if existing is None:
            existing = person_record(director, taken_directors)
            pack["directors"].append(existing)
            taken_directors.add(existing["code"])
        movie["directors"] = [{"code": existing["code"], "billingOrder": 0}]
        movie["frenchTitle"] = french
        movie["releaseYear"] = year
        countries = []
        for item in movie.get("countries") or []:
            country = item["code"]
            if country == "SLOVAKIA":
                country = "CZECH"
            if country not in known_countries or any(current["code"] == country for current in countries):
                continue
            countries.append({"code": country, "isPrimary": False})
        countries = [item for item in countries if item["code"] != forced]
        countries.insert(0, {"code": forced, "isPrimary": True})
        movie["countries"] = countries[:2]
        movie["countries"][0]["isPrimary"] = True
        for item in movie["countries"][1:]:
            item["isPrimary"] = False
        movie["genreCodes"] = [item for item in movie.get("genreCodes") or [] if item in known_genres] or ["DRAME"]
        movie["characteristicCodes"] = [item for item in chars if item in known_chars]
        if code == "EMPIRE_WARHOL_1964":
            movie["isExperimental"] = True
        pack["movies"].append(movie)
        movies_by_code[code] = movie
        for collection_code in collection_codes:
            collections[collection_code]["movies"].append({"code": code, "displayOrder": 99})
            resort(collections[collection_code], movies_by_code)
        poster_ok = False
        if code == "BULLET_IN_THE_HEAD_1990":
            source = next(POSTER_SRC.glob(code + ".*"), None)
            destination = POSTER_DST / f"{code}.jpg"
            if source and not destination.exists():
                shutil.copyfile(source, destination)
                poster_ok = True
            elif destination.exists():
                poster_ok = True
        elif details is not None:
            poster_ok = save_poster(client, details, code)
        added.append(code)
        lines.append(f"ADDED {code} poster={poster_ok} tmdb={details.get('id') if details else 'batch'}")

    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    existing_input = INPUT.read_text(encoding="utf-8") if INPUT.is_file() else ""
    kept = []
    added_codes = set(added)
    for raw in existing_input.splitlines():
        if any(code in raw for code in added_codes):
            continue
        if "VAL_RIE_ET_LA_SEMAINE_DES_MERVEILLES_1970" in raw and "VALERIE_ET_LA_SEMAINE_DES_MERVEILLES_1970" in added_codes:
            continue
        kept.append(raw)
    def cell(value: str) -> str:
        return '"' + value.replace('"', "'") + '"'
    for french, year, director, code in failed:
        line = ";".join([cell(french), str(year), cell(director), code, cell(french)])
        if code in "\n".join(kept):
            continue
        kept.append(line)
    text = "\n".join(kept).rstrip() + "\n"
    INPUT.write_text(text, encoding="utf-8")
    lines.insert(0, f"added={len(added)} failed={len(failed)} movies={len(pack['movies'])}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[0])


if __name__ == "__main__":
    main()
