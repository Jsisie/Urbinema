import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData/batchPosters/.env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.05)
for person_id in (52909, 20310, 21905, 4101729, 5537972):
    details = client.request_json(f"/person/{person_id}", {"language": "en-US"})
    names = [str(details.get("name") or "")]
    names.extend(item for item in (details.get("also_known_as") or []) if isinstance(item, str))
    safe = " | ".join(name.encode("ascii", "replace").decode("ascii") for name in names[:8])
    print(person_id, "photo", bool(details.get("profile_path")), safe)
