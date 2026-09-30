"""Argentique threshold text: 40. Pack 35."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
pack = json.loads(CATALOG.read_text(encoding="utf-8"))
badge = next(item for item in pack["badges"] if item["code"] == "033")
badge["description"] = "Voir 40 films en noir et blanc non muets."
pack["version"] = 35
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
shutil.copyfile(CATALOG, COPY)
print("version", pack["version"])
