"""Ajoute Fantômas à la collection muette et recopie le pack importé."""

import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog = root / "app/src/main/assets/catalog/catalog_v3.json"
pack = json.loads(catalog.read_text(encoding="utf-8"))
movies = {item["code"]: item for item in pack["movies"]}
muet = next(item for item in pack["collections"] if item["code"] == "COLLECTION_012")
codes = [ref["code"] for ref in muet["movies"]]
if "FANTOMAS_1913" not in codes:
    codes.append("FANTOMAS_1913")
ranked = sorted(codes, key=lambda code: (int(movies[code]["releaseYear"]), code))
muet["movies"] = [{"code": code, "displayOrder": index + 1} for index, code in enumerate(ranked)]
temporary = catalog.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(catalog)
shutil.copyfile(catalog, root / "app/src/main/assets/catalog/catalog.json")
print(f"muet={len(muet['movies'])} first={muet['movies'][0]['code']} movies={len(pack['movies'])}")
