"""Build parcours 1 into catalog_v3: four missing films, one new director, path texts."""
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchPosters"))
sys.path.insert(0, str(ROOT / "batchsData" / "batchReals"))
from catalog_enrich import french_overview, movie_format, scores_for  # noqa: E402
from posters_batch import TmdbClient, load_env  # noqa: E402
from reals_batch import TMDB_IMAGE, biography_of, profile_path, search_people  # noqa: E402

load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.15)

LIST_PATH = ROOT / "specs/Listes_Fonctionnelles/Listes_Des_Parcours.txt"
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
POSTERS = ROOT / "app/src/main/assets/media/posters"
PHOTOS = ROOT / "app/src/main/assets/media/directors"


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("œ", "oe").replace("æ", "ae")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


FILM_CODES = {
    "la sortie de l usine lumiere a lyon": "LA_SORTIE_DES_USINES_LUMIERE_1895",
    "le voyage dans la lune": "VOYAGE_DANS_LA_LUNE_1902",
    "naissance d une nation": "NAISSANCE_D_UNE_NATION_1915",
    "le mecano de la general": "LE_MECANICIEN_DE_LA_GENERAL_1926",
    "la souriante madame beudet": "LA_SOURIANTE_MADAME_BEUDET_1923",
    "coeur fidele": "COEUR_FIDELE_1923",
    "la glace a trois faces": "LA_GLACE_A_TROIS_FACES_1927",
    "napoleon": "NAPOLEON_1927",
    "le cabinet du docteur caligari": "CABINET_DU_DOCTEUR_CALIGARI_1920",
    "nosferatu le vampire": "NOSFERATU_1922",
    "les trois lumieres": "LES_TROIS_LUMIERES_1921",
    "metropolis": "METROPOLIS_1927",
    "la greve": "LA_GREVE_1925",
    "le cuirasse potemkine": "LE_CUIRASSE_POTEMKINE_1925",
    "la mere": "LA_MERE_1926",
    "l homme a la camera": "L_HOMME_A_LA_CAMERA_1929",
    "la coquille et le clergyman": "LA_COQUILLE_ET_LE_CLERGYMAN_1928",
    "un chien andalou": "UN_CHIEN_ANDALOU_1929",
    "l age d or": "L_AGE_D_OR_1930",
    "le sang d un poete": "LE_SANG_D_UN_PO_TE_1930",
    "la chevauchee fantastique": "LA_CHEVAUCHEE_FANTASTIQUE_1939",
    "autant en emporte le vent": "AUTANT_EN_EMPORTE_LE_VENT_1939",
    "citizen kane": "CITIZEN_KANE_1941",
    "casablanca": "CASABLANCA_1942",
    "rome ville ouverte": "ROMA_CITTA_APERTA_1945",
    "paisa": "PAISA_1946",
    "le voleur de bicyclette": "LE_VOLEUR_DE_BICYCLETTE_1948",
    "la terre tremble": "LA_TERRE_TREMBLE_1948",
    "le beau serge": "LE_BEAU_SERGE_1958",
    "les quatre cents coups": "LES_QUATRE_CENTS_COUPS_1959",
    "a bout de souffle": "A_BOUT_DE_SOUFFLE_1960",
    "cleo de 5 a 7": "CLEO_DE_5_A_7_1962",
    "contes cruels de la jeunesse": "CONTES_CRUELS_DE_LA_JEUNESSE_1960",
    "la pendaison": "LA_PENDAISON_1968",
    "la femme insecte": "LA_FEMME_INSECTE_1963",
    "eros massacre": "EROS_MASSACRE_1969",
    "le miroir aux alouettes": "THE_SHOP_ON_MAIN_STREET_1965",
    "les petites marguerites": "LES_PETITES_MARGUERITES_1966",
    "trains etroitement surveilles": "TRAINS_ETROITEMENT_SURVEILLES_1966",
    "au feu les pompiers": "THE_FIREMEN_S_BALL_1967",
    "in the mood for love": "IN_THE_MOOD_FOR_LOVE_2000_KAR_WAI",
    "mulholland drive": "MULHOLLAND_DRIVE_2001",
    "mad max fury road": "MAD_MAX_FURY_ROAD_2015",
    "parasite": "PARASITE_2019_JOON_HO",
}

