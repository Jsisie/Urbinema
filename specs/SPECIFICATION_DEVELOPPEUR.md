# Spécification développeur — Urbinema

**Version :** 1.12 — 0.3.5  
**Date :** 2026-10-01  
**Statut :** document de reprise. Il décrit le code réellement livré.

Ce document est le mode d’emploi pour reprendre le projet. Les décisions
produit restent dans `DECISIONS_ACTEES.txt`. Les formules restent dans
`FORMULE_MATHEMATIQUE.txt` et `FORMULE_NIVEAUX_XP.txt`. En cas d’écart, le
code et les tests font foi.

**Lire les docs avec l’app à côté.** Ce fichier décrit le code **0.3.5**
(`versionCode` 24). Les cahiers fonctionnel / IHM / technique, les décisions
et la FAQ collent à cet état. Un comportement vu à l’écran a toujours une
trace ici (navigation §2, persistence §3, règles §2.4 / §7, carte §2.2.1).
Un chiffre de spec (XP quêtes 100/250/500, **25 XP** film si collection suivie, 3 badges, pack JSON **47**, Room **11**, cliquet,
10 collections en cours, 10 avatars) se retrouve dans le code (`FunctionalLimits`) et, s’il est visible, dans `strings.xml`.

---

## 0. En 30 secondes

Urbinema est une application Android **100 % locale**.

- Le fichier JSON `app/src/main/assets/catalog/catalog.json` est **uniquement
  une graine éditoriale**. Il est relu quand sa `version` est **strictement
  supérieure** à celle déjà en Room. Les tables `user_*` ne sont jamais touchées.
  `catalog_v1.json` est l’archive V1 ; `catalog_v2.json` l’archive V2 ;
  `catalog_v3.json` est le pack courant recopié vers `catalog.json`.
- Un **nouveau profil** démarre à **0 film vu, rang Novice, niveau 1, 0 XP**.
  Le catalogue V3 part du V2 dédoublonné (titre + année + réalisateur).
- Ensuite, **tout vit dans SQLite** : `urbinema.db`.
- Fermer l’appli, tuer le process, redémarrer le téléphone : films vus,
  collections terminées, badges, XP, rang, quêtes, pseudo et thème
  **restent**.
- Une future mise à jour du JSON **relit le pack** seulement si sa `version`
  est strictement supérieure. L’upsert se fait par codes stables. Les tables
  `user_*` ne sont jamais touchées.

---

## 1. Lancer le projet

### 1.1 Prérequis

| Élément | Valeur |
| --- | --- |
| IDE | Android Studio (Narwhal / Hedgehog ou plus récent) |
| Application ID | `fr.jsisie.urbinema` |
| Module Gradle / Android Studio | `:urbinema` (dossier physique `app/`) |
| versionName / versionCode | `0.3.5` / `24` |
| APK debug | `urbinema-debug.apk` |
| minSdk | 26 |
| compileSdk / targetSdk | 36 / 36 |
| JVM du module | Java 17 |
| JVM Gradle recommandée | JBR fourni par Android Studio |
| Gradle wrapper | 8.13 |
| AGP | 8.13.2 |
| Kotlin | 2.0.21, compilateur K2 |
| UI | Jetpack Compose + Material 3 (couleurs **fixes**, pas de Material You) |

Le JBR local est déclaré dans `.gradle/config.properties` :

```text
java.home=D:\Softwares\JetBrains\ToolBox\Android Studio\jbr
```

Ce chemin dépend du poste. `local.properties` (SDK Android) aussi. Aucun des
deux ne doit être versionné.

### 1.2 Ouverture Android Studio

1. Ouvrir le dossier racine `Urbinema/` (celui qui contient `settings.gradle.kts`).
2. Laisser Gradle synchroniser.
3. Choisir un émulateur ou un téléphone **API 26+**.
4. Lancer la configuration **urbinema** (Run).

Au premier lancement l’application :

1. importe `assets/catalog/catalog.json` dans Room (si pack plus récent) ;
2. active la config de rang lissée v0.3.1 ;
3. affiche l’onboarding **pseudo + âge + avatar** s’il n’y a pas de `users` **ou** si
   `birthDate` est null (install 0.1.6 « Léo » sans âge) : insert ou update ;
4. affiche Accueil, Collections, Atlas, Parcours, Profil.

### 1.3 Ligne de commande Windows

Depuis la racine du projet, avec le JBR Android Studio dans `JAVA_HOME` :

```powershell
$env:JAVA_HOME = 'D:\Softwares\JetBrains\ToolBox\Android Studio\jbr'
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

.\gradlew.bat :urbinema:testDebugUnitTest --no-daemon
.\gradlew.bat :urbinema:assembleDebug --no-daemon
```

Tests Room (appareil ou émulateur connecté) :

```powershell
.\gradlew.bat :urbinema:connectedDebugAndroidTest --no-daemon
```

Si un daemon Gradle est coincé :

```powershell
.\gradlew.bat --stop
```

L’APK debug sort dans `app/build/outputs/apk/debug/`.

---

## 2. Comment utiliser l’application

L’interface tutoie. Les chaînes sont en français (`values/strings.xml`) et
anglais (`values-en/strings.xml`). La langue suit la locale du système.

### 2.1 Navigation

Cinq onglets bas :

