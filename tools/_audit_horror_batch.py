"""Print the fetched horror batch so mismatches can be caught before merge."""
import json
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
payload = json.loads((ROOT / "batchsData/batchPosters/output/catalog/movies.json").read_text(encoding="utf-8"))
lines = []
for movie in payload["movies"]:
    directors = ", ".join(item["code"] for item in movie.get("directors") or [])
    countries = ", ".join(item["code"] for item in movie.get("countries") or [])
    lines.append(
        f"{movie['code']} | {movie.get('frenchTitle')} | {movie.get('originalTitle')} | {movie['releaseYear']} | {movie['durationMinutes']} | {directors} | {countries} | {', '.join(movie.get('genreCodes') or [])}"
    )
out = ROOT / "tools/output/_horror_batch.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("movies", len(payload["movies"]), "newDirs", len(payload.get("newDirectors") or []), "newCountries", len(payload.get("newCountries") or []))
