from pathlib import Path
raw = Path(r"D:\Programs\Android_Studio\projets\Urbinema\specs\Listes_Fonctionnelles\Listes_Des_Parcours.txt").read_text(encoding="utf-8")
section = raw.split("# WORK-IN PROGRESS")[0]
body = section.split("**Courants** :", 1)[1]
idx = body.find("Films clés")
Path(r"D:\Programs\Android_Studio\projets\Urbinema\tools\output\_repr_films.txt").write_text(repr(body[idx:idx+700]), encoding="utf-8")
