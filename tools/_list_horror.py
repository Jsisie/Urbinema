"""Temporary horror film list for the editorial folder."""
import json
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog.json").read_text(encoding="utf-8"))
directors = {item["code"]: item["displayName"] for item in pack["directors"]}
chars = {item["code"]: item for item in pack["characteristics"]}
HORROR_GENRES = {"HORREUR", "EPOUVANTE"}
HORROR_CHARS = {"GIALLO", "CINEMA_GORE", "GRINDHOUSE"}
COURANT_TYPES = {"MOVEMENT", "WAVE", "CURRENT", "SCHOOL", "PERIOD", "STYLE"}
SKIP = {"CINEMA_D_AUTEUR"}

rows = []
for movie in pack["movies"]:
    genres = set(movie.get("genreCodes") or [])
    codes = set(movie.get("characteristicCodes") or [])
    if not (genres & HORROR_GENRES or codes & HORROR_CHARS):
        continue
    title = movie.get("frenchTitle") or movie.get("originalTitle")
    names = []
    for item in sorted(movie.get("directors") or [], key=lambda value: value.get("billingOrder", 0)):
        names.append(directors.get(item["code"], item["code"]))
    courants = []
    for code in codes:
        meta = chars.get(code)
        if not meta or meta.get("typeCode") not in COURANT_TYPES or code in SKIP:
            continue
        courants.append(meta["name"])
    rows.append((movie["releaseYear"], title, ", ".join(names), ", ".join(courants)))

rows.sort(key=lambda row: (row[0], row[1].casefold()))
lines = [
    "TEMPORAIRE — à supprimer.",
    "Films d'horreur du catalogue : genre Horreur ou Épouvante,",
    "ou caractéristique Giallo, Cinéma gore, Grindhouse.",
    f"{len(rows)} films.",
    "",
]
for year, title, names, courants in rows:
    tail = courants if courants else "—"
    lines.append(f"- {title} — {year} — {names} — {tail}")

out = ROOT / "specs/Listes_Fonctionnelles/TEMP_Films_Horreur.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("films", len(rows))
