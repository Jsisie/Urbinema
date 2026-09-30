import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
FR = (
    "Claire Denis, née le 21 avril 1946 à Paris, est une réalisatrice et scénariste française. "
    "Son cinéma traverse l'Afrique de l'Ouest coloniale et postcoloniale, et la France contemporaine. "
    "Elle a notamment réalisé Chocolat (1988), Beau Travail (1999), souvent cité parmi les grands films "
    "des années 1990, Trouble Every Day (2001), 35 Rhums (2008) et White Material (2009). "
    "High Life (2018) et Avec amour et acharnement (2022) suivent ; ce dernier lui vaut l'Ours d'argent "
    "de la mise en scène à la Berlinale. Pour Stars at Noon (2022), elle reçoit le Grand Prix du Festival "
    "de Cannes, partagé avec Close de Lukas Dhont."
)
pack = json.loads(CATALOG.read_text(encoding="utf-8"))
claire = next(item for item in pack["directors"] if item["code"] == "CLAIRE_DENIS")
claire["biography"] = FR
beau = next(item for item in pack["movies"] if item["code"] == "BEAU_TRAVAIL_1999")
beau["frenchTitle"] = "Beau Travail"
temporary = CATALOG.with_suffix(".json.tmp")
temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(CATALOG)
tmp = COPY.with_suffix(".json.tmp")
shutil.copyfile(CATALOG, tmp)
tmp.replace(COPY)
print("ok", pack["version"], len(FR))