| Onglet | Rôle |
| --- | --- |
| Accueil | Rang, niveau, XP, quêtes de la semaine (collées sous l’XP), **collections en cours** (suivies, **pas** à 100 %, **pas** cadenassées), historique en **titres**. Barre haute : ☰ à gauche, logo à **droite** (tap = `LogoAboutDialog`, version `BuildConfig.VERSION_NAME`). |
| Collections | Groupées par `track`. Initiation ouverte ; cadenas Initiation (≥ 1 Vu) puis cadenas **entre groupes** (2 collections commencées). Suivies en or. Non suivie = 0 %. Terminée = or + check. |
| Atlas | Listes (onglet). **?** = aide. **Étoiles** = carte du ciel (`atlas/sky`). |
| Parcours | Rang détaillé, quêtes, collections en cours. `?` → Aide. |
| Profil | Pseudo, rang, niveau/XP, **jusqu’à 3 badges** vitrine (maintenir = condition au-dessus du doigt), stats (totaux, pas cliquables). Réglages via l’icône ⚙ (thème, langue, grain, Aide, reset, À propos). |

Le tiroir (☰ sur **chaque onglet**) ouvre les index : rangs, badges, collections, recherche,
statistiques. Plus d’entrée « Tous les courants » : les pays et courants vivent
dans Atlas.

L’onglet actif : retaper l’onglet revient à sa page principale (pile vidée jusqu’à la racine, liste remonte en haut via `tabResetTick`). Changer d’onglet **conserve** l’écran ouvert : `selectTab` utilise `saveState = true` / `restoreState = true` (`popUpTo` start). Une fiche, le ciel ou la puce Atlas survivent au passage par un autre onglet.

### 2.2 Gestes métier V1

- Ouvrir une collection → descriptions + films de **cette** collection (refusée
  si `locked` : dialogue FR).
- **Suivre cette collection** l’ajoute à `user_followed_collections` (Accueil +
  Parcours, **sauf** si déjà 100 %). Au départ : **zéro** collection suivie.
  Unfollow interdit si `completed`.
- Ouvrir un film → fiche + **Marquer comme vu** à **la date du jour locale**
  (`LocalDate.now(ZoneId.systemDefault())`). Pas de calendrier. Le bouton passe
  tout de suite à **Film vu**, grisé, non cliquable (`optimisticWatchedIds` +
  `paintFilmWatched` avant le write Room).
- Un film ne peut être validé **qu’une fois**.
- Un pays / courant / genre / décennie n’affiche que **ses** films et **ses**
  collections éditoriales.
- Un genre sur la fiche film ouvre Atlas filtré sur ce genre.
- La validation écrit dans Room, recalcule rang + badges, met à jour les quêtes.
  Tag Logcat `UrbinemaProgress`.
- Si la collection suivie passe à 100 % : dialogue de félicitations, elle sort
  des « en cours ».
- Le rang **ne recule jamais**.
- Le niveau XP **ne recule jamais** (`users.maxLevelReached`), sauf recalage
  si le tarif film du ledger change. Un film Vu = **25 XP une fois**, et seulement s’il est dans une collection suivie.
  Quêtes 100 / 250 / 500.
- Réglages → **Réinitialiser les données** : `SettingsScreen` ouvre le
  dialogue localisé `reset_data_*`. Les chaînes sont lues **avant**
  l’`AlertDialog` (même motif que cadenas / félicitations). `RESET_CONFIRMATION_DELAY_SECONDS = 10`
  pilote un `LaunchedEffect` annulé à la fermeture ; le bouton destructif
  reste désactivé et affiche `(10)` à `(1)`, puis confirme et efface
  **uniquement** la progression. Le catalogue et le profil restent.
- Onglet Atlas = listes. Icône étoiles = carte du ciel. Tap film =
  recentrer la constellation ; tap territoire = feuille + fiche.

### 2.2.1 Carte du ciel (0.2.3)

L’onglet Atlas **est** les listes (`atlas`). Carte du ciel : `atlas/sky`.

Vue par défaut `MapLayer.AROUND_FILM` : `CinemaMapLayout.buildAround`.
Film au centre, territoires du film en **secteurs par type** (réal, pays,
genre… rayons un peu distincts), jusqu’à 12 films liés plus loin.
`CinemaMapLayout.dedupeConstellation` enlève un nœud homonyme (collection
« Akira Kurosawa » si le réalisateur est déjà là). Tap un autre film =
recentre. Tap un territoire = feuille + navigation. Les puces sont
Autour du film, Pays et Décennies. `MAX_SCALE = 14`. Fiche film : « Voir
sur la carte ». Recherche titre : voir ci-dessous (`SkyMapExpandingSearch`).

Couleurs **par type**, pas seulement par état d’exploration : films ivoire,
vus / centre or, réalisateurs cyan `#5EC8D8`, pays corail `#E07A5F`,
genres rose `#D489C0`, courants violet `#7A5CB8`, décennies orange
`#E0A45C`, collections bleu `#6EA8FF`. Non exploré = cercle pointillé
de la couleur du type. Légende colorée sous le hint, en bas à gauche.

`MainViewModel.cinemaMap(layer, focusMovieCode)`. Tests : `CinemaMapTest`.

Le titre de barre est `R.string.sky_map` (« Carte du ciel »). À **droite**,
`SkyMapExpandingSearch` : cercle 40 dp, s’ouvre en pilule 228 dp
(`animateDpAsState` 280 ms, `RoundedCornerShape` 50 %), icône ancrée à
droite, 8 dp avant le `?`. `searchMovies` / `movieTitleHits` sur VF et VO.
Tap un hit : `mapFocus` + `AROUND_FILM` et fermeture. Champ vide + IME
masqué : `onDismiss`.

Le Canvas reste `#07060D` en salle obscure. En salle éclairée il reprend
le papier du thème. Cahier technique §8, IHM §10, fonctionnel §11.

### 2.3 Thème et grain

`UrbinemaThemeMode` : Dark, Light, System, Cyanotype, Tirage, Rayonnage,
Affiche, Velours, NuitAmericaine. Persistant via DataStore
(`ThemePreference`). Pas de couleurs dynamiques Material You. Palettes
extra : Source Serif 4 + Source Sans 3 (`SourceTypography`). Libellés du
sélecteur en anglais (`dark_theme`, `theme_cyanotype`, …) ; « Thème » /
« Fermer » traduits.

