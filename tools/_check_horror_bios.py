import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
rows = (root / "tools/output/_horror_new_directors.txt").read_text(encoding="utf-8").splitlines()
codes = [line.split(";")[0] for line in rows if line.strip()]
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
by = {d["code"]: d for d in pack["directors"]}
photos = root / "app/src/main/assets/media/directors"
fr = en = photo = missing = 0
for code in codes:
    d = by.get(code)
    if d is None:
        missing += 1
        continue
    if (d.get("biography") or "").strip():
        fr += 1
    if (d.get("biographyEn") or "").strip():
        en += 1
    if (photos / f"{code}.jpg").is_file() and (photos / f"{code}.jpg").stat().st_size > 0:
        photo += 1
print("version", pack["version"], "movies", len(pack["movies"]), "dirs", len(pack["directors"]))
print("new", len(codes), "fr", fr, "en", en, "photo", photo, "absent", missing)
