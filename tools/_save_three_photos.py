import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
DEST = ROOT / "app/src/main/assets/media/directors"
PHOTOS = ROOT / "batchsData/batchReals/output/photos"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w342"
IDS = {
    "MASATO_HARADA": 52909,
    "TAKASHI_SHIMIZU": 20310,
    "DANNY_PANG": 21905,
}

load_env(ROOT / "batchsData/batchPosters/.env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.05)
pack = json.loads(CATALOG.read_text(encoding="utf-8"))
by = {item["code"]: item for item in pack["directors"]}
PHOTOS.mkdir(parents=True, exist_ok=True)
for code, person_id in IDS.items():
    details = client.request_json(f"/person/{person_id}", {"language": "en-US"})
    path = details.get("profile_path")
    data, _kind = client.download(f"{TMDB_IMAGE}{path}")
    (PHOTOS / f"{code}.jpg").write_bytes(data)
    shutil.copyfile(PHOTOS / f"{code}.jpg", DEST / f"{code}.jpg")
    print(code, len(data))
palfi = by["PALFI_GYORGY"]
palfi["displayName"] = "György Pálfi"
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
tmp = COPY.with_suffix(".json.tmp")
shutil.copyfile(CATALOG, tmp)
tmp.replace(COPY)
print("palfi")