Grain argentique : switch persisté. `Modifier.filmGrain` sur le `Box`
racine (`drawBehind`, tuile 128 px `ImageShader` Repeat). Voile ~0,032,
specks ~7–9 %. Plus de composable overlay plein écran.

`LocalizedContent` fournit `LocalContext` et `LocalConfiguration`. Les
`AlertDialog` (badges, collections, **reset données**) lisent les chaînes via
`stringResource` **avant** le dialogue, sinon la fenêtre Android ignore
la locale Compose. Le menu de tri stats pré-résout aussi ses libellés.

Pop-up badge : codes déjà fêtés dans DataStore
(`badge_celebration_seeded` + `badge_celebration_codes`). Premier snapshot
Room + prefs = marquer comme vus, **pas** de replay à la réouverture.
Nouveaux codes seulement après hydratation. Reset données : liste vide,
seeded reste vrai. La file contient les `BadgeUi`, pas seulement leurs noms,
afin que `BadgeUnlockedDialog` affiche aussi `BadgeArtwork` sous le message.

Les résumés de films passent les crédits ordonnés à `listDirectorLabel` :
un nom par ligne, deux noms maximum et `...` après le deuxième. Les cartes
réservent donc deux lignes au réalisateur sans réduire la place du titre.

    Historique Accueil : 30 dernières (`HistoryUi.HOME_PREVIEW_LIMIT`) + bouton
« Voir tout l’historique » (`history`). DAO `observeActivity` LIMIT 2000.
Libellés via `stringResource` (`history_*_body`), pas de FR/EN figé dans
le ViewModel.

### 2.3.1 Mode dev

Dans `gradle.properties`, la ligne `urbinema.devTools=false` est le défaut.
La passer à `true`, puis recompiler. Elle alimente `BuildConfig.DEV_TOOLS`
dans `app/build.gradle.kts`. Tant qu’elle est fausse, le bouton n’existe pas.

Le switch **Mode dev** est dans Réglages, juste avant le grain. Il est mémorisé
(DataStore `dev_mode`) et ne fait rien si l’APK a été compilé avec la
propriété à false.

Activé : les collections ne sont plus verrouillées par le palier précédent.
Sous le rang (Accueil et Profil), une barre et `score / reste` jusqu’au
prochain rang (plancher → seuil, gain du dernier film, Vw, D, P, rang brut),
puis la même chose pour l’XP du niveau (`XP dans le niveau / reste`).

### 2.4 Règles collections (code 0.1.11)

Constante Initiation : `COLLECTION_INITIATION`. Premier déblocage =
au moins un film d’Initiation dans `user_movies`. Hollywood classique et
tout le reste restent **cadenassés** tant que cette porte n’est pas ouverte.
Le cliquet `users.unlockedTrackOrdinal` **ne contourne jamais** Initiation :
un reset (bouton Réglages) remet le cliquet à −1 **et** vide `user_movies`,
donc Hollywood redevient inaccessible.

Un palier « commencé » pour ouvrir le groupe suivant = collection **suivie**
et au moins 2 films vus. Les titres partagés (Initiation ∩ Nouvel Hollywood)
ne comptent pas sans suivi. Un groupe vide ne débloque **pas** le suivant.
Au plus **10** collections en cours (`FunctionalLimits.MAX_IN_PROGRESS_COLLECTIONS`).

Le catalogue est chargé **une fois** après bootstrap (`allMoviesWithRelations`),
pas via 12 `Flow` `@Relation`. Les `refresh()` UI sont debounce
(`UI_REFRESH_DEBOUNCE_MS`).

`currentCollections` (Accueil / Parcours) = followed && !completed &&
!locked.

Les dialogues de cadenas résolvent les chaînes **avant** l’`AlertDialog`
(locale Compose du dialogue Android sinon).

Profil : au plus **3 badges** (`users.showcaseBadgeCodes`). Avatar packagé
`users.avatarCode` (`AVATAR_01`…), choisi à l’onboarding et changeable dans
Réglages. Liste complète : roue en haut à droite, choix parmi les badges
débloqués. Non obtenus en niveaux de gris. Ordre liste : rareté (difficulté)
puis `code` (`001` avant `002`).

`CollectionTrack` : GATEWAY / CLUB / DARKROOM / CINEMATHEQUE / OFFSCREEN.
Legacy JSON `JOURNEY` → CLUB, `DEMANDING` → CINEMATHEQUE.

Libellés barre basse : `maxLines = 1`, 11 sp.

Pays : noms sans accent pour le tri (`Egypte`, `Etats-Unis`).

---

## 3. Données : JSON vs Room (persistence)

C’est le point le plus important.

### 3.1 Ce que n’est PAS le JSON

`catalog.json` n’est **pas** le stockage runtime. Ce n’est pas un fichier
lu/écrit à chaque ouverture. Ce n’est pas un savegame. Modifier le JSON **après**
le premier lancement **ne change rien** sur un téléphone déjà initialisé.

### 3.2 Ce qu’est le JSON

C’est un **pack éditorial versionné**, embarqué dans l’APK :

```text
app/src/main/assets/catalog/catalog.json
```

Il décrit le monde : films, pays, continents, réalisateurs, caractéristiques,
genres, ères, collections, 10 rangs, 38 badges, 59 quêtes types (19 Bronze, 20 Argent, 20 Or).
Le pack courant est la version **47** (1613 films, 28 collections, biographies de réalisateurs et textes éditoriaux en français et en anglais quand les deux existent). `catalog.json` est la copie de `catalog_v3.json`. Les portraits sont des fichiers `assets/media/directors/{CODE}.jpg`, lus par code, sans ligne `mediaAssets`. La collection `COLLECTION_027` (« Cinéma des premiers temps ») est sur le groupe `GATEWAY`, avec 17 films de 1892 à 1906.

