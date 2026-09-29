"""Confirm the Brighton filmmakers before saving a portrait."""
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.1)
ids = [1037369, 3566497, 1037661, 935707, 110347, 110348, 1161489]
lines = []
for person_id in ids:
    details = client.request_json(f"/person/{person_id}", {"language": "fr-FR"})
    bio = str(details.get("biography") or "").replace("\n", " ")
    lines.append(
        f"{person_id}\t{details.get('name')}\t{details.get('birthday')}\t{details.get('known_for_department')}\t{bio[:220]}"
    )
out = ROOT / "tools" / "output" / "_premiers_bios_probe.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ok")
