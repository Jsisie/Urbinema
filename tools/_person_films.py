"""Second passage : filmographie du réalisateur pour les titres encore absents."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "batchsData/batchPosters"))

import _fetch_remaining as fetch  # noqa: E402
from posters_batch import TmdbClient, load_env  # noqa: E402

MISSING = {
    "THE_SPOOKY_BUNCH_1980",
    "THE_SECRET_1979",
    "THE_CLUB_1981",
    "NOMAD_1982",
    "L_INCIDENT_DU_CANON_NOIR_1985",
    "EMPIRE_WARHOL_1964",
}


def person_id(client: TmdbClient, name: str) -> int | None:
    payload = client.request_json("/search/person", {"query": name, "language": "en-US", "page": "1"})
    for item in payload.get("results") or []:
        if fetch.covers(name, str(item.get("name") or "")):
            return int(item["id"])
    return None


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters" / ".env")
    api_key = (os.environ.get("TMDB_API_KEY") or "").strip()
    client = TmdbClient(api_key, os.environ.get("TMDB_ACCESS_TOKEN") or "", 0.15)
    lines: list[str] = []
    targets = [item for item in fetch.TARGETS if item[0] in MISSING]
    for code, year, director, french, queries, _collections, _forced, _chars in targets:
        pid = person_id(client, director)
        lines.append(f"PERSON {code} {director} id={pid}")
        if pid is None:
            continue
        credits = client.request_json(f"/person/{pid}/movie_credits", {"language": "en-US"})
        movies = list(credits.get("crew") or [])
        directed = [item for item in movies if item.get("job") == "Director"]
        close = []
        for item in directed:
            release = str(item.get("release_date") or "")
            item_year = int(release[:4]) if len(release) >= 4 and release[:4].isdigit() else 0
            title = str(item.get("title") or item.get("original_title") or "")
            if item_year and abs(item_year - year) <= 3:
                close.append(f"{item.get('id')}|{item_year}|{title}|{item.get('original_title')}")
        lines.extend(close or ["(aucun film proche)"])
    out = ROOT / "tools/output/_person_films.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"lines={len(lines)}")


if __name__ == "__main__":
    main()
