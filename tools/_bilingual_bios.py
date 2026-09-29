"""Fetch a French and an English biography for every director. Resumable."""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
sys.path.insert(0, str(ROOT / "batchsData" / "batchReals"))
from reals_batch import fold, matches, queries_for, search_people  # noqa: E402
from posters_batch import TmdbClient, load_env  # noqa: E402

FOOTER = re.compile(
    r"(source\s*:\s*article\b.*wikip|"
    r"description (de l'article ci-dessus|above from the wikipedia)|"
    r"licensed under cc-by-sa.*wikipedia|"
    r"^©\s*wikip|"
    r"traduit avec www\.deepl\.com)",
    re.I,
)


def strip_wiki(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").strip()
    parts = re.split(r"\n\s*\n", cleaned)
    while parts:
        lines = parts[-1].split("\n")
        changed = False
        while lines and FOOTER.search(lines[-1].strip()):
            lines.pop()
            changed = True
        if lines and not changed and FOOTER.search(parts[-1]):
            parts.pop()
            continue
        rebuilt = "\n".join(lines).strip()
        if not rebuilt:
            parts.pop()
            continue
        parts[-1] = rebuilt
        break
    return "\n\n".join(part.strip() for part in parts if part.strip()).strip()


def biography(client: TmdbClient, person_id: int, language: str) -> str:
    payload = client.request_json(f"/person/{person_id}", {"language": language})
    return strip_wiki(str(payload.get("biography") or ""))


load_env(ROOT / "batchsData" / "batchPosters" / ".env")
client = TmdbClient(os.environ.get("TMDB_API_KEY", ""), os.environ.get("TMDB_ACCESS_TOKEN", ""), 0.12)
pack = json.loads((ROOT / "app/src/main/assets/catalog/catalog_v3.json").read_text(encoding="utf-8"))
out = ROOT / "tools" / "output" / "bios_lang.json"
done = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
rows = [
    {
        "code": director["code"],
        "firstName": director.get("firstName") or "",
        "lastName": director.get("lastName") or "",
        "displayName": director.get("displayName") or director["code"],
    }
    for director in pack["directors"]
    if director["code"] not in done
]
print(f"todo={len(rows)} already={len(done)}", flush=True)
ok = miss = 0
for index, row in enumerate(rows, start=1):
    chosen_id = None
    best = (-1, -1.0)
    try:
        for item in search_people(client, queries_for(row)):
            details = client.request_json(
                f"/person/{int(item['id'])}",
                {"language": "en-US"},
            )
            if not matches(row["displayName"], details):
                continue
            score = (1 if details.get("profile_path") else 0, float(item.get("popularity") or 0))
            if score > best:
                best = score
                chosen_id = int(item["id"])
        record = {"status": "NOT_FOUND", "fr": "", "en": ""}
        if chosen_id is not None:
            french = biography(client, chosen_id, "fr-FR")
            english = biography(client, chosen_id, "en-US")
            record = {"status": "OK", "tmdbId": chosen_id, "fr": french, "en": english}
            ok += 1
        else:
            miss += 1
    except Exception as exc:
        record = {"status": "ERROR", "fr": "", "en": "", "error": str(exc)}
        miss += 1
    done[row["code"]] = record
    if index % 20 == 0:
        out.write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"progress={index} ok={ok} miss={miss}", flush=True)

out.write_text(json.dumps(done, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"done ok={ok} miss={miss} stored={len(done)}", flush=True)
