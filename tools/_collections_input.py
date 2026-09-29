import re
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
text = (root / "tools/output/_coll_match.txt").read_text(encoding="utf-8")
skip = {
    "Days of Being Wild",
    "Le Bal des pompiers",
    "Le Cerf-volant bleu",
    "Harlan County War",
    "Fallen Angels",
}
extra_directors = {
    "Fantomas": "Louis Feuillade",
}

def slug(title: str, year: str) -> str:
    folded = re.sub(r"[^A-Za-z0-9]+", "_", title)
    folded = re.sub(r"_+", "_", folded).strip("_").upper()
    return f"{folded[:60]}_{year}"

lines = ["frenchTitle;releaseYear;director;code;originalTitle"]
count = 0
for raw in text.splitlines():
    if not raw.startswith("MISS\t"):
        continue
    parts = raw.split("\t")
    year, title, director = parts[1], parts[2], parts[3]
    if title in skip:
        continue
    director = extra_directors.get(title, director).replace(" et ", " & ")
    def cell(value: str) -> str:
        return '"' + value.replace('"', "'") + '"'
    lines.append(";".join([cell(title), year, cell(director), slug(title, year), cell(title)]))
    count += 1
path = root / "batchPosters/input/input_collections.txt"
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("to_fetch", count)
