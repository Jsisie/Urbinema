"""TMDB → objet film Urbinema (même schéma que catalog_v1.json / movies[])."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any

# TMDB genre id → code éditorial déjà présent dans le pack.
TMDB_GENRES = {
    12: "AVENTURE",
    14: "FANTASTIQUE",
    16: "ANIMATION",
    18: "DRAME",
    27: "HORREUR",
    28: "ACTION",
    35: "COMEDIE",
    36: "HISTORIQUE",
    37: "WESTERN",
    53: "THRILLER",
    80: "POLICIER",
    99: "DOCUMENTAIRE",
    878: "SCIENCE_FICTION",
    9648: "MYSTERE",
    10402: "MUSICAL",
    10749: "ROMANCE",
    10751: "FAMILLE",
    10752: "GUERRE",
}

ISO_OVERRIDES = {
    "US": "USA",
    "GB": "UK",
    "SU": "RUSSIA",
    "XC": "CZECH",
    "CS": "CZECH",
    "DD": "GERMANY",
    "DE": "GERMANY",
    "KR": "SOUTH_KOREA",
    "TW": "TAIWAN",
    "HK": "HONG_KONG",
    "YU": "YUGOSLAVIA",
    "AN": "NETHERLANDS",
    "BU": "BURKINA_FASO",
}


def clamp01(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 2)


def movie_format(minutes: int) -> str:
    if minutes < 40:
        return "SHORT"
    if minutes < 60:
        return "MEDIUM"
    if minutes >= 180:
        return "EXTENDED"
    return "FEATURE"


def scores_for(
    code: str,
    year: int,
    silent: bool,
    experimental: bool,
    demand: float,
) -> tuple[float, float, float, float]:
    digest = hashlib.md5(code.encode("utf-8")).hexdigest()
    jitter = int(digest[:4], 16) / 65535.0
    age = (2028 - year) / float(2028 - 1880)
    historical_distance = clamp01(0.16 + 0.72 * age + 0.08 * jitter)
    artistic_demand = clamp01(
        0.30
        + 0.42 * demand
        + (0.08 if silent else 0.0)
        + (0.16 if experimental else 0.0)
        + 0.06 * jitter
    )
    historical_richness = clamp01(0.48 + 0.38 * age + 0.12 * demand)
    cultural_richness = clamp01(
        0.46 + 0.30 * demand + 0.14 * (1.0 - jitter) + (0.06 if year < 1960 else 0.0)
    )
    return historical_distance, artistic_demand, historical_richness, cultural_richness


def ascii_slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    slug = re.sub(r"[^A-Za-z0-9]+", "_", stripped).strip("_").upper()
    return re.sub(r"_+", "_", slug)


def movie_code(title: str, year: int, explicit: str = "") -> str:
    if explicit.strip():
        return explicit.strip().strip("[]")
    slug = ascii_slug(title) or "FILM"
    return f"{slug}_{year}"


def fold_name(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def keyword_names(details: dict[str, Any]) -> list[str]:
    payload = details.get("keywords") or {}
    items = payload.get("keywords") or payload.get("results") or []
    names: list[str] = []
    for item in items:
        name = fold_name(str(item.get("name") or ""))
        if name:
            names.append(name)
    return names


def has_keyword(names: list[str], *needles: str) -> bool:
    return any(any(needle in name for needle in needles) for name in names)


def french_title(details: dict[str, Any], fallback: str) -> str:
    title = str(details.get("title") or "").strip()
    original = str(details.get("original_title") or "").strip()
    if title and fold_name(title) != fold_name(original):
        return title
    for block in (details.get("translations") or {}).get("translations") or []:
        if block.get("iso_639_1") != "fr":
            continue
        data = block.get("data") or {}
        candidate = str(data.get("title") or "").strip()
        if candidate:
            return candidate
    for alt in (details.get("alternative_titles") or {}).get("titles") or []:
        # BE and CH are multilingual country tags, not French language tags:
        # accepting them imported Dutch titles as frenchTitle in the catalog.
        if alt.get("iso_3166_1") == "FR":
            candidate = str(alt.get("title") or "").strip()
            if candidate:
                return candidate
    return fallback or title or original


def french_overview(details: dict[str, Any]) -> str:
    overview = str(details.get("overview") or "").strip()
    if overview:
        return overview
    for block in (details.get("translations") or {}).get("translations") or []:
        if block.get("iso_639_1") != "fr":
            continue
        data = block.get("data") or {}
        candidate = str(data.get("overview") or "").strip()
        if candidate:
            return candidate
    return ""


def split_person_name(display: str) -> tuple[str | None, str]:
    parts = [part for part in display.replace(".", " ").split() if part]
    if not parts:
        return None, display
    if len(parts) == 1:
        return None, parts[0]
    return " ".join(parts[:-1]), parts[-1]


def director_code_from_name(display: str) -> str:
    slug = ascii_slug(display)
    return slug or "DIRECTOR"


def match_director(catalog: dict[str, Any], display: str) -> dict[str, Any] | None:
    wanted = fold_name(display)
    if not wanted:
        return None
    tokens = [part for part in wanted.split() if len(part) > 1]
    last = tokens[-1] if tokens else wanted
    exact: dict[str, Any] | None = None
    last_hits: list[dict[str, Any]] = []
    for item in catalog.get("directors") or []:
        folded = fold_name(str(item.get("displayName") or ""))
        if folded == wanted:
            exact = item
            break
        if last and last in folded.split():
            last_hits.append(item)
    if exact:
        return exact
    if len(last_hits) == 1:
        return last_hits[0]
    return None


def iso_to_country(catalog: dict[str, Any], iso: str) -> dict[str, Any] | None:
    code = ISO_OVERRIDES.get(iso.upper(), "")
    by_iso = {str(item.get("isoCode") or "").upper(): item for item in catalog.get("countries") or []}
    by_code = {str(item.get("code") or ""): item for item in catalog.get("countries") or []}
    if code and code in by_code:
        return by_code[code]
    return by_iso.get(iso.upper())


def map_countries(
    catalog: dict[str, Any],
    details: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapped: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in details.get("production_countries") or []:
        iso = str(item.get("iso_3166_1") or "").upper()
        name = str(item.get("name") or iso)
        if not iso or iso in seen:
            continue
        seen.add(iso)
        known = iso_to_country(catalog, iso)
        if known:
            mapped.append({"code": known["code"], "isPrimary": False})
            continue
        suggested = ISO_OVERRIDES.get(iso) or ascii_slug(name) or iso
        unknown.append({"code": suggested, "name": name, "isoCode": iso, "continentCodes": []})
        mapped.append({"code": suggested, "isPrimary": False})
        if len(mapped) >= 2:
            break
    if mapped:
        mapped[0]["isPrimary"] = True
        mapped = mapped[:2]
    return mapped, unknown


def map_genres(details: dict[str, Any], keyword_list: list[str]) -> list[str]:
    codes: list[str] = []
    for item in details.get("genres") or []:
        genre_id = item.get("id")
        mapped = TMDB_GENRES.get(int(genre_id)) if isinstance(genre_id, int) else None
        if mapped and mapped not in codes:
            codes.append(mapped)
    if has_keyword(keyword_list, "film noir") and "FILM_NOIR" not in codes:
        codes.append("FILM_NOIR")
    return codes


def map_characteristics(
    catalog: dict[str, Any],
    details: dict[str, Any],
    year: int,
    country_codes: list[str],
    genre_codes: list[str],
    keyword_list: list[str],
    director_entries: list[dict[str, Any]],
    silent: bool,
    experimental: bool,
) -> list[str]:
    existing = {str(item.get("code")) for item in catalog.get("characteristics") or []}
    picked: list[str] = []

    def add(code: str) -> None:
        if code in existing and code not in picked:
            picked.append(code)

    for entry in director_entries:
        for code in entry.get("characteristicCodes") or []:
            # Period/wave tags on the director must not spill onto every film.
            if code in {
                "NOUVELLE_VAGUE_FRANCAISE", "HOLLYWOOD_CLASSIQUE", "NEW_HOLLYWOOD",
                "NEOREALISME_ITALIEN", "EXPRESSIONNISME_ALLEMAND", "CINEMA_SOVIETIQUE",
                "NOUVELLE_VAGUE_IRANIENNE", "INDIAN_PARALLEL", "KOREAN_NEW_WAVE",
            }:
                continue
            add(str(code))

    primary = country_codes[0] if country_codes else ""
    if silent:
        add("CINEMA_MUET_MOUVEMENT")
    if experimental:
        add("CINEMA_EXPERIMENTAL")
    if has_keyword(keyword_list, "surreal"):
        add("SURREALISME")
    if has_keyword(keyword_list, "film noir"):
        add("FILM_NOIR_STYLE")
    if has_keyword(keyword_list, "neo-noir", "neo noir"):
        add("NEO_NOIR")
    if has_keyword(keyword_list, "samurai", "jidaigeki", "jidai-geki"):
        add("JIDAIGEKI")
    if has_keyword(keyword_list, "giallo"):
        add("GIALLO")
    if has_keyword(keyword_list, "road movie"):
        add("ROAD_MOVIE")
    if has_keyword(keyword_list, "melodrama", "melodrame"):
        add("MELODRAME")
    if "ANIMATION" in genre_codes:
        add("ANIMATION_DAUTEUR")
    if "WESTERN" in genre_codes:
        if primary == "ITALY" or 1962 <= year <= 1978:
            add("SPAGHETTI_WESTERN")
        else:
            add("WESTERN_CLASSIQUE")
    if "DOCUMENTAIRE" in genre_codes:
        add("DOCUMENTAIRE_POETIQUE")
    if primary == "USA" and 1930 <= year <= 1960:
        add("HOLLYWOOD_CLASSIQUE")
    if primary == "USA" and 1967 <= year <= 1980:
        add("NEW_HOLLYWOOD")
    if primary == "JAPAN" and 1930 <= year <= 1965:
        add("AGE_OR_CINEMA_JAPONAIS")
    if primary == "ITALY" and 1944 <= year <= 1954:
        add("NEOREALISME_ITALIEN")
    # Nouvelle Vague is not "any French film 1958–1968" (Welles, Polish co-pros…).
    if primary == "FRANCE" and 1930 <= year <= 1939:
        add("REALISME_POETIQUE")
    if primary == "GERMANY" and 1919 <= year <= 1933:
        add("EXPRESSIONNISME_ALLEMAND")
    if primary == "GERMANY" and 1966 <= year <= 1982:
        add("NOUVEAU_CINEMA_ALLEMAND")
    if primary == "RUSSIA":
        add("CINEMA_SOVIETIQUE")
        if year <= 1930:
            add("MONTAGE_SOVIETIQUE")
    if primary == "IRAN":
        add("NOUVELLE_VAGUE_IRANIENNE")
    if primary == "SOUTH_KOREA" and year >= 1990:
        add("KOREAN_NEW_WAVE")
    if primary == "HONG_KONG" and 1980 <= year <= 2004:
        add("HONG_KONG_NEW_WAVE")
    if primary == "TAIWAN" and 1982 <= year <= 2001:
        add("TAIWAN_NEW_CINEMA")
    if primary == "BRAZIL" and 1960 <= year <= 1972:
        add("CINEMA_NOVO")
    if primary == "INDIA":
        add("INDIAN_PARALLEL")
    if primary in {"SENEGAL", "MALI", "ALGERIA", "EGYPT"}:
        add("CINEMA_AFRICAIN")
    if primary == "UK" and 1956 <= year <= 1970:
        add("NOUVELLE_VAGUE_BRITANNIQUE")
    if primary == "POLAND" and 1956 <= year <= 1968:
        add("ECOLE_POLONAISE")
    if primary == "CZECH" and 1963 <= year <= 1969:
        add("NOUVELLE_VAGUE_TCHEQUE")
    if primary == "DENMARK" and 1995 <= year <= 2005:
        add("DOGME_95")
    return picked


def tmdb_directors(details: dict[str, Any]) -> list[str]:
    crew = (details.get("credits") or {}).get("crew") or []
    names = [str(person.get("name") or "") for person in crew if person.get("job") == "Director"]
    return [name for name in names if name]


def build_movie(
    *,
    code: str,
    csv_title: str,
    csv_original: str,
    csv_year: int,
    csv_director: str,
    demand: float,
    details: dict[str, Any],
    catalog: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    keywords = keyword_names(details)
    year = int(str(details.get("release_date") or "0000")[:4] or csv_year)
    if year < 1880:
        year = csv_year
    runtime = int(details.get("runtime") or 0)
    if runtime <= 0:
        warnings.append("durée TMDB absente")
        runtime = 1
    original = str(details.get("original_title") or csv_original or csv_title).strip()
    french = french_title(details, csv_title)
    synopsis = french_overview(details)
    if not synopsis:
        warnings.append("synopsis TMDB vide")
        synopsis = ""

    silent = year <= 1929 or has_keyword(keywords, "silent film", "silent era", "muet")
    color = has_keyword(keywords, "technicolor", "eastmancolor", "in color", "colour")
    experimental = has_keyword(keywords, "experimental", "avant-garde", "avant garde")
    black_and_white = (not color) and (
        has_keyword(keywords, "black and white", "noir et blanc") or year <= 1954 or silent
    )

    names = tmdb_directors(details)
    if csv_director and not names:
        names = [part.strip() for part in re.split(r"\s*&\s*|,", csv_director) if part.strip()]
    director_refs: list[dict[str, Any]] = []
    new_directors: list[dict[str, Any]] = []
    matched_entries: list[dict[str, Any]] = []
    for index, name in enumerate(names):
        known = match_director(catalog, name)
        if known:
            director_refs.append({"code": known["code"], "billingOrder": index})
            matched_entries.append(known)
            continue
        generated = director_code_from_name(name)
        first, last = split_person_name(name)
        director_refs.append({"code": generated, "billingOrder": index})
        new_directors.append(
            {
                "code": generated,
                "firstName": first,
                "lastName": last,
                "displayName": name,
                "characteristicCodes": [],
            }
        )

    countries, new_countries = map_countries(catalog, details)
    if not countries:
        warnings.append("aucun pays TMDB")
    genre_codes = map_genres(details, keywords)
    country_codes = [item["code"] for item in countries]
    characteristics = map_characteristics(
        catalog,
        details,
        year,
        country_codes,
        genre_codes,
        keywords,
        matched_entries,
        silent,
        experimental,
    )
    hd, ad, hr, cr = scores_for(code, year, silent, experimental, demand)
    movie: dict[str, Any] = {
        "code": code,
        "originalTitle": original,
        "frenchTitle": french,
        "releaseYear": year,
        "durationMinutes": runtime,
        "format": movie_format(runtime),
        "synopsis": synopsis,
        "historicalDistance": hd,
        "artisticDemand": ad,
        "historicalRichness": hr,
        "culturalRichness": cr,
        "countries": countries,
        "directors": director_refs,
        "genreCodes": genre_codes,
        "characteristicCodes": characteristics,
    }
    if silent:
        movie["isSilent"] = True
    if black_and_white:
        movie["isBlackAndWhite"] = True
    if experimental:
        movie["isExperimental"] = True
    return movie, new_directors, new_countries, warnings
