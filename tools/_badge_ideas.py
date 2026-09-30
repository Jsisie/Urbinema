"""Catalog coverage for unused badge axes. UTF-8 file, ASCII console."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog.json").read_text(encoding="utf-8"))
movies = pack["movies"]
genres = {g["code"]: g["name"] for g in pack["genres"]}
continents = {c["code"]: c["name"] for c in pack["continents"]}
country_continent = {c["code"]: c.get("continentCodes") or [] for c in pack["countries"]}
country_name = {c["code"]: c["name"] for c in pack["countries"]}

lines = [f"movies {len(movies)} version {pack['version']}"]

fmt = Counter(m["format"] for m in movies)
lines.append("formats " + ", ".join(f"{k} {v}" for k, v in fmt.most_common()))
lines.append(f"silent {sum(1 for m in movies if m.get('isSilent'))}")
lines.append(f"bw {sum(1 for m in movies if m.get('isBlackAndWhite'))}")
lines.append(f"experimental {sum(1 for m in movies if m.get('isExperimental'))}")
lines.append(f"copro {sum(1 for m in movies if len(m.get('countries') or []) > 1)}")
lines.append(f"multi director {sum(1 for m in movies if len(m.get('directors') or []) > 1)}")
lines.append(f"under 40 min {sum(1 for m in movies if (m.get('durationMinutes') or 0) < 40)}")
lines.append(f"under 60 min {sum(1 for m in movies if (m.get('durationMinutes') or 0) < 60)}")
lines.append(f"year >= 2000 {sum(1 for m in movies if m['releaseYear'] >= 2000)}")
lines.append(f"year >= 2010 {sum(1 for m in movies if m['releaseYear'] >= 2010)}")
lines.append(f"year >= 1990 {sum(1 for m in movies if m['releaseYear'] >= 1990)}")
lines.append(f"year < 1930 {sum(1 for m in movies if m['releaseYear'] < 1930)}")

genre_n = Counter()
for m in movies:
    for code in m.get("genreCodes") or []:
        genre_n[code] += 1
lines.append("")
lines.append("--- genres ---")
for code, n in genre_n.most_common():
    lines.append(f"{n:4d}  {genres.get(code, code)}")

cont_n = Counter()
for m in movies:
    primary = next(c["code"] for c in m["countries"] if c.get("isPrimary"))
    for cont in country_continent.get(primary, []):
        cont_n[cont] += 1
lines.append("")
lines.append("--- primary continent ---")
for code, n in cont_n.most_common():
    lines.append(f"{n:4d}  {continents.get(code, code)}")

# countries with few films
primary = Counter()
for m in movies:
    primary[next(c["code"] for c in m["countries"] if c.get("isPrimary"))] += 1
rare = [(n, country_name.get(c, c)) for c, n in primary.items() if n <= 3]
lines.append("")
lines.append(f"primary countries with 1-3 films: {len(rare)}")
lines.append(f"primary countries with exactly 1: {sum(1 for n, _ in rare if n == 1)}")

canon = {"USA", "FRANCE", "ITALY", "JAPAN", "UNITED_KINGDOM", "UK", "GERMANY"}
# detect UK code
lines.append("country codes sample " + ", ".join(sorted(country_name)[:8]))
outside = 0
for m in movies:
    primary_code = next(c["code"] for c in m["countries"] if c.get("isPrimary"))
    if primary_code not in {"USA", "FRANCE", "ITALY", "JAPAN", "UNITED_KINGDOM", "GERMANY", "GBR"}:
        outside += 1
lines.append(f"primary not US/FR/IT/JP/UK/DE: {outside}")

# africa / latam / middle east by continent codes present
lines.append("continent codes " + ", ".join(f"{k}={v}" for k, v in continents.items()))

collections = []
for col in pack.get("collections") or []:
    collections.append((len(col.get("movies") or []), col.get("name")))
collections.sort(reverse=True)
lines.append("")
lines.append(f"collections {len(collections)}")
for n, name in collections:
    lines.append(f"{n:4d}  {name}")

# bw that are not silent
lines.append(f"bw and not silent {sum(1 for m in movies if m.get('isBlackAndWhite') and not m.get('isSilent'))}")
lines.append(f"sound color {sum(1 for m in movies if not m.get('isBlackAndWhite') and not m.get('isSilent'))}")

# decades
dec = Counter(m["releaseYear"] // 10 * 10 for m in movies)
lines.append("")
lines.append("--- decades ---")
for year in sorted(dec):
    lines.append(f"{year}  {dec[year]}")

out = ROOT / "tools/output/_badge_ideas.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("lines", len(lines))
