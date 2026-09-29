#!/usr/bin/env python3
"""Photos et biographies TMDB des réalisateurs. Hors APK."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "batchPosters"))

from posters_batch import TmdbClient, fold, load_env  # noqa: E402

CONFIG_PATH = ROOT / "config.json"
TMDB_IMAGE = "https://image.tmdb.org/t/p"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def resolve(config: dict, key: str) -> Path:
    path = Path(config[key])
    return path if path.is_absolute() else (ROOT / path)


def cell(value: str) -> str:
    text = (value or "").replace('"', "'")
    if any(ch in text for ch in ";\n\""):
        return f'"{text}"'
    return text


def read_input(path: Path) -> list[dict[str, str]]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = next(csv.reader([line], delimiter=";"))
        if len(parts) < 4:
            continue
        rows.append(
            {
                "code": parts[0].strip(),
                "firstName": parts[1].strip(),
                "lastName": parts[2].strip(),
                "displayName": parts[3].strip(),
            }
        )
    return rows


def generate(config: dict) -> None:
    catalog = json.loads(resolve(config, "catalogPath").read_text(encoding="utf-8"))
    destination = resolve(config, "inputFile")
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# code;firstName;lastName;displayName",
        f"# {len(catalog.get('directors') or [])} réalisateurs",
        "",
    ]
    for director in catalog.get("directors") or []:
        lines.append(
            ";".join(
                [
                    director["code"],
                    cell(director.get("firstName") or ""),
                    cell(director.get("lastName") or ""),
                    cell(director.get("displayName") or director["code"]),
                ]
            )
        )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"input={len(catalog.get('directors') or [])}")


def person_names(details: dict) -> list[str]:
    names = [str(details.get("name") or "")]
    for item in details.get("also_known_as") or []:
        if isinstance(item, str) and item.strip():
            names.append(item.strip())
    return [name for name in names if name]


def matches(display: str, details: dict) -> bool:
    wanted = fold(display)
    if not wanted:
        return False
    names = person_names(details)
    if any(fold(name) == wanted for name in names):
        return True
    wanted_tokens = [part for part in wanted.split() if len(part) >= 2]
    if len(wanted_tokens) <= 1:
        return False
    wanted_set = set(wanted_tokens)
    for name in names:
        tokens = [part for part in fold(name).split() if len(part) >= 2]
        if set(tokens) == wanted_set:
            return True
    return False


def search_people(client: TmdbClient, queries: list[str]) -> list[dict]:
    seen: set[int] = set()
    found: list[dict] = []
    for query in queries:
        if not query.strip():
            continue
        payload = client.request_json(
            "/search/person",
            {"query": query, "language": "en-US", "include_adult": "false", "page": "1"},
        )
        for item in payload.get("results") or []:
            person_id = item.get("id")
            if not isinstance(person_id, int) or person_id in seen:
                continue
            seen.add(person_id)
            found.append(item)
            if len(found) >= 6:
                return found
    return found


def biography_of(client: TmdbClient, person_id: int) -> tuple[dict, str]:
    french = client.request_json(f"/person/{person_id}", {"language": "fr-FR", "append_to_response": "images"})
    text = str(french.get("biography") or "").strip()
    if text:
        return french, text
    english = client.request_json(f"/person/{person_id}", {"language": "en-US"})
    return french, str(english.get("biography") or "").strip()


def profile_path(details: dict) -> str | None:
    path = details.get("profile_path")
    if path:
        return str(path)
    profiles = list((details.get("images") or {}).get("profiles") or [])
    profiles.sort(key=lambda item: -int(item.get("width") or 0))
    for item in profiles:
        if item.get("file_path"):
            return str(item["file_path"])
    return None


def queries_for(row: dict[str, str]) -> list[str]:
    display = row["displayName"]
    western = " ".join(part for part in (row["firstName"], row["lastName"]) if part).strip()
    ordered = [display]
    if western and fold(western) != fold(display):
        ordered.append(western)
    return ordered


def fetch(config: dict, limit: int, force: bool) -> None:
    load_env(ROOT / ".env")
    load_env(ROOT.parent / "batchPosters" / ".env")
    api_key = (os.environ.get("TMDB_API_KEY") or "").strip()
    if not api_key and not (os.environ.get("TMDB_ACCESS_TOKEN") or "").strip():
        raise SystemExit("TMDB manquant : .env dans batchReals ou batchPosters")
    client = TmdbClient(api_key, os.environ.get("TMDB_ACCESS_TOKEN") or "", float(config.get("sleepSeconds") or 0.2))
    rows = read_input(resolve(config, "inputFile"))
    if limit > 0:
        rows = rows[:limit]
    photo_dir = resolve(config, "photoDir")
    photo_dir.mkdir(parents=True, exist_ok=True)
    bios_path = resolve(config, "biosFile")
    bios: dict[str, str] = {}
    if bios_path.is_file():
        bios = json.loads(bios_path.read_text(encoding="utf-8"))
    report_path = resolve(config, "reportFile")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    size = str(config.get("profileSize") or "w342")
    ok = missing = nophoto = 0
    report_rows = []
    for index, row in enumerate(rows, start=1):
        code = row["code"]
        photo = photo_dir / f"{code}.jpg"
        if not force and photo.is_file() and photo.stat().st_size > 0 and bios.get(code):
            report_rows.append((code, "SKIP", "", row["displayName"]))
            continue
        chosen = None
        best_score = (-1, -1.0)
        for item in search_people(client, queries_for(row)):
            details, bio = biography_of(client, int(item["id"]))
            if not matches(row["displayName"], details):
                continue
            has_photo = 1 if profile_path(details) else 0
            popularity = float(item.get("popularity") or 0)
            score = (has_photo, popularity)
            if score > best_score:
                best_score = score
                chosen = (details, bio, int(item["id"]))
        if chosen is None:
            missing += 1
            report_rows.append((code, "NOT_FOUND", "", row["displayName"]))
            continue
        details, bio, person_id = chosen
        if bio:
            bios[code] = bio
        path = profile_path(details)
        if path and (force or not photo.is_file()):
            data, _kind = client.download(f"{TMDB_IMAGE}/{size}{path}")
            if data:
                photo.write_bytes(data)
        if photo.is_file() and photo.stat().st_size > 0:
            ok += 1
            report_rows.append((code, "OK", str(person_id), details.get("name") or ""))
        else:
            nophoto += 1
            report_rows.append((code, "NO_PHOTO", str(person_id), details.get("name") or ""))
        if index % 25 == 0:
            bios_path.parent.mkdir(parents=True, exist_ok=True)
            bios_path.write_text(json.dumps(bios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"progress={index} ok={ok} missing={missing} nophoto={nophoto}", flush=True)
    bios_path.parent.mkdir(parents=True, exist_ok=True)
    bios_path.write_text(json.dumps(bios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["code", "status", "tmdbId", "name"])
        writer.writerows(report_rows)
    print(f"ok={ok} missing={missing} nophoto={nophoto} bios={len(bios)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["generate", "fetch", "all"])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    config = load_config()
    if args.action in {"generate", "all"}:
        generate(config)
    if args.action in {"fetch", "all"}:
        fetch(config, args.limit, args.force)


if __name__ == "__main__":
    main()
