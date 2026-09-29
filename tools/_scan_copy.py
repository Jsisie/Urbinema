"""Count short synopses and Wikipedia footers. ASCII summary only."""
import json
import re
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
v3 = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
v1 = json.loads((root / "app/src/main/assets/catalog/catalog_v1.json").read_text(encoding="utf-8"))
v1_codes = {movie["code"] for movie in v1["movies"]}
lengths = []
short = 0
for movie in v3["movies"]:
    if movie["code"] not in v1_codes:
        continue
    size = len((movie.get("synopsis") or "").strip())
    lengths.append(size)
    if size < 160:
        short += 1
lengths.sort()
decades = {}
for movie in v3["movies"]:
    bucket = int(movie.get("releaseYear") or 0) // 10
    decades[bucket] = decades.get(bucket, 0) + 1
missing = [year for year in range(189, 203) if decades.get(year, 0) == 0]
wiki = 0
samples = []
for director in v3["directors"]:
    text = director.get("biography") or ""
    if re.search(r"wikip", text, re.I):
        wiki += 1
        if len(samples) < 8:
            tail = text.strip().split("\n")[-1][:180]
            samples.append(f"{director['code']}\t{tail}")
lines = [
    f"v1={len(v1_codes)} v3={len(v3['movies'])} v1_in_v3_short_lt160={short}",
    f"len_min={lengths[0] if lengths else 0} p50={lengths[len(lengths)//2] if lengths else 0} max={lengths[-1] if lengths else 0}",
    f"missing_decades={missing}",
    f"wiki_bios={wiki}",
    *samples,
]
out = root / "tools/output/_copy_scan.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"short={short} wiki={wiki} missing={len(missing)}")
