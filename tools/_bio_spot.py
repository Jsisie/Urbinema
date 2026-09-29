"""Spot-check bios and short synopses after the Wikipedia strip."""
import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
out = []
out.append(f"version={pack.get('version')} movies={len(pack['movies'])} directors={len(pack['directors'])}")

both = fr_only = en_only = none = 0
short = []
for director in pack["directors"]:
    fr = (director.get("biography") or "").strip()
    en = (director.get("biographyEn") or "").strip()
    if fr and en:
        both += 1
    elif fr:
        fr_only += 1
    elif en:
        en_only += 1
    else:
        none += 1
    for field, text in (("biography", fr), ("biographyEn", en)):
        if text and len(text) < 40:
            short.append(f"{director['code']}\t{field}\t{len(text)}\t{text[:80]}")
out.append(f"bios_both={both} fr_only={fr_only} en_only={en_only} none={none} tiny={len(short)}")

wanted = {
    "AKIRA_KUROSAWA",
    "FRANCIS_FORD_COPPOLA",
    "MIKE_NICHOLS",
    "CHING_SIU_TUNG",
}
by_code = {d["code"]: d for d in pack["directors"]}
for code in wanted:
    director = by_code.get(code)
    if not director:
        out.append(f"MISSING {code}")
        continue
    for field in ("biography", "biographyEn"):
        text = director.get(field) or ""
        tail = text[-180:].replace("\n", " | ")
        head = text[:120].replace("\n", " | ")
        out.append(f"{code}\t{field}\tlen={len(text)}\thead={head}\ttail={tail}")

movie = next(m for m in pack["movies"] if "EMPORTE" in m["code"] or "GONE_WITH" in m["code"] or "AUTANT" in m["code"])
out.append(f"film={movie['code']} syn_len={len(movie.get('synopsis') or '')}")
out.append((movie.get("synopsis") or "")[:400])

badges = {b["code"]: b.get("description") for b in pack.get("badges", [])}
for code in ("002", "003", "004", "015", "016", "017", "018", "020", "027"):
    out.append(f"badge {code}: {badges.get(code)}")

(root / "tools/output/_bio_spot.txt").write_text("\n".join(out) + "\n" + "\n".join(short[:30]), encoding="utf-8")
print("wrote")
