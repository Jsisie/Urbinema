import json
import re
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
lines = []
pattern = re.compile(r".{0,80}(Wikip[eé]dia|Wikipedia article|©Wikipedia).{0,80}", re.I)
for director in pack["directors"]:
    for field in ("biography", "biographyEn"):
        text = director.get(field) or ""
        found = pattern.search(text)
        if found:
            lines.append(f"{director['code']}\t{field}\t{found.group(0).replace(chr(10), ' ')}")
(root / "tools/output/_wiki_left.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines))
