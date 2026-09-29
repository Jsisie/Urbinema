import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.1)
details = client.movie_details(42984, "fr-FR")
crew = (details.get("credits") or {}).get("crew") or []
lines = [f"jobs={sorted({str(person.get('job')) for person in crew})}"]
for person in crew:
    if "direct" in str(person.get("job") or "").lower() or "imamura" in str(person.get("name") or "").lower():
        lines.append(f"{person.get('job')}\t{person.get('name')}\t{person.get('id')}")
(ROOT / "tools/output/_insect_crew.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
