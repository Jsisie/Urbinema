import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
v3 = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
copy = json.loads((root / "app/src/main/assets/catalog/catalog.json").read_text(encoding="utf-8"))
rows = (root / "tools/output/_horror_new_directors.txt").read_text(encoding="utf-8").splitlines()
codes = [line.split(";")[0] for line in rows if line.strip()]
by = {d["code"]: d for d in v3["directors"]}
photos = root / "app/src/main/assets/media/directors"
posters = root / "app/src/main/assets/media/posters"
neither = []
no_photo = []
for code in codes:
    d = by[code]
    fr = (d.get("biography") or "").strip()
    en = (d.get("biographyEn") or "").strip()
    if not fr and not en:
        neither.append(code)
    photo = photos / f"{code}.jpg"
    if not photo.is_file() or photo.stat().st_size <= 0:
        no_photo.append(code)
movies = {m["code"]: m for m in v3["movies"]}
import csv

input_path = root / "batchsData/batchPosters/input/input_horror.txt"
with input_path.open(encoding="utf-8", newline="") as handle:
    checks = [row["code"] for row in csv.DictReader(handle, delimiter=";")]
checks += [
    "LA_FEMME_DES_SABLES_1964",
    "L_EMPIRE_DES_SENS_1976",
    "LA_DERNIERE_VAGUE_1977",
    "THE_CRIMINAL_LIFE_OF_ARCHIBALDO_DE_LA_CRUZ_1955",
    "LE_SILENCE_DES_AGNEAUX_1991",
]
print("v3", v3["version"], len(v3["movies"]), len(v3["directors"]))
print("copy", copy["version"], len(copy["movies"]), len(copy["directors"]), "same", v3 == copy)
print("director_code", any(d["code"] == "DIRECTOR" for d in v3["directors"]))
print("neither", ",".join(neither) or "-")
print("no_photo", ",".join(no_photo) or "-")
missing_poster = []
for code, movie in movies.items():
    if code in checks or code.startswith("LOISEAU") or "ARGENTO" in str(movie.get("directors")):
        pass
for code in checks:
    movie = movies.get(code)
    if movie is None:
        print("MISSING", code)
        continue
    poster = posters / f"{code}.jpg"
    if not poster.is_file() or poster.stat().st_size <= 0:
        missing_poster.append(code)
    dirs = ",".join(item["code"] for item in movie["directors"])
    countries = ",".join(
        ("*" if c["isPrimary"] else "") + c["code"] for c in movie["countries"]
    )
    chars = ",".join(movie.get("characteristicCodes") or [])
    genres = ",".join(movie.get("genreCodes") or [])
    title = movie.get("frenchTitle") or movie.get("originalTitle") or ""
    title = title.encode("ascii", "replace").decode("ascii")
    print(f"{code}|{movie['releaseYear']}|{title}|{dirs}|{countries}|{genres}|{chars}|poster={poster.is_file()}")
print("missing_posters_checked", ",".join(missing_poster) or "-")
