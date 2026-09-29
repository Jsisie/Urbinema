"""Ajoute le courant Cinéma documentaire, distinct du genre homonyme."""

import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog = root / "app/src/main/assets/catalog/catalog_v3.json"
pack = json.loads(catalog.read_text(encoding="utf-8"))
if not any(item["code"] == "DOCUMENTAIRE" for item in pack["characteristics"]):
    pack["characteristics"].append(
        {
            "code": "DOCUMENTAIRE",
            "name": "Cinéma documentaire",
            "typeCode": "STYLE",
            "description": "Le réel comme sujet : enquête, portrait ou essai, plutôt que le reportage illustré.",
        }
    )
movies = {item["code"]: item for item in pack["movies"]}
collection = next(item for item in pack["collections"] if item["code"] == "COLLECTION_025")
for ref in collection["movies"]:
    movie = movies[ref["code"]]
    codes = movie.setdefault("characteristicCodes", [])
    if "DOCUMENTAIRE" not in codes:
        codes.append("DOCUMENTAIRE")
temporary = catalog.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(catalog)
shutil.copyfile(catalog, root / "app/src/main/assets/catalog/catalog.json")
print(f"doc_films={len(collection['movies'])} chars={len(pack['characteristics'])}")
