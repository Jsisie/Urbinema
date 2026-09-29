"""Match the Cinéma des premiers temps list against catalog_v3."""
import json
import re
import unicodedata
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
out = root / "tools/output/_premiers_match.txt"

FILMS = [
    ("Pauvre Pierrot", 1892),
    ("Experimental Sound Film", 1894),
    ("Annie Oakley", 1894),
    ("La Sortie de l'usine Lumière à Lyon", 1895),
    ("L'Arroseur arrosé", 1895),
    ("L'Arrivée d'un train en gare de La Ciotat", 1895),
    ("Le Manoir du Diable", 1896),
    ("Le Panorama du Grand Canal vu d'un bateau", 1896),
    ("Escamotage d'une dame au théâtre Robert-Houdin", 1896),
    ("Un homme de têtes", 1898),
    ("La Fée aux choux", 1900),
    ("Grandma's Reading Glass", 1900),
    ("The Big Swallow", 1901),
    ("Le Voyage dans la Lune", 1902),
    ("Le Vol du grand rapide", 1903),
    ("Alice Guy tourne une phonoscène", 1905),
    ("Les Résultats du féminisme", 1906),
]


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


lines = []
lines.append(f"version={pack['version']} movies={len(pack['movies'])} collections={len(pack['collections'])}")
orders = [c["displayOrder"] for c in pack["collections"]]
lines.append(f"displayOrders={sorted(orders)}")
bios = sum(1 for d in pack["directors"] if (d.get("biography") or "").strip())
lines.append(f"directors={len(pack['directors'])} bios={bios}")

early = [m for m in pack["movies"] if (m.get("releaseYear") or 9999) <= 1906]
lines.append(f"films_year_le_1906={len(early)}")
for movie in sorted(early, key=lambda item: (item["releaseYear"], item["code"])):
    lines.append(
        f"EARLY\t{movie['releaseYear']}\t{movie['code']}\t{movie.get('frenchTitle')}\t{movie.get('originalTitle')}"
    )

lines.append("--- MATCH ---")
for title, year in FILMS:
    wanted = fold(title)
    hits = []
    for movie in pack["movies"]:
        titles = [fold(movie.get("frenchTitle") or ""), fold(movie.get("originalTitle") or "")]
        if wanted in titles or any(wanted in item or item in wanted for item in titles if len(item) >= 8 and len(wanted) >= 8):
            delta = abs(int(movie.get("releaseYear") or 0) - year)
            hits.append((delta, movie["code"], movie.get("releaseYear"), movie.get("frenchTitle")))
    hits.sort()
    if not hits:
        lines.append(f"MISS\t{year}\t{title}")
    else:
        for delta, code, got_year, french in hits[:4]:
            lines.append(f"HIT\t{year}\t{title}\t{code}\t{got_year}\tdelta={delta}\t{french}")

posters = root / "app/src/main/assets/media/posters"
directors = root / "app/src/main/assets/media/directors"
lines.append(f"poster_files={len(list(posters.glob('*.jpg')))}")
lines.append(f"director_files={len(list(directors.glob('*.jpg')))}")
catalog_json = (root / "app/src/main/assets/catalog/catalog.json").read_bytes()
catalog_v3 = (root / "app/src/main/assets/catalog/catalog_v3.json").read_bytes()
lines.append(f"files_equal={catalog_json == catalog_v3}")

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out} lines={len(lines)}")
