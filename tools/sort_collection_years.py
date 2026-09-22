#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sort each collection's films by release year (pack 17)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_V2 = ROOT / "app/src/main/assets/catalog/catalog_v2.json"
CATALOG_LIVE = ROOT / "app/src/main/assets/catalog/catalog.json"


def title_of(movie: dict) -> str:
    return (movie.get("frenchTitle") or movie.get("originalTitle") or "").casefold()


def main() -> None:
    pack = json.loads(CATALOG_V2.read_text(encoding="utf-8"))
    by_code = {movie["code"]: movie for movie in pack["movies"]}
    for collection in pack["collections"]:
        rows = list(collection.get("movies") or [])
        rows.sort(
            key=lambda row: (
                by_code[row["code"]]["releaseYear"],
                title_of(by_code[row["code"]]),
                row["code"],
            )
        )
        collection["movies"] = [
            {"code": row["code"], "displayOrder": index}
            for index, row in enumerate(rows, start=1)
        ]
        years = [by_code[row["code"]]["releaseYear"] for row in collection["movies"]]
        print(f"{collection['code']} {collection['name']}: {years[0]}-{years[-1]} ({len(years)})")
    pack["version"] = 17
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
    CATALOG_V2.write_text(text, encoding="utf-8")
    shutil.copyfile(CATALOG_V2, CATALOG_LIVE)
    print(f"pack {pack['version']} collections={len(pack['collections'])}")


if __name__ == "__main__":
    main()
