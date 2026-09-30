import json
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((root / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
copy = json.loads((root / "app/src/main/assets/catalog/catalog.json").read_text(encoding="utf-8"))
claire = next(d for d in pack["directors"] if d["code"] == "CLAIRE_DENIS")
print("same", pack == copy, "version", pack["version"])
print("FR", (claire.get("biography") or "").encode("ascii", "replace").decode("ascii"))
print("EN", (claire.get("biographyEn") or "")[:240].encode("ascii", "replace").decode("ascii"))
photo = root / "app/src/main/assets/media/directors/CLAIRE_DENIS.jpg"
print("photo", photo.is_file(), photo.stat().st_size if photo.is_file() else 0)
codes = [
    "L_HORLOGER_DE_SAINT_PAUL_1974",
    "LA_MORT_EN_DIRECT_1980",
    "COUP_DE_TORCHON_1981",
    "L_627_1992",
    "MADEMOISELLE_2016",
    "SYMPATHY_FOR_MR_VENGEANCE_2002",
    "JE_VEUX_JUSTE_EN_FINIR_2020",
    "CHOCOLAT_1988",
    "WHITE_MATERIAL_2009",
    "POLYTECHNIQUE_2009",
    "LA_SAISON_DES_GOYAVES_2000",
    "BEAU_TRAVAIL_1999",
    "35_SHOTS_OF_RUM_2008",
    "TROUBLE_EVERY_DAY_2001",
]
movies = {m["code"]: m for m in pack["movies"]}
for code in codes:
    movie = movies[code]
    title = (movie.get("frenchTitle") or "").encode("ascii", "replace").decode("ascii")
    dirs = ",".join(i["code"] for i in movie["directors"])
    chars = ",".join(movie.get("characteristicCodes") or [])
    primary = next(c["code"] for c in movie["countries"] if c["isPrimary"])
    poster = (root / "app/src/main/assets/media/posters" / f"{code}.jpg").is_file()
    bw = movie.get("isBlackAndWhite")
    print(f"{code}|{movie['releaseYear']}|{title}|{dirs}|{primary}|{chars}|bw={bw}|poster={poster}|syn={len(movie.get('synopsis') or '')}")
badge = next(b for b in pack["badges"] if b["code"] == "032")
print("badge", badge["description"].encode("ascii", "replace").decode("ascii"))