FIGURE_CODES = {
    "louis auguste lumiere": "LOUIS_LUMIERE",
    "georges melies": "GEORGES_MELIES",
    "d w griffith": "DW_GRIFFITH",
    "charlie chaplin": "CHARLIE_CHAPLIN",
    "buster keaton": "BUSTER_KEATON",
    "abel gance": "ABEL_GANCE",
    "jean epstein": "JEAN_EPSTEIN",
    "germaine dulac": "GERMAINE_DULAC",
    "robert wiene": "ROBERT_WIENE",
    "f w murnau": "FW_MURNAU",
    "fritz lang": "FRITZ_LANG",
    "serguei eisenstein": "SERGEI_EISENSTEIN",
    "sergei eisenstein": "SERGEI_EISENSTEIN",
    "dziga vertov": "DZIGA_VERTOV",
    "vsevolod poudovkine": "VSEVOLOD_PUDOVKIN",
    "luis bunuel": "LUIS_BUNUEL",
    "man ray": "MAN_RAY",
    "jean cocteau": "JEAN_COCTEAU",
    "john ford": "JOHN_FORD",
    "alfred hitchcock": "ALFRED_HITCHCOCK",
    "howard hawks": "HOWARD_HAWKS",
    "orson welles": "ORSON_WELLES",
    "roberto rossellini": "ROBERTO_ROSSELLINI",
    "vittorio de sica": "VITTORIO_DE_SICA",
    "luchino visconti": "LUCHINO_VISCONTI",
    "francois truffaut": "FRANCOIS_TRUFFAUT",
    "jean luc godard": "JEAN_LUC_GODARD",
    "agnes varda": "AGNES_VARDA",
    "eric rohmer": "ERIC_ROHMER",
    "nagisa oshima": "NAGISA_OSHIMA",
    "masahiro shinoda": "MASAHIRO_SHINODA",
    "shohei imamura": "SHOHEI_IMAMURA",
    "kiju yoshida": "YOSHISHIGE_YOSHIDA",
    "milos forman": "MILOS_FORMAN",
    "vera chytilova": "VERA_CHYTILOVA",
    "jiri menzel": "JIRI_MENZEL",
    "jaromil jires": "JAROMIL_JIRES",
    "christopher nolan": "CHRISTOPHER_NOLAN",
    "bong joon ho": "BONG_JOON_HO",
    "denis villeneuve": "DENIS_VILLENEUVE",
    "celine sciamma": "CELINE_SCIAMMA",
}

STEP_CODES = [
    "CINEMA_MUET_MOUVEMENT",
    "IMPRESSIONNISME_FRANCAIS",
    "EXPRESSIONNISME_ALLEMAND",
    "MONTAGE_SOVIETIQUE",
    "SURREALISME",
    "HOLLYWOOD_CLASSIQUE",
    "NEOREALISME_ITALIEN",
    "NOUVELLE_VAGUE_FRANCAISE",
    "NOUVELLE_VAGUE_JAPONAISE",
    "NOUVELLE_VAGUE_TCHEQUE",
    "CINEMA_CONTEMPORAIN_MOUVEMENT",
]

