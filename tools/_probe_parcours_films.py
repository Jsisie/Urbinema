"""Probe TMDB hits for the four parcours films."""
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.1)
queries = [
    ("La Coquille et le Clergyman", 1928),
    ("The Seashell and the Clergyman", 1928),
    ("Contes cruels de la jeunesse", 1960),
    ("Cruel Story of Youth", 1960),
    ("La Pendaison", 1968),
    ("Death by Hanging", 1968),
    ("La Femme insecte", 1963),
    ("The Insect Woman", 1963),
    ("Nippon konchuki", 1963),
]
lines = []
for query, year in queries:
    hits = client.search_movie(query, year, "en-US")[:4]
    lines.append(f"Q {query} {year} n={len(hits)}")
    for hit in hits:
        lines.append(
            f"  {hit.get('id')}\t{str(hit.get('release_date') or '')[:4]}\t{hit.get('title')}\t{hit.get('original_title')}"
        )
(ROOT / "tools/output/_parcours_probe.txt").write_text("\n".join(lines), encoding="utf-8")
print("probed")
