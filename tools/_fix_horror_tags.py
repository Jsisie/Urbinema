"""Drop the duplicate Free Cinema tag and correct the horror mislabels. Pack 36."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
INPUT = ROOT / "batchsData/batchReals/input/input_directors.txt"

# On the deleted tag: these films are the Free Cinema group, so they keep FREE_CINEMA.
REALLY_FREE = {
    "SATURDAY_NIGHT_AND_SUNDAY_MORNING_1960",
    "THE_LONELINESS_OF_THE_LONG_DISTANCE_RUNNER_1962",
    "THIS_SPORTING_LIFE_1963",
    "IF_1968",
}
# Loach sits on the kitchen-sink current that already names him, not on the 1956 programme.
KITCHEN = {"KES_1969"}

DROP_FREE = {
    "NIGHT_OF_THE_DEMON_1957",
    "LE_VOYEUR_1960",
    "INNOCENTS_THE_1961",
    "AN_AMERICAN_WEREWOLF_IN_LONDON_1981",
    "SHAUN_OF_THE_DEAD_2004",
    "REPULSION_1965",
}
DROP_KITCHEN = {"LE_VOYEUR_1960", "INNOCENTS_THE_1961"}


def drop(codes, *remove):
    return [code for code in codes if code not in remove]


def add(codes, *extra):
    for code in extra:
        if code not in codes:
            codes.append(code)
    return codes


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    known = {item["code"] for item in pack["directors"]}
    for record in (
        {
            "code": "CLAIRE_DENIS",
            "firstName": "Claire",
            "lastName": "Denis",
            "displayName": "Claire Denis",
            "characteristicCodes": ["NEW_FRENCH_EXTREMITY"],
            "biography": (
                "Claire Denis, née le 21 avril 1946 à Paris, est une cinéaste française. "
                "Elle a réalisé notamment Chocolat, Beau Travail et Trouble Every Day."
            ),
            "biographyEn": (
                "Claire Denis (born 21 April 1946) is a French film director. "
                "Her films include Chocolat, Beau Travail and Trouble Every Day."
            ),
        },
        {
            "code": "KIYOSHI_KUROSAWA",
            "firstName": "Kiyoshi",
            "lastName": "Kurosawa",
            "displayName": "Kiyoshi Kurosawa",
            "characteristicCodes": [],
            "biography": (
                "Kiyoshi Kurosawa (黒沢清), né le 19 juillet 1955 à Kobe, est un cinéaste japonais. "
                "Il a réalisé notamment Cure, Kaïro et Tokyo Sonata. "
                "Il n'a pas de lien de parenté avec Akira Kurosawa."
            ),
            "biographyEn": (
                "Kiyoshi Kurosawa (黒沢清, born 19 July 1955) is a Japanese film director. "
                "His films include Cure, Pulse and Tokyo Sonata. He is not related to Akira Kurosawa."
            ),
        },
    ):
        if record["code"] in known:
            raise SystemExit(f"director already exists {record['code']}")
        pack["directors"].append(record)

    for director in pack["directors"]:
        if director["code"] == "KEN_LOACH":
            director["characteristicCodes"] = ["NOUVELLE_VAGUE_BRITANNIQUE"]

    seen_british = []
    for movie in pack["movies"]:
        codes = list(movie.get("characteristicCodes") or [])
        code = movie["code"]
        if "BRITISH_NEW_WAVE" in codes:
            seen_british.append(code)
            codes = drop(codes, "BRITISH_NEW_WAVE")
            if code in REALLY_FREE:
                codes = add(codes, "FREE_CINEMA")
            if code in KITCHEN:
                codes = add(codes, "NOUVELLE_VAGUE_BRITANNIQUE")
        if code in DROP_FREE:
            codes = drop(codes, "FREE_CINEMA", "BRITISH_NEW_WAVE")
        if code in DROP_KITCHEN:
            codes = drop(codes, "NOUVELLE_VAGUE_BRITANNIQUE")
        if code == "REPULSION_1965":
            codes = drop(codes, "NEW_HOLLYWOOD", "BRITISH_NEW_WAVE", "FREE_CINEMA")
        if code == "THE_HILLS_HAVE_EYES_1977":
            codes = drop(codes, "GRINDHOUSE", "NEW_HOLLYWOOD")
            codes = add(codes, "CINEMA_INDEPENDANT_AMERICAIN")
        if code == "POSSESSION_1981":
            codes = drop(codes, "CINEMA_DU_LOOK")
            codes = add(codes, "CINEMA_TRANSGRESSION")
            genres = list(movie.get("genreCodes") or [])
            for genre in ("DRAME", "FANTASTIQUE"):
                if genre not in genres:
                    genres.append(genre)
            movie["genreCodes"] = genres
        if code == "SANTA_SANGRE_1989":
            codes = drop(codes, "CINEMA_POLITIQUE_LATINO")
            codes = add(codes, "MELODRAME")
        if code == "LA_NUIT_DU_CHASSEUR_1955":
            codes = add(codes, "EXPRESSIONNISME_ALLEMAND")
        if code == "INTRUDER_THE_2004":
            codes = drop(codes, "NEW_FRENCH_EXTREMITY")
            countries = movie.get("countries") or []
            if not any(item.get("code") == "BELGIUM" and item.get("isPrimary") for item in countries):
                movie["countries"] = [{"code": "BELGIUM", "isPrimary": True}]
        if code == "CURE_1997":
            codes = drop(codes, "JIDAIGEKI", "AGE_OR_CINEMA_JAPONAIS")
            movie["directors"] = [{"code": "KIYOSHI_KUROSAWA", "billingOrder": 0}]
        if code == "TROUBLE_EVERY_DAY_2001":
            movie["directors"] = [{"code": "CLAIRE_DENIS", "billingOrder": 0}]
        movie["characteristicCodes"] = codes

    expected = {
        "KES_1969",
        "DOCTEUR_FOLAMOUR_1964",
        "BLOW_UP_1966",
        "PERFORMANCE_1970",
        "LE_VOYEUR_1960",
        "INNOCENTS_THE_1961",
        "THE_BRIDGE_ON_THE_RIVER_KWAI_1957",
        "REPULSION_1965",
        "THE_SERVANT_1963",
        "LOLITA_1962",
        "NIGHT_OF_THE_DEMON_1957",
        "SATURDAY_NIGHT_AND_SUNDAY_MORNING_1960",
        "THE_LONELINESS_OF_THE_LONG_DISTANCE_RUNNER_1962",
        "THIS_SPORTING_LIFE_1963",
        "A_HARD_DAY_S_NIGHT_1964",
        "IF_1968",
    }
    if set(seen_british) != expected:
        raise SystemExit(f"unexpected BRITISH_NEW_WAVE films: {sorted(set(seen_british) ^ expected)}")

    before = len(pack["characteristics"])
    pack["characteristics"] = [
        item for item in pack["characteristics"] if item["code"] != "BRITISH_NEW_WAVE"
    ]
    if len(pack["characteristics"]) != before - 1:
        raise SystemExit("characteristic was not removed")

    def codes_of(movie_code):
        movie = next(item for item in pack["movies"] if item["code"] == movie_code)
        return movie

    checks = {
        "NIGHT_OF_THE_DEMON_1957": lambda m: "FREE_CINEMA" not in m["characteristicCodes"] and "BRITISH_NEW_WAVE" not in m["characteristicCodes"],
        "LE_VOYEUR_1960": lambda m: "NOUVELLE_VAGUE_BRITANNIQUE" not in m["characteristicCodes"],
        "SHAUN_OF_THE_DEAD_2004": lambda m: "FREE_CINEMA" not in m["characteristicCodes"],
        "AN_AMERICAN_WEREWOLF_IN_LONDON_1981": lambda m: "FREE_CINEMA" not in m["characteristicCodes"],
        "TROUBLE_EVERY_DAY_2001": lambda m: m["directors"][0]["code"] == "CLAIRE_DENIS" and "NEW_FRENCH_EXTREMITY" in m["characteristicCodes"],
        "CURE_1997": lambda m: m["directors"][0]["code"] == "KIYOSHI_KUROSAWA" and "JIDAIGEKI" not in m["characteristicCodes"] and "NEO_NOIR" in m["characteristicCodes"],
        "LA_NUIT_DU_CHASSEUR_1955": lambda m: "EXPRESSIONNISME_ALLEMAND" in m["characteristicCodes"] and "HOLLYWOOD_CLASSIQUE" in m["characteristicCodes"],
        "REPULSION_1965": lambda m: "NEW_HOLLYWOOD" not in m["characteristicCodes"] and "FREE_CINEMA" not in m["characteristicCodes"],
        "THE_HILLS_HAVE_EYES_1977": lambda m: "GRINDHOUSE" not in m["characteristicCodes"] and "CINEMA_INDEPENDANT_AMERICAIN" in m["characteristicCodes"],
        "POSSESSION_1981": lambda m: "CINEMA_DU_LOOK" not in m["characteristicCodes"] and "CINEMA_TRANSGRESSION" in m["characteristicCodes"],
        "SANTA_SANGRE_1989": lambda m: "CINEMA_POLITIQUE_LATINO" not in m["characteristicCodes"] and "SURREALISME" in m["characteristicCodes"],
        "INTRUDER_THE_2004": lambda m: "NEW_FRENCH_EXTREMITY" not in m["characteristicCodes"] and any(c["code"] == "BELGIUM" and c["isPrimary"] for c in m["countries"]),
        "SATURDAY_NIGHT_AND_SUNDAY_MORNING_1960": lambda m: "FREE_CINEMA" in m["characteristicCodes"] and "BRITISH_NEW_WAVE" not in m["characteristicCodes"],
        "KES_1969": lambda m: "NOUVELLE_VAGUE_BRITANNIQUE" in m["characteristicCodes"] and "FREE_CINEMA" not in m["characteristicCodes"],
    }
    for movie_code, test in checks.items():
        if not test(codes_of(movie_code)):
            raise SystemExit(f"check failed {movie_code}")
    if any(
        "BRITISH_NEW_WAVE" in (item.get("characteristicCodes") or [])
        or item.get("characteristicCode") == "BRITISH_NEW_WAVE"
        for item in pack["directors"]
    ):
        raise SystemExit("director still points at BRITISH_NEW_WAVE")

    pack["version"] = 36
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY)

    lines = INPUT.read_text(encoding="utf-8").splitlines()
    for row in ("CLAIRE_DENIS;Claire;Denis;Claire Denis", "KIYOSHI_KUROSAWA;Kiyoshi;Kurosawa;Kiyoshi Kurosawa"):
        if row not in lines:
            lines.append(row)
    INPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("directors", len(pack["directors"]), "version", pack["version"])


if __name__ == "__main__":
    main()
