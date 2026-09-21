#!/usr/bin/env python3
"""Batch Urbinema : affiches TMDB et/ou fiches film au format catalog_v1.json."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

from catalog_enrich import build_movie, movie_code

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
ENV_PATH = ROOT / ".env"
TMDB_API = "https://api.themoviedb.org/3"
TMDB_IMAGE = "https://image.tmdb.org/t/p"
TPDB_SEARCH = "https://theposterdb.com/search"
USER_AGENT = "UrbinemaPosterBatch/1.0 (local catalog; educational)"
IMAGE_EXTS = (".webp", ".png", ".jpg", ".jpeg")
CONTENT_TYPE_EXT = {
    "image/webp": ".webp",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
}


@dataclass
class MovieRow:
    title: str
    year: int
    director: str
    code: str
    original_title: str = ""
    line_no: int = 0
    tmdb_id: str = ""
    demand: float | None = None


@dataclass
class FetchResult:
    code: str
    title: str
    year: int
    director: str
    status: str
    source: str = ""
    tmdb_id: str = ""
    matched_title: str = ""
    poster_file: str = ""
    error: str = ""
    tpdb_url: str = ""
    movie: dict[str, Any] | None = None
    warnings: str = ""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path)


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    # Keep letters from any script (Hangul, etc.), not only ASCII.
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


def title_score(query: str, candidate: str) -> float:
    left, right = fold(query), fold(candidate)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    if left in right or right in left:
        return 0.92
    return SequenceMatcher(None, left, right).ratio()


def year_of(release_date: str | None) -> int | None:
    if not release_date or len(release_date) < 4 or not release_date[:4].isdigit():
        return None
    return int(release_date[:4])


def csv_quote(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def parse_code(raw: str) -> str:
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    return text


HEADER_ALIASES = {
    "title": "title",
    "titre": "title",
    "frenchtitle": "title",
    "titrefr": "title",
    "year": "year",
    "annee": "year",
    "releaseyear": "year",
    "director": "director",
    "realisateur": "director",
    "code": "code",
    "originaltitle": "original_title",
    "titreoriginal": "original_title",
    "tmdbid": "tmdb_id",
    "demand": "demand",
}


def detect_delimiter(sample: str) -> str:
    return ";" if sample.count(";") >= sample.count(",") else ","


def parse_demand(raw: str) -> float | None:
    text = raw.strip().replace(",", ".")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError(f"demand invalide: {raw}") from exc
    if not 0 <= value <= 1:
        raise ValueError(f"demand hors [0, 1]: {raw}")
    return value


def parse_fields(
    fields: dict[str, str],
    line_no: int,
) -> MovieRow:
    title = fields.get("title", "").strip()
    year_raw = fields.get("year", "").strip()
    director = fields.get("director", "").strip()
    original = fields.get("original_title", "").strip()
    tmdb_id = fields.get("tmdb_id", "").strip()
    demand = parse_demand(fields.get("demand", "")) if fields.get("demand") else None
    if not title or not year_raw.isdigit():
        raise ValueError(f"ligne {line_no}: titre et année numérique obligatoires")
    year = int(year_raw)
    code = parse_code(fields.get("code", "")) or movie_code(title, year)
    return MovieRow(
        title=title,
        year=year,
        director=director,
        code=code,
        original_title=original,
        line_no=line_no,
        tmdb_id=tmdb_id,
        demand=demand,
    )


def parse_input_line(line: str, line_no: int, delimiter: str = ";") -> MovieRow:
    try:
        row = next(csv.reader([line], delimiter=delimiter, quotechar='"'))
    except csv.Error as exc:
        raise ValueError(f"ligne {line_no}: CSV invalide ({exc})") from exc
    cells = [cell.strip() for cell in row]
    if len(cells) < 2:
        raise ValueError(f"ligne {line_no}: au moins titre et année")
    fields = {
        "title": cells[0],
        "year": cells[1],
        "director": cells[2] if len(cells) > 2 else "",
        "code": cells[3] if len(cells) > 3 else "",
        "original_title": cells[4] if len(cells) > 4 else "",
        "demand": cells[5] if len(cells) > 5 else "",
        "tmdb_id": cells[6] if len(cells) > 6 else "",
    }
    return parse_fields(fields, line_no)


def is_header_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return HEADER_ALIASES.get(re.sub(r"[^a-z0-9]+", "", cells[0].casefold())) == "title"


def read_input(path: Path) -> list[MovieRow]:
    movies: list[MovieRow] = []
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    first = next((line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("#")), "")
    delimiter = detect_delimiter(first)
    header: list[str] | None = None
    for line_no, raw in enumerate(raw_lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            cells = next(csv.reader([line], delimiter=delimiter, quotechar='"'))
        except csv.Error as exc:
            raise ValueError(f"ligne {line_no}: CSV invalide ({exc})") from exc
        cells = [cell.strip() for cell in cells]
        if header is None and is_header_row(cells):
            header = cells
            continue
        if header:
            fields: dict[str, str] = {}
            for index, name in enumerate(header):
                key = HEADER_ALIASES.get(re.sub(r"[^a-z0-9]+", "", name.casefold()))
                if key and index < len(cells):
                    fields[key] = cells[index]
            movies.append(parse_fields(fields, line_no))
        else:
            movies.append(parse_input_line(line, line_no, delimiter))
    return movies


def existing_poster(output_dir: Path, code: str) -> Path | None:
    for ext in IMAGE_EXTS:
        candidate = output_dir / f"{code}{ext}"
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    return None


def tpdb_search_url(title: str, year: int) -> str:
    return f"{TPDB_SEARCH}?term={quote(f'{title} {year}')}"


class TmdbClient:
    def __init__(self, api_key: str, access_token: str, sleep_seconds: float) -> None:
        self.api_key = api_key
        self.access_token = access_token
        self.sleep_seconds = sleep_seconds

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _url(self, path: str, params: dict[str, Any] | None = None) -> str:
        query = dict(params or {})
        if not self.access_token:
            query["api_key"] = self.api_key
        encoded = urlencode(query, doseq=True)
        return f"{TMDB_API}{path}?{encoded}" if encoded else f"{TMDB_API}{path}"

    def request_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return json.loads(self._request(self._url(path, params), self._headers()).decode("utf-8"))

    def download(self, url: str) -> tuple[bytes, str]:
        data, content_type = self._request(url, {"User-Agent": USER_AGENT}, want_type=True)
        return data, content_type

    def _request(
        self,
        url: str,
        headers: dict[str, str],
        want_type: bool = False,
        retries: int = 4,
    ) -> bytes | tuple[bytes, str]:
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                request = Request(url, headers=headers, method="GET")
                with urlopen(request, timeout=30) as response:
                    payload = response.read()
                    content_type = response.headers.get_content_type() or ""
                    if self.sleep_seconds:
                        time.sleep(self.sleep_seconds)
                    return (payload, content_type) if want_type else payload
            except HTTPError as exc:
                last_error = exc
                if exc.code == 429 or 500 <= exc.code < 600:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise
            except URLError as exc:
                last_error = exc
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"échec HTTP après {retries} essais: {url} ({last_error})")

    def search_movie(self, query: str, year: int, language: str) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        base = {
            "query": query,
            "include_adult": "false",
            "language": language,
            "page": "1",
        }
        payload = self.request_json("/search/movie", {**base, "primary_release_year": str(year)})
        results = list(payload.get("results") or [])
        if results:
            return results
        return list((self.request_json("/search/movie", base).get("results") or []))

    def movie_details(self, movie_id: int, language: str) -> dict[str, Any]:
        return self.request_json(
            f"/movie/{movie_id}",
            {
                "language": language,
                "append_to_response": "credits,images,keywords,translations,alternative_titles",
                "include_image_language": "fr,en,null",
            },
        )


def generate_input(config: dict[str, Any]) -> Path:
    catalog_path = resolve_path(config["catalogPath"])
    input_path = resolve_path(config["inputFile"])
    catalog = load_json(catalog_path)
    directors = {
        item["code"]: item.get("displayName") or item["code"]
        for item in catalog.get("directors", [])
    }
    movies = catalog.get("movies", [])
    input_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Généré depuis catalog_v1.json — une ligne = un film.",
        "# Format : \"titre FR\";année;\"réalisateur\";CODE;\"titre original\"",
        f"# {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} — {len(movies)} films",
        "",
    ]
    for movie in movies:
        names: list[str] = []
        for credit in sorted(movie.get("directors", []), key=lambda item: item.get("billingOrder", 0)):
            names.append(directors.get(credit["code"], credit["code"]))
        lines.append(
            ";".join(
                [
                    csv_quote(movie.get("frenchTitle") or movie.get("originalTitle") or movie["code"]),
                    str(movie["releaseYear"]),
                    csv_quote(" & ".join(names)),
                    movie["code"],
                    csv_quote(movie.get("originalTitle") or ""),
                ]
            )
        )
    input_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Écrit {len(movies)} films -> {input_path}")
    return input_path


def director_names(details: dict[str, Any]) -> list[str]:
    crew = (details.get("credits") or {}).get("crew") or []
    return [person.get("name", "") for person in crew if person.get("job") == "Director" and person.get("name")]


def director_match(expected: str, details: dict[str, Any]) -> float:
    wanted = fold(expected)
    if not wanted:
        return 0.0
    tokens = [part for part in wanted.split() if len(part) > 1]
    last = tokens[-1] if tokens else wanted
    best = 0.0
    for name in director_names(details):
        folded = fold(name)
        if folded == wanted:
            return 1.0
        if last and last in folded.split():
            best = max(best, 0.85)
        best = max(best, SequenceMatcher(None, wanted, folded).ratio())
    return best


def pick_poster_path(details: dict[str, Any], preferred: list[str]) -> str | None:
    posters = list((details.get("images") or {}).get("posters") or [])
    rank = {code: index for index, code in enumerate(preferred)}

    def key(item: dict[str, Any]) -> tuple[int, float, int]:
        language = item.get("iso_639_1") or "xx"
        return (
            rank.get(language, 50),
            -float(item.get("vote_average") or 0),
            -int(item.get("width") or 0),
        )

    posters.sort(key=key)
    for item in posters:
        path = item.get("file_path")
        if path:
            return path
    return details.get("poster_path")


def score_candidate(
    row: MovieRow,
    details: dict[str, Any],
    year_tolerance: int,
    extra_titles: list[str] | None = None,
) -> float | None:
    titles = [
        details.get("title") or "",
        details.get("original_title") or "",
        *(extra_titles or []),
    ]
    best_title = max(title_score(row.title, candidate) for candidate in titles)
    if row.original_title:
        best_title = max(best_title, max(title_score(row.original_title, candidate) for candidate in titles))
    director = director_match(row.director, details)
    # Titre trop éloigné + pas de réalisateur : on jette.
    if best_title < 0.45 and director < 0.7:
        return None
    tmdb_year = year_of(details.get("release_date"))
    if tmdb_year is None:
        if best_title >= 0.85 and director >= 0.85:
            delta = 0
        else:
            return None
    else:
        delta = abs(tmdb_year - row.year)
        max_delta = year_tolerance
        # Restaurations / dates TV TMDB (ex. Out 1 : 1971 vs 1990).
        if best_title >= 0.8 and director >= 0.85:
            max_delta = max(year_tolerance, 25)
        if delta > max_delta:
            return None
    year_points = 1.0 if delta == 0 else 0.55
    return (year_points * 40) + (best_title * 40) + (director * 30) + (8 if details.get("poster_path") else 0)


def search_candidates(client: TmdbClient, row: MovieRow, limit: int) -> list[dict[str, Any]]:
    seen: set[int] = set()
    ordered: list[dict[str, Any]] = []
    queries = [(row.title, "fr-FR"), (row.title, "en-US")]
    if row.original_title and fold(row.original_title) != fold(row.title):
        queries.append((row.original_title, "en-US"))
        queries.append((row.original_title, "fr-FR"))
    per_query = max(limit, 5)
    for query, language in queries:
        added = 0
        for item in client.search_movie(query, row.year, language):
            movie_id = item.get("id")
            if not isinstance(movie_id, int) or movie_id in seen:
                continue
            seen.add(movie_id)
            ordered.append(item)
            added += 1
            if added >= per_query:
                break
    return ordered


def extension_for(url: str, content_type: str) -> str:
    mapped = CONTENT_TYPE_EXT.get(content_type.lower())
    if mapped:
        return mapped
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in IMAGE_EXTS:
        return suffix
    return ".jpg"


def resolve_tmdb(
    client: TmdbClient,
    row: MovieRow,
    config: dict[str, Any],
) -> tuple[dict[str, Any] | None, str]:
    if row.tmdb_id.isdigit():
        return client.movie_details(int(row.tmdb_id), "fr-FR"), row.tmdb_id
    candidates = search_candidates(client, row, int(config.get("maxSearchResults", 5)))
    best: tuple[float, dict[str, Any]] | None = None
    for item in candidates:
        details = client.movie_details(int(item["id"]), "fr-FR")
        extra = [str(item.get("title") or ""), str(item.get("original_title") or "")]
        score = score_candidate(row, details, int(config.get("yearTolerance", 1)), extra)
        if score is None:
            continue
        if best is None or score > best[0]:
            best = (score, details)
    if best is None:
        return None, ""
    return best[1], str(best[1].get("id") or "")


def save_poster(
    client: TmdbClient,
    details: dict[str, Any],
    code: str,
    config: dict[str, Any],
    output_dir: Path,
    force: bool,
    dry_run: bool,
) -> tuple[str, str]:
    existing = existing_poster(output_dir, code)
    if existing and config.get("skipExisting", True) and not force:
        return "SKIP_EXISTING", existing.name
    poster_path = pick_poster_path(details, list(config.get("preferredLanguages") or ["fr", "xx", "en"]))
    if not poster_path:
        return "NO_POSTER", ""
    filename = f"{code}.jpg"
    if dry_run:
        return "DRY_RUN", filename
    size = str(config.get("posterSize") or "w780")
    url = f"{TMDB_IMAGE}/{size}{poster_path}"
    payload, content_type = client.download(url)
    if not payload:
        return "ERROR", ""
    ext = extension_for(url, content_type)
    dest = output_dir / f"{code}{ext}"
    dest.write_bytes(payload)
    return "OK", dest.name


def fetch_one(
    client: TmdbClient,
    row: MovieRow,
    config: dict[str, Any],
    output_dir: Path,
    force: bool,
    dry_run: bool,
) -> FetchResult:
    result = FetchResult(
        code=row.code,
        title=row.title,
        year=row.year,
        director=row.director,
        status="NOT_FOUND",
        tpdb_url=tpdb_search_url(row.title, row.year),
    )
    existing = existing_poster(output_dir, row.code)
    if existing and config.get("skipExisting", True) and not force:
        result.status = "SKIP_EXISTING"
        result.source = "disk"
        result.poster_file = existing.name
        return result

    details, tmdb_id = resolve_tmdb(client, row, config)
    if details is None:
        result.status = "NOT_FOUND"
        result.error = "aucun match TMDB assez sûr"
        result.source = "tpdb_manual"
        return result
    result.tmdb_id = tmdb_id
    result.matched_title = str(details.get("title") or details.get("original_title") or "")
    status, filename = save_poster(client, details, row.code, config, output_dir, force, dry_run)
    result.source = "tmdb" if status != "SKIP_EXISTING" else "disk"
    result.poster_file = filename
    if status == "NO_POSTER":
        result.status = "NO_POSTER"
        result.error = f"TMDB id={result.tmdb_id} sans affiche"
        return result
    if status == "ERROR":
        result.status = "ERROR"
        result.error = "téléchargement vide"
        return result
    result.status = status
    return result


def write_report(path: Path, results: list[FetchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            [
                "code",
                "title",
                "year",
                "director",
                "status",
                "source",
                "tmdb_id",
                "matched_title",
                "poster_file",
                "error",
                "tpdb_search_url",
            ]
        )
        for item in results:
            writer.writerow(
                [
                    item.code,
                    item.title,
                    item.year,
                    item.director,
                    item.status,
                    item.source,
                    item.tmdb_id,
                    item.matched_title,
                    item.poster_file,
                    item.error,
                    item.tpdb_url,
                ]
            )


def summarize(results: list[FetchResult]) -> str:
    counts: dict[str, int] = {}
    for item in results:
        counts[item.status] = counts.get(item.status, 0) + 1
    parts = [f"{status}={count}" for status, count in sorted(counts.items())]
    return ", ".join(parts) if parts else "aucun film"


def require_tmdb_auth() -> tuple[str, str]:
    load_env(ENV_PATH)
    api_key = (os.environ.get("TMDB_API_KEY") or "").strip()
    token = (os.environ.get("TMDB_ACCESS_TOKEN") or "").strip()
    if not api_key and not token:
        raise SystemExit(
            "Clé TMDB manquante. Copie .env.example vers .env et renseigne TMDB_API_KEY "
            "(https://www.themoviedb.org/settings/api)."
        )
    return api_key, token


def fetch_posters(
    config: dict[str, Any],
    limit: int | None,
    force: bool,
    dry_run: bool,
    input_path: Path | None = None,
) -> int:
    source = input_path or resolve_path(config["inputFile"])
    output_dir = resolve_path(config["outputDir"])
    report_path = resolve_path(config["reportFile"])
    log_path = resolve_path(config["logFile"])
    if not source.is_file():
        raise SystemExit(f"Fichier d'entrée introuvable: {source}\nLance d'abord: python posters_batch.py generate")
    movies = read_input(source)
    if limit is not None:
        movies = movies[:limit]
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    api_key, token = require_tmdb_auth()
    client = TmdbClient(api_key, token, float(config.get("sleepSeconds") or 0.3))
    results: list[FetchResult] = []
    print(f"{len(movies)} films à traiter -> {output_dir}")
    try:
        for index, row in enumerate(movies, start=1):
            print(f"[{index}/{len(movies)}] {row.code} — {row.title} ({row.year})")
            try:
                result = fetch_one(client, row, config, output_dir, force, dry_run)
            except Exception as exc:  # noqa: BLE001 - on continue le batch
                result = FetchResult(
                    code=row.code,
                    title=row.title,
                    year=row.year,
                    director=row.director,
                    status="ERROR",
                    error=str(exc),
                    tpdb_url=tpdb_search_url(row.title, row.year),
                )
            results.append(result)
            print(f"    {result.status} {result.source} {result.poster_file or result.error}".rstrip())
    finally:
        write_report(report_path, results)
        log_path.write_text(
            f"{datetime.now(timezone.utc).isoformat()} {summarize(results)}\n",
            encoding="utf-8",
        )
    print(f"Rapport: {report_path}")
    print(summarize(results))
    failures = [item for item in results if item.status in {"NOT_FOUND", "NO_POSTER", "ERROR"}]
    return 1 if failures else 0


def merge_unique(items: list[dict[str, Any]], key: str = "code") -> list[dict[str, Any]]:
    seen: set[str] = set()
    ordered: list[dict[str, Any]] = []
    for item in items:
        code = str(item.get(key) or "")
        if not code or code in seen:
            continue
        seen.add(code)
        ordered.append(item)
    return ordered


def catalog_from_tmdb(
    config: dict[str, Any],
    limit: int | None,
    force: bool,
    dry_run: bool,
    download_posters: bool,
    input_path: Path | None = None,
) -> int:
    input_file = input_path or resolve_path(config.get("catalogInputFile") or config["inputFile"])
    output_dir = resolve_path(config["outputDir"])
    catalog_path = resolve_path(config["catalogPath"])
    movies_path = resolve_path(config.get("catalogOutputFile") or "output/catalog/movies.json")
    report_path = resolve_path(config.get("catalogReportFile") or "output/reports/catalog_report.csv")
    log_path = resolve_path(config["logFile"])
    if not input_file.is_file():
        raise SystemExit(f"Fichier d'entrée introuvable: {input_file}")
    catalog = load_json(catalog_path)
    movies = read_input(input_file)
    if limit is not None:
        movies = movies[:limit]
    output_dir.mkdir(parents=True, exist_ok=True)
    movies_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    api_key, token = require_tmdb_auth()
    client = TmdbClient(api_key, token, float(config.get("sleepSeconds") or 0.3))
    default_demand = float(config.get("defaultDemand") or 0.7)
    results: list[FetchResult] = []
    built: list[dict[str, Any]] = []
    new_directors: list[dict[str, Any]] = []
    new_countries: list[dict[str, Any]] = []
    print(f"{len(movies)} films → JSON {movies_path}")
    try:
        for index, row in enumerate(movies, start=1):
            print(f"[{index}/{len(movies)}] {row.code} — {row.title} ({row.year})")
            result = FetchResult(
                code=row.code,
                title=row.title,
                year=row.year,
                director=row.director,
                status="NOT_FOUND",
                tpdb_url=tpdb_search_url(row.title, row.year),
            )
            try:
                details, tmdb_id = resolve_tmdb(client, row, config)
                if details is None:
                    result.error = "aucun match TMDB assez sûr"
                    result.source = "tpdb_manual"
                    results.append(result)
                    print(f"    {result.status} {result.error}")
                    continue
                movie, directors, countries, warnings = build_movie(
                    code=row.code,
                    csv_title=row.title,
                    csv_original=row.original_title,
                    csv_year=row.year,
                    csv_director=row.director,
                    demand=row.demand if row.demand is not None else default_demand,
                    details=details,
                    catalog=catalog,
                )
                built.append(movie)
                new_directors.extend(directors)
                new_countries.extend(countries)
                result.tmdb_id = tmdb_id
                result.matched_title = str(movie.get("frenchTitle") or "")
                result.movie = movie
                result.warnings = " | ".join(warnings)
                result.source = "tmdb"
                result.status = "OK"
                if download_posters:
                    poster_status, filename = save_poster(
                        client, details, row.code, config, output_dir, force, dry_run
                    )
                    result.poster_file = filename
                    if poster_status == "NO_POSTER":
                        result.status = "NO_POSTER"
                        result.error = "fiche OK, pas d'affiche"
                    elif poster_status == "ERROR":
                        result.status = "ERROR"
                        result.error = "fiche OK, téléchargement affiche vide"
                    elif poster_status == "SKIP_EXISTING":
                        result.source = "tmdb+disk"
                    elif poster_status == "DRY_RUN":
                        result.status = "DRY_RUN"
            except Exception as exc:  # noqa: BLE001
                result.status = "ERROR"
                result.error = str(exc)
            results.append(result)
            extra = result.poster_file or result.error or result.warnings
            print(f"    {result.status} {result.source} {extra}".rstrip())
    finally:
        payload = {
            "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "tmdb",
            "movies": built,
            "newDirectors": merge_unique(new_directors),
            "newCountries": merge_unique(new_countries),
        }
        movies_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_report(report_path, results)
        log_path.write_text(
            f"{datetime.now(timezone.utc).isoformat()} catalog {summarize(results)}\n",
            encoding="utf-8",
        )
    print(f"JSON: {movies_path} ({len(built)} films)")
    print(f"Rapport: {report_path}")
    print(summarize(results))
    failures = [item for item in results if item.status in {"NOT_FOUND", "ERROR"}]
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch TMDB Urbinema : affiches, et/ou fiches film JSON."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["generate", "fetch", "posters", "catalog", "all"],
        help="generate = CSV depuis le pack, fetch/posters = affiches, "
        "catalog = JSON films + affiches, all = generate + posters",
    )
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Chemin vers config.json")
    parser.add_argument("--input", default=None, help="CSV / TXT d'entrée (sinon config)")
    parser.add_argument("--limit", type=int, default=None, help="N premiers films seulement")
    parser.add_argument("--force", action="store_true", help="Retélécharger même si le fichier existe")
    parser.add_argument("--dry-run", action="store_true", help="Cherche TMDB sans écrire les images")
    parser.add_argument(
        "--no-posters",
        action="store_true",
        help="Mode catalog : JSON seulement, pas d'affiches",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_json(Path(args.config))
    input_path = Path(args.input) if args.input else None
    command = "fetch" if args.command == "posters" else args.command
    if command in {"generate", "all"}:
        generate_input(config)
    if command == "catalog":
        return catalog_from_tmdb(
            config,
            args.limit,
            args.force,
            args.dry_run,
            download_posters=not args.no_posters,
            input_path=input_path,
        )
    if command in {"fetch", "all"}:
        return fetch_posters(config, args.limit, args.force, args.dry_run, input_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
