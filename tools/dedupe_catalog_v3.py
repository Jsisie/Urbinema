"""Copy catalog_v2 → catalog_v3 and drop only clear duplicate movies.

catalog_v2.json is read-only. A film stays unless it is the same work as another:
same directors, no conflicting part number, release years within one year
(two years when the original titles match once spaces are removed), durations
within 20 minutes when both are known, and at least one title equal after
folding spaces and punctuation.

Dropped codes are listed in movieAliases so an already-installed database can
move "vu" / XP onto the film that remains.
"""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "src" / "main" / "assets" / "catalog"
SRC = ASSETS / "catalog_v2.json"
DST = ASSETS / "catalog_v3.json"
LIVE = ASSETS / "catalog.json"
PACK_VERSION = 20
REPORT = ROOT / "tools" / "output" / "catalog_v3_dedupe_report.txt"

ARTICLES = {
    "the", "le", "la", "les", "l", "un", "une", "a", "an", "el", "il", "lo",
    "los", "las", "der", "die", "das", "de", "du", "des", "d", "of", "and", "et",
}
PART_BEFORE_YEAR = re.compile(r"_(\d+)_(\d{4})(?:_|$)")


def fold(text: str) -> str:
    raw = unicodedata.normalize("NFD", text or "")
    raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    raw = raw.lower()
    raw = re.sub(r"[^\w\s]", " ", raw)
    return " ".join(raw.split())


def compact(text: str) -> str:
    folded = fold(text)
    tokens = [word for word in folded.split() if word not in ARTICLES]
    return "".join(tokens or folded.split())


def titles_of(movie: dict) -> set[str]:
    out = set()
    for key in ("originalTitle", "frenchTitle"):
        value = movie.get(key)
        if value:
            folded = compact(value)
            if folded:
                out.add(folded)
    return out


def director_key(movie: dict) -> tuple[str, ...]:
    codes = sorted({row.get("code", "") for row in movie.get("directors") or []} - {""})
    return tuple(codes)


def part_index(code: str) -> str | None:
    match = PART_BEFORE_YEAR.search(code)
    return match.group(1) if match else None


def richness(movie: dict, collection_hits: dict[str, int]) -> tuple:
    code = movie["code"]
    return (
        collection_hits.get(code, 0),
        1 if movie.get("posterMediaCode") else 0,
        len(movie.get("characteristicCodes") or []),
        len(movie.get("genreCodes") or []),
        len(movie.get("synopsis") or ""),
        1 if movie.get("countries") else 0,
        -len(code),
    )


def same_work(left: dict, right: dict) -> bool:
    dirs_l, dirs_r = director_key(left), director_key(right)
    if not dirs_l or dirs_l != dirs_r:
        return False
    if part_index(left["code"]) != part_index(right["code"]):
        return False
    year_gap = abs(int(left["releaseYear"]) - int(right["releaseYear"]))
    left_titles, right_titles = titles_of(left), titles_of(right)
    if not left_titles or not right_titles or not (left_titles & right_titles):
        return False
    originals_match = compact(left.get("originalTitle") or "") == compact(right.get("originalTitle") or "")
    if year_gap > (2 if originals_match and compact(left.get("originalTitle") or "") else 1):
        return False
    dur_l = int(left.get("durationMinutes") or 0)
    dur_r = int(right.get("durationMinutes") or 0)
    duration_far = bool(dur_l and dur_r and abs(dur_l - dur_r) > 20)
    orig_l = compact(left.get("originalTitle") or "")
    orig_r = compact(right.get("originalTitle") or "")
    fr_l = compact(left.get("frenchTitle") or "")
    fr_r = compact(right.get("frenchTitle") or "")
    same_titles = bool(orig_l and orig_l == orig_r and fr_l and fr_l == fr_r)
    if duration_far and not same_titles:
        return False
    return True


def merge_codes(keeper: dict, loser: dict) -> None:
    for field in ("genreCodes", "characteristicCodes"):
        keeper[field] = list(dict.fromkeys((keeper.get(field) or []) + (loser.get(field) or [])))
    if not keeper.get("frenchTitle") and loser.get("frenchTitle"):
        keeper["frenchTitle"] = loser["frenchTitle"]
    if len(loser.get("synopsis") or "") > len(keeper.get("synopsis") or ""):
        keeper["synopsis"] = loser["synopsis"]
    if not keeper.get("posterMediaCode") and loser.get("posterMediaCode"):
        keeper["posterMediaCode"] = loser["posterMediaCode"]
    if not keeper.get("countries") and loser.get("countries"):
        keeper["countries"] = loser["countries"]
    if not keeper.get("directors") and loser.get("directors"):
        keeper["directors"] = loser["directors"]
    if not keeper.get("durationMinutes") and loser.get("durationMinutes"):
        keeper["durationMinutes"] = loser["durationMinutes"]