Titres : `originalTitle` est toujours la valeur de repli affichée.
`frenchTitle` est facultatif et ne doit exister que pour un véritable titre
français distinct. Le batch TMDB n'accepte comme titre alternatif français
que le territoire `FR` : `BE` et `CH` sont multilingues et ont déjà injecté
des titres néerlandais dans cette colonne.

Modèle Kotlin : `data/importer/CatalogPack.kt`.  
Validateur : `data/importer/CatalogValidator.kt`.  
Import transactionnel : `data/importer/CatalogImporter.kt`.

### 3.3 Ce qu’est Room

Fichier SQLite de l’app :

```text
urbinema.db
```

Nom défini par `UrbinemaDatabase.DATABASE_NAME`. Android le place dans le
répertoire privé de l’application (`databases/`). Il survit :

- à la fermeture de l’app ;
- au swipe hors de la liste des apps ;
- au redémarrage de l’appareil.

Il est perdu seulement si l’utilisateur **désinstalle** l’app, vide le
stockage de l’app, ou confirme **Réinitialiser les données** (progression
seulement).

`android:allowBackup="false"` : pas de sauvegarde automatique Google qui
réinjecterait un état inattendu.

### 3.4 Premier lancement vs lancements suivants

`AppBootstrapper.initialize()` :

1. Si le pack JSON a une `version` **strictement supérieure** à
   `catalog_versions` → upsert éditorial (codes stables). Sinon no-op.
2. Si la config active n'est pas `RANK_V031_DURATION_WEIGHTED` → désactiver
   l'ancienne, puis activer ou insérer la configuration lissée.
3. Si aucun utilisateur local → **ne rien créer**. L’UI bloque sur
   l’onboarding (pseudo + âge + avatar) puis insère `users` avec `birthDate`
   approximée (1er janvier de l’année `année_courante - âge`) et `avatarCode`.
   approximée (1er janvier de l’année `année_courante - âge`).
   Si un utilisateur existe **sans** `birthDate` → même pop-up, **update**
   username + birthDate (cas 0.1.6).

Les tables `user_*` ne sont jamais réécrites par l’import.

Donc : **aucune mise à jour JSON ne peut écraser films vus, badges,
collections terminées, XP, rang ou quêtes.**

### 3.5 Ce qui est persistant (et où)

| Donnée | Stockage | Survive à la fermeture | Effacé par reset progression | Effacé par désinstall |
| --- | --- | --- | --- | --- |
| Catalogue (films, collections, badges définitions, rangs, quêtes types, pays…) | Room `urbinema.db` | oui | non | oui |
| Films vus + date | `user_movies` | oui | oui | oui |
| Collections suivies | `user_followed_collections` | oui | oui | oui |
| Badges obtenus | `user_badges` | oui | oui | oui |
| Collections terminées / progression | dérivé de `user_movies` ∩ `collections_movies` | oui | oui | oui |
| Quêtes de la semaine + snapshots | `user_quests` | oui | oui | oui |
| XP | `xp_transactions` (ledger immuable) | oui | oui | oui |
| Rang affiché + ratchet | `users.rankingId` + `user_progress_state` | oui | oui (retour rang 1) | oui |
| Niveau max atteint | `users.maxLevelReached` | oui | oui (retour 1) | oui |
| Historique | `activity_events` | oui | oui | oui |
| Pseudo | `users.username` | oui | **non** | oui |
| Âge (année de naissance approx.) | `users.birthDate` | oui | **non** | oui |
| Avatar packagé | `users.avatarCode` | oui | **non** | oui |
| Cliquet groupes collections | `users.unlockedTrackOrdinal` | oui | oui (retour −1) | oui |
| Badges vitrine (max 3) | `users.showcaseBadgeCodes` | oui | oui | oui |
| Thème / langue / grain | DataStore `urbinema_preferences` | oui | **non** | oui |

Les collections « terminées » ne sont pas une table séparée. Une collection est
terminée **pour l’UI** quand elle est **suivie** et que tous ses films
(`collections_movies`) sont dans `user_movies`. Recalculée à chaque lecture.
Sans suivi, le pourcentage affiché reste 0.

### 3.6 Mise à jour future du catalogue

Politique V1 volontairement non définie (FAQ). Tant qu’elle n’existe pas :

- pour **développer** un nouveau pack : désinstaller l’app, ou vider les données,
  puis relancer → nouvel import ;
- pour **un utilisateur déjà en jeu** : il faudra plus tard un merge par **codes
  stables** (`SEPT_SAMOURAIS_1954`, badge `001`, collection `NEOREALISME_ITALIEN`,
  etc.), jamais par IDs Room auto-incrémentés, et **jamais** un replace des
  tables `user_*`.

Les moteurs métier (badges, rang, quêtes) identifient tout par `EditorialCode`,
pas par `movieId` / `badgeId`.

### 3.7 Inspection locale pendant le debug

Android Studio → App Inspection → Database Inspector → `urbinema.db`.

Tables utiles : `movies`, `user_movies`, `user_badges`, `xp_transactions`,
`user_quests`, `catalog_versions`, `users`.

---

## 4. Quoi charger / comment enrichir les données

### 4.1 Catalogue de démo actuel

Le pack V1 n’est **pas** le catalogue produit final (cible 20 collections, 50
caractéristiques). Pack actuel **v11** : **~405 films, 15 collections**
(Initiation en tête, 10 classiques publics). Pays sans accents. Expressionnisme
allemand en `CLUB` (Ciné-club), pas en Cinémathèque.

Films :

- `SEPT_SAMOURAIS_1954` — 七人の侍 / Les Sept Samouraïs (Kurosawa, 1954)
- `ROMA_CITTA_APERTA_1945` — Roma città aperta / Rome, ville ouverte (Rossellini, 1945)
- `CLEO_DE_5_A_7_1962` — Cléo de 5 à 7 (Varda, 1962)

