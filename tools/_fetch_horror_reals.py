"""Photos and FR/EN bios for the directors added with the horror batch."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "batchsData" / "batchReals"))
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, fold, load_env  # noqa: E402
from reals_batch import biography_of, matches, profile_path, search_people  # noqa: E402
from _strip_wiki import strip_wiki  # noqa: E402

CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
ROWS = ROOT / "tools/output/_horror_new_directors.txt"
PHOTOS = ROOT / "batchsData/batchReals/output/photos"
DEST = ROOT / "app/src/main/assets/media/directors"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w342"


def choose(client, display: str, last: str):
    found = search_people(client, [display, f"{last}".strip()])
    chosen = None
    best = (-1, -1.0)
    for item in found:
        details, _bio = biography_of(client, int(item["id"]))
        if not matches(display, details):
            if fold(last) not in fold(str(details.get("name") or "")):
                continue
        has_photo = 1 if profile_path(details) else 0
        score = (1 if matches(display, details) else 0, has_photo, float(item.get("popularity") or 0))
        if score > best:
            best = score
            chosen = (details, int(item["id"]))
    return chosen


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters/.env")
    client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_code = {item["code"]: item for item in pack["directors"]}
    PHOTOS.mkdir(parents=True, exist_ok=True)
    ok = missing = 0
    for raw in ROWS.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        code, _first, last, display = raw.split(";")
        chosen = choose(client, display, last)
        director = by_code.get(code)
        if director is None or chosen is None:
            missing += 1
            continue
        details, person_id = chosen
        french = client.request_json(f"/person/{person_id}", {"language": "fr-FR"})
        english = client.request_json(f"/person/{person_id}", {"language": "en-US"})
        fr = strip_wiki(str(french.get("biography") or ""))
        en = strip_wiki(str(english.get("biography") or ""))
        if fr:
            director["biography"] = fr
        if en:
            director["biographyEn"] = en
        path = profile_path(details) or profile_path(french)
        if path:
            data, _kind = client.download(f"{TMDB_IMAGE}{path}")
            if data:
                (PHOTOS / f"{code}.jpg").write_bytes(data)
                shutil.copyfile(PHOTOS / f"{code}.jpg", DEST / f"{code}.jpg")
        ok += 1
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY)
    print("ok", ok, "missing", missing)


if __name__ == "__main__":
    main()
