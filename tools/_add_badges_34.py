"""Six badges, pack 34."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"

NEW = [
    ("033", "Argentique", "Voir 50 films en noir et blanc non muets.", 3, "FORM"),
    ("034", "En une bobine", "Voir 30 courts métrages.", 4, "FORM"),
    ("035", "Le Réel", "Voir 20 documentaires.", 3, "GENRE"),
    ("036", "Lumière d'Afrique", "Voir 20 films issus du continent Africain.", 4, "COUNTRY"),
    ("037", "Notre siècle", "Voir 50 films sortis depuis 2000.", 2, "TIME"),
    ("038", "Image par image", "Voir 20 films d'animation.", 4, "GENRE"),
]

pack = json.loads(CATALOG.read_text(encoding="utf-8"))
existing = {item["code"] for item in pack["badges"]}
for code, name, description, difficulty, category in NEW:
    if code in existing:
        raise SystemExit(f"badge already present {code}")
    pack["badges"].append({
        "code": code,
        "name": name,
        "description": description,
        "difficulty": difficulty,
        "category": category,
    })
pack["version"] = 34
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
shutil.copyfile(CATALOG, COPY)
print("badges", len(pack["badges"]), "version", pack["version"])
