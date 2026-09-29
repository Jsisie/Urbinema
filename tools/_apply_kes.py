"""Replace the Kes synopsis with the Ken Loach film overview."""
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
details = client.movie_details(13384, "fr-FR")
french = ""
english = str(details.get("overview") or "").strip()
for block in (details.get("translations") or {}).get("translations") or []:
    lang = str(block.get("iso_639_1") or "")
    text = str((block.get("data") or {}).get("overview") or "").strip()
    if lang == "fr" and len(text) > len(french):
        french = text
    if lang == "en" and len(text) > len(english):
        english = text
chosen = french if len(french) >= 100 else english
note = f"fr={len(french)} en={len(english)} chosen={len(chosen)}\n{chosen[:240]}"
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
pack = json.loads(CATALOG.read_text(encoding="utf-8"))
movie = next(item for item in pack["movies"] if item["code"] == "KES_1969")
if len(chosen) > len(movie.get("synopsis") or ""):
    movie["synopsis"] = chosen
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
    note = "applied\n" + note
else:
    note = "skipped\n" + note
(ROOT / "tools/output/_kes_apply.txt").write_text(note, encoding="utf-8")
print("done")
