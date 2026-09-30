"""List films on the three British-wave tags, plus the horror titles to fix."""
import json
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
dirs = {d["code"]: d["displayName"] for d in pack["directors"]}
chars = {c["code"]: c["name"] for c in pack["characteristics"]}
watch = {
    "BRITISH_NEW_WAVE",
    "FREE_CINEMA",
    "NOUVELLE_VAGUE_BRITANNIQUE",
}
needles = (
    "peur", "voyeur", "innocent", "loup", "shaun", "intruder", "indringer",
    "trouble every", "cure", "chasseur", "repulsion", "répulsion", "colline",
    "possession", "santa sangre", "vampyr", "diabolique", "lèvres", "levres",
    "malpertuis", "angst", "faux-semblant", "november",
)
lines = ["=== characteristics ==="]
for code, name in chars.items():
    if any(token in (code + " " + name).lower() for token in (
        "free", "british", "kitchen", "goth", "horror", "gore", "j-horror",
        "jidai", "extrem", "look", "surreal", "latino", "belg", "flamand",
        "thriller", "neo-noir", "neo_noir", "psycholog", "body", "cronenberg",
        "avant", "muet", "clouzot", "suspense", "folk", "magique", "erotique",
        "erotique", "gothique", "transgress", "baroque", "survie", "survival",
        "independant", "canadien", "autrich", "estonien", "auteur",
    )):
        lines.append(f"{code} = {name}")

lines.append("")
lines.append("=== tagged films ===")
for movie in pack["movies"]:
    codes = set(movie.get("characteristicCodes") or [])
    title = (movie.get("frenchTitle") or movie.get("originalTitle") or "").lower()
    hit = codes & watch or any(n in title for n in needles)
    if not hit:
        continue
    names = ", ".join(dirs.get(d["code"], d["code"]) for d in movie.get("directors") or [])
    shown = ", ".join(chars.get(c, c) for c in movie.get("characteristicCodes") or [])
    genres = ", ".join(movie.get("genreCodes") or [])
    lines.append(
        f"{movie['code']} | {movie.get('frenchTitle')} | {movie['releaseYear']} | {names} | {genres} | {shown}"
    )

# references outside movies
blob_keys = ("collections", "paths", "directors")
lines.append("")
lines.append("=== other refs ===")
for director in pack["directors"]:
    if "BRITISH_NEW_WAVE" in (director.get("characteristicCodes") or []):
        lines.append(f"director {director['code']} {director['displayName']}")
for col in pack.get("collections") or []:
    if "BRITISH_NEW_WAVE" in (col.get("characteristicCodes") or []):
        lines.append(f"collection {col['code']} {col['name']}")
for path in pack.get("paths") or []:
    for step in path.get("steps") or []:
        if step.get("characteristicCode") == "BRITISH_NEW_WAVE":
            lines.append(f"path step {step['code']}")

out = ROOT / "tools/output/_free_cinema.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("lines", len(lines))
