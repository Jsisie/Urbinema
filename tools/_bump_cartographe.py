"""Cartographe: 50 countries -> 40. Pack 32."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"

pack = json.loads(CATALOG.read_text(encoding="utf-8"))
badge = next(item for item in pack["badges"] if item["code"] == "007")
if badge["description"] != "Explorer 50 pays.":
    raise SystemExit(f"unexpected description: {badge['description']}")
badge["description"] = "Explorer 40 pays."
pack["version"] = 32
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
shutil.copyfile(CATALOG, COPY)
print("version", pack["version"])
