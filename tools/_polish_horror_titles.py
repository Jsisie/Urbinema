"""Restore the French titles from the horror input, and credit Hawks on The Thing."""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
INPUT = ROOT / "batchsData/batchPosters/input/input_horror.txt"


def main() -> None:
    with INPUT.open(encoding="utf-8", newline="") as handle:
        wanted = {row["code"]: row["frenchTitle"] for row in csv.DictReader(handle, delimiter=";")}
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    changed = 0
    for movie in pack["movies"]:
        title = wanted.get(movie["code"])
        if title and movie.get("frenchTitle") != title:
            movie["frenchTitle"] = title
            changed += 1
        if movie["code"] == "LA_CHOSE_D_UN_AUTRE_MONDE_1951":
            codes = [item["code"] for item in movie["directors"]]
            if "HOWARD_HAWKS" not in codes:
                movie["directors"].append({"code": "HOWARD_HAWKS", "billingOrder": len(movie["directors"])})
                changed += 1
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY.with_suffix(".json.tmp"))
    COPY.with_suffix(".json.tmp").replace(COPY)
    print("changed", changed, "version", pack["version"])


if __name__ == "__main__":
    main()
