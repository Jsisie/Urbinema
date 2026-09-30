"""Move films off the fake DIRECTOR person (Naruse's name, other people's films). Pack 31."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
INPUT = ROOT / "batchsData/batchReals/input/input_directors.txt"

REPLACE = {
    "NUAGES_FLOTTANTS_1955": "MIKIO_NARUSE",
    "AU_BORD_DE_LA_MER_BLEUE_1936": "BORIS_BARNET",
    "THE_END_OF_ST_PETERSBURG_1927": "VSEVOLOD_PUDOVKIN",
    "IL_ETAIT_UNE_FOIS_UN_MERLE_CHANTEUR_1970": "OTAR_IOSSELIANI",
    "THE_ASTHENIC_SYNDROME_1989": "KIRA_MURATOVA",
    "THE_LONG_FAREWELL_1971": "KIRA_MURATOVA",
    "SONG_OF_THE_EXILE_1990": "ANN_HUI",
    "VENGEANCE_IS_MINE_1979": "SHOHEI_IMAMURA",
    "THE_BALLAD_OF_NARAYAMA_1983": "SHOHEI_IMAMURA",
    "MY_FRIEND_IVAN_LAPSHIN_1985": "ALEXE_GUERMAN",
    "KHRUSTALYOV_MY_CAR_1998": "ALEXE_GUERMAN",
    "BALLAD_OF_A_SOLDIER_1959": "GRIGORI_TCHOUKHRAI",
    "THE_COMMISSAR_1967": "ALEXANDRE_ASKOLDOV",
    "THE_STREET_FIGHTER_1974": "SHIGEHIRO_OZAWA",
    "TEARS_OF_THE_BLACK_TIGER_2000": "WISIT_SASANATIENG",
    "ONG_BAK_2003": "PRACHYA_PINKAEW",
    "CARGO_200_2007": "ALEXE_BALABANOV",
    "ILO_ILO_2013": "ANTHONY_CHEN",
    "TANGERINES_2013": "ZAZA_URUSHADZE",
}

NEW = [
    ("ALEXE_GUERMAN", "Alexeï", "Guerman", "Alexeï Guerman"),
    ("GRIGORI_TCHOUKHRAI", "Grigori", "Tchoukhraï", "Grigori Tchoukhraï"),
    ("ALEXANDRE_ASKOLDOV", "Alexandre", "Askoldov", "Alexandre Askoldov"),
    ("SHIGEHIRO_OZAWA", "Shigehiro", "Ozawa", "Shigehiro Ozawa"),
    ("WISIT_SASANATIENG", "Wisit", "Sasanatieng", "Wisit Sasanatieng"),
    ("PRACHYA_PINKAEW", "Prachya", "Pinkaew", "Prachya Pinkaew"),
    ("ALEXE_BALABANOV", "Alexeï", "Balabanov", "Alexeï Balabanov"),
    ("ANTHONY_CHEN", "Anthony", "Chen", "Anthony Chen"),
    ("ZAZA_URUSHADZE", "Zaza", "Urushadze", "Zaza Urushadze"),
]

FRENCH_BIO = (
    "Mikio Naruse (成瀬巳喜男), né le 20 août 1905 à Tokyo et mort le 2 juillet 1969, "
    "est un cinéaste japonais. Il a réalisé près de 90 films entre 1930 et 1967, "
    "surtout des drames du quotidien centrés sur des femmes, souvent interprétés par "
    "Hideko Takamine, Kinuyo Tanaka ou Setsuko Hara."
)


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    known = {item["code"] for item in pack["directors"]}
    for code, first, last, display in NEW:
        if code in known:
            raise SystemExit(f"director already exists {code}")
        pack["directors"].append({
            "code": code,
            "firstName": first,
            "lastName": last,
            "displayName": display,
            "characteristicCodes": [],
        })
        known.add(code)
    for code in set(REPLACE.values()):
        if code not in known:
            raise SystemExit(f"missing director {code}")

    touched = 0
    for movie in pack["movies"]:
        directors = movie.get("directors") or []
        codes = [item.get("code") for item in directors]
        if "DIRECTOR" not in codes:
            continue
        touched += 1
        target = REPLACE.get(movie["code"])
        kept = [item for item in directors if item.get("code") != "DIRECTOR"]
        if target:
            if target not in {item.get("code") for item in kept}:
                kept.append({"code": target, "billingOrder": 0})
        if not kept:
            raise SystemExit(f"film left without a director {movie['code']}")
        for index, item in enumerate(kept):
            item["billingOrder"] = index
        movie["directors"] = kept

    if touched != 21:
        raise SystemExit(f"expected 21 DIRECTOR films, touched {touched}")

    naruse = next(item for item in pack["directors"] if item["code"] == "MIKIO_NARUSE")
    naruse["displayName"] = "Mikio Naruse"
    naruse["firstName"] = "Mikio"
    naruse["lastName"] = "Naruse"
    naruse["biography"] = FRENCH_BIO
    english = naruse.get("biographyEn") or ""
    if "成瀬巳喜男" not in english:
        naruse["biographyEn"] = english.replace("Mikio Naruse", "Mikio Naruse (成瀬巳喜男)", 1)

    before = len(pack["directors"])
    pack["directors"] = [item for item in pack["directors"] if item["code"] != "DIRECTOR"]
    if len(pack["directors"]) != before - 1:
        raise SystemExit("DIRECTOR person was not removed")
    if any(
        any(item.get("code") == "DIRECTOR" for item in movie.get("directors") or [])
        for movie in pack["movies"]
    ):
        raise SystemExit("DIRECTOR credit remains")

    pack["version"] = 31
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY)

    lines = INPUT.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if not line.startswith("DIRECTOR;")]
    for code, first, last, display in NEW:
        row = f"{code};{first};{last};{display}"
        if row not in lines:
            lines.append(row)
    INPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("directors", len(pack["directors"]), "version", pack["version"])


if __name__ == "__main__":
    main()
