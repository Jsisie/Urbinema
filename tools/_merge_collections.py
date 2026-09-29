"""Add the nine collections, adjust Cinéma muet, merge fetched films."""
import csv
import json
import re
import shutil
import unicodedata
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
catalog_path = root / "app/src/main/assets/catalog/catalog_v3.json"
match_path = root / "tools/output/_coll_match.txt"
batch_path = root / "batchPosters/output/catalog/movies_collections.json"
report_path = root / "batchPosters/output/reports/catalog_report.csv"
input_path = root / "batchPosters/input/input_collections.txt"
leftover_path = root / "batchPosters/input/input_movies.txt"
poster_src = root / "batchPosters/output/posters"
poster_dst = root / "app/src/main/assets/media/posters"
md_path = root / "specs/Listes_Fonctionnelles/Liste_Collections&Films.md"

ALIASES = {
    "Days of Being Wild": "NOS_ANNEES_SAUVAGES_1990",
    "Le Bal des pompiers": "THE_FIREMEN_S_BALL_1967",
    "Le Cerf-volant bleu": "THE_BLUE_KITE_1993",
    "Harlan County War": "HARLAN_COUNTY_U_S_A_1976",
    "Fallen Angels": "FALLEN_ANGELS_1995",
}
MUET_LONG = (
    "Le cinéma invente presque tous ses langages avant que la parole synchronisée ne les recouvre. "
    "Griffith monumentalise le récit, Feuillade enchaîne Fantômas et Les Vampires, Keaton, Chaplin et Lloyd "
    "font du corps une grammaire. L'Allemagne expressionniste, Flaherty, Murnau, l'URSS du montage et Dreyer "
    "prouvent que le silence n'est pas un manque. La Passion de Jeanne d'Arc colle aux visages, L'Aurore invente "
    "une caméra lyrique, Napoléon déborde l'écran. Revenir au muet, c'est réapprendre à voir avant d'écouter."
)
SPECS = [
    ("Free Cinema Britannique", "COLLECTION_018", 18, "CLUB", ["FREE_CINEMA"], ["UK"], "UK"),
    ("Âge d'or hongkongais", "COLLECTION_019", 19, "DARKROOM", ["HONG_KONG_NEW_WAVE"], ["HONG_KONG"], "HONG_KONG"),
    ("Cinéma américain post-Nouvel Hollywood", "COLLECTION_020", 20, "DARKROOM", [], ["USA"], "USA"),
    ("Cinéma Surréaliste et Onirique", "COLLECTION_021", 21, "DARKROOM", ["SURREALISME"], [], None),
    ("Post-néoréalisme italien", "COLLECTION_022", 22, "CINEMATHEQUE", [], ["ITALY"], "ITALY"),
    ("Nouvelle Vague tchécoslovaque", "COLLECTION_023", 23, "CINEMATHEQUE", ["NOUVELLE_VAGUE_TCHEQUE"], ["CZECH"], "CZECH"),
    ("Cinéma Chinois - Cinquième Génération", "COLLECTION_024", 24, "CINEMATHEQUE", ["CINQUIEME_GENERATION_CHINOISE"], ["CHINA"], "CHINA"),
    ("Cinéma Documentaire", "COLLECTION_025", 25, "CINEMATHEQUE", ["DOCUMENTAIRE"], [], None),
    ("Cinéma Expérimental et Formel", "COLLECTION_026", 26, "OFFSCREEN", ["CINEMA_EXPERIMENTAL"], [], None),
]


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def title_score(query: str, candidate: str) -> float:
    left, right = fold(query), fold(candidate)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    if len(shorter) >= 8 and shorter in longer:
        return 0.93
    import difflib
    return difflib.SequenceMatcher(None, left, right).ratio()


def tokens(text: str) -> set[str]:
    return {part for part in fold(text).split() if len(part) >= 4}


def descriptions(md: str, title: str) -> tuple[str, str]:
    marker = f"### {title}\n"
    start = md.index(marker) + len(marker)
    body = []
    for line in md[start:].splitlines():
        if line.startswith("### ") or line.startswith("## "):
            break
        if line.startswith("- "):
            break
        body.append(line)
    paragraphs = [part.strip() for part in "\n".join(body).split("\n\n") if part.strip()]
    if len(paragraphs) < 2:
        raise SystemExit(f"description manquante: {title}")
    return paragraphs[0], "\n\n".join(paragraphs[1:])


