"""Drop leftover Wikipedia attributions at the end of director biographies."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
ATTRIB = re.compile(
    r"(wikip[eé]dia|from wikipedia|\[wikipedia\]|- ?wikipedia|"
    r"source\s*:\s*(https://\S*wikipedia|wikipedia)|"
    r"description (ci-dessus|above from)|"
    r"extrait de wikip|courtesy wikipedia|contributeurs de wikip|"
    r"text under cc-by-sa|encyclop[eé]die libre)",
    re.I,
)


def strip_wiki(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").replace("\u200b", "")
    cleaned = re.sub(r"(?i)from wikipedia, the free encyclopedia\.?", "", cleaned)
    cleaned = re.sub(r"(?i)description above from the wikipedia article[^\n]*", "", cleaned)
    cleaned = re.sub(r"(?im)^\s*from wikipedia\.?\s*$", "", cleaned)
    match = None
    for found in ATTRIB.finditer(cleaned):
        match = found
    if match and match.start() >= max(0, len(cleaned) - 400):
        cleaned = cleaned[: match.start()]
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip(" \n\t.-–—:;,")
    if ATTRIB.search(cleaned) and len(cleaned) < 280:
        return ""
    return cleaned.strip()


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    changed = 0
    for director in pack["directors"]:
        for field in ("biography", "biographyEn"):
            current = director.get(field) or ""
            cleaned = strip_wiki(current)
            if cleaned != current:
                changed += 1
                if cleaned:
                    director[field] = cleaned
                else:
                    director.pop(field, None)
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
    print(f"changed={changed}")


if __name__ == "__main__":
    main()
