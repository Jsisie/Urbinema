"""Copy catalog_v2 → catalog_v3, drop near-duplicate movies, bump pack version."""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "src" / "main" / "assets" / "catalog"
SRC = ASSETS / "catalog_v2.json"
DST = ASSETS / "catalog_v3.json"
PACK_VERSION = 19
REPORT = ROOT / "tools" / "output" / "catalog_v3_dedupe_report.txt"

PART = re.compile(r"\b(pt|part|partie|vol|volume|episode|ep)\s*\.?\s*\d+\b", re.I)
ARTICLES = {
    "the", "le", "la", "les", "l", "un", "une", "a", "an", "el", "il", "lo",
    "los", "las", "der", "die", "das", "de", "du", "des", "d", "of", "and", "et",
}


def fold(text: str) -> str:
    raw = unicodedata.normalize("NFD", text or "")
    raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    raw = raw.lower()
    raw = PART.sub(" ", raw)
    raw = re.sub(r"[^\w\s]", " ", raw)
    return " ".join(raw.split())


def significant_tokens(folded: str) -> set[str]:
    return {word for word in folded.split() if word not in ARTICLES and len(word) > 1}


def titles_of(movie: dict) -> set[str]:
    out = set()
    for key in ("originalTitle", "frenchTitle"):
        value = movie.get(key)
        if value:
            folded = fold(value)
            if folded:
                out.add(folded)
    return out or {fold(movie.get("originalTitle") or movie["code"])}


def director_key(movie: dict) -> tuple[str, ...]:
    codes = sorted({row.get("code", "") for row in movie.get("directors") or []} - {""})
    return tuple(codes)


def richness(movie: dict, collection_hits: dict[str, int]) -> tuple:
    code = movie["code"]
    return (
        collection_hits.get(code, 0),
        1 if movie.get("posterMediaCode") else 0,
        len(movie.get("characteristicCodes") or []),
        len(movie.get("genreCodes") or []),
        len(movie.get("synopsis") or ""),
        -len(code),
    )


def token_close(left: str, right: str) -> bool:
    if left == right:
        return True
    if min(len(left), len(right)) >= 5 and (left.startswith(right) or right.startswith(left)):
        return True
    prefix = 0
    for ca, cb in zip(left, right):
        if ca != cb:
            break
        prefix += 1
    if prefix >= 6:
        return True
    return SequenceMatcher(None, left, right).ratio() >= 0.75


def titles_similar(left: set[str], right: set[str]) -> str | None:
    """Return 'strong' | 'weak' | None."""
    for a in left:
        for b in right:
            if a == b:
                return "strong"
            if min(len(a), len(b)) >= 8 and (a in b or b in a):
                return "strong"
            ta, tb = significant_tokens(a), significant_tokens(b)
            if ta and tb:
                if any(token_close(x, y) for x in ta for y in tb):
                    inter = {x for x in ta if any(token_close(x, y) for y in tb)}
                    union = ta | tb
                    if inter and len(inter) / len(union) >= 0.55:
                        return "weak" if inter != ta or inter != tb else "strong"
                    if len(ta) == 1 and len(tb) == 1 and token_close(next(iter(ta)), next(iter(tb))):
                        return "weak"
            if SequenceMatcher(None, a, b).ratio() >= 0.86:
                return "strong"
    return None


def code_year_stem(code: str) -> str:
    match = re.match(r"^(.+_\d{4})(?:_.+)?$", code)
    return match.group(1) if match else code


class UnionFind:
    def __init__(self, items: list[str]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: str) -> str:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def merge_codes(keeper: dict, loser: dict) -> None:
    for field in ("genreCodes", "characteristicCodes"):
        keeper[field] = list(dict.fromkeys((keeper.get(field) or []) + (loser.get(field) or [])))
    if not keeper.get("frenchTitle") and loser.get("frenchTitle"):
        keeper["frenchTitle"] = loser["frenchTitle"]
    if not keeper.get("synopsis") and loser.get("synopsis"):
        keeper["synopsis"] = loser["synopsis"]
    if not keeper.get("posterMediaCode") and loser.get("posterMediaCode"):
        keeper["posterMediaCode"] = loser["posterMediaCode"]


