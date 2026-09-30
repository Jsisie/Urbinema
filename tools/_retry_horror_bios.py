"""Second pass for horror directors that came back without a bio or a photo."""
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
PHOTOS = ROOT / "batchsData/batchReals/output/photos"
DEST = ROOT / "app/src/main/assets/media/directors"
TMDB_IMAGE = "https://image.tmdb.org/t/p/w342"
WANTED = [
    "JEAN_ROLLIN",
    "ALAN_ORMSBY",
    "JEFF_GILLEN",
    "LUKAS_FEIGELFELD",
    "MASATO_HARADA",
    "TAKASHI_SHIMIZU",
    "DANNY_PANG",
]


def ascii_name(value: str) -> str:
    return value.encode("ascii", "replace").decode("ascii")


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters/.env")
    client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_code = {item["code"]: item for item in pack["directors"]}
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for code in WANTED:
        director = by_code[code]
        display = director["displayName"]
        print("TRY", code, ascii_name(display))
        found = search_people(client, [display])
        chosen = None
        for item in found:
            details, _bio = biography_of(client, int(item["id"]))
            name = str(details.get("name") or "")
            print(
                "  hit",
                item["id"],
                ascii_name(name),
                "match",
                matches(display, details),
                "photo",
                bool(profile_path(details)),
                "bio",
                len(str(details.get("biography") or "")),
            )
            if matches(display, details) or fold(display) == fold(name):
                chosen = (details, int(item["id"]))
                break
        if chosen is None:
            print("  none")
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
        path = profile_path(details) or profile_path(french) or profile_path(english)
        if path:
            data, _kind = client.download(f"{TMDB_IMAGE}{path}")
            if data:
                (PHOTOS / f"{code}.jpg").write_bytes(data)
                shutil.copyfile(PHOTOS / f"{code}.jpg", DEST / f"{code}.jpg")
                print("  saved photo", len(data), "fr", len(fr), "en", len(en))
                continue
        print("  no photo", "fr", len(fr), "en", len(en))
    palfi = by_code.get("PALFI_GYORGY")
    if palfi is not None:
        print("PALFI", ascii_name(palfi.get("displayName") or ""))
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    tmp = COPY.with_suffix(".json.tmp")
    shutil.copyfile(CATALOG, tmp)
    tmp.replace(COPY)
    print("written")


if __name__ == "__main__":
    main()
