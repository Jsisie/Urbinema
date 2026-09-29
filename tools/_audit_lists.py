import json
from pathlib import Path
root = Path(r"app/src/main/assets")
pack = json.loads((root / "catalog/catalog_v3.json").read_text(encoding="utf-8"))
posters = root / "media/posters"
movies = {m["code"]: m for m in pack["movies"]}
missing = []
for movie in pack["movies"]:
    if not any((posters / f"{movie['code']}{ext}").exists() for ext in (".jpg", ".png", ".webp")):
        missing.append(f"{movie['code']}|{movie['frenchTitle']}|{movie['releaseYear']}")
print("MISSING")
print("\n".join(missing))
print("---SHARED---")
from collections import defaultdict
membership = defaultdict(list)
for collection in pack["collections"]:
    for ref in collection["movies"]:
        membership[ref["code"]].append(collection["name"])
for code, names in sorted(membership.items(), key=lambda item: movies[item[0]]["frenchTitle"]):
    if len(names) > 1:
        movie = movies[code]
        print(f"{movie['frenchTitle']} ({movie['releaseYear']}) :: {' | '.join(names)}")
