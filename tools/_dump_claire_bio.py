import json
from pathlib import Path

pack = json.loads(Path(r"D:\Programs\Android_Studio\projets\Urbinema\app\src\main\assets\catalog\catalog_v3.json").read_text(encoding="utf-8"))
claire = next(d for d in pack["directors"] if d["code"] == "CLAIRE_DENIS")
Path(r"D:\Programs\Android_Studio\projets\Urbinema\tools\output\_claire_en.txt").write_text(claire.get("biographyEn") or "", encoding="utf-8")
print("len", len(claire.get("biographyEn") or ""))
