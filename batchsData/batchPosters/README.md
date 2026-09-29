# Batch TMDB Urbinema

Script **hors APK** : l’application n’appelle jamais TMDB. Python 3.9+
(bibliothèque standard uniquement). Clé API dans `.env` local, jamais dans
Gradle. Voir `specs/ASSETS.md`.

Un seul point d’entrée : `posters_batch.py` (ou `run.ps1`). **Deux modes
de travail**, plus deux commandes utilitaires.

| Commande | Mode | Entrée | Sortie |
| --- | --- | --- | --- |
| `fetch` (alias `posters`) | **Affiches** | CSV / TXT, 1 ligne = 1 film | `{CODE}.jpg` dans `output/posters/` |
| `catalog` | **Fiches + affiches** | idem | JSON `output/catalog/movies.json` **et** les affiches |
| `generate` | utilitaire | pack `catalog_v1.json` | réécrit `input/input_movies.txt` |
| `all` | utilitaire | pack | `generate` puis `fetch` (affiches **seulement**) |

`catalog --no-posters` : JSON seulement, pas d’images.

---

## 0. Prérequis (une fois)

1. Python 3.9+ (`python --version`).
2. Compte gratuit [themoviedb.org](https://www.themoviedb.org/) →
   [Paramètres → API](https://www.themoviedb.org/settings/api) → **Clé d’API v3**
   (~32 caractères). Pas le jeton JWT long dans `TMDB_API_KEY`.
3. Dans `batchsData/batchPosters/` :

```powershell
cd D:\Programs\Android_Studio\projets\Urbinema\batchsData\batchPosters
copy .env.example .env
```

4. Coller dans `.env` :

```env
TMDB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Optionnel : `TMDB_ACCESS_TOKEN=` (jeton v4, prioritaire s’il est rempli).
Ne **pas** commiter `.env`.

---

## 1. Comment lancer

Toujours depuis `batchsData/batchPosters/` (sinon `run.ps1` s’y place tout seul).

### Mode affiches

Télécharge uniquement les posters, nommés comme `movies.code`.

```powershell
python posters_batch.py fetch
python posters_batch.py fetch --limit 5
python posters_batch.py posters --dry-run
.\run.ps1 -Action fetch -Limit 5
```

Pour (re)générer la liste depuis le pack de l’app **puis** tout télécharger :

```powershell
python posters_batch.py all
.\run.ps1
```

### Mode fiches + affiches

Construit un JSON collable dans `catalog_v1.json` (`movies[]`) et télécharge
les affiches des mêmes films.

```powershell
# CSV d’exemple (1 film)
python posters_batch.py catalog --input input/example_movies.csv

# Ton CSV
python posters_batch.py catalog --input chemin\vers\films.csv

# JSON seulement (pas d’images)
python posters_batch.py catalog --input films.csv --no-posters

# Les N premières lignes du CSV par défaut (input/input_movies.txt)
python posters_batch.py catalog --limit 3

.\run.ps1 -Action catalog -Input input/example_movies.csv
.\run.ps1 -Action catalog -Input films.csv -NoPosters
```

### Options communes

| Option | Effet |
| --- | --- |
| `--input CHEMIN` | CSV / TXT à lire (sinon `inputFile` de `config.json`) |
| `--limit N` | N premières lignes utiles seulement |
| `--force` | retélécharge une affiche déjà présente |
| `--dry-run` | parle à TMDB, **n’écrit pas** les images (le JSON `catalog` est quand même écrit) |
| `--no-posters` | mode `catalog` : pas d’affiches |
| `--config` | autre `config.json` |

Équivalents `run.ps1` : `-Action`, `-Input`, `-Limit`, `-Force`, `-DryRun`,
`-NoPosters`.

---

## 2. Quoi mettre en entrée

Un fichier **UTF-8**, **une ligne = un film**. Commentaires `#` ignorés.
Séparateur `;` (préféré) ou `,`. En-tête optionnel.

Fichier par défaut : `input/input_movies.txt` (produit par `generate`).
Exemple annoté : `input/example_movies.csv`.

### Sans en-tête (comme `generate`)

```text
"titre FR";année;"réalisateur";CODE;"titre original";demand;tmdbId
```

Minimum : titre + année.

```text
"Le Voyage de Chihiro";2001
"Le Voyage de Chihiro";2001;"Hayao Miyazaki";LE_VOYAGE_DE_CHIHIRO_2001;"千と千尋の神隠し"
```

### Avec en-tête

Noms reconnus (casse indifférente) : `frenchTitle` / `title` / `titre`,
`releaseYear` / `year` / `annee`, `director` / `realisateur`, `code`,
`originalTitle`, `demand`, `tmdbId`.

```text
frenchTitle;releaseYear;director;code;originalTitle
"Le Voyage de Chihiro";2001;"Hayao Miyazaki";LE_VOYAGE_DE_CHIHIRO_2001;"千と千尋の神隠し"
```

| Champ | Obligatoire | Rôle |
| --- | --- | --- |
| titre FR | **oui** | recherche TMDB (`fr-FR` puis `en-US`) |
| année | **oui** | filtre d’année |
| réalisateur | non | départage les homonymes ; rattache un code déjà au pack |
| CODE | non | nom de l’affiche et `movies.code` ; sinon slug `TITRE_ANNEE` |
| titre original | non | 2ᵉ recherche si le titre FR est ambigu |
| demand | non | levier d’exigence A, 0 à 1, défaut `0.70` |
| tmdbId | non | saute la recherche, fiche TMDB directe |

Le `CODE` peut s’écrire `LE_VOYAGE_DE_CHIHIRO_2001` ou `[LE_VOYAGE_DE_CHIHIRO_2001]`.

`python posters_batch.py generate` relit
`app/src/main/assets/catalog/catalog_v1.json` et réécrit
`input/input_movies.txt` (sans en-tête).

---

## 3. Quoi récupérer en sortie

```text
batchPosters/
├── input/
│   ├── input_movies.txt          ← liste du pack (après generate)
│   └── example_movies.csv        ← exemple 1 film
├── output/
│   ├── posters/{CODE}.jpg        ← affiches (fetch et catalog)
│   ├── catalog/movies.json       ← fiches (catalog seulement)
│   └── reports/
│       ├── fetch_report.csv      ← suivi mode affiches
│       ├── catalog_report.csv    ← suivi mode catalog
│       └── fetch_log.txt
└── posters_batch.py
```

Rien n’est copié dans l’APK tout seul.

### Mode affiches (`fetch`)

- Fichiers : `output/posters/{CODE}.jpg` (parfois `.webp` / `.png`).
- Rapport : `output/reports/fetch_report.csv`.
- Ensuite, **à la main** : copier vers
  `app/src/main/assets/media/posters/` puis Rebuild Android Studio.

Les fichiers déjà présents sont **sautés** (`skipExisting: true`), sauf
`--force`.

### Mode catalog

- JSON : `output/catalog/movies.json`
- Affiches : mêmes `{CODE}.jpg` que ci-dessus (sauf `--no-posters`)
- Rapport : `output/reports/catalog_report.csv`

Structure du JSON :

```json
{
  "generatedAt": "2026-09-19T16:27:52Z",
  "source": "tmdb",
  "movies": [ ],
  "newDirectors": [ ],
  "newCountries": [ ]
}
```

- **`movies`** : tableau à coller (ou fusionner) dans `catalog_v1.json` →
  `movies`. Chaque objet suit le schéma `MovieImport`.
- **`newDirectors`** : réalisateurs **absents du pack**. Les ajouter d’abord
  dans `directors[]`, sinon l’import Room refuse le film.
- **`newCountries`** : idem pour un pays sans code ISO déjà connu.

Exemple d’objet `movies[]` :

```json
{
  "code": "LE_VOYAGE_DE_CHIHIRO_2001",
  "originalTitle": "千と千尋の神隠し",
  "frenchTitle": "Le Voyage de Chihiro",
  "releaseYear": 2001,
  "durationMinutes": 126,
  "format": "FEATURE",
  "synopsis": "…",
  "historicalDistance": 0.37,
  "artisticDemand": 0.65,
  "historicalRichness": 0.63,
  "culturalRichness": 0.67,
  "countries": [{ "code": "JAPAN", "isPrimary": true }],
  "directors": [{ "code": "HAYAO_MIYAZAKI", "billingOrder": 0 }],
  "genreCodes": ["ANIMATION", "AVENTURE"],
  "characteristicCodes": ["ANIMATION_DAUTEUR"]
}
```

Champs remplis depuis TMDB autant que possible : titres FR / original, année,
durée, synopsis FR, pays (ISO → codes du pack), réalisateurs (match sur le
pack ou code généré), genres TMDB mappés, mots-clés, translations.
`format` : `SHORT` < 40 min, `MEDIUM` < 60, `FEATURE`, `EXTENDED` ≥ 180.
H/A/R/C : formule de `specs/FORMULE_MATHEMATIQUE.txt` (`demand` CSV ou 0,70).
Drapeaux `isSilent` / `isBlackAndWhite` / `isExperimental` seulement s’ils
sont vrais.

Les **caractéristiques** (courants, mouvements) sont un heuristique
(pays + années + keywords + héritage du réalisateur déjà au catalogue).
**Relire avant collage** dans le pack.

Durée TMDB peut différer d’1 minute de la fiche éditoriale (ex. Chihiro
126 vs 125).

---

## 4. Recette type : ajouter des films au catalogue

1. Préparer un CSV (titre + année au minimum).
2. `python posters_batch.py catalog --input mon.csv`
3. Ouvrir `output/catalog/movies.json`.
4. Si `newDirectors` / `newCountries` n’est pas vide : les copier dans le
   pack **avant** les films.
5. Copier les objets de `movies` dans `catalog_v1.json`.
6. Copier les JPG vers `app/src/main/assets/media/posters/`.
7. Incrémenter `"version"` du pack JSON si tu veux un réimport sur un
   téléphone déjà installé.
8. Rebuild / réinstall selon `specs/SPECIFICATION_DEVELOPPEUR.md` §4.2.

---

## 5. Comment ça marche (TMDB)

1. Recherche `GET /3/search/movie` (titre FR, puis original). Un titre FR
   ambigu (*Sortilèges*) ne bloque pas la recherche du titre original
   (*Out of the Past*).
2. Détail `GET /3/movie/{id}` :
   `append_to_response=credits,images,keywords,translations,alternative_titles`.
3. Score (année, titre, réalisateur). Date TMDB très décalée acceptée si
   titre **et** réalisateur collent (ex. *Out 1* 1971 vs 1990).
4. Affiche : langue `fr`, puis `xx`, puis `en` →
   `https://image.tmdb.org/t/p/w780{poster_path}`.

**ThePosterDB n’a pas d’API.** En cas d’échec, le rapport CSV contient une
URL de recherche manuelle. Sauver l’image sous `{CODE}.jpg` soi-même.

### Statuts (`*_report.csv`)

| status | Signification |
| --- | --- |
| `OK` | affiche et/ou fiche écrites |
| `SKIP_EXISTING` | affiche déjà sur disque (`fetch` s’arrête là ; `catalog` interroge quand même TMDB pour le JSON) |
| `DRY_RUN` | match TMDB, pas d’écriture d’image |
| `NOT_FOUND` | pas de match assez sûr |
| `NO_POSTER` | fiche TMDB OK, pas d’image (`catalog` écrit quand même le JSON) |
| `ERROR` | réseau / HTTP / disque |

---

## 6. API TMDB (debug)

Auth : query `api_key=` (clé v3) **ou** header `Authorization: Bearer` (v4).

```text
GET /3/search/movie?query=...&primary_release_year=2001&language=fr-FR
GET /3/movie/{id}?language=fr-FR&append_to_response=credits,images,keywords,translations,alternative_titles
https://image.tmdb.org/t/p/w780{poster_path}
```

Tailles courantes : `w342`, `w500`, `w780`, `original` (souvent trop lourd
pour l’APK).

---

## 7. `config.json`

| Clé | Défaut | Effet |
| --- | --- | --- |
| `catalogPath` | pack de l’app | source de `generate` + codes pays / réalisateurs / genres |
| `inputFile` | `input/input_movies.txt` | CSV par défaut |
| `outputDir` | `output/posters` | affiches |
| `catalogOutputFile` | `output/catalog/movies.json` | JSON mode catalog |
| `reportFile` | `output/reports/fetch_report.csv` | suivi affiches |
| `catalogReportFile` | `output/reports/catalog_report.csv` | suivi catalog |
| `posterSize` | `w780` | taille TMDB |
| `preferredLanguages` | `fr`, `xx`, `en` | choix d’affiche |
| `yearTolerance` | `1` | écart d’année accepté |
| `sleepSeconds` | `0.3` | pause anti rate-limit |
| `skipExisting` | `true` | ne pas écraser une affiche |
| `maxSearchResults` | `5` | candidats scorés **par** requête de titre |
| `defaultDemand` | `0.7` | A si le CSV n’a pas `demand` |

Pour un film mal matché : corriger la ligne (titre original, réalisateur ou
`tmdbId`) et relancer `fetch` / `catalog` sur ce CSV réduit.