def rewrite_refs(node, drop: dict[str, str]) -> None:
    if isinstance(node, dict):
        code = node.get("code")
        if isinstance(code, str) and code in drop:
            node["code"] = drop[code]
        for key, value in node.items():
            if key != "code":
                rewrite_refs(value, drop)
    elif isinstance(node, list):
        for value in node:
            rewrite_refs(value, drop)


def primary_country(movie: dict) -> bool:
    return any(row.get("isPrimary") and row.get("code") for row in movie.get("countries") or [])


def main() -> None:
    pack = json.loads(SRC.read_text(encoding="utf-8"))
    movies: list[dict] = pack["movies"]
    before = len(movies)
    by_code = {movie["code"]: movie for movie in movies}

    collection_hits: dict[str, int] = defaultdict(int)
    for collection in pack.get("collections") or []:
        for row in collection.get("movies") or []:
            collection_hits[row["code"]] += 1

    parent = {movie["code"]: movie["code"] for movie in movies}

    def find(code: str) -> str:
        while parent[code] != code:
            parent[code] = parent[parent[code]]
            code = parent[code]
        return code

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    by_director: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for movie in movies:
        dirs = director_key(movie)
        if dirs:
            by_director[dirs].append(movie)

    for group in by_director.values():
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if same_work(left, right):
                    union(left["code"], right["code"])

    clusters: dict[str, list[dict]] = defaultdict(list)
    for movie in movies:
        clusters[find(movie["code"])].append(movie)

    drop: dict[str, str] = {}
    for members in clusters.values():
        unique = []
        seen = set()
        for movie in members:
            if movie["code"] in seen:
                continue
            seen.add(movie["code"])
            unique.append(movie)
        if len(unique) < 2:
            continue
        ranked = sorted(unique, key=lambda movie: richness(movie, collection_hits), reverse=True)
        keeper = ranked[0]
        for loser in ranked[1:]:
            drop[loser["code"]] = keeper["code"]
            merge_codes(keeper, loser)

    for key, value in pack.items():
        if key == "movies":
            continue
        rewrite_refs(value, drop)

    for collection in pack.get("collections") or []:
        rows = collection.get("movies") or []
        kept_rows = []
        seen_codes = set()
        for row in rows:
            code = row["code"]
            if code in seen_codes:
                continue
            seen_codes.add(code)
            kept_rows.append(row)
        for index, row in enumerate(kept_rows):
            row["displayOrder"] = index + 1
        collection["movies"] = kept_rows

    kept_movies = [movie for movie in movies if movie["code"] not in drop]
    pack["movies"] = kept_movies
    pack["movieAliases"] = [
        {"from": loser, "to": keeper} for loser, keeper in sorted(drop.items())
    ]
    pack["version"] = PACK_VERSION

    missing_country = [movie["code"] for movie in kept_movies if not primary_country(movie)]
    known = {movie["code"] for movie in kept_movies}
    dangling = []
    for collection in pack.get("collections") or []:
        for row in collection.get("movies") or []:
            if row["code"] not in known:
                dangling.append(f"{collection.get('code')} -> {row['code']}")
    v2_codes = set(by_code)
    v3_codes = set(known)
    disappeared = sorted(v2_codes - v3_codes - set(drop))
    if missing_country or dangling or disappeared or set(drop) - (v2_codes - v3_codes):
        raise SystemExit(
            "Refusing to write catalog_v3: "
            f"missing_country={missing_country[:8]} dangling={dangling[:8]} "
            f"disappeared={disappeared[:8]}"
        )

    payload = json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
    DST.write_text(payload, encoding="utf-8")
    shutil.copyfile(DST, LIVE)

    lines = [
        f"source=catalog_v2.json movies_before={before} after={len(kept_movies)} "
        f"dropped={len(drop)} version={PACK_VERSION}",
        "rule=same directors + same compact title + year gap <= 1 "
        "(<= 2 if original titles match) + duration gap <= 20 + same part index",
        "",
    ]
    for loser, keeper in sorted(drop.items(), key=lambda item: item[1]):
        kept = by_code[keeper]
        gone = by_code[loser]
        lines.append(f"KEEP {keeper} | {kept.get('frenchTitle')} | {kept.get('originalTitle')}")
        lines.append(f"  DROP {loser} | {gone.get('frenchTitle')} | {gone.get('originalTitle')}")
    lines.append("")
    lines.append(f"aliases={len(drop)} every_v2_code_kept_or_aliased=yes primary_country=yes dangling_refs=0")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"dropped={len(drop)} after={len(kept_movies)} version={PACK_VERSION}")


if __name__ == "__main__":
    main()
