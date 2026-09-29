"""Add the Cinéma des premiers temps collection and its missing films."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
BATCH = ROOT / "batchsData/batchPosters/output/catalog/premiers_temps.json"
BIOS = ROOT / "batchsData/batchReals/output/bios.json"
POSTER_SRC = ROOT / "batchsData/batchPosters/output/posters"
POSTER_DST = ROOT / "app/src/main/assets/media/posters"
PHOTO_SRC = ROOT / "batchsData/batchReals/output/photos"
PHOTO_DST = ROOT / "app/src/main/assets/media/directors"

FILMS = [
    "PAUVRE_PIERROT_1892",
    "EXPERIMENTAL_SOUND_FILM_1894",
    "ANNIE_OAKLEY_1894",
    "LA_SORTIE_DES_USINES_LUMIERE_1895",
    "L_ARROSEUR_ARROSE_1895",
    "L_ARRIVEE_D_UN_TRAIN_1896",
    "LE_MANOIR_DU_DIABLE_1896",
    "PANORAMA_DU_GRAND_CANAL_1896",
    "ESCAMOTAGE_D_UNE_DAME_1896",
    "UN_HOMME_DE_TETES_1898",
    "LA_FEE_AUX_CHOUX_1900",
    "LA_LOUPE_DE_GRAND_MAMAN_1900",
    "THE_BIG_SWALLOW_1901",
    "VOYAGE_DANS_LA_LUNE_1902",
    "LE_VOL_DU_GRAND_RAPIDE_1903",
    "ALICE_GUY_TOURNE_UNE_PHONOSCENE_1905",
    "LES_CONSEQUENCES_DU_FEMINISME_1906",
]

DIRECTORS = [
    ("EMILE_REYNAUD", "Émile", "Reynaud", "Émile Reynaud"),
    ("WILLIAM_K_L_DICKSON", "William K.L.", "Dickson", "William K.L. Dickson"),
    ("WILLIAM_HEISE", "William", "Heise", "William Heise"),
    ("ALEXANDRE_PROMIO", "Alexandre", "Promio", "Alexandre Promio"),
    ("JAMES_WILLIAMSON", "James", "Williamson", "James Williamson"),
    ("GEORGE_ALBERT_SMITH", "George Albert", "Smith", "George Albert Smith"),
]

DIRECTOR_FIX = {
    "LA_FEE_AUX_CHOUX_1900": ["ALICE_GUY"],
    "ALICE_GUY_TOURNE_UNE_PHONOSCENE_1905": ["ALICE_GUY"],
    "LA_LOUPE_DE_GRAND_MAMAN_1900": ["GEORGE_ALBERT_SMITH"],
}
TITLE_FIX = {
    "L_ARROSEUR_ARROSE_1895": "L'Arroseur arrosé",
    "PANORAMA_DU_GRAND_CANAL_1896": "Le Panorama du Grand Canal vu d'un bateau",
    "UN_HOMME_DE_TETES_1898": "Un homme de têtes",
    "ALICE_GUY_TOURNE_UNE_PHONOSCENE_1905": "Alice Guy tourne une phonoscène",
}
SYNOPSIS_FIX = {
    "EXPERIMENTAL_SOUND_FILM_1894": "Dickson joue du violon devant un cornet : un des premiers essais de son.",
    "ANNIE_OAKLEY_1894": "Annie Oakley tire au fusil devant la caméra d'Edison.",
    "LE_MANOIR_DU_DIABLE_1896": "Un diable fait surgir une chauve-souris, des fantômes et un squelette.",
    "LA_LOUPE_DE_GRAND_MAMAN_1900": "Un enfant observe le monde à travers la loupe de sa grand-mère.",
}

DESCRIPTION = (
    "Les années 1892–1906, quand d'ingénieux bricoleurs inventent les premiers trucages, "
    "mouvements et drames d'un art qui n'a pas encore de règles."
)
LONG = (
    "Avant d'être une industrie ou un art classique, le cinéma a été une attraction foraine, "
    "un tour de magie et un laboratoire à ciel ouvert. De L'Arroseur arrosé au Voyage dans la Lune, "
    "en passant par les premiers travellings sur les canaux de Venise et l'invention du gros plan "
    "par l'École de Brighton, cette période pose les bases de tout ce qui suivra. Alice Guy, "
    "les frères Lumière, Georges Méliès ou Edwin S. Porter : ces pionniers n'avaient aucun modèle, "
    "ils ont tout inventé en marchant. Cette collection ne rassemble pas des longs-métrages à grand "
    "spectacle, c'est le carnet de croquis des premières fois du septième art."
)


def poster_exists(code: str) -> bool:
    return any((POSTER_DST / f"{code}{ext}").is_file() for ext in (".webp", ".png", ".jpg", ".jpeg"))


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    if any(item["code"] == "COLLECTION_027" for item in pack["collections"]):
        raise SystemExit("COLLECTION_027 already present")
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    bios = json.loads(BIOS.read_text(encoding="utf-8")) if BIOS.is_file() else {}
    known_genres = {item["code"] for item in pack["genres"]}
    known_chars = {item["code"] for item in pack["characteristics"]}
    known_countries = {item["code"] for item in pack["countries"]}
    director_codes = {item["code"] for item in pack["directors"]}
    movie_codes = {item["code"] for item in pack["movies"]}

    for code, first, last, display in DIRECTORS:
        if code in director_codes:
            continue
        record = {
            "code": code,
            "lastName": last,
            "displayName": display,
            "characteristicCodes": ["CINEMA_MUET_MOUVEMENT"],
            "firstName": first,
        }
        text = (bios.get(code) or "").strip()
        if text:
            record["biography"] = text
        pack["directors"].append(record)
        director_codes.add(code)

    inserted = []
    for movie in batch["movies"]:
        code = movie["code"]
        if code in movie_codes:
            raise SystemExit(f"movie already in catalog: {code}")
        if code in DIRECTOR_FIX:
            movie["directors"] = [
                {"code": director, "billingOrder": index}
                for index, director in enumerate(DIRECTOR_FIX[code])
            ]
        if code in TITLE_FIX:
            movie["frenchTitle"] = TITLE_FIX[code]
        if code == "ALICE_GUY_TOURNE_UNE_PHONOSCENE_1905":
            movie["releaseYear"] = 1905
        if not (movie.get("synopsis") or "").strip() and code in SYNOPSIS_FIX:
            movie["synopsis"] = SYNOPSIS_FIX[code]
        movie["isSilent"] = True
        movie["isBlackAndWhite"] = True
        chars = list(movie.get("characteristicCodes") or [])
        if "CINEMA_MUET_MOUVEMENT" not in chars:
            chars.append("CINEMA_MUET_MOUVEMENT")
        movie["characteristicCodes"] = chars
        unknown_genres = [item for item in movie.get("genreCodes") or [] if item not in known_genres]
        unknown_chars = [item for item in chars if item not in known_chars]
        unknown_countries = [item["code"] for item in movie.get("countries") or [] if item["code"] not in known_countries]
        unknown_directors = [item["code"] for item in movie.get("directors") or [] if item["code"] not in director_codes]
        if unknown_genres or unknown_chars or unknown_countries or unknown_directors:
            raise SystemExit(
                f"{code} unknown genres={unknown_genres} chars={unknown_chars} "
                f"countries={unknown_countries} directors={unknown_directors}"
            )
        if movie.get("durationMinutes", 0) <= 0:
            raise SystemExit(f"{code} duration")
        if not any(item.get("isPrimary") for item in movie.get("countries") or []):
            raise SystemExit(f"{code} primary country")
        pack["movies"].append(movie)
        movie_codes.add(code)
        inserted.append(code)

    missing = [code for code in FILMS if code not in movie_codes]
    if missing:
        raise SystemExit(f"missing films: {missing}")

    pack["collections"].append(
        {
            "code": "COLLECTION_027",
            "displayOrder": 27,
            "name": "Cinéma des premiers temps",
            "description": DESCRIPTION,
            "longDescription": LONG,
            "isPublished": True,
            "movies": [{"code": code, "displayOrder": index} for index, code in enumerate(FILMS, start=1)],
            "countryCodes": ["FRANCE", "USA", "UK"],
            "track": "GATEWAY",
        }
    )
    pack["version"] = 26

    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")

    copied_posters = 0
    for code in inserted:
        source = POSTER_SRC / f"{code}.jpg"
        if not source.is_file() or source.stat().st_size <= 0:
            raise SystemExit(f"poster missing: {code}")
        shutil.copyfile(source, POSTER_DST / source.name)
        copied_posters += 1
    copied_photos = 0
    for code, *_rest in DIRECTORS:
        source = PHOTO_SRC / f"{code}.jpg"
        if source.is_file() and source.stat().st_size > 0:
            PHOTO_DST.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, PHOTO_DST / source.name)
            copied_photos += 1
    linked_without_poster = [code for code in FILMS if code not in inserted and not poster_exists(code)]

    input_path = ROOT / "batchsData/batchReals/input/input_directors.txt"
    text = input_path.read_text(encoding="utf-8")
    extra = []
    for code, first, last, display in DIRECTORS:
        if f"{code};" not in text:
            extra.append(f"{code};{first};{last};{display}")
    if extra:
        text = text.replace("# 798 réalisateurs", "# 804 réalisateurs")
        input_path.write_text(text.rstrip() + "\n" + "\n".join(extra) + "\n", encoding="utf-8")

    print(
        f"version={pack['version']} movies={len(pack['movies'])} collections={len(pack['collections'])} "
        f"inserted={len(inserted)} posters={copied_posters} photos={copied_photos} "
        f"linked_without_poster={len(linked_without_poster)}"
    )
    if linked_without_poster:
        print("NEED_POSTER " + ",".join(linked_without_poster))


if __name__ == "__main__":
    main()
