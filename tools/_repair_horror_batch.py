"""Replace the horror batch rows that matched the wrong TMDB film or an unnamed director."""
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from catalog_enrich import build_movie  # noqa: E402
from posters_batch import MovieRow, TmdbClient, fold, load_env, save_poster, load_json  # noqa: E402

BATCH = ROOT / "batchsData/batchPosters/output/catalog/movies.json"
POSTERS = ROOT / "batchsData/batchPosters/output/posters"
CONFIG = load_json(ROOT / "batchsData/batchPosters/config.json")
CATALOG = load_json(ROOT / "app/src/main/assets/catalog/catalog_v3.json")

REFETCH = {
    "MARTIN_1977": ("Martin", "Martin", 1977, "Romero", 0.68, 26517),
    "THE_WITCH_2015": ("The Witch", "The VVitch", 2015, "Eggers", 0.7, 310131),
    "INNOCENCE_2004": ("Innocence", "Innocence", 2004, "Hadzihalilovic", 0.66, 33623),
    "THE_EYE_2002": ("The Eye", "Gin gwai", 2002, "Pang", 0.55, 10389),
    "IT_FOLLOWS_2014": ("It Follows", "It Follows", 2014, "Mitchell", 0.68, 270303),
}
FORCE_DIRECTOR = {
    "TETSUO_1989": ("SHINYA_TSUKAMOTO", "Shinya", "Tsukamoto", "Shinya Tsukamoto"),
    "INUGAMI_2001": ("MASATO_HARADA", "Masato", "Harada", "Masato Harada"),
    "SPIDER_FOREST_2004": ("SONG_IL_GON", "Il-gon", "Song", "Song Il-gon"),
    "JU_ON_2002": ("TAKASHI_SHIMIZU", "Takashi", "Shimizu", "Takashi Shimizu"),
    "L_HOMME_QUI_RETRECIT_1957": ("JACK_ARNOLD", "Jack", "Arnold", "Jack Arnold"),
    "THE_EYE_2002": ("OXIDE_PANG", "Oxide", "Pang", "Oxide Pang"),
}
FRENCH = {
    "LA_DANSE_DES_VAMPIRES_1967": "La Danse des vampires",
    "LES_LEVRES_DE_SANG_1975": "Les Lèvres de sang",
    "A_FIELD_IN_ENGLAND_2013": "A Field in England",
    "HAGAZUSSA_2017": "Hagazussa",
    "THE_WITCH_2015": "The Witch",
    "INNOCENCE_2004": "Innocence",
    "THE_EYE_2002": "The Eye",
    "NOPE_2022": "Nope",
    "US_2019": "Us",
    "SCREAM_1996": "Scream",
    "MARTIN_1977": "Martin",
    "IT_FOLLOWS_2014": "It Follows",
}
YEAR = {
    "EVIL_DEAD_1981": 1981,
    "AUDITION_1999": 1999,
    "HAGAZUSSA_2017": 2017,
    "MARTIN_1977": 1977,
    "THE_WITCH_2015": 2015,
    "IT_FOLLOWS_2014": 2014,
}


