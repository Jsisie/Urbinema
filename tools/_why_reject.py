import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "batchsData/batchPosters"))
import _fetch_remaining as fetch
from posters_batch import TmdbClient, load_env

load_env(ROOT / "batchsData/batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY") or "", os.environ.get("TMDB_ACCESS_TOKEN") or "", 0.1)
lines = []
for code, movie_id in fetch.FOUND_IDS.items():
    if code == "EMPIRE_WARHOL_1964":
        continue
    target = next(item for item in fetch.TARGETS if item[0] == code)
    _code, year, director, *_rest = target
    details = client.movie_details(movie_id, "fr-FR")
    blob = fetch.director_blob(details)
    jobs = sorted({str(person.get("job") or "") for person in (details.get("credits") or {}).get("crew") or []})
    lines.append(
        f"{code} ok={fetch.acceptable(code, year, director, details)} blob={blob!r} covers={fetch.covers(director, blob)} jobs={jobs[:8]}"
    )
(ROOT / "tools/output/_why_reject.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ok")
