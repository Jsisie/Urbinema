"""Affiche réalisateur et année TMDB des fiches encore refusées."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "batchsData/batchPosters"))
from posters_batch import TmdbClient, load_env  # noqa: E402

IDS = {
    "THE_SPOOKY_BUNCH_1980": 104681,
    "THE_SECRET_1979": 176219,
    "THE_CLUB_1981": 170319,
    "NOMAD_1982": 157229,
    "L_INCIDENT_DU_CANON_NOIR_1985": 176643,
}


def main() -> None:
    load_env(ROOT / "batchsData/batchPosters" / ".env")
    client = TmdbClient(os.environ.get("TMDB_API_KEY") or "", os.environ.get("TMDB_ACCESS_TOKEN") or "", 0.1)
    lines = []
    for code, movie_id in IDS.items():
        details = client.movie_details(movie_id, "en-US")
        crew = (details.get("credits") or {}).get("crew") or []
        directors = [f"{person.get('name')}|{person.get('job')}" for person in crew if person.get("job") == "Director"]
        lines.append(
            f"{code} {details.get('title')} | {details.get('original_title')} | {details.get('release_date')} | {directors}"
        )
    (ROOT / "tools/output/_id_check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
