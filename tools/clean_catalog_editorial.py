#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nettoie pays (1 par film) et courants trop larges, puis retire les pays vides."""
from __future__ import annotations

import json
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_V1 = ROOT / "app/src/main/assets/catalog/catalog_v1.json"
CATALOG_V2 = ROOT / "app/src/main/assets/catalog/catalog_v2.json"
CATALOG_LIVE = ROOT / "app/src/main/assets/catalog/catalog.json"
META_1000 = ROOT / "batchPosters/input/input_1000_meta.json"

NV_DIRECTORS = {
    "godard", "truffaut", "chabrol", "rohmer", "rivette", "varda", "resnais",
    "marker", "demy", "malle", "rozier", "kast", "vecchiali", "eustache",
    "pialat", "garrel", "franju", "rouch", "astruc", "doniol", "broca",
    "mocky", "pollet", "schroeder", "duras", "colpi", "robbegrillet",
    "doniolvalcroze",
}

STYLE_KEEP = {
    "GIALLO", "JIDAIGEKI", "SPAGHETTI_WESTERN", "FILM_NOIR_STYLE", "NEO_NOIR",
    "SURREALISME", "CINEMA_EXPERIMENTAL", "ROAD_MOVIE", "MELODRAME",
    "CINEMA_D_AUTEUR", "WESTERN_CLASSIQUE",
}

PERIOD_WINDOWS = {
    "NEOREALISME_ITALIEN": (1943, 1954, {"ITALY"}),
    "EXPRESSIONNISME_ALLEMAND": (1919, 1933, {"GERMANY"}),
    "REALISME_POETIQUE": (1930, 1939, {"FRANCE"}),
    "DOGME_95": (1995, 2005, {"DENMARK"}),
    "BRITISH_NEW_WAVE": (1956, 1970, {"UK"}),
    "ECOLE_POLONAISE": (1956, 1968, {"POLAND"}),
    "NOUVELLE_VAGUE_TCHEQUE": (1963, 1969, {"CZECH"}),
    "NOUVEAU_CINEMA_ALLEMAND": (1966, 1982, {"GERMANY"}),
    "HOLLYWOOD_CLASSIQUE": (1927, 1960, {"USA"}),
    "NEW_HOLLYWOOD": (1967, 1980, {"USA"}),
    "AGE_OR_CINEMA_JAPONAIS": (1930, 1965, {"JAPAN"}),
    "MONTAGE_SOVIETIQUE": (1919, 1934, {"RUSSIA", "UKRAINE"}),
}


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", "", stripped.casefold())


def director_keys(movie: dict, directors_by_code: dict) -> set[str]:
    keys: set[str] = set()
    for credit in movie.get("directors") or []:
        entry = directors_by_code.get(credit.get("code") or "")
        if not entry:
            continue
        last = fold(entry.get("lastName") or "")
        display = fold(entry.get("displayName") or "")
        if last:
            keys.add(last)
        if display:
            keys.add(display)
            keys.add(display[-12:])
    return keys


def country_codes(movie: dict) -> list[str]:
    return [item["code"] for item in movie.get("countries") or [] if item.get("code")]


def keep_nv(movie: dict, directors_by_code: dict, collection_codes: set[str]) -> bool:
    if movie["code"] in collection_codes:
        return True
    year = int(movie.get("releaseYear") or 0)
    # Années de la Vague (Cahiers + Rive gauche). Au-delà, ce n'est plus le mouvement.
    if year < 1958 or year > 1973:
        return False
    if "FRANCE" not in country_codes(movie) and not any(
        item.get("isPrimary") and item.get("code") == "FRANCE" for item in movie.get("countries") or []
    ):
        # After country cleanup the film is already nationality-only; check primary.
        primary = next((item["code"] for item in movie.get("countries") or [] if item.get("isPrimary")), None)
        if primary != "FRANCE":
            return False
    return bool(director_keys(movie, directors_by_code) & NV_DIRECTORS)


def keep_period(code: str, movie: dict, collection_films: set[str], editorial: str | None) -> bool:
    if movie["code"] in collection_films or editorial == code:
        return True
    window = PERIOD_WINDOWS.get(code)
    if not window:
        return True
    start, end, countries = window
    year = int(movie.get("releaseYear") or 0)
    if year < start or year > end:
        return False
    primary = next((item["code"] for item in movie.get("countries") or [] if item.get("isPrimary")), None)
    return primary in countries


