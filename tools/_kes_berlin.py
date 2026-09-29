"""Confirm Berlin Alexanderplatz and find the real Kes."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
lines = []
berlin = client.request_json("/tv/43189", {"language": "fr-FR"})
lines.append(f"berlin_name={berlin.get('name')} year={str(berlin.get('first_air_date') or '')[:4]}")
lines.append(str(berlin.get("overview") or "")[:500])
payload = client.request_json("/search/movie", {"query": "Kes", "language": "en-US"})
for hit in (payload.get("results") or [])[:12]:
    lines.append(
        f"kes\t{hit.get('id')}\t{str(hit.get('release_date') or '')[:4]}\t"
        f"{hit.get('title')}\t{hit.get('original_title')}\t{len(str(hit.get('overview') or ''))}"
    )
(ROOT / "tools/output/_kes_berlin.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
