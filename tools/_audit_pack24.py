"""Audit pack 24 : doublons, collections, pays, réalisateurs, fichiers jumeaux."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
JSON = ROOT / "app/src/main/assets/catalog/catalog.json"
POSTERS = ROOT / "app/src/main/assets/media/posters"
OUT = ROOT / "tools/output/_audit_pack24.txt"


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def main() -> None:
    raw_v3 = V3.read_bytes()
    raw_json = JSON.read_bytes()
    pack = json.loads(raw_v3)
    lines: list[str] = []
    lines.append(f"files_equal={raw_v3 == raw_json} v3={len(raw_v3)} json={len(raw_json)}")
    lines.append(
        f"version={pack['version']} movies={len(pack['movies'])} directors={len(pack['directors'])} collections={len(pack['collections'])}"
    )
    movies = pack["movies"]
    by_code = {item["code"]: item for item in movies}
    directors = {item["code"]: item for item in pack["directors"]}
    countries = {item["code"] for item in pack["countries"]}
    chars = {item["code"] for item in pack["characteristics"]}
    genres = {item["code"] for item in pack["genres"]}
    if len(by_code) != len(movies):
        lines.append(f"DUP_CODES {len(movies) - len(by_code)}")

    problems = []
    used = set()
    for movie in movies:
        country_list = movie.get("countries") or []
        primaries = [item for item in country_list if item.get("isPrimary")]
        if len(primaries) != 1 or not (1 <= len(country_list) <= 2):
            problems.append(f"COUNTRY {movie['code']}")
        for item in country_list:
            used.add(item["code"])
            if item["code"] not in countries:
                problems.append(f"UNKNOWN_COUNTRY {movie['code']} {item['code']}")
        refs = movie.get("directors") or []
        if not refs:
            problems.append(f"NO_DIRECTOR {movie['code']}")
        for ref in refs:
            if ref["code"] not in directors:
                problems.append(f"MISSING_DIRECTOR {movie['code']} {ref['code']}")
            elif ref["code"] == "DIRECTOR":
                problems.append(f"BLANK_DIRECTOR {movie['code']}")
        for code in movie.get("genreCodes") or []:
            if code not in genres:
                problems.append(f"BAD_GENRE {movie['code']} {code}")
        for code in movie.get("characteristicCodes") or []:
            if code not in chars:
                problems.append(f"BAD_CHAR {movie['code']} {code}")

    if used != countries:
        problems.append(f"COUNTRY_SET extra={sorted(countries - used)} missing={sorted(used - countries)}")

    membership: dict[str, list[str]] = defaultdict(list)
    for collection in pack["collections"]:
        seen = []
        years = []
        for ref in collection["movies"]:
            code = ref["code"]
            if code not in by_code:
                problems.append(f"MISSING_FILM {collection['code']} {code}")
                continue
            if code in seen:
                problems.append(f"TWICE_IN_COLLECTION {collection['code']} {code}")
            seen.append(code)
            years.append(int(by_code[code]["releaseYear"]))
            membership[code].append(collection["name"])
        if years != sorted(years):
            problems.append(f"YEAR_ORDER {collection['code']} {collection['name']}")
        orders = [ref["displayOrder"] for ref in collection["movies"]]
        if len(orders) != len(set(orders)):
            problems.append(f"DUP_ORDER {collection['code']}")
    orders = [item["displayOrder"] for item in pack["collections"]]
    if len(orders) != len(set(orders)):
        problems.append("DUP_COLLECTION_ORDER")

    shared = {code: names for code, names in membership.items() if len(names) > 1}
    lines.append(f"films_in_several_collections={len(shared)}")
    new_codes = {
        "COLLECTION_018", "COLLECTION_019", "COLLECTION_020", "COLLECTION_021", "COLLECTION_022",
        "COLLECTION_023", "COLLECTION_024", "COLLECTION_025", "COLLECTION_026",
    }
    new_names = {item["name"] for item in pack["collections"] if item["code"] in new_codes}
    new_shared = []
    for code, names in sorted(shared.items()):
        if any(name in new_names for name in names):
            movie = by_code[code]
            new_shared.append(f"{movie['frenchTitle']} ({movie['releaseYear']}) :: {' | '.join(names)}")
    lines.append("NEW_COLLECTION_OVERLAPS")
    lines.extend(new_shared or ["none"])

    # Near-duplicate works: compact title equal, year gap <= 1, director last-name overlap.
    buckets: dict[str, list[dict]] = defaultdict(list)
    for movie in movies:
        buckets[fold(movie.get("frenchTitle") or "")].append(movie)
        original = fold(movie.get("originalTitle") or "")
        if original and original != fold(movie.get("frenchTitle") or ""):
            buckets[original].append(movie)
    dup_pairs = []
    seen_pairs = set()
    for group in buckets.values():
        if len(group) < 2:
            continue
        unique = {item["code"]: item for item in group}
        items = list(unique.values())
        for left_index, left in enumerate(items):
            for right in items[left_index + 1 :]:
                pair = tuple(sorted((left["code"], right["code"])))
                if pair in seen_pairs:
                    continue
                if abs(int(left["releaseYear"]) - int(right["releaseYear"])) > 1:
                    continue
                left_names = {fold(directors[ref["code"]].get("displayName") or "") for ref in left["directors"] if ref["code"] in directors}
                right_names = {fold(directors[ref["code"]].get("displayName") or "") for ref in right["directors"] if ref["code"] in directors}
                left_last = {name.split()[-1] for name in left_names if name}
                right_last = {name.split()[-1] for name in right_names if name}
                if left_last & right_last or left_names & right_names:
                    seen_pairs.add(pair)
                    dup_pairs.append(
                        f"{left['code']} {left['frenchTitle']} {left['releaseYear']} <> {right['code']} {right['frenchTitle']} {right['releaseYear']}"
                    )
    lines.append(f"NEAR_DUPLICATES {len(dup_pairs)}")
    lines.extend(dup_pairs[:80])

    blank = [movie["code"] for movie in movies if any(ref["code"] == "DIRECTOR" for ref in movie.get("directors") or [])]
    lines.append(f"BLANK_DIRECTOR_COUNT {len(blank)}")

    new_movie_codes = []
    # posters missing only matters for films we added; report any movie whose code has no poster file among the newest 80 by file... skip, check all missing posters count
    missing_posters = [movie["code"] for movie in movies if not (POSTERS / f"{movie['code']}.jpg").exists() and not (POSTERS / f"{movie['code']}.png").exists() and not (POSTERS / f"{movie['code']}.webp").exists()]
    lines.append(f"MOVIES_WITHOUT_POSTER_FILE {len(missing_posters)}")

    lines.append("PROBLEMS " + ("none" if not problems else str(len(problems))))
    lines.extend(problems[:60])
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[0])
    print(lines[1])
    print(f"problems={len(problems)} shared={len(shared)} near={len(dup_pairs)} blank_director={len(blank)} no_poster={len(missing_posters)}")


if __name__ == "__main__":
    main()