def main() -> None:
    pack = json.loads(CATALOG_V2.read_text(encoding="utf-8"))
    v1 = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    meta = json.loads(META_1000.read_text(encoding="utf-8")) if META_1000.exists() else []
    v1_movies = {movie["code"]: movie for movie in v1.get("movies") or []}
    editorial = {row["code"]: row for row in meta if row.get("code")}
    directors_by_code = {item["code"]: item for item in pack.get("directors") or []}
    known_countries = {item["code"] for item in pack.get("countries") or []}

    nv_collection = next(
        (item for item in pack.get("collections") or [] if item.get("code") == "COLLECTION_002"),
        None,
    )
    nv_films = {row["code"] for row in (nv_collection or {}).get("movies") or []}
    collection_chars: dict[str, set[str]] = {}
    for collection in pack.get("collections") or []:
        for char in collection.get("characteristicCodes") or []:
            collection_chars.setdefault(char, set()).update(
                row["code"] for row in collection.get("movies") or []
            )

    nv_before = sum(
        1 for movie in pack["movies"] if "NOUVELLE_VAGUE_FRANCAISE" in (movie.get("characteristicCodes") or [])
    )
    multi_before = sum(1 for movie in pack["movies"] if len(movie.get("countries") or []) > 2)
    empty_countries_before = 0

    for movie in pack["movies"]:
        code = movie["code"]
        v1_movie = v1_movies.get(code)
        row = editorial.get(code)

        if row and row.get("countryCode") in known_countries:
            primary = row["countryCode"]
        elif v1_movie:
            v1_countries = v1_movie.get("countries") or []
            primary = next((item["code"] for item in v1_countries if item.get("isPrimary")), None)
            if not primary and v1_countries:
                primary = v1_countries[0]["code"]
        else:
            primary = next((item["code"] for item in movie.get("countries") or [] if item.get("isPrimary")), None)
            if not primary and movie.get("countries"):
                primary = movie["countries"][0]["code"]
        if not primary or primary not in known_countries:
            current = country_codes(movie)
            primary = next((item for item in current if item in known_countries), "USA")
        movie["countries"] = [{"code": primary, "isPrimary": True}]

        existing = [item for item in (movie.get("characteristicCodes") or []) if item]
        editorial_char = (row or {}).get("charCode")
        kept: list[str] = []

        def add(char: str) -> None:
            if char and char not in kept:
                kept.append(char)

        if editorial_char:
            add(editorial_char)
        if v1_movie:
            for char in v1_movie.get("characteristicCodes") or []:
                add(char)
        if movie.get("isSilent") or int(movie.get("releaseYear") or 0) <= 1929:
            add("CINEMA_MUET_MOUVEMENT")
        for char in existing:
            if char in STYLE_KEEP:
                add(char)

        if keep_nv(movie, directors_by_code, nv_films):
            add("NOUVELLE_VAGUE_FRANCAISE")
        elif "NOUVELLE_VAGUE_FRANCAISE" in kept:
            kept = [item for item in kept if item != "NOUVELLE_VAGUE_FRANCAISE"]

        for char in list(kept) + [item for item in existing if item not in kept]:
            if char == "NOUVELLE_VAGUE_FRANCAISE":
                continue
            if char in PERIOD_WINDOWS:
                if keep_period(char, movie, collection_chars.get(char, set()), editorial_char):
                    add(char)
                elif char in kept:
                    kept = [item for item in kept if item != char]
            elif char not in kept and char not in {
                "CINEMA_SOVIETIQUE", "NOUVELLE_VAGUE_IRANIENNE", "INDIAN_PARALLEL",
                "CINEMA_AFRICAIN", "KOREAN_NEW_WAVE", "DOCUMENTAIRE_POETIQUE",
                "ANIMATION_DAUTEUR", "HONG_KONG_NEW_WAVE",
            }:
                add(char)
            elif char in {
                "CINEMA_SOVIETIQUE", "NOUVELLE_VAGUE_IRANIENNE", "INDIAN_PARALLEL",
                "CINEMA_AFRICAIN", "KOREAN_NEW_WAVE", "DOCUMENTAIRE_POETIQUE",
                "ANIMATION_DAUTEUR", "HONG_KONG_NEW_WAVE",
            }:
                if editorial_char == char or code in collection_chars.get(char, set()):
                    add(char)
                elif char in kept and editorial_char != char and code not in collection_chars.get(char, set()):
                    # Country-dump tags: keep only editorial / collection membership.
                    if char != editorial_char:
                        kept = [item for item in kept if item != char]

        movie["characteristicCodes"] = kept

    used_countries = {item["code"] for movie in pack["movies"] for item in movie.get("countries") or []}
    before_countries = len(pack["countries"])
    pack["countries"] = [item for item in pack["countries"] if item["code"] in used_countries]
    empty_countries_before = before_countries - len(pack["countries"])

    for collection in pack.get("collections") or []:
        collection["countryCodes"] = [
            code for code in collection.get("countryCodes") or [] if code in used_countries
        ]

    nv_after = sum(
        1 for movie in pack["movies"] if "NOUVELLE_VAGUE_FRANCAISE" in (movie.get("characteristicCodes") or [])
    )
    max_countries = max(len(movie.get("countries") or []) for movie in pack["movies"])

    pack["version"] = 15
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
    CATALOG_V2.write_text(text, encoding="utf-8")
    shutil.copyfile(CATALOG_V2, CATALOG_LIVE)
    print(f"NV {nv_before} -> {nv_after}")
    print(f"films with >2 countries before cleanup: {multi_before}")
    print(f"max countries/film: {max_countries}")
    print(f"removed empty countries: {empty_countries_before} (now {len(pack['countries'])})")
    print(f"pack version {pack['version']}, movies {len(pack['movies'])}")


if __name__ == "__main__":
    main()
