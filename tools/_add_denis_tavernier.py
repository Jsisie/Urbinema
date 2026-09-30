"""Add the Tavernier / Park / Kaufman / Denis / Villeneuve / Dang films and fix Claire Denis credits."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from catalog_enrich import build_movie  # noqa: E402
from posters_batch import TmdbClient, fold, load_env, pick_poster_path  # noqa: E402
from _strip_wiki import strip_wiki  # noqa: E402

CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
POSTERS = ROOT / "app/src/main/assets/media/posters"
DIRECTORS = ROOT / "app/src/main/assets/media/directors"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w780"
TMDB_FACE = "https://image.tmdb.org/t/p/w342"

# code, french title, year, search titles, director hint, forced director, currents
FILMS = [
    ("L_HORLOGER_DE_SAINT_PAUL_1974", "L'Horloger de Saint-Paul", 1974,
     ["L'Horloger de Saint-Paul", "The Clockmaker of St. Paul"], "Tavernier", "BERTRAND_TAVERNIER", []),
    ("LA_MORT_EN_DIRECT_1980", "La Mort en direct", 1980,
     ["La Mort en direct", "Death Watch"], "Tavernier", "BERTRAND_TAVERNIER", []),
    ("COUP_DE_TORCHON_1981", "Coup de torchon", 1981,
     ["Coup de torchon"], "Tavernier", "BERTRAND_TAVERNIER", []),
    ("L_627_1992", "L.627", 1992,
     ["L.627", "L 627"], "Tavernier", "BERTRAND_TAVERNIER", []),
    ("MADEMOISELLE_2016", "Mademoiselle", 2016,
     ["The Handmaiden", "Mademoiselle", "Ah-ga-ssi"], "Park", "PARK_CHAN_WOOK", ["MELODRAME"]),
    ("SYMPATHY_FOR_MR_VENGEANCE_2002", "Sympathy for Mr. Vengeance", 2002,
     ["Sympathy for Mr. Vengeance", "Boksuneun naui geot"], "Park", "PARK_CHAN_WOOK", ["KOREAN_NEW_WAVE"]),
    ("JE_VEUX_JUSTE_EN_FINIR_2020", "Je veux juste en finir", 2020,
     ["I'm Thinking of Ending Things"], "Kaufman", "CHARLIE_KAUFMAN", ["SURREALISME"]),
    ("CHOCOLAT_1988", "Chocolat", 1988,
     ["Chocolat"], "Denis", "CLAIRE_DENIS", ["CINEMA_D_AUTEUR"]),
    ("WHITE_MATERIAL_2009", "White Material", 2009,
     ["White Material"], "Denis", "CLAIRE_DENIS", []),
    ("POLYTECHNIQUE_2009", "Polytechnique", 2009,
     ["Polytechnique"], "Villeneuve", "DENIS_VILLENEUVE", []),
    ("LA_SAISON_DES_GOYAVES_2000", "La Saison des goyaves", 2000,
     ["The Guava Season", "Mua oi", "La Saison des goyaves"], "Minh", "DANG_NHAT_MINH", [], 276689),
]


def ascii_text(value: str) -> str:
    return (value or "").encode("ascii", "replace").decode("ascii")


def director_names(details: dict) -> list[str]:
    names = []
    for person in (details.get("credits") or {}).get("crew") or []:
        if person.get("job") == "Director" and person.get("name"):
            names.append(str(person["name"]))
    return names


def hint_ok(names: list[str], hint: str) -> bool:
    needle = fold(hint)
    for name in names:
        folded = fold(name)
        if needle in folded.split() or needle in folded:
            return True
    return False


def choose(client: TmdbClient, titles: list[str], year: int, hint: str) -> dict:
    seen: set[int] = set()
    for title in titles:
        for item in client.search_movie(title, year, "fr-FR"):
            movie_id = item.get("id")
            if not isinstance(movie_id, int) or movie_id in seen:
                continue
            seen.add(movie_id)
            details = client.movie_details(movie_id, "fr-FR")
            release = str(details.get("release_date") or "")
            got_year = int(release[:4]) if len(release) >= 4 and release[:4].isdigit() else 0
            names = director_names(details)
            if abs(got_year - year) > 1:
                continue
            if not hint_ok(names, hint):
                print("  skip", movie_id, ascii_text(str(details.get("title") or "")), got_year, ascii_text(" / ".join(names)))
                continue
            return details
    raise SystemExit(f"no match for {titles[0]} {year} {hint}")


def save_jpeg(client: TmdbClient, url: str, dest: Path) -> int:
    data, _kind = client.download(url)
    if not data or not data.startswith(b"\xff\xd8"):
        raise SystemExit(f"not a jpeg: {dest.name}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return len(data)


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters/.env")
    client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    known = {item["code"] for item in pack["characteristics"]}
    directors = {item["code"] for item in pack["directors"]}
    movies = {item["code"]: item for item in pack["movies"]}
    for film in FILMS:
        code, _title, _year, _queries, _hint, director, currents = film[:7]
        if code in movies:
            raise SystemExit(f"already in catalog: {code}")
        if director not in directors:
            raise SystemExit(f"missing director {director}")
        for current in currents:
            if current not in known:
                raise SystemExit(f"missing current {current}")

    built = []
    for film in FILMS:
        code, french, year, queries, hint, director, currents = film[:7]
        forced_id = film[7] if len(film) > 7 else None
        print("FETCH", code)
        if forced_id:
            details = client.movie_details(forced_id, "fr-FR")
            names = director_names(details)
            if not hint_ok(names, hint):
                raise SystemExit(f"id {forced_id} is not {code}: {ascii_text(' / '.join(names))}")
        else:
            details = choose(client, queries, year, hint)
        movie, _new_dirs, new_countries, warnings = build_movie(
            code=code,
            csv_title=french,
            csv_original=queries[-1],
            csv_year=year,
            csv_director=hint,
            demand=0.66,
            details=details,
            catalog=pack,
        )
        if new_countries:
            raise SystemExit(f"unknown country on {code}: {new_countries}")
        movie["frenchTitle"] = french
        movie["releaseYear"] = year
        movie["directors"] = [{"code": director, "billingOrder": 0}]
        movie["characteristicCodes"] = list(currents)
        if code == "POLYTECHNIQUE_2009":
            movie["isBlackAndWhite"] = True
        poster = pick_poster_path(details, ["fr", "xx", "en"])
        if not poster:
            raise SystemExit(f"no poster {code}")
        size = save_jpeg(client, f"{TMDB_IMAGE}{poster}", POSTERS / f"{code}.jpg")
        names = ", ".join(director_names(details))
        print(
            "  OK",
            movie["releaseYear"],
            ascii_text(movie.get("originalTitle") or ""),
            ascii_text(names),
            ",".join(item["code"] for item in movie["countries"]),
            ",".join(movie["genreCodes"]),
            "poster",
            size,
            "warn",
            ascii_text(" | ".join(warnings)),
        )
        built.append(movie)

    for movie in pack["movies"]:
        if movie["code"] in {"BEAU_TRAVAIL_1999", "35_SHOTS_OF_RUM_2008", "TROUBLE_EVERY_DAY_2001"}:
            movie["directors"] = [{"code": "CLAIRE_DENIS", "billingOrder": 0}]
        if movie["code"] in {"BEAU_TRAVAIL_1999", "35_SHOTS_OF_RUM_2008"}:
            movie["characteristicCodes"] = [
                item for item in movie.get("characteristicCodes") or [] if item != "NEW_FRENCH_EXTREMITY"
            ]
        if movie["code"] == "35_SHOTS_OF_RUM_2008":
            movie["frenchTitle"] = "35 Rhums"

    claire = next(item for item in pack["directors"] if item["code"] == "CLAIRE_DENIS")
    people = client.request_json("/search/person", {"query": "Claire Denis", "language": "en-US", "page": "1"})
    person_id = None
    for item in people.get("results") or []:
        if fold(str(item.get("name") or "")) == fold("Claire Denis"):
            person_id = int(item["id"])
            break
    if person_id is None:
        raise SystemExit("Claire Denis not found")
    french_person = client.request_json(f"/person/{person_id}", {"language": "fr-FR"})
    english_person = client.request_json(f"/person/{person_id}", {"language": "en-US"})
    fr = strip_wiki(str(french_person.get("biography") or ""))
    en = strip_wiki(str(english_person.get("biography") or ""))
    if fr:
        claire["biography"] = fr
    if en:
        claire["biographyEn"] = en
    claire["characteristicCodes"] = []
    path = french_person.get("profile_path") or english_person.get("profile_path")
    if not path:
        raise SystemExit("Claire Denis has no photo")
    face = save_jpeg(client, f"{TMDB_FACE}{path}", DIRECTORS / "CLAIRE_DENIS.jpg")
    print("CLAIRE", person_id, "photo", face, "fr", len(fr), "en", len(en))

    pack["movies"].extend(built)
    for badge in pack["badges"]:
        if badge["code"] == "032":
            badge["description"] = "Voir 50 films d'horreur."
    pack["version"] = 38
    horror = sum(1 for movie in pack["movies"] if "HORREUR" in (movie.get("genreCodes") or []))
    denis_films = [
        movie["code"] for movie in pack["movies"]
        if any(item["code"] == "CLAIRE_DENIS" for item in movie["directors"])
    ]
    print("version", pack["version"], "movies", len(pack["movies"]), "directors", len(pack["directors"]), "horror", horror)
    print("denis", ",".join(denis_films))
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    tmp = COPY.with_suffix(".json.tmp")
    shutil.copyfile(CATALOG, tmp)
    tmp.replace(COPY)
    print("written")


if __name__ == "__main__":
    main()
