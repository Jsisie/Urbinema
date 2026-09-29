"""Probe TMDB overviews for the ten films left with a short synopsis."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)
done = json.loads((ROOT / "tools/output/synopses.json").read_text(encoding="utf-8"))
lines = []
payload = {}
for code, row in done.items():
    if row.get("status") != "KEEP" or not str(row.get("tmdbId") or "").isdigit():
        continue
    details = client.movie_details(int(row["tmdbId"]), "en-US")
    overviews = {"default": str(details.get("overview") or "").strip()}
    for block in (details.get("translations") or {}).get("translations") or []:
        lang = str(block.get("iso_639_1") or "")
        if lang not in {"fr", "en"}:
            continue
        text = str((block.get("data") or {}).get("overview") or "").strip()
        if text and len(text) > len(overviews.get(lang, "")):
            overviews[lang] = text
    payload[code] = overviews
    lines.append(
        f"{code}\tdefault={len(overviews.get('default', ''))}\t"
        f"fr={len(overviews.get('fr', ''))}\ten={len(overviews.get('en', ''))}"
    )
(ROOT / "tools/output/_keep_overviews.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "tools/output/_keep_overviews.txt").write_text("\n".join(lines), encoding="utf-8")
print("probed", len(lines))
