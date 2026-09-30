"""Attach key films that the first parser skipped (single-asterisk titles). Pack 30."""
import ast
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
CATALOG = ROOT / "app/src/main/assets/catalog/catalog_v3.json"
COPY = ROOT / "app/src/main/assets/catalog/catalog.json"
LIST_PATH = ROOT / "specs/Listes_Fonctionnelles/Listes_Des_Parcours.txt"


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("œ", "oe").replace("æ", "ae")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def film_codes() -> dict:
    tree = ast.parse((ROOT / "tools/_build_parcours.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "FILM_CODES" for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit("FILM_CODES missing")


def films_by_step() -> list:
    codes = film_codes()
    section = LIST_PATH.read_text(encoding="utf-8").split("# WORK-IN PROGRESS")[0]
    body = section.split("**Courants** :", 1)[1]
    chunks = re.split(r"\n- ([^\n]+?):\s*\n", body)[1:]
    steps = []
    for index in range(0, len(chunks), 2):
        block = chunks[index + 1]
        film_block = re.search(r"Films clés :\s*\n(.+)", block, re.S).group(1)
        movies = []
        for line in film_block.splitlines():
            if not line.strip().startswith("-"):
                continue
            film = re.search(r"\*+([^*]+)\*+", line)
            if not film:
                raise SystemExit(f"unparsed film line {line.strip()}")
            key = fold(film.group(1))
            code = codes.get(key)
            if not code:
                raise SystemExit(f"unmapped film {film.group(1)}")
            movies.append(code)
        if len(movies) != 4:
            raise SystemExit(f"expected 4 films for {chunks[index].strip()}, got {movies}")
        steps.append(movies)
    if len(steps) != 11:
        raise SystemExit(f"expected 11 steps, got {len(steps)}")
    return steps


def main() -> None:
    movies = films_by_step()
    pack = json.loads(CATALOG.read_text(encoding="utf-8"))
    known = {movie["code"] for movie in pack["movies"]}
    path = pack["paths"][0]
    if path["code"] != "PARCOURS_001" or len(path["steps"]) != 11:
        raise SystemExit("unexpected path shape")
    for step, codes in zip(path["steps"], movies):
        missing = [code for code in codes if code not in known]
        if missing:
            raise SystemExit(f"missing movies on {step['code']}: {missing}")
        step["movies"] = codes
    pack["version"] = 30
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)
    shutil.copyfile(CATALOG, COPY)
    print("version", pack["version"], "steps", len(movies))


if __name__ == "__main__":
    main()
