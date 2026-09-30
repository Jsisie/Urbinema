import json
from pathlib import Path

pack = json.loads(Path("app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
lines = []
for movie in pack["movies"]:
    codes = [d.get("code") for d in movie.get("directors", [])]
    if "DIRECTOR" in codes or "MIKIO_NARUSE" in codes:
        titles = movie.get("frenchTitle") or movie.get("originalTitle")
        lines.append(
            f"{movie['code']}\t{movie.get('releaseYear')}\t{titles}\t{','.join(codes)}"
        )
Path("tools/output/_director_bucket.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
