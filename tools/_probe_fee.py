"""Check whether La Fée aux choux 1900 is a different TMDB film."""
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.1)
lines = []
for year in (1896, 1900, 1902):
    hits = client.search_movie("La Fée aux choux", year, "fr-FR")
    lines.append(f"## {year} n={len(hits)}")
    for item in hits[:5]:
        lines.append(f"{item.get('id')}\t{item.get('release_date')}\t{item.get('title')}\t{item.get('original_title')}")
out = ROOT / "tools" / "output" / "_fee_choux.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ok")
