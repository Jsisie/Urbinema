"""Match Liste_Collections films against catalog_v3. Report only."""
import json
import re
import unicodedata
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
md = (root / "specs/Listes_Fonctionnelles/Liste_Collections&Films.md").read_text(encoding="utf-8")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))

WANTED = {
    "Free Cinema Britannique",
    "Cinéma muet",
    "Âge d'or hongkongais",
    "Cinéma américain post-Nouvel Hollywood",
    "Cinéma Surréaliste et Onirique",
    "Post-néoréalisme italien",
    "Nouvelle Vague tchécoslovaque",
    "Cinéma Chinois - Cinquième Génération",
    "Cinéma Documentaire",
    "Cinéma Expérimental et Formel",
}


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def parse_sections(text: str) -> dict[str, list[dict]]:
    sections: dict[str, list[dict]] = {}
    current = None
    for raw in text.splitlines():
        if raw.startswith("### "):
            title = raw[4:].strip()
            current = title if title in WANTED else None
            if current:
                sections[current] = []
            continue
        if current is None or not raw.startswith("- "):
            continue
        line = raw[2:].replace("**", "")
        line = re.sub(r"\bbb\s+", "", line)
        line = re.sub(r"^s\s+", "", line)
        parts = [part.strip(" -") for part in re.split(r"\s+[—–-]\s+", line) if part.strip(" -")]
        year_hits = []
        for index, part in enumerate(parts):
            match = re.fullmatch(r"(\d{4})(?:\s*[–-]\s*(\d{4}))?", part)
            if match:
                year_hits.append((index, int(match.group(2) or match.group(1))))
        if not year_hits or not parts:
            sections[current].append({"raw": raw, "title": line, "year": 0, "director": ""})
            continue
        year_index, year = year_hits[-1]
        title = parts[0]
        director = " & ".join(part for index, part in enumerate(parts) if index not in {0, year_index})
        sections[current].append({"raw": raw, "title": title, "year": year, "director": director})
    return sections


def score(query: str, candidate: str) -> float:
    left, right = fold(query), fold(candidate)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    if len(shorter) >= 8 and shorter in longer:
        return 0.93
    # cheap ratio
    import difflib
    return difflib.SequenceMatcher(None, left, right).ratio()


names = {item["code"]: item.get("displayName") or "" for item in pack["directors"]}
movies = []
for movie in pack["movies"]:
    people = [names.get(ref["code"], "") for ref in movie.get("directors") or []]
    lasts = set()
    for person in people:
        tokens = [part for part in fold(person).split() if len(part) > 2]
        if tokens:
            lasts.add(tokens[-1])
    movies.append(
        {
            "code": movie["code"],
            "year": int(movie.get("releaseYear") or 0),
            "french": movie.get("frenchTitle") or "",
            "original": movie.get("originalTitle") or "",
            "lasts": lasts,
            "people": " & ".join(people),
        }
    )

sections = parse_sections(md)
lines = []
for name, films in sections.items():
    lines.append(f"\n## {name} ({len(films)})")
    for film in films:
        best = None
        for movie in movies:
            if abs(movie["year"] - film["year"]) > 1:
                continue
            value = max(score(film["title"], movie["french"]), score(film["title"], movie["original"]))
            if best is None or value > best[0]:
                best = (value, movie)
        if best and best[0] >= 0.86:
            movie = best[1]
            flag = "OK" if best[0] >= 0.97 else "MAYBE"
            lines.append(
                f"{flag}\t{best[0]:.2f}\t{film['year']}\t{film['title']}\t{movie['code']}\t{movie['year']}\t{movie['french']}"
            )
        else:
            stop = {"john", "jean", "paul", "marc", "mark", "anne", "anna", "pierre", "david", "peter"}
            wanted = set()
            for person in re.split(r"\s*(?:&|,| et )\s*", film["director"]):
                for part in fold(person).split():
                    if len(part) >= 5 or (len(part) >= 4 and part not in stop):
                        wanted.add(part)
            hits = [
                movie
                for movie in movies
                if wanted
                and any(token in fold(movie["people"]).split() for token in wanted)
                and abs(movie["year"] - film["year"]) <= 1
            ]
            hit_text = " | ".join(
                f"{movie['code']} {movie['year']} {movie['french']}" for movie in hits[:4]
            )
            lines.append(f"MISS\t{film['year']}\t{film['title']}\t{film['director']}\t{hit_text}")

out = root / "tools/output/_coll_match.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("sections", len(sections), "lines", len(lines))
