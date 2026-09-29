"""Copie les photos de réalisateurs et écrit les biographies dans le pack."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
BIOS = ROOT / "batchsData/batchReals/output/bios.json"
PHOTOS = ROOT / "batchsData/batchReals/output/photos"
DEST = ROOT / "app/src/main/assets/media/directors"


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    bios = json.loads(BIOS.read_text(encoding="utf-8")) if BIOS.is_file() else {}
    written = 0
    for director in pack["directors"]:
        text = (bios.get(director["code"]) or "").strip()
        if text:
            director["biography"] = text
            written += 1
        else:
            director.pop("biography", None)
    pack["version"] = 25
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
    DEST.mkdir(parents=True, exist_ok=True)
    copied = 0
    for photo in PHOTOS.glob("*.jpg"):
        if photo.stat().st_size <= 0:
            continue
        shutil.copyfile(photo, DEST / photo.name)
        copied += 1
    print(f"bios={written} photos={copied} directors={len(pack['directors'])} version={pack['version']}")


if __name__ == "__main__":
    main()
