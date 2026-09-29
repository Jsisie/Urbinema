"""Probe TMDB people for the new early-cinema directors."""
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.12)
queries = [
    "Émile Reynaud",
    "William K.L. Dickson",
    "William Kennedy Laurie Dickson",
    "William Heise",
    "Alexandre Promio",
    "James Williamson",
    "George Albert Smith",
]
lines = []
for query in queries:
    payload = client.request_json(
        "/search/person",
        {"query": query, "language": "en-US", "include_adult": "false", "page": "1"},
    )
    hits = payload.get("results") or []
    lines.append(f"## {query} n={len(hits)}")
    for item in hits[:5]:
        lines.append(
            f"{item.get('id')}\tpop={item.get('popularity')}\tphoto={bool(item.get('profile_path'))}\t{item.get('known_for_department')}\t{item.get('name')}"
        )
out = ROOT / "tools" / "output" / "_premiers_people.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ok")
