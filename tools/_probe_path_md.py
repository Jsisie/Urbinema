import json
from pathlib import Path

pack = json.loads(Path("app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
codes = {m["code"] for m in pack["movies"]}
out = []
for path in pack["paths"]:
    for step in path["steps"]:
        missing = [c for c in step["movies"] if c not in codes]
        stars = []
        for fact in step["facts"]:
            if "*" in fact["title"] or "*" in fact["body"]:
                stars.append(fact["title"] + " || " + fact["body"])
        out.append(
            f"{step['code']} movies={len(step['movies'])} missing={len(missing)} facts={len(step['facts'])} figures={len(step['figures'])}"
        )
        for line in stars:
            out.append("  STAR " + line.replace("\n", " "))
        if missing:
            out.append("  MISS " + ", ".join(missing))
Path("tools/output/_path_md.txt").write_text("\n".join(out), encoding="utf-8")
print("ok", len(out))
