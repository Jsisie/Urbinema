"""Cherche les bonnes personnes TMDB pour Kirk Wong et Patrick Tam."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402


def main() -> None:
    load_env(ROOT / "batchPosters" / ".env")
    client = TmdbClient(os.environ.get("TMDB_API_KEY") or "", os.environ.get("TMDB_ACCESS_TOKEN") or "", 0.1)
    lines = []
    for query in ("Kirk Wong", "Wong Chi-keung", "Patrick Tam", "Patrick Tam Kar-ming", "Tam Kar Ming"):
        payload = client.request_json("/search/person", {"query": query, "language": "en-US"})
        lines.append(f"QUERY {query}")
        for item in (payload.get("results") or [])[:6]:
            lines.append(f"  {item.get('id')}|{item.get('name')}|{item.get('known_for_department')}")
            credits = client.request_json(f"/person/{item['id']}/movie_credits", {"language": "en-US"})
            directed = [movie for movie in credits.get("crew") or [] if movie.get("job") == "Director"]
            for movie in directed[:12]:
                lines.append(
                    f"    {movie.get('id')}|{str(movie.get('release_date') or '')[:4]}|{movie.get('title')}|{movie.get('original_title')}"
                )
    (ROOT / "tools/output/_person_probe.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"lines={len(lines)}")


if __name__ == "__main__":
    main()
