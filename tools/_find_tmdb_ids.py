"""Find TMDB ids for the five mismatched films. Writes UTF-8, prints counts."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

QUERIES = [
    "Martin",
    "The Witch",
    "The VVitch",
    "Innocence",
    "The Eye",
    "Gin gwai",
    "It Follows",
]
load_env(ROOT / "batchsData/batchPosters/.env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.1)
lines = []
for query in QUERIES:
    payload = client.request_json("/search/movie", {
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": "1",
    })
    lines.append(f"## {query}")
    for item in (payload.get("results") or [])[:8]:
        lines.append(f"{item.get('id')} | {item.get('release_date')} | {item.get('title')} | {item.get('original_title')}")
    lines.append("")
out = ROOT / "tools/output/_tmdb_ids.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("lines", len(lines))
