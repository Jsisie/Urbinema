"""Download portraits for the six new early-cinema directors, by known TMDB ids."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)

PEOPLE = {
    "EMILE_REYNAUD": 935707,
    "WILLIAM_K_L_DICKSON": 110347,
    "WILLIAM_HEISE": 110348,
    "ALEXANDRE_PROMIO": 1161489,
    "JAMES_WILLIAMSON": 1037369,
    "GEORGE_ALBERT_SMITH": 1037661,
}

photos = ROOT / "batchsData" / "batchReals" / "output" / "photos"
bios_path = ROOT / "batchsData" / "batchReals" / "output" / "bios.json"
bios = json.loads(bios_path.read_text(encoding="utf-8")) if bios_path.is_file() else {}
lines = []
for code, person_id in PEOPLE.items():
    french = client.request_json(f"/person/{person_id}", {"language": "fr-FR", "append_to_response": "images"})
    text = str(french.get("biography") or "").strip()
    if not text:
        english = client.request_json(f"/person/{person_id}", {"language": "en-US", "append_to_response": "images"})
        text = str(english.get("biography") or "").strip()
        details = english
    else:
        details = french
    if text:
        bios[code] = text
    path = details.get("profile_path")
    if not path:
        profiles = list((details.get("images") or {}).get("profiles") or [])
        profiles.sort(key=lambda item: -int(item.get("width") or 0))
        if profiles:
            path = profiles[0].get("file_path")
    photo = photos / f"{code}.jpg"
    if path:
        data, _kind = client.download(f"https://image.tmdb.org/t/p/w342{path}")
        if data:
            photo.write_bytes(data)
    lines.append(f"{code}\t{person_id}\t{details.get('name')}\tbio={len(text)}\tphoto={photo.is_file()}")

bios_path.write_text(json.dumps(bios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "tools" / "output" / "_premiers_people_saved.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("saved")
