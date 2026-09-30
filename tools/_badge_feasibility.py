"""Count catalog coverage for three badges and the country set. Writes UTF-8, prints ASCII."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog.json"
OUT = ROOT / "tools/output/_badge_counts.txt"

pack = json.loads(CATALOG.read_text(encoding="utf-8"))
movies = pack["movies"]
char_meta = {item["code"]: item for item in pack["characteristics"]}
type_name = {item["typeCode"]: item["name"] for item in pack["characteristicTypes"]}
directors = {item["code"]: item["displayName"] for item in pack["directors"]}
countries = pack["countries"]

char_films: dict[str, set[str]] = {}
dir_films: dict[str, set[str]] = {}
primary = Counter()
any_country = Counter()
long_films = []

for movie in movies:
    code = movie["code"]
    for item in movie.get("characteristicCodes") or []:
        char_films.setdefault(item, set()).add(code)
    for item in movie.get("directors") or []:
        dir_films.setdefault(item["code"], set()).add(code)
    prim = next(c["code"] for c in movie["countries"] if c.get("isPrimary"))
    primary[prim] += 1
    for c in movie["countries"]:
        any_country[c["code"]] += 1
    minutes = movie.get("durationMinutes") or 0
    if minutes >= 300:
        long_films.append((minutes, movie.get("frenchTitle") or movie.get("originalTitle"), code))

lines = []
lines.append(f"movies {len(movies)}")
lines.append(f"characteristics defined {len(char_meta)}")
lines.append(f"characteristic types {type_name}")
lines.append("")
lines.append("=== Encyclopedie Vivante: characteristics with N films ===")
lines.append("Badge counts every characteristic on the film, all types, threshold 10, need 30.")


def bucket(counts, label):
    ge10 = [c for c in counts if c >= 10]
    ge15 = [c for c in counts if c >= 15]
    ge20 = [c for c in counts if c >= 20]
    lines.append(
        f"{label}: n={len(counts)} >=10 {len(ge10)} >=15 {len(ge15)} >=20 {len(ge20)}"
    )


by_type: dict[str, list[int]] = {}
rows = []
for code, films in char_films.items():
    meta = char_meta.get(code, {})
    kind = meta.get("typeCode", "?")
    name = meta.get("name", code)
    n = len(films)
    by_type.setdefault(kind, []).append(n)
    rows.append((n, kind, name, code))
rows.sort(reverse=True)
bucket([n for n, _, _, _ in rows], "ALL types actually on films")
for kind, counts in sorted(by_type.items()):
    bucket(counts, f"type {kind} ({type_name.get(kind, kind)})")

# defined but unused
unused = [code for code in char_meta if code not in char_films]
lines.append(f"characteristics with zero films {len(unused)}")
lines.append("")
lines.append("--- characteristics with at least 10 films ---")
for n, kind, name, code in rows:
    if n < 10:
        break
    lines.append(f"{n:4d}  {kind:12s}  {name}")
lines.append("")
lines.append("--- characteristics with 7 to 9 films ---")
for n, kind, name, code in rows:
    if 7 <= n <= 9:
        lines.append(f"{n:4d}  {kind:12s}  {name}")

lines.append("")
lines.append("=== Bibliotheque de Pellicule: directors ===")
dir_counts = sorted(((len(films), directors.get(code, code)) for code, films in dir_films.items()), reverse=True)
for threshold in (10, 8, 7, 6, 5):
    lines.append(f">= {threshold} films: {sum(1 for n, _ in dir_counts if n >= threshold)} directors")
lines.append("--- directors with at least 5 films ---")
for n, name in dir_counts:
    if n < 5:
        break
    lines.append(f"{n:4d}  {name}")

lines.append("")
lines.append("=== Grande Traversee: durationMinutes > 300 (strict, badge) and >= 300 ===")
over = [item for item in long_films if item[0] > 300]
exact = [item for item in long_films if item[0] == 300]
lines.append(f"> 300 min: {len(over)}")
lines.append(f"== 300 min: {len(exact)}")
lines.append(f">= 240 min (4h): {sum(1 for m in movies if (m.get('durationMinutes') or 0) > 240)}")
lines.append(f">= 180 min (3h, Temps suspendu uses > 180): {sum(1 for m in movies if (m.get('durationMinutes') or 0) > 180)}")
for minutes, title, code in sorted(long_films, reverse=True):
    lines.append(f"{minutes:4d} min  {title}  {code}")

lines.append("")
lines.append("=== Pays ===")
defined = {c["code"] for c in countries}
lines.append(f"countries in catalog list: {len(countries)}")
lines.append(f"distinct primary countries on films: {len(primary)}")
lines.append(f"distinct countries on films (primary or co-production): {len(any_country)}")
missing_primary = sorted(defined - set(primary))
lines.append(f"listed countries never primary: {len(missing_primary)}")
for code in missing_primary:
    name = next(c["name"] for c in countries if c["code"] == code)
    lines.append(f"  never primary: {name} ({any_country.get(code, 0)} co-productions)")
orphan = sorted(set(any_country) - defined)
lines.append(f"film countries missing from country list: {orphan}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT.name, "lines", len(lines))
