"""Fill the ten leftover short synopses when TMDB actually describes the film."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
overviews = json.loads((ROOT / "tools/output/_keep_overviews.json").read_text(encoding="utf-8"))

notes = []


def longest(block: dict, *keys: str) -> str:
    texts = [str(block.get(key) or "").strip() for key in keys]
    return max(texts, key=len)


# Kes 79243 is another film. Search the Ken Loach feature.
kes_hits = client.search_movie("Kes", 1969, "en-US")
kes_choice = None
for hit in kes_hits[:8]:
    title = str(hit.get("title") or hit.get("original_title") or "")
    year = str(hit.get("release_date") or "")[:4]
    overview = str(hit.get("overview") or "")
    notes.append(f"kes_hit\t{hit.get('id')}\t{year}\t{title}\t{len(overview)}")
    if title.lower() == "kes" and year == "1969" and len(overview) >= 80:
        kes_choice = overview
        break
if kes_choice:
    overviews["KES_1969"] = {"en": kes_choice, "fr": ""}

berlin_payload = client.request_json(
    "/search/tv",
    {"query": "Berlin Alexanderplatz", "first_air_date_year": "1980", "language": "fr-FR"},
)
for hit in (berlin_payload.get("results") or [])[:5]:
    name = str(hit.get("name") or hit.get("original_name") or "")
    year = str(hit.get("first_air_date") or "")[:4]
    overview = str(hit.get("overview") or "")
    notes.append(f"berlin_hit\t{hit.get('id')}\t{year}\t{name}\t{len(overview)}")
    if "alexanderplatz" in name.lower() and len(overview) >= 80:
        overviews["BERLIN_ALEXANDERPLATZ_1980"] = {"fr": overview, "en": ""}
        break

# Known wrong movie matches: do not keep their overviews unless replaced above.
skip_unless_replaced = {"KES_1969", "BERLIN_ALEXANDERPLATZ_1980"}

CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
pack = json.loads(CATALOG.read_text(encoding="utf-8"))
by_code = {movie["code"]: movie for movie in pack["movies"]}
changed = []
for code, block in overviews.items():
    french = str(block.get("fr") or "").strip()
    english = str(block.get("en") or block.get("default") or "").strip()
    if code in skip_unless_replaced and code not in changed:
        # Only accept a text written by the search above, which replaced the block.
        pass
    chosen = french if len(french) >= 100 else english
    if len(chosen) < 80:
        notes.append(f"skip\t{code}\tfr={len(french)}\ten={len(english)}")
        continue
    # Reject the two known false matches if the search did not replace them.
    if code == "KES_1969" and "serum" in chosen.lower():
        notes.append("skip\tKES wrong match")
        continue
    if code == "BERLIN_ALEXANDERPLATZ_1980" and "making of" in chosen.lower():
        notes.append("skip\tBERLIN making-of")
        continue
    movie = by_code[code]
    current = (movie.get("synopsis") or "").strip()
    if len(chosen) <= len(current):
        notes.append(f"skip\t{code}\tnot longer")
        continue
    movie["synopsis"] = chosen
    changed.append(f"{code}\t{len(current)}->{len(chosen)}")

temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
import shutil
shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
(ROOT / "tools/output/_keep_apply.txt").write_text(
    "\n".join(changed + notes), encoding="utf-8"
)
print(f"changed={len(changed)}")