NEW_MOVIES = [
    {
        "code": "LA_COQUILLE_ET_LE_CLERGYMAN_1928",
        "french": "La Coquille et le Clergyman",
        "queries": ["La Coquille et le Clergyman", "The Seashell and the Clergyman"],
        "year": 1928,
        "director_code": "GERMAINE_DULAC",
        "director_hint": "Dulac",
        "country": "FRANCE",
        "characteristic": "SURREALISME",
        "silent": True,
        "experimental": True,
        "demand": 0.8,
        "genres": ["DRAME"],
    },
    {
        "code": "CONTES_CRUELS_DE_LA_JEUNESSE_1960",
        "french": "Contes cruels de la jeunesse",
        "queries": ["Contes cruels de la jeunesse", "Cruel Story of Youth"],
        "year": 1960,
        "director_code": "NAGISA_OSHIMA",
        "director_hint": "Oshima",
        "country": "JAPAN",
        "characteristic": "NOUVELLE_VAGUE_JAPONAISE",
        "silent": False,
        "experimental": False,
        "demand": 0.62,
        "genres": ["DRAME"],
    },
    {
        "code": "LA_PENDAISON_1968",
        "french": "La Pendaison",
        "queries": ["La Pendaison", "Death by Hanging"],
        "year": 1968,
        "director_code": "NAGISA_OSHIMA",
        "director_hint": "Oshima",
        "country": "JAPAN",
        "characteristic": "NOUVELLE_VAGUE_JAPONAISE",
        "silent": False,
        "experimental": False,
        "demand": 0.7,
        "genres": ["DRAME"],
    },
    {
        "code": "LA_FEMME_INSECTE_1963",
        "french": "La Femme insecte",
        "queries": ["La Femme insecte", "The Insect Woman"],
        "year": 1963,
        "director_code": "SHOHEI_IMAMURA",
        "director_hint": "Imamura",
        "country": "JAPAN",
        "characteristic": "NOUVELLE_VAGUE_JAPONAISE",
        "silent": False,
        "experimental": False,
        "demand": 0.68,
        "genres": ["DRAME"],
    },
]