Plus : 42 pays, 6 continents, 15 collections, 10 rangs,
32 badges (codes `001`–`032`), 59 quêtes types (19 Bronze, 20 Argent, 20 Or).
Une quête de courant utilise `WATCH_CHARACTERISTIC_<CODE>` (déjà résolu par
`DefaultQuestRules`) et `targetCount`. Le nombre de films d’une liste vient de
`TerritoryUi.filmCount` (Atlas) ou de la taille de la liste affichée
(section « Films · N », cartes de collection, feuille de la carte).

Pour tester la persistence : marquer un film vu, tuer l’app, relancer → le
film reste vu, l’historique et l’XP/rang aussi.

### 4.2 Ajouter un film

1. Éditer `catalog_v3.json` (puis recopie vers `catalog.json`), tableau `movies`.
2. `code` **stable, unique, immuable** (convention `TITRE_ANNEE` ASCII).
3. Un et un seul pays `isPrimary: true`.
4. `format` : `FEATURE` | `SHORT` | `MEDIUM` | `EXTENDED` | `TV_SERIES` | `TV_MINISERIES`.
5. Coefficients `historicalDistance`, `artisticDemand`, `historicalRichness`,
   `culturalRichness` ∈ [0, 1].
6. Référencer uniquement des codes déjà présents (`countries`, `directors`,
   `genreCodes`, `characteristicCodes`).
7. Relier le film à une collection via `collections[].movies`.
8. Désinstaller l’app (ou vider les données) puis relancer pour réimporter.
9. Le test `CatalogFixtureTest` doit rester vert.

### 4.3 Ajouter une collection

Dans `collections` :

```json
{
  "code": "INITIATION",
  "displayOrder": 1,
  "name": "Initiation",
  "description": "Dix classiques pour ouvrir le reste.",
  "longDescription": "Une porte d’entrée, pas un palmarès.",
  "track": "GATEWAY",
  "isPublished": true,
  "movies": [
    { "code": "LE_ROI_LION_1994", "displayOrder": 1 }
  ],
  "characteristicCodes": [],
  "countryCodes": []
}
```

`displayOrder` de collection est unique. `track` ∈ GATEWAY | CLUB | DARKROOM |
CINEMATHEQUE | OFFSCREEN (legacy JOURNEY/DEMANDING acceptés). `isPublished: true`
pour qu’elle apparaisse dans l’UI.

### 4.4 Ajouter un badge

Deux endroits, **même code** :

1. JSON `badges` : libellé, description, difficulté, catégorie. Codes `001`…`030`
   déjà pris.
2. `BadgeRegistry.initial()` : la règle Kotlin. Sans règle, le badge s’affiche
   mais ne se débloque jamais.

Ne jamais identifier un badge par son `badgeId` Room.

### 4.5 Ajouter une quête type

1. JSON `quests` avec `ruleCode`, `difficulty` (`BRONZE`/`SILVER`/`GOLD`),
   `targetCount`. Le pack en contient **50** (16 Bronze, 17 Argent, 17 Or).
2. Les codes `WATCH_COUNTRY_*`, `WATCH_CONTINENT_*`, `WATCH_GENRE_*`,
   `WATCH_CHARACTERISTIC_*`, `WATCH_DECADE_*`, `WATCH_BEFORE_*`,
   `WATCH_FROM_*`, `WATCH_RUNTIME_OVER_*` sont résolus par motif dans
   `DefaultQuestRules`. Un alias explicite n’est utile que s’il ne suit pas
   ce schéma (`WATCH_SILENT`, `WATCH_GENRE_DRAMA` → `DRAME`, `DISTINCT_*`).
3. Chaque lundi 02:00, l'app tire **au hasard une quête par palier** parmi
   celles encore **faisables** : il doit rester assez de films non vus pour
   atteindre la cible (ex. pas « 3 films italiens » s'il n'en reste plus que 2).
   Une quête devenue impossible en cours de semaine est remplacée.
4. XP figé : Bronze 100, Argent 250, Or 500. Snapshoté dans `user_quests` au
   moment de l’assignation (une modification JSON ultérieure ne change pas une
   quête déjà distribuée).

Fenêtre : lundi 02:00 heure locale → lundi suivant 02:00. Non rétroactif.

### 4.6 Médias / affiches

Dossiers et conventions : `specs/ASSETS.md`.
`MediaPaths` + `assets/media/{kind}/{CODE}.webp`.
L’app affiche un placeholder si le fichier n’existe pas. Elle n’appelle
jamais TMDB : `batchPosters/` est un script **hors APK** pour remplir
`assets/media/posters/`. Coil est déjà en dépendance.

---

## 5. Architecture

Un seul module Android `:urbinema` (dossier physique `app/`), packages Clean / MVVM.

```text
fr.jsisie.urbinema
├── UrbinemaApplication.kt     Koin + bootstrap
├── MainActivity.kt            hôte Compose
├── app/
│   ├── di/AppModules.kt
│   ├── startup/AppBootstrapper.kt
│   └── MainViewModel.kt       pont Room → UI
├── data/
│   ├── db/                    Room : entities, DAO, relations, converters
│   ├── importer/
│   ├── media/                 chemins ASSET / FILE
│   ├── preferences/           DataStore thème, langue, grain
│   └── repository/            Catalog / Progress / coordinators
├── domain/                    Kotlin pur, zéro Android
│   ├── model/
│   ├── rank/                  formule v0.3.1
│   ├── xp/                    courbe 1–50
│   ├── quest/
│   ├── badge/
│   ├── collection/
│   └── validation/
└── ui/
    ├── UrbinemaApp.kt         navigation 5 onglets
    ├── screens/
    ├── components/
    ├── model/                 contrats UI + preview
    └── theme/                 Salle obscure / Salle éclairée
```

