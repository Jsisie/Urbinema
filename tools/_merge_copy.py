"""Apply badge copy, cleaned biographies and refreshed synopses. Pack 28."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"

BADGES = {
    "002": "Voir 20 films.",
    "003": "Voir 100 films.",
    "004": "Voir 300 films.",
    "015": "Voir 40 films sortis avant 1950.",
    "016": "Voir 100 films sortis avant 1960.",
    "017": "Voir 300 films sortis avant 1980.",
    "018": "Voir 20 films muets.",
    "020": "Voir un film de chaque décennie, de 1890 à 2020.",
    "027": "Voir 20 films de plus de trois heures.",
}
FOOTER = re.compile(
    r"(source\s*:\s*article\b.*wikip|"
    r"description (de l'article ci-dessus|above from the wikipedia)|"
    r"licensed under cc-by-sa.*wikipedia|"
    r"^©\s*wikip|"
    r"traduit avec www\.deepl\.com)",
    re.I,
)


def strip_wiki(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").strip()
    parts = re.split(r"\n\s*\n", cleaned)
    while parts:
        lines = parts[-1].split("\n")
        changed = False
        while lines and FOOTER.search(lines[-1].strip()):
            lines.pop()
            changed = True
        if lines and not changed and FOOTER.search(parts[-1]):
            parts.pop()
            continue
        rebuilt = "\n".join(lines).strip()
        if not rebuilt:
            parts.pop()
            continue
        parts[-1] = rebuilt
        break
    return "\n\n".join(part.strip() for part in parts if part.strip()).strip()


def looks_french(text: str) -> bool:
    sample = f" {text[:500].lower()} "
    french = sum(sample.count(word) for word in (" le ", " la ", " les ", " est ", " une ", " des ", " et "))
    english = sum(sample.count(word) for word in (" the ", " and ", " was ", " born ", " his ", " her "))
    return french >= english


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    synopses_path = ROOT / "tools/output/synopses.json"
    bios_path = ROOT / "tools/output/bios_lang.json"
    legacy_path = ROOT / "batchsData/batchReals/output/bios.json"
    synopses = json.loads(synopses_path.read_text(encoding="utf-8")) if synopses_path.is_file() else {}
    bios = json.loads(bios_path.read_text(encoding="utf-8")) if bios_path.is_file() else {}
    legacy = json.loads(legacy_path.read_text(encoding="utf-8")) if legacy_path.is_file() else {}

    replaced = 0
    for movie in pack["movies"]:
        record = synopses.get(movie["code"]) or {}
        text = (record.get("synopsis") or "").strip()
        if record.get("status") == "OK" and len(text) > len(movie.get("synopsis") or ""):
            movie["synopsis"] = text
            replaced += 1

    both = fr_only = en_only = 0
    for director in pack["directors"]:
        record = bios.get(director["code"]) or {}
        french = strip_wiki(record.get("fr") or "")
        english = strip_wiki(record.get("en") or "")
        previous = strip_wiki(legacy.get(director["code"]) or "")
        if isinstance(legacy.get(director["code"]), dict):
            previous = ""
        if previous and previous not in {french, english}:
            if looks_french(previous) and not french:
                french = previous
            elif not looks_french(previous) and not english:
                english = previous
        if not french and not english:
            current = strip_wiki(director.get("biography") or "")
            if current and looks_french(current):
                french = current
            elif current:
                english = current
        if french:
            director["biography"] = french
        else:
            director.pop("biography", None)
        if english and english != french:
            director["biographyEn"] = english
        else:
            director.pop("biographyEn", None)
        if french and english and english != french:
            both += 1
        elif french:
            fr_only += 1
        elif english:
            en_only += 1

    for badge in pack["badges"]:
        if badge["code"] in BADGES:
            badge["description"] = BADGES[badge["code"]]

    pack["version"] = 28
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
    print(
        f"version=28 synopses={replaced} bios_both={both} fr_only={fr_only} en_only={en_only}"
    )


if __name__ == "__main__":
    main()
