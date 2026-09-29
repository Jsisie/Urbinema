"""Replace the short hand-written synopses of the first catalog with TMDB overviews."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from catalog_enrich import french_overview  # noqa: E402
from posters_batch import MovieRow, TmdbClient, load_env, resolve_tmdb  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.2)
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
v1_codes = {
    movie["code"]
    for movie in json.loads((ROOT / "app/src/main/assets/catalog/catalog_v1.json").read_text(encoding="utf-8"))["movies"]
}
directors = {item["code"]: item.get("displayName") or "" for item in pack["directors"]}
out = ROOT / "tools" / "output" / "synopses.json"
done = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
config = {"maxSearchResults": 5, "yearTolerance": 1}
targets = []
for movie in pack["movies"]:
    synopsis = (movie.get("synopsis") or "").strip()
    if movie["code"] not in v1_codes or len(synopsis) >= 160 or movie["code"] in done:
        continue
    names = [directors.get(ref["code"], "") for ref in movie.get("directors") or []]
    targets.append((movie, " & ".join(name for name in names if name), synopsis))

print(f"todo={len(targets)} already={len(done)}", flush=True)
ok = miss = 0
for index, (movie, director, current) in enumerate(targets, start=1):
    row = MovieRow(
        title=movie.get("frenchTitle") or movie.get("originalTitle") or "",
        year=int(movie.get("releaseYear") or 0),
        director=director,
        code=movie["code"],
        original_title=movie.get("originalTitle") or "",
    )
    try:
        details, tmdb_id = resolve_tmdb(client, row, config)
    except Exception as exc:
        done[movie["code"]] = {"status": "ERROR", "error": str(exc)}
        miss += 1
        continue
    overview = french_overview(details) if details else ""
    if overview and len(overview) > len(current) and len(overview) >= 80:
        done[movie["code"]] = {"status": "OK", "tmdbId": tmdb_id, "synopsis": overview}
        ok += 1
    else:
        done[movie["code"]] = {"status": "KEEP", "tmdbId": tmdb_id}
        miss += 1
    if index % 20 == 0:
        out.write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"progress={index} ok={ok} miss={miss}", flush=True)

out.write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"done ok={ok} miss={miss} stored={len(done)}", flush=True)
