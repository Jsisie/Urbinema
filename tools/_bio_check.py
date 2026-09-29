import json
import importlib.util
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
spec = importlib.util.spec_from_file_location("merge", root / "tools/_merge_copy.py")
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)
legacy = json.loads((root / "batchsData/batchReals/output/bios.json").read_text(encoding="utf-8"))
langs = json.loads((root / "tools/output/bios_lang.json").read_text(encoding="utf-8"))
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
sample = legacy.get("AKIRA_KUROSAWA")
record = langs.get("AKIRA_KUROSAWA") or {}
lines = [
    f"legacy_type={type(sample).__name__} legacy_len={len(sample) if isinstance(sample, str) else -1}",
    f"legacy_fr={merge.looks_french(sample) if isinstance(sample, str) else None}",
    f"fetch_fr={len(record.get('fr') or '')} fetch_en={len(record.get('en') or '')} status={record.get('status')}",
    f"legacy_keys={len(legacy)} lang_keys={len(langs)}",
]
stripped = merge.strip_wiki(sample) if isinstance(sample, str) else ""
english = merge.strip_wiki(record.get("en") or "")
lines.append(f"stripped_len={len(stripped)} equal_en={stripped == english}")
director = next(item for item in pack["directors"] if item["code"] == "AKIRA_KUROSAWA")
lines.append(
    f"catalog_fr={len(director.get('biography') or '')} catalog_en={len(director.get('biographyEn') or '')}"
)
both = 0
for item in pack["directors"]:
    if item.get("biography") and item.get("biographyEn"):
        both += 1
lines.append(f"catalog_both={both}")
(root / "tools/output/_bio_check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ok")
