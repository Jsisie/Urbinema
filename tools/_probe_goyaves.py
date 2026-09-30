import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
from posters_batch import TmdbClient, fold, load_env  # noqa: E402

load_env(ROOT / "batchsData/batchPosters/.env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.05)
for query in ["The Guava Season", "Guava Season", "Mua oi", "Saison des goyaves", "Season of Guavas"]:
    payload = client.request_json("/search/movie", {"query": query, "language": "en-US", "page": "1"})
    print("Q", query.encode("ascii", "replace").decode("ascii"), "n", len(payload.get("results") or []))
    for item in (payload.get("results") or [])[:6]:
        title = str(item.get("title") or "").encode("ascii", "replace").decode("ascii")
        original = str(item.get("original_title") or "").encode("ascii", "replace").decode("ascii")
        print(" ", item.get("id"), item.get("release_date"), title, "|", original)