def main() -> None:
    shutil.copy2(SRC, DST)
    pack = json.loads(DST.read_text(encoding="utf-8"))
    movies: list[dict] = pack["movies"]
    collections: list[dict] = pack["collections"]
    by_code = {movie["code"]: movie for movie in movies}

    collection_hits: dict[str, int] = defaultdict(int)
    for collection in collections:
        for row in collection.get("movies") or []:
            collection_hits[row["code"]] += 1

    # Index by director, then compare nearby years + similar titles.
    by_director: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for movie in movies:
        dirs = director_key(movie)
        if dirs:
            by_director[dirs].append(movie)

    uf = UnionFind([movie["code"] for movie in movies])
    for group in by_director.values():
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if abs(int(left["releaseYear"]) - int(right["releaseYear"])) > 1:
                    continue
                kind = titles_similar(titles_of(left), titles_of(right))
                if not kind:
                    continue
                if kind == "weak":
                    dur_l = int(left.get("durationMinutes") or 0)
                    dur_r = int(right.get("durationMinutes") or 0)
                    if dur_l and dur_r and abs(dur_l - dur_r) > 20:
                        continue
                uf.union(left["code"], right["code"])

    by_stem: dict[str, list[dict]] = defaultdict(list)
    for movie in movies:
        by_stem[code_year_stem(movie["code"])].append(movie)
    for stem, group in by_stem.items():
        if len(group) < 2:
            continue
        for i, left in enumerate(group):
            for right in group[i + 1 :]:
                if director_key(left) and director_key(left) == director_key(right):
                    uf.union(left["code"], right["code"])
                elif abs(int(left["releaseYear"]) - int(right["releaseYear"])) <= 1:
                    uf.union(left["code"], right["code"])

    clusters: dict[str, list[dict]] = defaultdict(list)
    for movie in movies:
        clusters[uf.find(movie["code"])].append(movie)

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
        ranked = sorted(unique, key=lambda m: richness(m, collection_hits), reverse=True)
        keeper = ranked[0]
        for loser in ranked[1:]:
            drop[loser["code"]] = keeper["code"]
            merge_codes(keeper, loser)

    for collection in collections:
        rows = collection.get("movies") or []
        kept = []
        seen = set()
        for row in rows:
            code = drop.get(row["code"], row["code"])
            if code in seen:
                continue
            seen.add(code)
            kept.append({**row, "code": code})
        for index, row in enumerate(kept):
            row["displayOrder"] = index + 1
        collection["movies"] = kept

    kept_movies = [movie for movie in movies if movie["code"] not in drop]
    pack["movies"] = kept_movies
    pack["version"] = PACK_VERSION
    DST.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Same director + year still in the pack: leftover collisions to inspect.
    leftover: list[str] = []
    remaining_by_dir_year: dict[tuple, list[str]] = defaultdict(list)
    for movie in kept_movies:
        dirs = director_key(movie)
        if not dirs:
            continue
        remaining_by_dir_year[(dirs, movie["releaseYear"])].append(movie["code"])
    for key, codes in sorted(remaining_by_dir_year.items()):
        if len(codes) < 2:
            continue
        leftover.append(f"SAME_DIR_YEAR {key[1]} {','.join(key[0])}")
        for code in codes:
            movie = by_code[code]
            leftover.append(
                f"  {code} | {movie.get('frenchTitle') or ''} | {movie.get('originalTitle')}"
            )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"source={SRC.name} movies_before={len(movies)} after={len(kept_movies)} dropped={len(drop)} version={PACK_VERSION}",
        "",
    ]
    by_keeper: dict[str, list[str]] = defaultdict(list)
    for loser, keeper in sorted(drop.items()):
        by_keeper[keeper].append(loser)
    for keeper, losers in sorted(by_keeper.items()):
        lines.append(f"KEEP {keeper}")
        for loser in losers:
            lines.append(f"  DROP {loser}")
    lines.append("")
    lines.append(f"remaining_same_director_year_groups={len(leftover) and leftover.count('SAME_DIR_YEAR') or 0}")
    # count groups properly
    group_count = sum(1 for row in leftover if row.startswith("SAME_DIR_YEAR"))
    lines[-1] = f"remaining_same_director_year_groups={group_count}"
    lines.extend(leftover)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[0])
    print(f"remaining_same_director_year_groups={group_count}")
    print(f"report={REPORT}")


if __name__ == "__main__":
    main()
