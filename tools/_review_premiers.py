"""Review the premiers-temps fetch before merging it."""
import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
payload = json.loads(
    (root / "batchsData/batchPosters/output/catalog/premiers_temps.json").read_text(encoding="utf-8")
)
lines = []
for movie in payload["movies"]:
    directors = ",".join(ref["code"] for ref in movie.get("directors") or [])
    countries = ",".join(item["code"] for item in movie.get("countries") or [])
    lines.append(
        f"{movie['code']}\t{movie.get('releaseYear')}\t{movie.get('durationMinutes')}\t"
        f"{movie.get('format')}\t{directors}\t{countries}\t{movie.get('frenchTitle')}\t"
        f"{movie.get('originalTitle')}\tsyn={len(movie.get('synopsis') or '')}"
    )
lines.append("--- DIRECTORS ---")
for director in payload.get("newDirectors") or []:
    lines.append(f"{director['code']}\t{director.get('displayName')}\t{director.get('firstName')}\t{director.get('lastName')}")
(root / "tools/output/_premiers_review.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"movies={len(payload['movies'])} directors={len(payload.get('newDirectors') or [])}")
