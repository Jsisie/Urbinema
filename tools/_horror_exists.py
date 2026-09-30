"""See which requested horror titles and directors are already in the catalog."""
import json
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
chars = "\n".join(f"{c['code']} | {c['name']}" for c in pack["characteristics"])
dirs = "\n".join(f"{d['code']} | {d['displayName']}" for d in pack["directors"])
needles = [
    "argento", "bava", "rollin", "kawalerowicz", "ershov", "kropachyov", "zulawski", "żuławski",
    "harvey", "gunn", "gillen", "ormsby", "romero", "luna", "teshigahara", "oshima", "ōshima",
    "harada", "jee-woon", "chan", "nimibutr", "il-gon", "haggard", "wheatley", "eggers",
    "feigelfeld", "tsukamoto", "cronenberg", "palfi", "pálfi", "ducournau", "weir", "winner",
    "hadzihalilovic", "cosmatos", "fisher", "reeves", "craven", "cunningham", "nakata", "miike",
    "shimizu", "pang", "serrador", "ibanez", "ibáñez", "amenabar", "amenábar", "toro", "bayona",
    "nyby", "hawks", "arnold", "mitchell", "aster", "peele", "hooper", "raimi", "reiner",
    "demme", "boyle", "armstrong", "polanski", "bunuel", "buñuel", "clarke",
]
lines = ["=== chars ===", chars, "", "=== directors hit ==="]
for d in pack["directors"]:
    blob = (d["code"] + " " + d["displayName"]).casefold()
    if any(n in blob for n in needles):
        lines.append(f"{d['code']} | {d['displayName']}")
lines.append("")
lines.append("=== movies hit ===")
for m in pack["movies"]:
    blob = (m["code"] + " " + (m.get("frenchTitle") or "") + " " + (m.get("originalTitle") or "")).casefold()
    years = {1951, 1955, 1957, 1958, 1960, 1961, 1962, 1964, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1980, 1981, 1982, 1984, 1985, 1987, 1989, 1990, 1991, 1996, 1998, 1999, 2001, 2002, 2004, 2006, 2007, 2010, 2013, 2014, 2015, 2017, 2018, 2019, 2021, 2022}
    if m["releaseYear"] in years and any(n in blob for n in (
        "oiseau", "tenebre", "ténèbre", "phenomena", "phénomène", "archibald", "masque du demon", "mask of satan",
        "danse des vampire", "fearless vampire", "marque du diable", "mark of the devil", "levres de sang", "lèvres de sang",
        "mere jeanne", "mère jeanne", "viy", "vij", "diable", "szamanka", "carnival", "ganja", "deranged",
        "martin", "angoisse", "angoisse", "femme des sables", "woman in the dunes", "empire des sens", "in the realm",
        "inugami", "trois histoires", "three", "spider forest", "malevolent", "blood on satan", "penda",
        "field in england", "witch", "hagazussa", "tetsuo", "existenz", "taxiderm", "titane",
        "derniere vague", "dernière vague", "last wave", "sentinelle", "sentinel", "innocence",
        "black rainbow", "lighthouse", "frankenstein", "dracula", "inquisiteur", "witchfinder",
        "derniere maison", "dernière maison", "last house", "vendredi", "friday the 13", "griffes",
        "nightmare", "scream", "ring", "audition", "kairo", "pulse", "ju-on", "grudge", "the eye",
        "residence", "résidence", "revoltes", "révoltés", "who can kill", "autres", "echine", "échine",
        "orphelinat", "orpanage", "chose d", "thing from", "retrecit", "rétrécit", "shrinking",
        "it follows", "heredit", "hérédit", "us", "nope", "poltergeist", "evil dead", "misery",
        "silence des agneaux", "silence of the lambs", "28 days", "28 jours", "midsommar",
    )):
        lines.append(f"{m['code']} | {m.get('frenchTitle')} | {m['releaseYear']}")

out = ROOT / "tools/output/_horror_exists.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("chars", len(pack["characteristics"]), "dirs", len(pack["directors"]))
