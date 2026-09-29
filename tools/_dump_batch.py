import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
data = json.loads((root / "batchPosters/output/catalog/movies_collections.json").read_text(encoding="utf-8"))
names = {item["code"]: item.get("displayName") for item in data.get("newDirectors") or []}
lines = []
for movie in data["movies"]:
    people = []
    for ref in movie.get("directors") or []:
        people.append(names.get(ref["code"], ref["code"]))
    countries = ",".join(c["code"] for c in movie.get("countries") or [])
    lines.append(
        f"{movie['code']}\t{movie.get('releaseYear')}\t{movie.get('frenchTitle')}\t{movie.get('originalTitle')}\t{', '.join(people)}\t{countries}"
    )
(root / "tools/output/_batch_collections.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines))