Règles :

- `domain` n’importe pas Room, Compose, Android.
- Room est la source de vérité.
- Les IDs Room sont techniques. Les contrats métier parlent en `code`.
- `MainViewModel` mappe les entités vers les modèles UI. Les Composables ne
  connaissent pas Room.

Injection : Koin, modules dans `urbinemaModules`.

---

## 6. Schéma Room (version 10)

Export : `app/schemas/` (KSP `room.schemaLocation`).

### 6.1 Catalogue

`media_assets`, `movies`, `countries`, `continents`, `countries_continents`,
`movies_countries`, `directors`, `movies_directors`, `characteristic_types`,
`cinema_characteristics`, `directors_characteristics`, `movies_characteristics`,
`genres`, `movies_genres`, `eras`, `collections`, `collections_movies`,
`collections_characteristics`, `collections_countries`,
`collections_continents`, `collections_eras`, `rankings`, `badges`, `quests`,
`catalog_versions`, `learning_paths`, `learning_path_steps`,
`learning_path_facts`, `learning_path_figures`, `learning_path_movies`.

Contrainte physique hors annotations Room, recréée à chaque `onOpen` :

```sql
CREATE UNIQUE INDEX IF NOT EXISTS index_movies_countries_one_primary
ON movies_countries(movieId) WHERE isPrimary = 1;
```

Room ne connaît pas cet index. Toute migration doit le supprimer avant le
contrôle de schéma (`DROP INDEX IF EXISTS`), sinon l’ouverture plante.
`onOpen` le recrée juste après. `MIGRATION_7_8` ajoute `directors.biography`.
`MIGRATION_8_9` ajoute `directors.biographyEn`. Les deux retirent l'index
avant le contrôle. L'app affiche la biographie anglaise quand la langue est
l'anglais, sinon la française, et retombe sur l'autre si une langue manque.

`PRAGMA foreign_keys = ON` à chaque ouverture.

`collections.track` TEXT NOT NULL, ajouté par `MIGRATION_4_5` (défaut
`JOURNEY`). Room **v6** (`MIGRATION_5_6`) : `users.unlockedTrackOrdinal`,
`users.showcaseBadgeCodes`, `xp_transactions.source` / `movieId` (userQuestId
nullable). Room **v7** (`MIGRATION_6_7`) : `users.avatarCode`. Room **v8**
(`MIGRATION_7_8`) : `directors.biography`. Room **v9** (`MIGRATION_8_9`) :
`directors.biographyEn`. Room **v10** (`MIGRATION_9_10`) : tables des
parcours pédagogiques (ci-dessous). Elle retire aussi l'index partiel avant
le contrôle. Room **v11** (`MIGRATION_10_11`) : colonnes `*En` sur pays,
continents, courants, genres, collections, parcours (étapes, faits, figures),
rangs, badges et quêtes. L'UI prend le texte anglais si la langue est
l'anglais, sinon le français, et retombe sur l'autre si une langue manque.
Colonne film
`artisticDemand` = exigence A_f de la formule. Comment poser H/A/R/C :
`FORMULE_MATHEMATIQUE.txt` §1.bis.

### 6.2 Progression

`users`, `user_movies`, `user_followed_collections`, `user_badges`,
`user_quests`, `xp_transactions`, `activity_events`, `user_progress_state`.

`xp_transactions.userQuestId` est unique : une quête ne paie qu’une fois.

### 6.3 Moteur de rang persisté

`rank_engine_configs`, `rank_thresholds` (9 seuils, rangs 2 à 10),
`catalog_dimension_stats` (raretés Q et poids, ratchet catalogue).

### 6.4 Parcours pédagogiques

L'onglet **Parcours** (4e entrée) lit ces tables. L'ancien écran (rang, quêtes,
collections en cours) est le composable `ProgressScreen`, conservé dans
`Screens.kt`. Son appel est commenté dans `UrbinemaApp.kt`, juste au-dessus
de `PathsScreen`, avec la mention « Ancien onglet Parcours ».

La source éditoriale est `specs/Listes_Fonctionnelles/Listes_Des_Parcours.txt`.
L'app ne lit pas ce fichier. Elle lit le catalogue, clé `paths`, importée
dans Room quand `version` augmente. Pack courant : **47**.
Les champs `nameEn`, `summaryEn`, `descriptionEn`, `periodLabelEn`,
`transitionEn`, `titleEn`, `bodyEn`, `roleEn` nourrissent l'anglais.

Fichiers : `CatalogPack.kt` (`PathImport`), `CatalogImporter.persist`,
`MainViewModel` (`paths`), `ParcoursScreens.kt`. Dessins des bulles :
`app/src/main/assets/media/movements/{code du courant}.png` (aussi `.jpg` ou
`.webp`). `MediaKind.MOVEMENT`.

Forme JSON, un objet dans `paths` :

```json
{
  "code": "PARCOURS_001",
  "displayOrder": 1,
  "name": "Comment le cinéma est devenu un art",
  "summary": "Première phrase, affichée sur la liste.",
  "description": "Texte long, affiché en tête du fil.",
  "periodLabel": "1895 – aujourd'hui",
  "steps": [
    {
      "code": "PARCOURS_001_00",
      "position": 0,
      "characteristicCode": "CINEMA_MUET_MOUVEMENT",
      "name": "Cinéma muet",
      "periodLabel": "1895 – 1927",
      "description": "Texte de la fiche.",
      "facts": [{ "title": "La transition parlante", "body": "..." }],
      "figures": [{ "displayName": "Georges Méliès", "role": "Pionnier", "directorCode": "GEORGES_MELIES" }],
      "movies": ["VOYAGE_DANS_LA_LUNE_1902"],
      "transition": "Phrase vers la bulle suivante."
    }
  ]
}
```