def parse_match(text: str) -> dict[str, list[dict]]:
    sections: dict[str, list[dict]] = {}
    current = None
    for raw in text.splitlines():
        if raw.startswith("## "):
            current = raw[3:].split(" (")[0]
            sections[current] = []
            continue
        if current is None or not raw:
            continue
        parts = raw.split("\t")
        kind = parts[0]
        if kind in {"OK", "MAYBE"}:
            sections[current].append({"title": parts[3], "code": parts[4]})
        elif kind == "MISS":
            sections[current].append({"title": parts[2], "code": ALIASES.get(parts[2])})
    return sections


def slug_name(display: str) -> str:
    folded = unicodedata.normalize("NFKD", display)
    ascii_name = "".join(ch for ch in folded if not unicodedata.combining(ch))
    code = re.sub(r"[^A-Za-z0-9]+", "_", ascii_name).strip("_").upper()
    return code or "DIRECTOR"


def person(display: str) -> dict:
    parts = [part for part in display.replace(".", " ").split() if part]
    first = " ".join(parts[:-1]) if len(parts) > 1 else ""
    last = parts[-1] if parts else display
    return {
        "code": slug_name(display),
        "firstName": first,
        "lastName": last,
        "displayName": display,
        "characteristicCodes": [],
    }


def main() -> None:
    pack = json.loads(catalog_path.read_text(encoding="utf-8"))
    md = md_path.read_text(encoding="utf-8")
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    sections = parse_match(match_path.read_text(encoding="utf-8"))
    csv_rows = {}
    with input_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter=";"):
            csv_rows[row["code"]] = row

    known_countries = {item["code"] for item in pack["countries"]}
    known_genres = {item["code"] for item in pack["genres"]}
    known_chars = {item["code"] for item in pack["characteristics"]}
    known_directors = {item["code"]: item for item in pack["directors"]}
    movies_by_code = {item["code"]: item for item in pack["movies"]}
    director_names = {code: item.get("displayName") or "" for code, item in known_directors.items()}

    force_by_code = {}
    chars_by_code: dict[str, set[str]] = {}
    for title, _code, _order, _track, chars, _countries, force in SPECS:
        for film in sections.get(title, []):
            if film["code"]:
                continue
            # filled after we know the batch code
            film["pending"] = True
        for film in sections.get(title, []):
            pass

    batch_by_title = {}
    for movie in batch["movies"]:
        row = csv_rows.get(movie["code"], {})
        batch_by_title[row.get("frenchTitle") or movie.get("frenchTitle")] = movie

    for title, _code, _order, _track, chars, _countries, force in SPECS:
        for film in sections[title]:
            if film["code"]:
                if chars:
                    chars_by_code.setdefault(film["code"], set()).update(chars)
                continue
            movie = batch_by_title.get(film["title"])
            if movie is None:
                film["missing"] = True
                continue
            film["batch"] = movie["code"]
            if force:
                force_by_code[movie["code"]] = force
            if chars:
                chars_by_code.setdefault(movie["code"], set()).update(chars)

    fresh_directors = []
    inserted = []
    linked_existing = []
    rejected = []

    def director_blob(movie: dict) -> str:
        names = []
        for ref in movie.get("directors") or []:
            code = ref["code"]
            if code in director_names:
                names.append(director_names[code])
            else:
                for item in batch.get("newDirectors") or []:
                    if item["code"] == code:
                        names.append(item.get("displayName") or "")
        return " ".join(names)

    def same_work(batch_movie: dict, row: dict) -> str | None:
        query_titles = [row.get("frenchTitle") or "", batch_movie.get("frenchTitle") or "", batch_movie.get("originalTitle") or ""]
        wanted = tokens(row.get("director") or "")
        year = int(row.get("releaseYear") or batch_movie.get("releaseYear") or 0)
        best = None
        for movie in pack["movies"]:
            delta = abs(int(movie.get("releaseYear") or 0) - year)
            if delta > 1 and delta > 15:
                continue
            score = max(
                title_score(query, movie.get("frenchTitle") or "")
                for query in query_titles
                if query
            )
            score = max(score, max(title_score(query, movie.get("originalTitle") or "") for query in query_titles if query))
            people = " ".join(director_names.get(ref["code"], "") for ref in movie.get("directors") or [])
            director_ok = bool(wanted and tokens(people) & wanted)
            if score >= 0.9 and (director_ok or delta <= 1):
                if best is None or score > best[0]:
                    best = (score, movie["code"])
            elif score >= 0.8 and director_ok and delta <= 2:
                if best is None or score > best[0]:
                    best = (score, movie["code"])
        return best[1] if best else None

    def covers(csv_name: str, blob: str) -> bool:
        parts = [part for part in fold(csv_name).split() if len(part) >= 3]
        blob_tokens = set(fold(blob).split())
        return bool(parts) and all(part in blob_tokens for part in parts)

    for movie in batch["movies"]:
        row = csv_rows.get(movie["code"], {})
        csv_title = row.get("frenchTitle") or ""
        score = max(
            title_score(csv_title, movie.get("frenchTitle") or ""),
            title_score(csv_title, movie.get("originalTitle") or ""),
        )
        blob = director_blob(movie)
        csv_people = [part.strip() for part in re.split(r"\s*(?:&|,)\s*", row.get("director") or "") if part.strip()]
        directors_ok = bool(csv_people) and all(covers(name, blob) for name in csv_people)
        if movie["code"] in {"EMPIRE_1964", "THE_SECRET_1979", "THE_CLUB_1981", "NOMAD_1982"} or score < 0.72:
            rejected.append(f"BAD_MATCH {movie['code']} {movie.get('originalTitle')} score={score:.2f}")
            continue
        existing = same_work(movie, row)
        if existing:
            linked_existing.append((movie["code"], existing, row.get("frenchTitle")))
            for films in sections.values():
                for film in films:
                    if film.get("batch") == movie["code"]:
                        film["code"] = existing
            continue
        csv_directors = [part.strip() for part in re.split(r"\s*(?:&|,)\s*", row.get("director") or "") if part.strip()]
        refs = []
        source_refs = movie.get("directors") or [] if directors_ok else []
        for index, ref in enumerate(source_refs):
            code = ref["code"]
            display = ""
            if code in known_directors:
                refs.append({"code": code, "billingOrder": index})
                continue
            created = next((item for item in batch.get("newDirectors") or [] if item["code"] == code), None)
            if created and created["code"] != "DIRECTOR" and slug_name(created.get("displayName") or "") == created["code"]:
                if created["code"] not in known_directors and all(item["code"] != created["code"] for item in fresh_directors):
                    fresh_directors.append(
                        {
                            "code": created["code"],
                            "firstName": created.get("firstName") or "",
                            "lastName": created.get("lastName") or "",
                            "displayName": created.get("displayName") or created["code"],
                            "characteristicCodes": [],
                        }
                    )
                refs.append({"code": created["code"], "billingOrder": len(refs)})
                continue
            display = csv_directors[index] if index < len(csv_directors) else (created or {}).get("displayName") or ""
            if not display:
                continue
            made = person(display)
            if made["code"] not in known_directors and all(item["code"] != made["code"] for item in fresh_directors):
                fresh_directors.append(made)
            refs.append({"code": made["code"], "billingOrder": len(refs)})
        if not directors_ok:
            refs = []
            for display in csv_directors:
                existing_director = next(
                    (item for item in pack["directors"] if fold(item.get("displayName") or "") == fold(display)),
                    None,
                )
                if existing_director is None:
                    existing_director = next((item for item in fresh_directors if fold(item["displayName"]) == fold(display)), None)
                if existing_director is None:
                    existing_director = person(display)
                    fresh_directors.append(existing_director)
                refs.append({"code": existing_director["code"], "billingOrder": len(refs)})
        if not refs:
            rejected.append(f"NO_DIRECTOR {movie['code']}")
            continue
        countries = []
        for item in movie.get("countries") or []:
            code = item["code"]
            if code == "SLOVAKIA":
                code = "CZECH"
            if code not in known_countries:
                continue
            if all(current["code"] != code for current in countries):
                countries.append({"code": code, "isPrimary": False})
        forced = force_by_code.get(movie["code"])
        if forced:
            countries = [item for item in countries if item["code"] != forced]
            countries.insert(0, {"code": forced, "isPrimary": True})
        countries = countries[:2]
        if not countries:
            rejected.append(f"NO_COUNTRY {movie['code']}")
            continue
        countries[0]["isPrimary"] = True
        for item in countries[1:]:
            item["isPrimary"] = False
        movie["countries"] = countries
        movie["directors"] = refs
        movie["genreCodes"] = [code for code in movie.get("genreCodes") or [] if code in known_genres] or ["DRAME"]
        extra = set(chars_by_code.get(movie["code"], set()))
        if int(movie.get("releaseYear") or 0) <= 1929:
            extra.add("CINEMA_MUET_MOUVEMENT")
        movie["characteristicCodes"] = [code for code in extra if code in known_chars]
        if movie["code"] in movies_by_code:
            rejected.append(f"CODE_TAKEN {movie['code']}")
            continue
        if movie["code"] == "FANTOMAS_1913":
            movie["frenchTitle"] = "Fantômas"
            movie["originalTitle"] = "Fantômas"
        pack["movies"].append(movie)
        movies_by_code[movie["code"]] = movie
        inserted.append(movie["code"])
        for films in sections.values():
            for film in films:
                if film.get("batch") == movie["code"]:
                    film["code"] = movie["code"]
        poster = next(poster_src.glob(movie["code"] + ".*"), None)
        if poster and poster.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            shutil.copyfile(poster, poster_dst / (movie["code"] + poster.suffix.lower().replace(".jpeg", ".jpg")))

    pack["directors"].extend(fresh_directors)

    def ordered(films: list[dict]) -> list[dict]:
        ranked = []
        for film in films:
            code = film.get("code")
            if not code or code not in movies_by_code:
                continue
            ranked.append((int(movies_by_code[code].get("releaseYear") or 0), code))
        ranked.sort()
        seen = set()
        result = []
        for year, code in ranked:
            if code in seen:
                continue
            seen.add(code)
            result.append({"code": code, "displayOrder": len(result) + 1, "year": year})
        return result

    muet = next(item for item in pack["collections"] if item["code"] == "COLLECTION_012")
    kept = []
    for ref in muet["movies"]:
        movie = movies_by_code[ref["code"]]
        if int(movie.get("releaseYear") or 0) <= 1906:
            continue
        kept.append(ref["code"])
    fantomas = sections["Cinéma muet"][0]
    if fantomas.get("code"):
        kept.append(fantomas["code"])
    if "LES_VAMPIRES_1915" not in kept:
        kept.append("LES_VAMPIRES_1915")
    muet_films = ordered([{"code": code} for code in kept])
    muet["movies"] = [{"code": item["code"], "displayOrder": item["displayOrder"]} for item in muet_films]
    muet["longDescription"] = MUET_LONG

    for title, code, order, track, chars, countries, _force in SPECS:
        films = ordered(sections[title])
        missing = [film["title"] for film in sections[title] if not film.get("code")]
        pack["collections"].append(
            {
                "code": code,
                "displayOrder": order,
                "name": title,
                "description": descriptions(md, title)[0],
                "longDescription": descriptions(md, title)[1],
                "isPublished": True,
                "movies": [{"code": item["code"], "displayOrder": item["displayOrder"]} for item in films],
                "characteristicCodes": chars,
                "countryCodes": countries,
                "track": track,
            }
        )
        print(f"COLLECTION {title} films={len(films)} missing={missing}")

    orders = [item["displayOrder"] for item in pack["collections"]]
    if len(orders) != len(set(orders)):
        raise SystemExit(f"displayOrder en double {orders}")
    pack["version"] = 24
    catalog_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failures = []
    if report_path.is_file():
        with report_path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                if row.get("status") in {"NOT_FOUND", "NO_POSTER", "ERROR"}:
                    failures.append(row)
    existing = leftover_path.read_text(encoding="utf-8") if leftover_path.is_file() else ""
    extra_lines = []
    for row in failures:
        if row["code"] in existing:
            continue
        def cell(value: str) -> str:
            return '"' + (value or "").replace('"', "'") + '"'
        extra_lines.append(
            ";".join([cell(row["title"]), row["year"], cell(row["director"]), row["code"], cell(row["title"])])
        )
    if extra_lines:
        if not existing.endswith("\n"):
            existing += "\n"
        leftover_path.write_text(existing + "\n".join(extra_lines) + "\n", encoding="utf-8")

    summary = root / "tools/output/_collections_merge.txt"
    lines = [
        f"inserted={len(inserted)} linked={len(linked_existing)} rejected={len(rejected)} movies={len(pack['movies'])} version={pack['version']}",
        "INSERTED " + ", ".join(inserted),
        "LINKED " + " | ".join(f"{src}->{dst}" for src, dst, _title in linked_existing),
        "REJECTED " + " | ".join(rejected),
    ]
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[0])


if __name__ == "__main__":
    main()