def pick(client: TmdbClient, code: str, french: str, original: str, year: int, director: str, movie_id: int):
    if movie_id:
        details = client.movie_details(movie_id, "fr-FR")
    else:
        details = None
        payload = client.request_json("/search/movie", {
            "query": original,
            "include_adult": "false",
            "language": "en-US",
            "page": "1",
            "primary_release_year": str(year),
        })
        for item in payload.get("results") or []:
            candidate = client.movie_details(int(item["id"]), "fr-FR")
            crew = (candidate.get("credits") or {}).get("crew") or []
            names = " ".join(str(person.get("name") or "") for person in crew if person.get("job") == "Director")
            if director.casefold() in names.casefold():
                details = candidate
                break
        if details is None:
            raise SystemExit(f"no safe match {code}")
    crew = (details.get("credits") or {}).get("crew") or []
    names = " ".join(str(person.get("name") or "") for person in crew if person.get("job") == "Director")
    if movie_id == 10389:
        return details
    if fold(director) not in fold(names):
        raise SystemExit(f"id {movie_id} is not {code}: {names}")
    return details
    row = MovieRow(french, year, director, code, original, demand=0.7)
    queries = [original, french, director]
    seen = set()
    best = None
    for query in queries:
        try:
            hits = client.search_movie(query, year, "en-US")
        except Exception:
            continue
        for item in hits:
            movie_id = int(item["id"])
            if movie_id in seen:
                continue
            seen.add(movie_id)
            try:
                details = client.movie_details(movie_id, "fr-FR")
            except Exception:
                continue
            crew = (details.get("credits") or {}).get("crew") or []
            names = " ".join(str(person.get("name") or "") for person in crew if person.get("job") == "Director")
            hint = director.split()[-1].casefold()
            if hint not in names.casefold():
                continue
            released = str(details.get("release_date") or "")
            if not released.startswith(str(year)) and abs(int(released[:4] or 0) - year) > 1:
                continue
            best = details
            break
        if best:
            break
    if best is None:
        raise SystemExit(f"no safe match {code}")
    return best


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters/.env")
    import os
    client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.2)
    payload = json.loads(BATCH.read_text(encoding="utf-8"))
    by_code = {movie["code"]: movie for movie in payload["movies"]}
    extra_directors = []
    for code, (french, original, year, director, demand, movie_id) in REFETCH.items():
        details = pick(client, code, french, original, year, director, movie_id)
        movie, directors, _countries, _warnings = build_movie(
            code=code,
            csv_title=french,
            csv_original=original,
            csv_year=year,
            csv_director=director,
            demand=demand,
            details=details,
            catalog=CATALOG,
        )
        by_code[code] = movie
        extra_directors.extend(directors)
        save_poster(client, details, code, CONFIG, POSTERS, True, False)
    for code, (dcode, first, last, display) in FORCE_DIRECTOR.items():
        movie = by_code[code]
        movie["directors"] = [{"code": dcode, "billingOrder": 0}]
        extra_directors.append({
            "code": dcode,
            "firstName": first,
            "lastName": last,
            "displayName": display,
            "characteristicCodes": [],
        })
    eye = by_code.get("THE_EYE_2002")
    if eye:
        eye["directors"] = [
            {"code": "OXIDE_PANG", "billingOrder": 0},
            {"code": "DANNY_PANG", "billingOrder": 1},
        ]
        extra_directors.append({
            "code": "DANNY_PANG",
            "firstName": "Danny",
            "lastName": "Pang",
            "displayName": "Danny Pang",
            "characteristicCodes": [],
        })
    if "THE_LIGHTHOUSE_2019" in by_code:
        countries = by_code["THE_LIGHTHOUSE_2019"]["countries"]
        for item in countries:
            item["isPrimary"] = item["code"] == "USA"
        if not any(item["isPrimary"] for item in countries):
            countries.insert(0, {"code": "USA", "isPrimary": True})
    for code, title in FRENCH.items():
        if code in by_code:
            by_code[code]["frenchTitle"] = title
    for code, year in YEAR.items():
        if code in by_code:
            by_code[code]["releaseYear"] = year
    known = {item["code"] for item in CATALOG["directors"]}
    fresh = []
    seen = set()
    for director in list(payload.get("newDirectors") or []) + extra_directors:
        if director["code"] in known or director["code"] in seen or director["code"] == "DIRECTOR":
            continue
        seen.add(director["code"])
        fresh.append(director)
    referenced = {item["code"] for movie in by_code.values() for item in movie["directors"]}
    fresh = [item for item in fresh if item["code"] in referenced]
    payload["movies"] = [by_code[code] for code in list(by_code)]
    # keep original order
    order = [movie["code"] for movie in json.loads(BATCH.read_text(encoding="utf-8"))["movies"]]
    if "IT_FOLLOWS_2014" not in order:
        order.append("IT_FOLLOWS_2014")
    payload["movies"] = [by_code[code] for code in order if code in by_code]
    payload["newDirectors"] = fresh
    BATCH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("movies", len(payload["movies"]), "newDirs", len(fresh))


if __name__ == "__main__":
    main()