`position` 0 est la bulle du haut. `transition` est le texte du point
d'interrogation **entre cette bulle et la suivante**. La fenêtre n'affiche
que cette phrase, sans titre et sans les noms des courants. La dernière bulle
n'a pas de `transition`. `directorCode` est facultatif : sans lui, la figure
reste du texte (acteur, théoricien). S'il est présent, il doit exister dans
`directors`. `movies` et `characteristicCode` doivent exister. L'ordre des
tableaux `facts`, `figures` et `movies` est l'ordre affiché.

Modifier un parcours : éditer `name`, `summary`, `description` ou
`periodLabel` (et les champs `*En` pour l'anglais) dans `catalog_v3.json`, copier vers `catalog.json`, monter
`version` d'un cran.

Ajouter un parcours : un nouvel objet dans `paths`, `code` et `displayOrder`
uniques, au moins une étape. La liste de l'onglet affiche chaque objet.

Ajouter un courant dans un parcours : un objet de plus dans `steps`.
`code` unique dans tout le catalogue (`PARCOURS_001_11`), `position` unique
dans ce parcours. Décaler les `position` suivantes. La `transition` de
l'étape d'avant devient le lien vers la nouvelle ; la nouvelle porte la
transition vers la suivante. Le dessin est le fichier
`media/movements/{characteristicCode}.png`. Si le courant n'existe pas encore,
l'ajouter aussi dans `characteristics` (`typeCode` déjà présent :
`MOVEMENT`, `WAVE`, `PERIOD`, `STYLE`…).

Modifier une transition : changer la chaîne `transition` de l'étape du
dessus. Chaîne vide ou champ absent : pas de point d'interrogation.

Modifier un « À savoir », une figure ou un film : éditer le tableau
correspondant. Retirer un `directorCode` rend la figure non cliquable.
Ajouter un film qui n'est pas dans `movies` : le créer (affiche dans
`media/posters/{CODE}.jpg`, réalisateur, pays, synopsis) et noter la ligne
dans `batchsData/batchPosters/input/`. Un réalisateur nouveau : fiche dans
`directors`, photo `media/directors/{CODE}.jpg`, ligne dans
`batchsData/batchReals/input/input_directors.txt`.

Après toute modification du JSON : `version` strictement plus grande, copie
`catalog_v3.json` → `catalog.json`. L'import ne vide pas la progression.

---

## 7. Moteurs métier — où changer les formules

### 7.1 Rang v0.3.1

Fichiers : `domain/rank/RankEngine.kt`, `RankDefaults`.

- Volume / diversité / profondeur, ρ = 0,5 (`attenuationExponent`).
- Volume lissé : `1,02 × ln(1 + Vw / 25)` via `volumeScore`.
- Diversité lissée : `Dmax × (D / Dmax)^1,2` via
  `smoothedDiversity`. `Dmax` est la somme des références de tous les
  territoires ; la couverture complète conserve ainsi son ancienne valeur.
- Durée : `RankDurationDefaults` contient tous les ancrages
  (`10 min → 0,10`, `20 → 0,20`, `30 → 1`). `durationFactor()` interpole
  entre eux. Le facteur multiplie le poids de volume et alimente
  l'exposition cumulée de chaque territoire ; diversité et profondeur
  travaillent sur cette exposition, pas sur un simple nombre entier de films.
- 8 dimensions, parts : caractéristique 0,25 · réalisateur 0,20 · pays 0,18 ·
  décennie 0,15 · continent 0,07 · ère 0,05 · genre 0,05 · forme 0,05.
- 9 seuils (rangs 2–10) dans `RankDefaults.thresholds` :
  `1,80 / 3,00 / 4,20 / 5,40 / 6,60 / 7,80 / 9,20 / 10,80 / 12,50`.
- Recalcul : `ProgressionCoordinator.recalculate(userId)` après chaque film vu.
- Le rang affiché = `max(rang calculé, rang déjà affiché)`.

La configuration active porte le code `RANK_V031_DURATION_WEIGHTED`. Au démarrage,
`AppBootstrapper` désactive une ancienne configuration et active ou insère
celle-ci. Les constantes `25` et `1,2` appartiennent à cette version de formule ;
les λ et parts restent enregistrés dans `rank_engine_configs`.

Les rangs 8–10 restent quantitatifs en V1 (pas encore de critères qualitatifs).

### 7.2 XP 1–50

Fichier : `domain/xp/XpEngine.kt`.

Deux sources, ledger `xp_transactions` :

- **FILM** : **25 XP** (`FunctionalLimits.FILM_XP_IN_FOLLOWED_COLLECTION`) une seule fois, et seulement si le film est dans une collection **suivie** au moment du marquage. Sinon 0. Pas de rattrapage des films déjà vus.
- **QUEST** : Bronze 100, Argent 250, Or 500. Assiduité.

Courbe exacte :

| Point | XP cumulé |
| --- | --- |
| T(1) | 0 |
| T(20) | 9 200 |
| T(25)→T(50) | palier 3 202 XP / niveau |
| T(49) | 96 798 |
| T(50) | 100 000 |

Segments dans `XpConfiguration.exactV1Segments`. Modifier la courbe **là**,
puis faire passer `XpEngineTest`.

Le niveau affiché ne redescend pas. L’XP total est la somme du ledger
`xp_transactions` (FILM + QUEST), pas un champ mutable sur `users`.

### 7.3 Quêtes

`domain/quest/QuestEngine.kt` + `WeeklyQuestCoordinator`.

Assignation lundi 02:00 local. Progression non rétroactive : seuls les films
validés **pendant** la fenêtre comptent. Récompenses snapshotées.

### 7.4 Badges

