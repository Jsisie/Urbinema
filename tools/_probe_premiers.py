"""Probe TMDB for the missing early films. Writes UTF-8, prints only ASCII statuses."""
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(
    os.environ.get("TMDB_API_KEY", ""),
    os.environ.get("TMDB_ACCESS_TOKEN", ""),
    0.15,
)

QUERIES = [
    ("Pauvre Pierrot", 1892),
    ("Pauvre Pierrot", 1892),
    ("Dickson Experimental Sound Film", 1894),
    ("Annie Oakley", 1894),
    ("L'Arroseur arrosé", 1895),
    ("The Sprinkler Sprinkled", 1895),
    ("Le Manoir du diable", 1896),
    ("The House of the Devil", 1896),
    ("Panorama du Grand Canal pris d'un bateau", 1896),
    ("Panorama of the Grand Canal", 1896),
    ("Escamotage d'une dame au théâtre Robert-Houdin", 1896),
    ("The Vanishing Lady", 1896),
    ("Un homme de têtes", 1898),
    ("The Four Troublesome Heads", 1898),
    ("Grandma's Reading Glass", 1900),
    ("The Big Swallow", 1901),
    ("Alice Guy tourne une phonoscène", 1905),
    ("Alice Guy tourne une phonoscène", 1907),
]

lines = []
for query, year in QUERIES:
    hits = client.search_movie(query, year, "fr-FR")
    if not hits:
        hits = client.search_movie(query, year, "en-US")
    lines.append(f"## {year} | {query} | n={len(hits)}")
    for item in hits[:6]:
        title = item.get("title") or ""
        original = item.get("original_title") or ""
        date = item.get("release_date") or ""
        lines.append(f"{item.get('id')}\t{date}\t{title}\t{original}")

out = ROOT / "tools" / "output" / "_premiers_tmdb.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {len(lines)} lines")
