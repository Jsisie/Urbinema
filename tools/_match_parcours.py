"""Match parcours 1 key films and figures against the current catalog."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("œ", "oe").replace("æ", "ae")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


movies = []
for movie in pack["movies"]:
    movies.append(
        {
            "code": movie["code"],
            "year": movie.get("releaseYear"),
            "titles": fold(
                " ".join(
                    filter(
                        None,
                        [movie.get("frenchTitle"), movie.get("originalTitle"), movie["code"].replace("_", " ")],
                    )
                )
            ),
            "directors": [ref["code"] for ref in movie.get("directors") or []],
        }
    )
directors = {fold(item.get("displayName") or ""): item["code"] for item in pack["directors"]}
directors.update({fold(item["code"].replace("_", " ")): item["code"] for item in pack["directors"]})

films = [
    ("La Sortie de l'usine Lumière à Lyon", 1895, ["sortie usine", "sortie des usines"]),
    ("Le Voyage dans la Lune", 1902, ["voyage dans la lune", "voyage lune"]),
    ("Naissance d'une nation", 1915, ["naissance d une nation", "birth of a nation"]),
    ("Le Mécano de la General", 1926, ["mecano de la general", "general"]),
    ("La Souriante Madame Beudet", 1923, ["souriante madame beudet", "madame beudet"]),
    ("Cœur fidèle", 1923, ["coeur fidele"]),
    ("La Glace à trois faces", 1927, ["glace a trois faces"]),
    ("Napoléon", 1927, ["napoleon"]),
    ("Le Cabinet du docteur Caligari", 1920, ["caligari"]),
    ("Nosferatu le vampire", 1922, ["nosferatu"]),
    ("Les Trois Lumières", 1921, ["trois lumieres", "mude tod", "der mude tod"]),
    ("Metropolis", 1927, ["metropolis"]),
    ("La Grève", 1924, ["greve", "stachka", "strike"]),
    ("Le Cuirassé Potemkine", 1925, ["potemkine", "potemkin"]),
    ("La Mère", 1926, ["mere", "mat"]),
    ("L'Homme à la caméra", 1929, ["homme a la camera", "man with a movie camera"]),
    ("La Coquille et le Clergyman", 1928, ["coquille", "clergyman"]),
    ("Un chien andalou", 1929, ["chien andalou"]),
    ("L'Âge d'or", 1930, ["age d or"]),
    ("Le Sang d'un poète", 1932, ["sang d un poete"]),
    ("La Chevauchée fantastique", 1939, ["chevauchee fantastique", "stagecoach"]),
    ("Autant en emporte le vent", 1939, ["emporte le vent", "gone with the wind"]),
    ("Citizen Kane", 1941, ["citizen kane"]),
    ("Casablanca", 1942, ["casablanca"]),
    ("Rome, ville ouverte", 1945, ["rome ville ouverte", "roma citta aperta"]),
    ("Païsa", 1946, ["paisa"]),
    ("Le Voleur de bicyclette", 1948, ["voleur de bicyclette", "bicycle thieves", "ladri di biciclette"]),
    ("La Terre tremble", 1948, ["terre tremble", "terra trema"]),
    ("Le Beau Serge", 1958, ["beau serge"]),
    ("Les Quatre Cents Coups", 1959, ["quatre cents coups"]),
    ("À bout de souffle", 1960, ["bout de souffle"]),
    ("Cléo de 5 à 7", 1962, ["cleo de 5"]),
    ("Contes cruels de la jeunesse", 1960, ["contes cruels", "cruel story of youth"]),
    ("La Pendaison", 1968, ["pendaison", "koshikei", "death by hanging"]),
    ("La Femme insecte", 1963, ["femme insecte", "insect woman"]),
    ("Éros + Massacre", 1969, ["eros", "massacre"]),
    ("Le Miroir aux alouettes", 1965, ["miroir aux alouettes", "shop on main street", "obchod na korze"]),
    ("Les Petites Marguerites", 1966, ["petites marguerites", "sedmikrasky", "daisies"]),
    ("Trains étroitement surveillés", 1966, ["trains etroitement", "ostre sledovane vlaky", "closely watched"]),
    ("Au feu, les pompiers !", 1967, ["pompiers", "hori ma panenko", "firemen"]),
    ("In the Mood for Love", 2000, ["mood for love", "huayang"]),
    ("Mulholland Drive", 2001, ["mulholland"]),
    ("Mad Max: Fury Road", 2015, ["fury road", "mad max"]),
    ("Parasite", 2019, ["parasite", "gisaengchung"]),
]
people = [
    "Louis Lumière", "Auguste Lumière", "Georges Méliès", "D.W. Griffith", "Charlie Chaplin",
    "Buster Keaton", "Louis Delluc", "Abel Gance", "Jean Epstein", "Germaine Dulac",
    "Robert Wiene", "F.W. Murnau", "Fritz Lang", "Conrad Veidt", "Sergueï Eisenstein",
    "Dziga Vertov", "Lev Koulechov", "Vsevolod Poudovkine", "Luis Buñuel", "Salvador Dalí",
    "Man Ray", "Antonin Artaud", "Jean Cocteau", "John Ford", "Alfred Hitchcock",
    "Howard Hawks", "Orson Welles", "Victor Fleming", "Michael Curtiz", "Roberto Rossellini",
    "Vittorio De Sica", "Luchino Visconti", "Cesare Zavattini", "François Truffaut",
    "Jean-Luc Godard", "Agnès Varda", "Éric Rohmer", "Claude Chabrol", "Nagisa Ōshima",
    "Masahiro Shinoda", "Shohei Imamura", "Kijū Yoshida", "Miloš Forman", "Věra Chytilová",
    "Jiří Menzel", "Jaromil Jireš", "Ján Kadár", "Elmar Klos", "Wong Kar-wai", "David Lynch",
    "George Miller", "Bong Joon-ho", "Christopher Nolan", "Denis Villeneuve", "Celine Sciamma",
]

lines = []
for title, year, keys in films:
    hits = []
    for movie in movies:
        if any(key in movie["titles"] for key in keys) and abs((movie["year"] or 0) - year) <= 2:
            hits.append(f"{movie['code']}({movie['year']})")
    lines.append(f"FILM\t{title}\t{year}\t{' | '.join(hits) if hits else 'MISSING'}")
lines.append("")
for name in people:
    code = directors.get(fold(name))
    lines.append(f"PERSON\t{name}\t{code or 'MISSING'}")
(ROOT / "tools/output/_parcours_match.txt").write_text("\n".join(lines), encoding="utf-8")
print("films", sum(1 for line in lines if line.startswith("FILM")))