`domain/badge/BadgeRegistry.kt`. Codes `001`–`032`. Jamais retirés une fois
obtenus. À l’unlock : pop-up FR/EN (« Félicitations ! Vous avez débloqué
le badge « … » ! ») et illustration locale de 72 dp. Les trois badges vitrine
du Profil : tant qu’on appuie, un libellé `BadgeUi.condition` s’affiche au-dessus du doigt ; il disparaît au relâchement.

### 7.5 Collections

`domain/collection/CollectionProgressEngine.kt` + mapping UI dans
`MainViewModel`. Le moteur calcule le % brut films vus / films de la collection.
L’UI **force 0** si la collection n’est pas suivie, et n’or-ifie les titres
vus que si elle l’est. Complétion UI = followed && 100 %.

---

## 8. UI, i18n, thème

- Navigation : `ui/UrbinemaApp.kt`. Routes film `movie/{movieCode}`, collection
  `collection/{collectionCode}`, listes `atlas`, ciel `atlas/sky`.
- Contrat UI : `ui/model/UiModels.kt`. Previews via `PreviewUrbinemaViewModel`
  (données fictives, sans Room).
- Thèmes : `Theme.kt` (`UrbinemaThemeMode`), palettes `ThemeSalleObscure.kt`,
  `ThemeSalleEclairee.kt`, `ThemeCyanotype.kt`, `ThemeTirage.kt`,
  `ThemeRayonnage.kt`, `ThemeAffiche.kt`, `ThemeVelours.kt`,
  `ThemeNuitAmericaine.kt`, sélecteur `ThemePicker.kt`. Tokens via
  `UrbinemaThemeTokens`.
- Chaînes : toujours `stringResource`, jamais de texte dur dans les Composables
  (sauf contenus éditoriaux issus du catalogue : titres originaux, noms de
  collections, descriptions JSON). Dialogues cadenas / 100 % / reset : strings
  FR/EN, **pré-résolues hors `AlertDialog`**.
- Tutoiement FR. EN parallèle obligatoire. Listes de films en anglais = titre
  original ; fiche : pas de sous-titre VF.
- Historique : reconstruit dans `refreshUnsafe` après chargement des films ;
  filet `titleFromEditorialCode` si le film manque encore.
- Stats détaillées : `MainViewModel.statsShares` + `NamedListScreen` /
  `StatsListSort`. Calcul au moment de l’ouverture, pas à chaque composition
  Accueil.
- Grain : `UrbinemaApp.filmGrain` (tuile). Logo Accueil : `LogoAboutDialog`.
- Carte : `SkyMapExpandingSearch` dans `InteractiveMapScreen.kt`.
- Launcher : `tools/generate_launcher_icons.py` lit
  `res/drawable-nodpi/logo_urbinema.png`.

Le sélecteur de langue dans Réglages est **effectif**. Le grain argentique est
un switch **persisté** (DataStore). Aide : `HelpScreen`, entrée Réglages + `?`
Parcours.

---

## 9. Tests

| Test | Rôle |
| --- | --- |
| `domain/xp/XpEngineTest` | seuils T(20), T(49), T(50), ratchet de niveau |
| `domain/rank/RankEngineTest` | v0.3.1, deux lissages, ratchet de rang |
| `domain/quest/QuestEngineTest` | fenêtres lundi 02:00, non-rétroactivité |
| `domain/validation/ValidationTest` | pays primaire, codes |
| `domain/ProgressionRulesTest` | règles transverses |
| `domain/map/CinemaMapTest` | layout ciel : continents, frise, co-occurrence, hit-test, caméra |
| `androidTest/.../UrbinemaDatabaseTest` | FK, index primaire unique, import atomique |

Lancer d’abord les unit tests : ils ne nécessitent pas d’émulateur.

---

## 10. Fichiers de spec autour du code

| Fichier | Usage |
| --- | --- |
| `specs/SPECIFICATION_DEVELOPPEUR.md` | ce document, reprise code |
| `specs/CahierDesCharges_Fonctionnel_v2.md` | produit |
| `specs/CahierDesCharges_Technique.md` | contraintes techniques |
| `specs/CahierDesCharges_IHM.md` | écrans, thème, accessibilité |
| `specs/DECISIONS_ACTEES.txt` | décisions figées |
| `specs/ROADMAP_V2_V3.md` | V1 close, V2 = carte Canvas |
| `specs/ASSETS.md` | dossiers et branchement médias |
| `specs/FAQ_CAHIER_FONCTIONNEL.txt` | questions encore ouvertes |
| `specs/FORMULE_MATHEMATIQUE.txt` | rang |
| `specs/FORMULE_NIVEAUX_XP.txt` | XP |
| `batchPosters/README.md` | script hors-app : affiches TMDB et fiches JSON |
| `README.md` | démarrage court |

---

## 11. Limites assumées (état 0.2.3)

- Catalogue **démo** (~405 films, 15 collections), pas encore les 20 collections
  / 50 caractéristiques du cahier produit.
- Atlas = listes (`atlas`). Carte du ciel Canvas **livrée** (0.2.3) :
  icône étoiles, autour d’un film par défaut, couleurs par type, pas
  d’affiches. XP film = **10** (essai). Calibrage après usage.
- Pas de dé-validation d’un film vu ni d’édition de la date (date = jour local).
- Images : architecture prête (`ASSETS.md`). Déposer `{CODE}.jpg|png|webp`
  dans `assets/media/…` les rend visibles ; sans fichier = placeholder.
  Aucun appel réseau dans l’app.
- Avatars V1 : 10 visuels packagés (`AVATAR_01`…`10`), carrousel
  coulissant à l’onboarding et dans Réglages. Photo photothèque : plus tard.
- Cadenas **entre groupes** : **fait** (2 collections commencées + cliquet).
- Scores de rang jamais affichés (seulement rang, axes qualitatifs, XP).

Ces limites ne remettent pas en cause la persistence : tout ce qui est acquis
dans Room survit à la fermeture de l’application.
