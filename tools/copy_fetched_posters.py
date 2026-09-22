#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy fetched posters into the APK assets and keep only failures in input."""
from __future__ import annotations

import csv
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "batchPosters" / "input" / "input_movies.txt"
REPORT = ROOT / "batchPosters" / "output" / "reports" / "fetch_report.csv"
SRC = ROOT / "batchPosters" / "output" / "posters"
DST = ROOT / "app" / "src" / "main" / "assets" / "media" / "posters"
EXTS = (".jpg", ".jpeg", ".png", ".webp")
MIN_BYTES = 4_000
KEEP_STATUSES = {"NOT_FOUND", "NO_POSTER", "ERROR"}


def poster_for(code: str, folder: Path) -> Path | None:
    for ext in EXTS:
        path = folder / f"{code}{ext}"
        if path.is_file() and path.stat().st_size >= MIN_BYTES:
            return path
    return None


def parse_input() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for raw in INPUT.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.lower().startswith("frenchtitle"):
            continue
        cells = next(csv.reader([line], delimiter=";", quotechar='"'))
        if len(cells) < 4:
            raise SystemExit(f"bad input line: {line}")
        rows.append((cells[3].strip(), line))
    return rows


def parse_report() -> dict[str, str]:
    if not REPORT.is_file():
        raise SystemExit(f"missing report {REPORT}")
    statuses: dict[str, str] = {}
    with REPORT.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter=";"):
            code = (row.get("code") or "").strip()
            status = (row.get("status") or "").strip()
            if code:
                statuses[code] = status
    return statuses


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    input_rows = parse_input()
    statuses = parse_report()
    copied = 0
    kept: list[str] = []
    removed: list[str] = []
    counts = Counter()
    for code, line in input_rows:
        status = statuses.get(code, "NOT_FOUND")
        counts[status] += 1
        src = poster_for(code, SRC)
        if src is not None:
            dest = DST / src.name
            shutil.copy2(src, dest)
            copied += 1
        if status in KEEP_STATUSES and poster_for(code, DST) is None:
            kept.append(line)
        else:
            removed.append(code)

    header = [
        "# Films sans affiche TMDB (relancer : python posters_batch.py fetch).",
        "frenchTitle;releaseYear;director;code;originalTitle;demand;tmdbId",
    ]
    INPUT.write_text("\n".join(header + kept) + ("\n" if kept else "\n"), encoding="utf-8")
    print(f"report statuses: {dict(counts)}")
    print(f"copied to assets: {copied}")
    print(f"removed from input (poster OK): {len(removed)}")
    print(f"kept in input (no poster): {len(kept)}")
    for line in kept:
        print(f"  KEEP {line}")


if __name__ == "__main__":
    main()