def strip_wiki(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n")
    cleaned = re.sub(r"(?i)from wikipedia, the free encyclopedia\.?", "", cleaned)
    cleaned = re.sub(r"(?i)description above from the wikipedia article[^\n]*", "", cleaned)
    return cleaned.strip()


def director_names(details: dict) -> str:
    crew = (details.get("credits") or {}).get("crew") or []
    return " ".join(fold(str(person.get("name") or "")) for person in crew if person.get("job") == "Director")


def find_movie(spec: dict) -> dict:
    hint = fold(spec["director_hint"])
    for query in spec["queries"]:
        for language in ("fr-FR", "en-US"):
            for hit in client.search_movie(query, spec["year"], language)[:6]:
                details = client.movie_details(int(hit["id"]), "fr-FR")
                year_text = str(details.get("release_date") or "")[:4]
                year = int(year_text) if year_text.isdigit() else 0
                if abs(year - spec["year"]) > 1:
                    continue
                names = director_names(details)
                if hint not in names:
                    english = client.movie_details(int(hit["id"]), "en-US")
                    names = f"{names} {director_names(english)}"
                if hint not in names:
                    continue
                blob = fold(f"{details.get('title') or ''} {details.get('original_title') or ''} {hit.get('title') or ''}")
                if fold(query) not in blob and fold(spec["french"]) not in blob:
                    tokens = [token for token in fold(query).split() if len(token) > 3]
                    if not tokens or not any(token in blob for token in tokens):
                        continue
                return details
    raise SystemExit(f"no tmdb match for {spec['code']}")


def save_poster(details: dict, code: str) -> None:
    poster = details.get("poster_path")
    if not poster:
        raise SystemExit(f"no poster for {code}")
    payload, _kind = client.download(f"{TMDB_IMAGE}/w780{poster}")
    if not payload:
        raise SystemExit(f"poster download failed {code}")
    POSTERS.mkdir(parents=True, exist_ok=True)
    (POSTERS / f"{code}.jpg").write_bytes(payload)


def movie_row(spec: dict, details: dict) -> dict:
    runtime = int(details.get("runtime") or 0)
    if runtime <= 0:
        runtime = 40 if spec["code"].endswith("1928") else 100
    distance, demand, historical, cultural = scores_for(
        spec["code"], spec["year"], spec["silent"], spec["experimental"], spec["demand"]
    )
    overview = french_overview(details) or str(details.get("overview") or "").strip()
    return {
        "code": spec["code"],
        "originalTitle": str(details.get("original_title") or spec["french"]),
        "frenchTitle": spec["french"],
        "releaseYear": spec["year"],
        "durationMinutes": runtime,
        "format": movie_format(runtime),
        "synopsis": overview,
        "historicalDistance": distance,
        "artisticDemand": demand,
        "historicalRichness": historical,
        "culturalRichness": cultural,
        "isSilent": spec["silent"],
        "isBlackAndWhite": spec["year"] < 1970,
        "isExperimental": spec["experimental"],
        "countries": [{"code": spec["country"], "isPrimary": True}],
        "directors": [{"code": spec["director_code"], "billingOrder": 0}],
        "genreCodes": spec["genres"],
        "characteristicCodes": [spec["characteristic"]],
    }


def add_imamura(pack: dict) -> None:
    if any(item["code"] == "SHOHEI_IMAMURA" for item in pack["directors"]):
        return
    # Person id taken from the director credit of La Femme insecte (TMDB 42984).
    details, french_bio = biography_of(client, 20025)
    birthday = str(details.get("birthday") or "")
    if not birthday.startswith("1926"):
        raise SystemExit(f"unexpected imamura birthday {birthday}")
    english = client.request_json(f"/person/{details['id']}", {"language": "en-US"})
    english_bio = strip_wiki(str(english.get("biography") or ""))
    french_bio = strip_wiki(french_bio)
    path = profile_path(details) or profile_path(english)
    if path:
        payload, _kind = client.download(f"{TMDB_IMAGE}/w780{path}")
        if payload:
            PHOTOS.mkdir(parents=True, exist_ok=True)
            (PHOTOS / "SHOHEI_IMAMURA.jpg").write_bytes(payload)
    director = {
        "code": "SHOHEI_IMAMURA",
        "firstName": "Shōhei",
        "lastName": "Imamura",
        "displayName": "Shōhei Imamura",
        "characteristicCodes": ["NOUVELLE_VAGUE_JAPONAISE"],
    }
    if french_bio:
        director["biography"] = french_bio
    if english_bio and english_bio != french_bio:
        director["biographyEn"] = english_bio
    pack["directors"].append(director)


def parse_path() -> dict:
    raw = LIST_PATH.read_text(encoding="utf-8")
    section = raw.split("# WORK-IN PROGRESS")[0]
    title = re.search(r"## I\. (.+)", section).group(1).strip()
    description = re.search(r"\*\*Description :\*\*\s*(.+?)\n\n\*\*Transitions", section, re.S).group(1).strip()
    description = re.sub(r"\n+", "\n\n", description)
    transitions = []
    for match in re.finditer(r"- .+?➔ .+?:\n\s+- (.+)", section):
        transitions.append(match.group(1).strip())
    body = section.split("**Courants** :", 1)[1]
    chunks = re.split(r"\n- ([^\n]+?):\s*\n", body)[1:]
    steps = []
    for index in range(0, len(chunks), 2):
        name = chunks[index].strip()
        block = chunks[index + 1]
        period = re.search(r"Années :\s*\n\s*- (.+)", block).group(1).strip()
        step_description = re.search(r"Description :\s*\n\s*- (.+?)\n\s*- A savoir :", block, re.S).group(1).strip()
        facts = []
        fact_block = re.search(r"A savoir :\s*\n(.+?)\n\s*- Figures clés :", block, re.S).group(1)
        for fact in re.finditer(r"\*\*(.+?)\*\*\s*:\s*(.+)", fact_block):
            facts.append({"title": fact.group(1).strip(), "body": fact.group(2).strip()})
        figures = []
        figure_block = re.search(r"Figures clés :\s*\n(.+?)\n\s*- Films clés :", block, re.S).group(1)
        for line in figure_block.splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            role_match = re.search(r"\(([^)]+)\)\s*$", line)
            role = role_match.group(1).strip() if role_match else ""
            names = re.findall(r"\*\*(.+?)\*\*", line)
            for person in names:
                figures.append({
                    "displayName": person.strip(),
                    "role": role,
                    "directorCode": FIGURE_CODES.get(fold(person)),
                })
        movies = []
        film_block = re.search(r"Films clés :\s*\n(.+)", block, re.S).group(1)
        for line in film_block.splitlines():
            if not line.strip().startswith("-"):
                continue
            film = re.search(r"\*{2,3}([^*]+)\*{2,3}", line)
            if not film:
                continue
            key = fold(film.group(1))
            code = FILM_CODES.get(key)
            if not code:
                raise SystemExit(f"unmapped film {film.group(1)}")
            movies.append(code)
        steps.append({
            "code": f"PARCOURS_001_{index // 2:02d}",
            "position": index // 2,
            "characteristicCode": STEP_CODES[index // 2],
            "name": name,
            "periodLabel": period,
            "description": step_description,
            "facts": facts,
            "figures": figures,
            "movies": movies,
            "transition": transitions[index // 2] if index // 2 < len(transitions) else None,
        })
    if len(steps) != 11 or len(transitions) != 10:
        raise SystemExit(f"parse steps={len(steps)} transitions={len(transitions)}")
    summary = description.split("\n\n")[0]
    return {
        "code": "PARCOURS_001",
        "displayOrder": 1,
        "name": title,
        "summary": summary,
        "description": description,
        "periodLabel": "1895 – aujourd'hui",
        "steps": steps,
    }


def main() -> None:
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    existing = {movie["code"] for movie in pack["movies"]}
    added = []
    input_lines = ["frenchTitle;releaseYear;director;code;originalTitle;demand;tmdbId"]
    for spec in NEW_MOVIES:
        if spec["code"] in existing:
            continue
        details = find_movie(spec)
        save_poster(details, spec["code"])
        row = movie_row(spec, details)
        pack["movies"].append(row)
        added.append(spec["code"])
        input_lines.append(
            f"\"{spec['french']}\";{spec['year']};\"{spec['director_hint']}\";{spec['code']};"
            f"\"{row['originalTitle']}\";{spec['demand']};{details.get('id')}"
        )
    add_imamura(pack)
    if not any(item["code"] == "CINEMA_CONTEMPORAIN_MOUVEMENT" for item in pack["characteristics"]):
        pack["characteristics"].append({
            "code": "CINEMA_CONTEMPORAIN_MOUVEMENT",
            "name": "Cinéma contemporain",
            "typeCode": "PERIOD",
            "description": "L'ère d'hybridation du cinéma, après les manifestes du XXe siècle : métissage des formes, du numérique et des regards mondiaux.",
        })
    path = parse_path()
    known = {movie["code"] for movie in pack["movies"]}
    directors = {item["code"] for item in pack["directors"]}
    characteristics = {item["code"] for item in pack["characteristics"]}
    for step in path["steps"]:
        if step["characteristicCode"] not in characteristics:
            raise SystemExit(f"missing characteristic {step['characteristicCode']}")
        for code in step["movies"]:
            if code not in known:
                raise SystemExit(f"missing movie {code}")
        for figure in step["figures"]:
            code = figure.get("directorCode")
            if code and code not in directors:
                raise SystemExit(f"missing director {code}")
            if not code:
                figure.pop("directorCode", None)
        if not step["transition"]:
            step.pop("transition", None)
    pack["paths"] = [path]
    pack["version"] = 29
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, ROOT / "app/src/main/assets/catalog/catalog.json")
    input_path = ROOT / "batchsData/batchPosters/input/input_parcours.txt"
    input_path.write_text("\n".join(input_lines) + "\n", encoding="utf-8")
    directors_input = ROOT / "batchsData/batchReals/input/input_directors.txt"
    line = "SHOHEI_IMAMURA;Shōhei;Imamura;Shōhei Imamura\n"
    current = directors_input.read_text(encoding="utf-8")
    if "SHOHEI_IMAMURA;" not in current:
        directors_input.write_text(current.rstrip() + "\n" + line, encoding="utf-8")
    (ROOT / "tools/output/_parcours_build.txt").write_text(
        f"added={','.join(added) or 'none'}\nsteps={len(path['steps'])}\nversion=29\n",
        encoding="utf-8",
    )
    print("built", len(added))


if __name__ == "__main__":
    main()
