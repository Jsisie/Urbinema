"""Contrôles structurels du pack après l'ajout des collections."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
posters = ROOT / "app/src/main/assets/media/posters"
lines = []
country_codes = {item["code"] for item in pack["countries"]}
used = set()
problems = []
for movie in pack["movies"]:
    countries = movie.get("countries") or []
    primaries = [item for item in countries if item.get("isPrimary")]
    if len(primaries) != 1 or not (1 <= len(countries) <= 2):
        problems.append(f"COUNTRY {movie['code']} {countries}")
    for item in countries:
        used.add(item["code"])
        if item["code"] not in country_codes:
            problems.append(f"UNKNOWN_COUNTRY {movie['code']} {item['code']}")
    directors = movie.get("directors") or []
    if not directors or any(item["code"] == "DIRECTOR" for item in directors):
        problems.append(f"DIRECTOR {movie['code']}")
if used != country_codes:
    problems.append(f"USED_DIFF extra={sorted(country_codes-used)} missing={sorted(used-country_codes)}")
orders = [item["displayOrder"] for item in pack["collections"]]
if len(orders) != len(set(orders)):
    problems.append("DUP_DISPLAY")
by_code = {item["code"]: item for item in pack["movies"]}
directors = {item["code"]: item.get("displayName") for item in pack["directors"]}
for collection in pack["collections"]:
    years = [by_code[ref["code"]]["releaseYear"] for ref in collection["movies"]]
    if years != sorted(years):
        problems.append(f"YEAR_ORDER {collection['code']} {collection['name']}")
    if len({ref["code"] for ref in collection["movies"]}) != len(collection["movies"]):
        problems.append(f"DUP_FILM {collection['code']}")
muet = next(item for item in pack["collections"] if item["code"] == "COLLECTION_012")
muet_codes = [ref["code"] for ref in muet["movies"]]
for banned in ("LA_SORTIE_DES_USINES_LUMIERE_1895", "L_ARRIVEE_D_UN_TRAIN_1896", "LA_FEE_AUX_CHOUX_1896", "VOYAGE_DANS_LA_LUNE_1902", "LE_VOL_DU_GRAND_RAPIDE_1903"):
    if banned in muet_codes:
        problems.append(f"MUET_STILL {banned}")
if "FANTOMAS_1913" not in muet_codes or "LES_VAMPIRES_1915" not in muet_codes:
    problems.append("MUET_MISSING")
if "Méliès" in muet["longDescription"] or "Avant 1930" in muet["longDescription"] or "Lune" in muet["longDescription"]:
    problems.append("MUET_TEXT")
hitch = next(item for item in pack["collections"] if item["code"] == "COLLECTION_017")
if hitch["name"] != "Hitchcock — Le suspense comme forme":
    problems.append(f"HITCH {hitch['name']}")
empire = by_code["EMPIRE_1964"]
if "romain" not in empire["frenchTitle"].casefold() and "empire" not in empire["frenchTitle"].casefold():
    problems.append(f"EMPIRE_ROMAN {empire['frenchTitle']}")
warhol = by_code.get("EMPIRE_WARHOL_1964")
if warhol is None or directors[warhol["directors"][0]["code"]] != "Andy Warhol":
    problems.append("WARHOL")
checks = {
    "THE_SECRET_1979": "Ann Hui",
    "THE_SPOOKY_BUNCH_1980": "Ann Hui",
    "THE_CLUB_1981": "Kirk Wong",
    "NOMAD_1982": "Patrick Tam",
    "POLICE_STORY_1985": "Jackie Chan",
    "PEDICAB_DRIVER_1989": "Sammo Hung",
    "THE_EXTRAS_1978": "Yim Ho",
    "NIGHT_MAIL_1936": "Basil Wright",
    "BULLET_IN_THE_HEAD_1990": "John Woo",
    "L_INCIDENT_DU_CANON_NOIR_1985": "Huang Jianxin",
}
for code, name in checks.items():
    movie = by_code[code]
    names = [directors[item["code"]] for item in movie["directors"]]
    primary = next(item["code"] for item in movie["countries"] if item["isPrimary"])
    poster = (posters / f"{code}.jpg").exists()
    if name not in names:
        problems.append(f"BAD_DIRECTOR {code} {names}")
    lines.append(f"{code} dir={names} primary={primary} poster={poster} year={movie['releaseYear']}")
new_codes = [
    "O_DREAMLAND_1953", "FANTOMAS_1913", "THE_EXTRAS_1978", "BLOOD_SIMPLE_1984", "LE_SANG_D_UN_PO_TE_1930",
    "LES_POINGS_DANS_LES_POCHES_1965", "QUELQUE_CHOSE_D_AUTRE_1963", "LE_VOLEUR_DE_CHEVAUX_1986",
    "DRIFTERS_1929", "T_O_U_C_H_I_N_G_1968", "VALERIE_ET_LA_SEMAINE_DES_MERVEILLES_1970",
    "LE_SOLEIL_DANS_UN_FILET_1962", "LE_CR_MATEUR_1969", "UN_ET_HUIT_1983", "LE_VIEUX_PUITS_1987",
    "LA_LUNE_TENTATRICE_1996", "EMPIRE_WARHOL_1964", "THE_SECRET_1979", "THE_SPOOKY_BUNCH_1980",
    "THE_CLUB_1981", "NOMAD_1982", "L_INCIDENT_DU_CANON_NOIR_1985", "BULLET_IN_THE_HEAD_1990",
]
missing_posters = [code for code in new_codes if not (posters / f"{code}.jpg").exists()]
lines.insert(0, f"version={pack['version']} movies={len(pack['movies'])} directors={len(pack['directors'])} collections={len(pack['collections'])}")
lines.append("PROBLEMS " + ("none" if not problems else " | ".join(problems)))
lines.append("MISSING_POSTERS " + (", ".join(missing_posters) if missing_posters else "none"))
for collection in pack["collections"]:
    if collection["displayOrder"] >= 18 or collection["code"] == "COLLECTION_012":
        lines.append(f"{collection['code']} {collection['name']} films={len(collection['movies'])} track={collection['track']}")
(ROOT / "tools/output/_collections_check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(lines[0])
print(lines[-12] if len(lines) > 12 else lines[-1])
