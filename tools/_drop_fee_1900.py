"""Drop the 1900 Fée aux choux duplicate and keep the 1896 film in the collection."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
REMOVED = "LA_FEE_AUX_CHOUX_1900"
KEPT = "LA_FEE_AUX_CHOUX_1896"

pack = json.loads(CATALOG.read_text(encoding="utf-8"))
before = len(pack["movies"])
pack["movies"] = [movie for movie in pack["movies"] if movie["code"] != REMOVED]
if len(pack["movies"]) != before - 1:
    raise SystemExit(f"expected to remove one movie, removed {before - len(pack['movies'])}")
if not any(movie["code"] == KEPT and any(ref["code"] == "ALICE_GUY" for ref in movie["directors"]) for movie in pack["movies"]):
    raise SystemExit("1896 film missing or not Alice Guy")

collection = next(item for item in pack["collections"] if item["code"] == "COLLECTION_027")
codes = [item["code"] for item in collection["movies"]]
if REMOVED not in codes:
    raise SystemExit("1900 film not in the collection")
index = codes.index(REMOVED)
codes[index] = KEPT
# Place the 1896 film just after the other 1896 titles and before 1898.
codes.remove(KEPT)
anchor = codes.index("ESCAMOTAGE_D_UNE_DAME_1896")
codes.insert(anchor + 1, KEPT)
if len(codes) != len(set(codes)):
    raise SystemExit("duplicate film in collection")
collection["movies"] = [{"code": code, "displayOrder": order} for order, code in enumerate(codes, start=1)]

aliases = pack.setdefault("movieAliases", [])
if not any(item.get("from") == REMOVED for item in aliases):
    aliases.append({"from": REMOVED, "to": KEPT})

pack["version"] = 27
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")

poster = ROOT / "app/src/main/assets/media/posters/LA_FEE_AUX_CHOUX_1900.jpg"
if poster.is_file():
    poster.unlink()

print(
    f"version={pack['version']} movies={len(pack['movies'])} "
    f"collection={len(collection['movies'])} order={codes.index(KEPT) + 1}"
)
