"""List the early films whose synopsis TMDB did not improve."""
import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
done = json.loads((root / "tools/output/synopses.json").read_text(encoding="utf-8"))
by_code = {movie["code"]: movie for movie in pack["movies"]}
lines = []
for code, row in done.items():
    if row.get("status") != "KEEP":
        continue
    movie = by_code[code]
    text = (movie.get("synopsis") or "").replace("\n", " ")
    lines.append(f"{code}\t{movie.get('frenchTitle')}\t{len(text)}\t{text}")
(root / "tools/output/_keep_syn.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
