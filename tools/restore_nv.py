#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retag the genuine French New Wave (1958–1973, core directors)."""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clean_catalog_editorial import keep_nv  # noqa: E402

CATALOG_V2 = ROOT / "app/src/main/assets/catalog/catalog_v2.json"
CATALOG_LIVE = ROOT / "app/src/main/assets/catalog/catalog.json"


def main() -> None:
    pack = json.loads(CATALOG_V2.read_text(encoding="utf-8"))
    directors_by_code = {item["code"]: item for item in pack.get("directors") or []}
    nv_collection = next(
        (item for item in pack.get("collections") or [] if item.get("code") == "COLLECTION_002"),
        None,
    )
    nv_films = {row["code"] for row in (nv_collection or {}).get("movies") or []}
    before = sum(
        1 for movie in pack["movies"] if "NOUVELLE_VAGUE_FRANCAISE" in (movie.get("characteristicCodes") or [])
    )
    added = 0
    removed = 0
    for movie in pack["movies"]:
        chars = list(movie.get("characteristicCodes") or [])
        had = "NOUVELLE_VAGUE_FRANCAISE" in chars
        genuine = keep_nv(movie, directors_by_code, nv_films)
        if genuine and not had:
            chars.append("NOUVELLE_VAGUE_FRANCAISE")
            added += 1
        elif had and not genuine:
            chars = [code for code in chars if code != "NOUVELLE_VAGUE_FRANCAISE"]
            removed += 1
        movie["characteristicCodes"] = chars
    after = sum(
        1 for movie in pack["movies"] if "NOUVELLE_VAGUE_FRANCAISE" in (movie.get("characteristicCodes") or [])
    )
    pack["version"] = 15
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
    CATALOG_V2.write_text(text, encoding="utf-8")
    shutil.copyfile(CATALOG_V2, CATALOG_LIVE)
    print(f"NV {before} -> {after} (added {added}, removed {removed})")
    dirs = {item["code"]: item.get("displayName") for item in pack["directors"]}
    tagged = [
        movie for movie in pack["movies"]
        if "NOUVELLE_VAGUE_FRANCAISE" in (movie.get("characteristicCodes") or [])
    ]
    tagged.sort(key=lambda movie: movie["releaseYear"])
    for movie in tagged:
        credits = movie.get("directors") or []
        name = dirs.get(credits[0]["code"], "?") if credits else "?"
        title = movie.get("frenchTitle") or movie.get("originalTitle")
        print(f"{movie['releaseYear']} {title} — {name}")


if __name__ == "__main__":
    main()
