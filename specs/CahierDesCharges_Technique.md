# Cahier des charges technique

### Urbinema

**Version :** 0.12  
**Statut :** Cadrage technique aligné sur **0.2.8** (catalogue `catalog.json` v19, graine `catalog_v3.json`)  
**Lié à :** `CahierDesCharges_Fonctionnel_v2.md`, `CahierDesCharges_IHM.md`, `DECISIONS_ACTEES.txt`, `ROADMAP_V2_V3.md`  
**Emplacement :** tous les documents de cadrage vivent dans `specs/`

------

# Sommaire

1. [Contexte et principes](#1-contexte-et-principes) — dont **§1.5 environnement Android Studio**
2. [Périmètre technique](#2-périmètre-technique)
3. [Cibles (OS, devices, orientation)](#3-cibles-os-devices-orientation)
4. [Stack V1](#4-stack-v1)
5. [Architecture logicielle](#5-architecture-logicielle) — dont **§5.5 qualité et conventions de code**
6. [Données (Room)](#6-données-room)
7. [Alimentation du catalogue](#7-alimentation-du-catalogue)
8. [Carte (Canvas Compose)](#8-carte-canvas-compose)
9. [Navigation et UI](#9-navigation-et-ui)
10. [Réseau et APIs externes](#10-réseau-et-apis-externes)
11. [Build](#11-build)
12. [Tests et qualité](#12-tests-et-qualité)
13. [Évolutivité (sans overkill)](#13-évolutivité-sans-overkill)
14. [Hors stack V1 / plus tard](#14-hors-stack-v1--plus-tard)

------

# 1. Contexte et principes

## 1.1. À qui s’adresse le logiciel

La V1 est une **application Android locale**, conçue d’abord pour **un utilisateur** (Léo).

Un horizon lointain possible : partage d’un APK à quelques proches, éventuellement Play Store. Ordre de grandeur assumé : 1 personne, puis éventuellement 10–30. Ce n’est **pas** une hypothèse de charge (pas de milliers d’utilisateurs simultanés).

## 1.2. Compte

Pas d’authentification (pas d’e-mail, pas Google, pas de mot de passe, pas de backend).

Le profil Room contient un pseudo obligatoire et des métadonnées facultatives
(e-mail non authentifiant, nom, prénom, date de naissance, pays, avatar).

Pas de synchronisation multi-appareils en V1. Désinstallation = perte des données locales (un export ultérieur reste une soupape, ce n’est pas un compte).

## 1.3. Ce que « scalable » veut dire ici

Ne pas se peindre dans le coin si, dans 6 mois ou 2 ans, l’app sort du cadre « un téléphone » :

- IDs stables côté métier (`filmId` Urbinema, `collectionId`, `badgeId`, `questId`, etc.) ;
- règles de progression **déterministes**, testables **sans Android** ;
- contenu éditorial en **base**, pas hardcodé dans les écrans ;
- un profil local déjà modélisé comme « un utilisateur » (même s’il n’y en a qu’un).

Ça ne veut **pas** dire : microservices, Auth, Firebase « au cas où », Kubernetes, ni une usine à modules pour la forme.

## 1.4. Priorité du développement

Le cœur du code, c’est le **cœur fonctionnel** : catalogue éditorial,
validation des films proposés, collections, quêtes, badges, XP, niveaux,
rangs, Atlas/carte, historique et statistiques.

Pas de social, pas de chat, pas de profil public, pas de classement.

## 1.5. Environnement de développement

Le projet est **ouvert, édité, compilé et exécuté dans Android Studio**. Ce n’est pas un détail de confort : c’est une contrainte qui s’impose à toute la structure du dépôt.

Conséquences concrètes :

- **projet Gradle Android standard**, reconnu tel quel à l’ouverture du dossier : `settings.gradle.kts`, `build.gradle.kts` racine, module `app` avec son propre `build.gradle.kts`, `gradle/libs.versions.toml`, wrapper Gradle versionné (`gradlew`, `gradlew.bat`, `gradle/wrapper/`) ;
- **aucune structure exotique** : pas de layout de dossiers inventé, pas de build system parallèle, pas de scripts qui court-circuitent Gradle. Ce que fait le bouton *Run* doit être ce que fait la ligne de commande ;
- **arborescence de sources conventionnelle** : `app/src/main/java|kotlin`, `app/src/main/res`, `app/src/test` pour les tests JVM, `app/src/androidTest` s’il en faut ;
- **AGP, Gradle et Kotlin sur des versions mutuellement compatibles**, et compatibles avec la version d’Android Studio utilisée — c’est la source d’erreur la plus fréquente sur un projet Android neuf ;
- `.gitignore` Android standard : `build/`, `.gradle/`, `local.properties`, fichiers d’IDE. En particulier, **`local.properties` n’est jamais versionné** (il contient le chemin du SDK, propre à la machine) ;
- fichiers d’IDE (`.idea/`) globalement ignorés, à l’exception éventuelle de ce qui est réellement partageable ;
- **le SDK Android et les images d’émulateur sont gérés par Android Studio**, pas par un script d’installation maison.

Le script d’import du catalogue (§7) ne doit pas casser cette règle : soit c’est une tâche Gradle du projet, soit c’est un outil séparé qui produit un fichier que l’application lit. Pas un troisième système de build.

### Genèse du projet

**Le squelette est généré par Léo depuis Android Studio** (*New Project → Empty Activity*, template Compose). C’est le bon choix : le template produit un triplet AGP / Gradle / Kotlin cohérent avec l’IDE installé, ce qu’un squelette écrit à la main risque toujours de rater.

Reste ensuite à ma charge : les dépendances et le `libs.versions.toml`, la configuration des modules, les réglages de build, puis l’intégralité du code applicatif.

------

# 2. Périmètre technique

## 2.1. V1 — dans le périmètre

- App Android native (Kotlin / Compose).
- Base **Room** : catalogue Urbinema + progression du profil local.
- Catalogue **fermé** : uniquement les films proposés par Urbinema. Sa taille **N** grandit en continu (une centaine au lancement, puis 500, puis 1000, puis davantage) — pas le cinéma mondial. Aucune de ces valeurs n’est écrite en dur.
- **Atlas scrollable** (listes + filtres) depuis 0.1.6.
- **Carte du ciel** : Compose **Canvas custom**, livrée en **0.2.1** (V2).
  Voir §8. Pas de bibliothèque de graphe.
- Navigation Compose.
- Alimentation du catalogue par **batch / script** vers Room (pas de CMS web).

## 2.2. V1 — hors périmètre

- TMDb / toute API films **dans l’app** (enrichissement, recherche mondiale,
  posters distants). Un script hors-app `batchPosters/` peut préparer des
  affiches à embarquer ; l’APK reste offline.
- Compte cloud, sync, multi-profil.
- Import Letterboxd / SensCritique / historique personnel exhaustif.
- Affiches sur la carte du ciel.
- Films comme nœuds positionnés (pas 0.2.1).
- Back-office web d’administration.
- Fonctionnalités sociales.

## 2.3. Nature du produit (impact technique)

Urbinema **n’est pas** un journal de films vus (clone Letterboxd).

C’est un **parcours cinématographique guidé et gamifié**. L’utilisateur ne renseigne pas tout ce qu’il voit dans sa vie : il **valide les films que l’application lui propose**. Les quêtes du type « 5 films asiatiques dans le mois » s’appuient **uniquement** sur ce catalogue et ces validations.

V1 : usage personnel, déclarations **non contrôlées** (honor system). Pas de triche à « détecter ».

Détail produit : voir `DECISIONS_ACTEES.txt` et le cahier fonctionnel (nature du catalogue).

------

# 3. Cibles (OS, devices, orientation)

| Cible | V1 |
| ----- | --- |
| OS | Android téléphone |
| Tablette | Acceptable (layouts adaptables), pas une cible de design dédiée jour 1 |
| TV / PC / Wear / Auto | Non |
| Orientation | **Portrait = usage principal.** Paysage : prévu, livrable en **deux temps** (d’abord un portrait solide, puis paysage) tout en restant une base d’app téléphone — ne pas verrouiller le manifeste en portrait-only de façon définitive si ça complique le second temps |
| minSdk | **API 26 — décidé.** Pas d’effort de compatibilité pour les anciens téléphones |
| targetSdk / compileSdk | Dernière API stable au moment du projet (Play exigera un target récent de toute façon le jour d’un store) |

Pas de foldable comme cible. Pas de desktop Compose.

------

# 4. Stack V1

## 4.1. Langage et UI

- **Kotlin 2.x (compilateur K2)** — langage unique de l’app et des scripts Gradle.
- **Jetpack Compose + Material 3** — UI.
- **Compose Canvas** — dessin de la carte du ciel (**0.2.1**). **Pas de bibliothèque de graphe tierce.**
  Le placement des nœuds est du **domain** (`CinemaMapLayout`), pas de l’UI.
- **Coroutines + Flow** — asynchrone, observation Room, calculs de progression.

## 4.2. Données et architecture

- **Room + KSP** — unique base locale : catalogue éditorial **et** progression (tables séparées, voir §6).
- **Koin** — injection de dépendances.
- **MVVM + Clean Architecture** — UI / domaine / data séparés. Le métier (rang, badges, quêtes, collections) ne vit pas dans les Composables.
- **DataStore** (Preferences) — thème, langue, grain argentique, **codes de
  badges déjà célébrés** (`badge_celebration_seeded` + liste). Le sélecteur
  de langue est **effectif** (`Configuration.setLocales` via `LocalContext`) ;
  les dialogues (cadenas, félicitations) **pré-résolvent** les chaînes hors
  de l’`AlertDialog` avec `LocalContext.resources`. Réglages légers. Le profil
  et le pseudo ont une seule source de vérité : `users` dans Room.

## 4.3. Navigation et médias

- **Jetpack Compose Navigation** — graphe d’écrans V1 (carte, collections, fiche film, quêtes, profil, etc.). On part là-dessus ; on réévaluera si le graphe explose.
- **Coil 3** — chargement et cache des images locales dès la V1 (affiches,
  portraits, badges, collections, avatars). Jamais utilisé dans le Canvas de
  l'Atlas/carte. La V0.1 peut rester textuelle.

## 4.4. Build

- **Gradle Kotlin DSL** (`.gradle.kts`).
- **Version Catalogs** (`gradle/libs.versions.toml`).
- **KSP** (Room, et tout processeur de symboles — pas KAPT).

## 4.5. Explicitement retiré de la stack V1

- **Ktor Client** — pas d’API externe **dans l’APK**. `batchPosters/` est un
  script Python local, pas une dépendance Gradle.
- Toute lib de graphe (GraphView, Force-directed, etc.).
- Backend, Firebase, Auth.

## 4.6. Compléments recommandés (légers, pas du « scaling »)

- **kotlinx.serialization** — si le batch d’import catalogue passe par JSON.
- **kotlinx.datetime** (ou `java.time`) — quêtes mensuelles / hebdo, calendrier de l’appareil.
- **JUnit** sur le module / package `domain` — moteur de règles.

------

# 5. Architecture logicielle

## 5.1. Intention

Code **propre et moderne**, lisible, testable. Pas une cathédrale.

Un seul module Gradle `app` au départ, avec des **packages** clairs, suffit. Extraire `domain` / `data` en modules Gradle reste possible plus tard **sans changer les règles métier**, si le projet grossit. On ne crée pas 6 modules le jour 1.

## 5.2. Couches

```text
ui (Compose, ViewModels, navigation, Canvas carte)
        ↓
domain (modèles métier, use cases, moteur de progression)
        ↓
data (Room, DataStore, import batch)
```

- **UI (MVVM)** : état d’écran, aucune règle métier dans le Canvas.
- **Domain** : « l’utilisateur a validé ce film » → progression des quêtes,
  attribution atomique d'XP, niveau dérivé, recalcul collections, badges, rang,
  statistiques et états de l'Atlas. **Pur Kotlin**, sans `android.*`.
  Y compris `CinemaMapLayout` (positions, hit-test, caméra) : l’UI ne calcule
  pas où mettre la France.
- **Data** : persistance. Le catalogue n’est pas « téléchargé TMDb », il est **déjà en Room**.

Les règles métier précises (seuils de rang et niveau, caractéristiques,
conditions de badges et quêtes) restent externalisées et vivent dans `domain`,
jamais dans l'UI.

## 5.3. Source de vérité progression

Ensemble des **validations** (films du catalogue marqués vus) + pack de contenu en base + horloge **locale de l’appareil** pour les quêtes temporelles **et** pour `watchedOn`.

Règle : **recalcul déterministe** depuis les validations et les journaux
d'événements. Le retrait d’un film recalcule rang, collections et statistiques.
Badges et XP déjà attribués restent acquis.

Logs de debug : tag Logcat unique **`UrbinemaProgress`** (validation, XP de
quête, recalcul de rang). Pas d’autre canal.

L’historique Accueil est **reconstruit** dans le refresh UI à partir de
`activity_events` **après** chargement des films, pour afficher les titres
et non les codes. L’Accueil n’en montre que **50** ; l’écran `history`
prend jusqu’à 2000 lignes (`observeActivity`). Les phrases sont des
`stringResource` (`history_*_body`), pas du FR/EN figé dans le ViewModel.

Exceptions persistées : rang maximal atteint, raretés figées par version,
badges obtenus et transactions d'XP.

## 5.4. Moteur de rang

Le calcul du rang est le composant métier le plus sensible du projet. Il est **entièrement spécifié** : `FORMULE_MATHEMATIQUE.txt` (v0.3), analyse dans `RETOUR_FORMULE_RANG.txt`, lecture fonctionnelle au §9.4 du cahier fonctionnel.

Trois axes : volume pondéré par l’exigence des films, diversité (bornée, elle sature) et profondeur (non bornée).

Contraintes d’implémentation :

- **Kotlin pur**, dans `domain`, sans dépendance Android — condition pour pouvoir le tester et le calibrer sans émulateur ;
- **déterministe et indépendant de l’ordre** : le score se recalcule intégralement à partir de l’ensemble des films validés et du catalogue courant, sans rejouer un historique ;
- **paramètres externalisés** : une vingtaine de coefficients à calibrer, jamais dispersés en dur dans le code, modifiables sans recompiler ;
- **statistiques de catalogue précalculées par version** et persistées (rareté et poids de dimension, avec leur cliquet) ;
- **banc d’essai** : un harnais de simulation sur profils types, à écrire **en même temps** que le moteur. Sans lui, le calibrage se ferait à l’aveugle sur l’émulateur.

Coût en performance : négligeable. Le calcul est linéaire en nombre de caractéristiques distinctes possédées par l’utilisateur — recalcul complet instantané, même à 5000 films validés. Aucun calcul incrémental nécessaire.

------

## 5.5. Qualité et conventions de code

Exigence explicite de Léo, à tenir dès le premier commit — ces règles coûtent peu au début et très cher à rattraper.

### Lisibilité

- **Fonctions courtes, responsabilités uniques.** Pas de Composable de 400 lignes, pas de ViewModel fourre-tout.
- **KDoc sur toute fonction publique**, expliquant *ce qu’elle fait et pourquoi*. Une documentation qui paraphrase le corps de la fonction est du bruit ; celle qui explique une contrainte ou une décision est utile.
- Le moteur de rang mérite un traitement particulier : chaque étape du calcul porte le nom de la notion du cahier fonctionnel (`diversity`, `depth`, `weightedVolume`), afin que le code se relise avec la formule à côté.
- Nommage en anglais dans le code, vocabulaire du domaine conservé
  (`CinemaCharacteristic`, `Rank`, `Badge`, `Quest`, `Collection`).

### Structure

- **Patrons de conception appliqués là où ils servent**, jamais pour la forme : Repository entre `domain` et `data`, use cases pour les opérations métier, `sealed interface` pour les états d’écran et les résultats, Factory pour les paramètres de calcul. Pas d’abstraction sans second implémenteur plausible.
- **État remonté** (*state hoisting*) : les Composables reçoivent un état et émettent des événements, ils n’en produisent pas.
- **Composables sans effet de bord**, `@Preview` sur tout composant réutilisable.
- **Aucune logique métier dans l’UI.** La règle se vérifie simplement : le module `domain` ne compile aucun import `android.*` ni `androidx.compose.*`.

### Rien en dur

Aucune couleur, dimension, chaîne de caractères ou constante de calcul écrite en dur dans un écran. Trois systèmes de configuration l’imposent :

| Quoi | Où | Règle |
| --- | --- | --- |
| Couleurs, typographie, formes | `ui/theme/` — **un fichier par thème** | L’application ne connaît que des jetons sémantiques |
| Textes | `res/values*/strings.xml` — **un fichier par langue** | Zéro chaîne en dur, pluriels par `plurals`, jamais de concaténation |
| Coefficients du rang | configuration dédiée du `domain` | Les 20 paramètres modifiables sans recompiler |

Détail et arborescence : `CahierDesCharges_IHM.md` §21.

### Internationalisation dès le départ

Français par défaut, anglais prévu. Mettre l’i18n en place au premier écran ne coûte presque rien ; la rétro-adapter sur trente écrans coûte plusieurs jours. Conséquences concrètes au §21.3 du cahier IHM.

------

# 6. Données (Room)

Room est le bon outil V1 : quelques milliers de films, nombreuses relations
N–N et progression entièrement locale.

Le schéma détaillé ci-dessous constitue le contrat à traduire en `@Entity`.
La future Spec Développeur reprendra les noms Kotlin et les migrations exactes
une fois le code créé.

## 6.1. Conventions de schéma

- PK techniques : `Long` auto-générés, nommées `<entity>Id`.
- Codes métier : `TEXT NOT NULL UNIQUE`, stables et utilisés par les règles.
  Un code ne change jamais même si l'ID saute pendant un import.
- Toutes les tables de catalogue ont `isActive`, `createdAt`, `updatedAt`.
  On **désactive** une entrée référencée ; on ne la supprime pas.
- Dates métier stockées en `Instant` UTC ; date de visionnage (`watchedOn`) en
  `LocalDate` **du fuseau de l’appareil** (`Clock.systemDefaultZone()`), jamais
  UTC — un Vu à 00:03 locale ne doit pas être rejeté comme « futur ».
- Enums persistées sous forme de codes texte stables, jamais par ordinal.
- Chaque FK possède un index. Chaque jonction possède une PK composite.
- `PRAGMA foreign_keys = ON` ; aucune relation ne repose sur une convention
  implicite.

## 6.2. Catalogue éditorial

### Films et médias

| Table | Colonnes structurantes |
| --- | --- |
| `movies` | `movieId`, `code`, `originalTitle`, `frenchTitle?`, `releaseYear`, `durationMinutes`, `format`, `synopsis?`, `posterMediaId?`, `historicalDistance`, `artisticDemand`, `historicalRichness`, `culturalRichness`, `isSilent`, `isBlackAndWhite`, `isExperimental`, `isActive` |
| `media_assets` | `mediaAssetId`, `code`, `storageType` (`ASSET`/`FILE`), `path`, `contentDescriptionKey?`, `mimeType?` |

`durationMinutes` reste la valeur brute. `format` vaut `SHORT`, `MEDIUM`,
`FEATURE` ou `EXTENDED` et reste explicite : une règle éditoriale ne doit pas
être recalculée à chaque requête.

Une FK nullable vers `media_assets` est utilisée sur toute entité affichable :
`movies`, `directors`, `badges`, `collections`, `cinema_characteristics`,
`countries`, `continents`, `genres`, `eras`, `rankings` et `users`.
Suppression d'un média : `SET NULL`. Les chemins pointent vers des assets
packagés ou des fichiers privés de l'application, jamais vers un chemin absolu
de la machine.

### Géographie

| Table | Colonnes structurantes |
| --- | --- |
| `countries` | `countryId`, `code`, `name`, `isoCode?`, `imageMediaId?` |
| `continents` | `continentId`, `code`, `name`, `imageMediaId?` |
| `countries_continents` | `countryId`, `continentId` — PK composite |
| `movies_countries` | `movieId`, `countryId`, `isPrimary` — PK composite |

`movies_countries.isPrimary` est obligatoire. Deux garanties :

1. **au plus un** pays principal par film, via un index SQLite partiel unique
   sur `movieId WHERE isPrimary = 1` créé par migration/callback ;
2. **au moins un** pays principal, validé dans la transaction d'import avant
   commit.

Une simple contrainte `CHECK` ne peut pas compter les autres lignes d'une table
SQLite : prétendre faire respecter « exactement un » avec un `CHECK` serait
faux. Le validateur d'import est donc une partie obligatoire du système.

### Réalisateurs, genres et caractéristiques

| Table | Colonnes structurantes |
| --- | --- |
| `directors` | `directorId`, `code`, `firstName?`, `lastName`, `displayName`, `portraitMediaId?` |
| `movies_directors` | `movieId`, `directorId`, `billingOrder` — PK composite |
| `directors_characteristics` | `directorId`, `characteristicId` — PK composite ; nécessaire notamment au badge Nouvelle Vague |
| `genres` | `genreId`, `code`, `name`, `description?`, `imageMediaId?` |
| `movies_genres` | `movieId`, `genreId` — PK composite |
| `characteristic_types` | `typeCode` PK, `name` — données : `MOVEMENT`, `CURRENT`, `STYLE`, `PERIOD`, `SCHOOL`, `WAVE` |
| `cinema_characteristics` | `characteristicId`, `code`, `name`, `typeCode` FK, `description?`, `imageMediaId?` |
| `movies_characteristics` | `movieId`, `characteristicId` — PK composite |

Un film possède zéro à plusieurs genres et caractéristiques, et un à plusieurs
réalisateurs. `billingOrder` conserve l'ordre d'affichage des co-réalisateurs.
Le type de caractéristique vit dans une table afin d'être extensible sans
migration de schéma.

### Époques, collections et rangs

| Table | Colonnes structurantes |
| --- | --- |
| `eras` | `eraId`, `code`, `name`, `startYear`, `endYear`, `description?`, `imageMediaId?` |
| `collections` | `collectionId`, `code`, `displayOrder`, `name`, `description?`, `longDescription?`, `track` (`GATEWAY`/`CLUB`/`DARKROOM`/`CINEMATHEQUE`/`OFFSCREEN`), `coverMediaId?`, `isPublished` |
| `collections_movies` | `collectionId`, `movieId`, `displayOrder` — PK composite |
| `collections_characteristics` | `collectionId`, `characteristicId` |
| `collections_countries` | `collectionId`, `countryId` |
| `collections_continents` | `collectionId`, `continentId` |
| `collections_eras` | `collectionId`, `eraId` |
| `rankings` | `rankingId`, `code`, `displayOrder` unique, `name`, `description`, `imageMediaId?` |

Les quatre tables de cibles de collection évitent le piège d'une relation
polymorphe `targetType + targetId`, impossible à protéger par de vraies FK.
Une collection peut n'avoir aucune cible ou en posséder plusieurs.

`displayOrder` est un entier éditorial, distinct de l'ID et modifiable.
Le code (`INITIATION`, `NEOREALISME_ITALIEN`, …) reste stable. `track` classe
la liste UI. Les anciens codes JSON `JOURNEY` / `DEMANDING` sont acceptés à
l’import et mappés vers `CLUB` / `CINEMATHEQUE`. Room **version 5** a ajouté
`collections.track` (`MIGRATION_4_5`, défaut `JOURNEY`). Room **version 7**
(`MIGRATION_5_6` puis `MIGRATION_6_7`) : `users.unlockedTrackOrdinal`,
`users.showcaseBadgeCodes`, `users.avatarCode`. Le ledger XP des films
utilise `xp_transactions.source` / `movieId`.

Le cadenas Initiation n’est **pas** une colonne de collection : il est dérivé
(≥ 1 film Vu dans Initiation) puis **latché** dans `users.unlockedTrackOrdinal`.
Un groupe ouvert ne se recadenasse plus. La complétion 100 % non plus :
`followed` reste vrai, l’UI masque la collection des « en cours » **et**
ignore les collections encore cadenassées.

### Badges et quêtes

| Table | Colonnes structurantes |
| --- | --- |
| `badges` | `badgeId`, `code` unique, `name`, `description`, `difficulty` (1..5), `category`, `iconMediaId?`, `isActive` |
| `quests` | `questId`, `code`, `name`, `description`, `difficulty` (`BRONZE`/`SILVER`/`GOLD`), `ruleCode`, `targetCount`, `isActive` |

Les règles de badges sont un registre Kotlin typé indexé par `badge.code`.
L'ID auto-généré n'entre jamais dans une règle. Même principe possible pour
`quest.ruleCode`, les instances hebdomadaires restant en base.

## 6.3. Profil et progression

| Table | Colonnes structurantes |
| --- | --- |
| `users` | `userId`, `email?`, `username`, `firstName?`, `lastName?`, `birthDate?`, `countryId?`, `avatarMediaId?`, `avatarCode?`, `rankingId`, `maxLevelReached`, `unlockedTrackOrdinal`, `showcaseBadgeCodes?`, `createdAt` |
| `user_movies` | `userId`, `movieId`, `watchedOn`, `validatedAt` — PK composite |
| `user_badges` | `userId`, `badgeId`, `earnedAt` — PK composite |
| `user_quests` | `userQuestId`, `userId`, `questId`, `startsAt`, `expiresAt`, `progress`, `targetCountSnapshot`, `xpRewardSnapshot`, `completedAt?`, `status` |
| `xp_transactions` | `xpTransactionId`, `userId`, `userQuestId?` unique, `movieId?`, `source` (`QUEST`/`FILM`), `amount`, `earnedAt` |
| `activity_events` | `activityEventId`, `userId`, `type`, `occurredAt`, `payloadJson` |

`users` ne contient pas d'âge : il vieillirait mal. `birthDate` facultative est
la donnée stable. L'e-mail est une métadonnée facultative, pas un identifiant
d'authentification en V1.

`rankingId` référence le rang maximal acquis et constitue directement le
cliquet : le rang brut recalculé n'est pas persisté comme seconde vérité.

L'XP cumulée est la somme de `xp_transactions` ; le niveau est dérivé de
`FORMULE_NIVEAUX_XP.txt`. Cette source de vérité évite qu'un entier `totalXp`
diverge après une correction. Un cache pourra être ajouté seulement si une
mesure de performance le justifie.

`maxLevelReached` est le cliquet de niveau : ajuster la courbe ne fait jamais
redescendre un niveau déjà affiché.

`targetCountSnapshot` et `xpRewardSnapshot` figent les paramètres d'une quête
au moment de son attribution : modifier le catalogue ne réécrit pas une semaine
en cours. L'unicité de `xp_transactions.userQuestId` empêche une double
récompense.

`activity_events` alimente l'historique de l'accueil. Son `payloadJson` est une
projection d'affichage versionnée, pas une source de vérité métier.

## 6.4. Contraintes de suppression

- Catalogue (`movies`, pays, genres, caractéristiques, réalisateurs,
  collections, badges, quêtes, rangs) : `ON DELETE RESTRICT`.
- Jonctions éditoriales : suppression explicite dans une transaction ; pas de
  cascade silencieuse sur une entité encore publiée.
- Suppression du profil local : `CASCADE` vers `user_movies`, `user_badges`,
  `user_quests`, `xp_transactions`, `activity_events`.
- Badge obtenu : `RESTRICT` sur le badge, jamais supprimé ; désactivation
  éditoriale seulement.
- Toutes les écritures multi-tables passent par un Repository transactionnel.

### Ce que SQL garantit, et ce qu'il ne peut pas garantir seul

Room/SQLite garantit réellement : `NOT NULL`, PK, FK, unicité, index, valeurs
par défaut et suppression `RESTRICT/CASCADE/SET NULL`.

Les invariants qui portent sur plusieurs lignes — « exactement un pays
principal », « les neuf seuils de rang sont croissants », « la progression
d'une quête ne dépasse pas son objectif » — ne se résument pas proprement à une
annotation Room. Ils sont validés dans le domaine et dans la transaction
d'import, avec tests d'intégration. L'index partiel garantit en plus
« au plus un pays principal ».

Les bornes simples sont également validées à l'import et avant écriture :

- `durationMinutes > 0`, année dans une plage plausible ;
- H/A/R/C dans `[0,1]` ;
- difficulté de badge dans `[1,5]` ;
- `startYear <= endYear` ;
- XP attribuée strictement positive ;
- dates de visionnage non futures.

Forcer artificiellement toute cette logique dans des triggers SQL rendrait le
schéma Room fragile sans améliorer la sûreté : la stratégie retenue combine
contraintes SQL structurelles, types Kotlin et validation transactionnelle.

## 6.5. Index et requêtes

Index minimum :

- tous les codes uniques ;
- `movies(originalTitle)`, `movies(frenchTitle)`, `movies(releaseYear)` ;
- chaque FK de jonction dans les deux sens ;
- `user_movies(userId, watchedOn)` ;
- `user_quests(userId, startsAt, expiresAt, status)` ;
- `activity_events(userId, occurredAt DESC)` ;
- index partiel unique du pays principal.
- unicité `(collectionId, displayOrder)` dans `collections_movies` ;
- unicité `(movieId, billingOrder)` dans `movies_directors`.

Paging 3 est retenu pour les listes de films par nœud, avec pages d'environ
50 éléments, filtres et tris produits directement par Room.

La recherche reste locale. Un index FTS sur titres original/français et
réalisateurs sera ajouté si les mesures sur le catalogue réel le justifient.

## 6.6. Atlas et future carte

L'Atlas V1 ne nécessite aucune coordonnée : il projette les relations du
catalogue en listes et cartes scrollables.

La future carte conserve son layout séparément :
`map_nodes`, `map_edges`, coordonnées et version de layout. Un film n'a jamais
de coordonnées directement dans `movies`.

------

# 7. Alimentation du catalogue

Le contenu n’est pas saisi film par film dans l’UI Android (hors éventuellement plus tard).

V1 :

- catalogue source en **JSON versionné**, lisible dans Git et validé par
  `kotlinx.serialization` ;
- un outil d'import valide toutes les FK, les codes uniques, les intervalles,
  les notes et l'unicité du pays principal, puis produit la base Room
  préchargée placée dans `assets` ;
- l’« admin » V1, c’est **l’auteur du batch** (Léo + plus tard le code d’import), pas une appli web.

Le JSON est la source éditoriale ; la base `.db` générée est un artefact, jamais
éditée à la main. Un import invalide échoue en entier avec un rapport lisible.

Mises à jour de contenu : pack JSON dont la `version` est strictement
supérieure → upsert par codes stables, tables `user_*` intactes.
Pack prêt 0.2.1 : **`"version": 12`**, ~405 films, 15 collections (dont Initiation), 32 badges, 50 quêtes types.
Une grosse delta (retrait de films d’une collection déjà à 100 %) reste à
éprouver. Pas de synchronisation serveur.

------

# 8. Atlas puis carte du ciel (0.2.1)

Ce chapitre explique **comment** la carte est construite. Le *pourquoi*
métier est dans le cahier fonctionnel §11. L’apparence (gestes, couleurs,
feuille) est dans le cahier IHM §10. Ici : les notions de Canvas, caméra,
monde / écran, hit-test — le vocabulaire d’une carte 2D custom, sans
bibliothèque de graphe ni moteur de jeu.

------

## 8.1. Deux surfaces, deux technologies UI

| Surface | Fichier | Techno Compose |
| --- | --- | --- |
| **Atlas** | `ui/screens/Screens.kt` (`AtlasScreen`) | Listes, puces, `LazyColumn` — widgets Material |
| **Carte du ciel** | `ui/map/InteractiveMapScreen.kt` | Un seul `Canvas` + gestes pointeur |

L’onglet Atlas **est** les listes (`atlas`). La carte du ciel est une
route `atlas/sky` (icône étoiles en haut à droite). Onglet bas : « Atlas ».
☰ reste sur l’onglet (c’est un onglet, pas un écran poussé).

Les **données** viennent de Room. En vue « Autour du film », les nœuds
mélangent un film, ses territoires (secteurs par `MapNodeKind`), et jusqu’à
12 films liés. `dedupeConstellation` retire les libellés homonymes.
Couleur = type (`skyKindColor`), pas seulement l’état d’exploration.

------

## 8.2. Qu’est-ce qu’un Canvas Compose ?

Un écran Compose habituel empile des composants (Text, Button, LazyColumn).
Chacun a une taille, une position dans un layout. C’est mal adapté à une
carte : 200 points, zoom, déplacement, traits entre eux.

`Canvas { … }` offre une **surface de pixels**. Dans le lambda `DrawScope`,
on dessine soi-même : cercles, lignes, texte. Rien n’est un « widget
cliquable ». Conséquences :

1. **Le zoom n’agrandit pas des Views.** On redessine tout à chaque frame
   avec d’autres coordonnées.
2. **Un tap n’est pas un `clickable`.** Il faut convertir le doigt en
   coordonnée, puis chercher le nœud le plus proche (**hit-test**).
3. **TalkBack ne voit pas les étoiles.** D’où l’Atlas liste, obligatoire.

Ce n’est **pas** un moteur de jeu (pas de Unity, pas de physique continue,
pas de sprites). Quelques dizaines de pas de « relaxation » au *build* du
graphe, puis les positions sont **figées**.

**Pas de lib tierce** (pas GraphView, pas Maps, pas MPAndroidChart). Tout
tient dans `domain/map/` + un Composable.

------

## 8.3. Deux espaces : monde et écran

C’est l’idée centrale. Sans ça, zoom et pan sont incompréhensibles.

**Espace monde** — coordonnées *stables* des nœuds, centrées autour de
`(0, 0)`, sans unité (pas des dp). Exemple : la France à `(-40, 12)`, le
Japon à `(210, -8)`. Elles ne bougent pas quand tu pinces. Calculées une
fois par calque + catalogue dans `CinemaMapLayout.build`.

**Espace écran** — pixels du `Canvas` (0,0 = coin haut-gauche du viewport).
C’est là que le doigt tape.

La **caméra** fait le pont :

```text
écranX = mondeX × scale + panX
écranY = mondeY × scale + panY
```

- `scale` : zoom (0.28 = vue d’ensemble, 6.5 = très près).
- `panX` / `panY` : décalage en pixels.

Inversement, pour un tap :

```text
mondeX = (écranX − panX) / scale
```

`MapCamera.worldToScreenX/Y` et `screenToWorldX/Y` encapsulent ça.
`CinemaMapLayout.fit` calcule la caméra qui **cadre** tout le graphe dans
le viewport (marge 86 %). `focus` cadre un nœud au centre. `zoomAround`
zoome **autour du centroid des deux doigts** : le point monde sous les
doigts reste sous les doigts (sinon le ciel « saute »).

------

## 8.4. Caméra live vs état Compose

Un `mutableStateOf<MapCamera>` à chaque micro-mouvement du pinch
recomposerait trop. L’écran tient une `LiveCamera` (trois `Float` mutables)
et un compteur `frame`. Le geste écrit dans `LiveCamera` puis incrémente
`frame` → un redraw. Le `Canvas` lit `live.snapshot()`.

Changement de calque, recentrage, tap sur une étoile : interpolation
`animateCamera` (spring Compose, damping 0.86). Ce n’est **pas** de la
physique des nœuds, seulement la caméra qui glisse.

Bornes : `MIN_SCALE = 0.22`, `MAX_SCALE = 14`.

------

## 8.5. Gestes (pointeur, pas `transformable`)

`pointerInput` + `awaitEachGesture` :

| Geste | Comportement |
| --- | --- |
| Un doigt, déplacement > touchSlop | **Pan** : on ajoute le delta à `panX`/`panY` |
| Deux doigts | **Pinch** : `calculateZoom` + `calculatePan` via `zoomAround` au centroid |
| Un doigt, relâché sans drag | **Tap** : hit-test. Film (vue autour) = recentrer la constellation. Sinon feuille + `focus` |

Le hit-test travaille **en monde**. Le rayon écran reste à peu près
constant : `DEFAULT_HIT_RADIUS / scale` (26 px monde au zoom 1, plus
large quand on est dézoomé pour rester tapable).

------

## 8.6. Placement des nœuds (`CinemaMapLayout`)

Le ViewModel (`MainViewModel.cinemaMap`) prépare des **graines**
(`MapSeed` : code + groupe continent éventuel) et des **sacs** (pour
chaque film, la liste des codes du calque). Le layout est **pur**
(aucun Android) : déterministe pour un catalogue donné.

| Calque | Placement | Pourquoi |
| --- | --- | --- |
| **Autour du film** (défaut) | Centre = film, anneau 1 = ses territoires, anneau 2 = jusqu’à 12 films (plus lié = plus près) | Catalogue sans tout afficher |
| Pays, réalisateurs | **Grappes** : un centre par continent (cercle), sunflower local | 42 pays / ~200 auteurs lisibles par région |
| Décennies | **Frise** gauche → droite, légère sinusoïde | Le temps se lit |
| Courants, genres, collections | Sunflower global + **relaxation** | Les territoires souvent vus ensemble se rapprochent |

`buildAround` : `CinemaMapLayout.buildAround(focusId, members)`. Score d’un
voisin : réal +4, collection/courant +3, pays/décennie +2, genre +1.
Angle d’un film lié = moyenne circulaire des territoires partagés.

**Sunflower** : points sur une spirale d’or (angle d’or). Remplit un
disque sans aligner les nœuds en grille.

**Relaxation** (pas un moteur) : 12 à 36 itérations. Tous les nœuds se
repoussent un peu ; les paires **liées** s’attirent selon le poids.
Puis on arrête. Les positions sont stockées dans `CinemaMapGraph.nodes`.

Réalisateurs : le **groupe** = continent du pays le plus fréquent sur
leurs films du catalogue. Labels de continent dessinés au barycentre.

------

## 8.7. Liens (arêtes)

Sauf décennies : une arête = deux codes qui apparaissent **ensemble sur
au moins un film** (`cooccurrenceEdges`). Poids = nombre de films en
commun. Décennies : voisins après tri numérique (`1950—1960—1970`).

Plafond **`MAX_EDGES = 100`** (les plus lourdes). Les genres surtout
produiraient un grillage illisible.

Aucune arête « décorative ». Si elle est dessinée, Room peut l’expliquer.

------

## 8.8. Hit-test

`CinemaMapLayout.hitTest(graph, mondeX, mondeY, radius)` : plus proche
nœud dont le centre est dans le rayon. Linéaire sur `nodes.size` (centaines
de points, négligeable). Pas d’arbre spatial en 0.2.1.

------

## 8.9. Dessin (ordre dans le Canvas)

1. Fond radial `#1B1430` → `#07060D` (nuit, **même en thème clair** :
   salle obscure).
2. Deux halos violet / or très faibles + ~70 « poussières » d’étoiles
   décoratives (déterministes, pas des nœuds).
3. Traits (`SkyLink` `#8B7AC7`, alpha selon le poids).
4. Labels de groupe (continents).
5. Nœuds : cercle pointillé si non exploré, plein sinon, halo si en cours,
   point sombre au centre si maîtrisé, anneau or + **pulse** si
   sélectionné.
6. Labels de nœuds : toujours si sélectionné / exploré / peu de nœuds ;
   sinon seulement à partir d’un zoom (plus exigeant sur Réalisateurs).

Couleurs nœuds : gris `#6A6480` (non exploré), violet `#7A5CB8` (en
cours), ivoire `#F4EFE6` (exploré), or `#E8C68A` (complété / maîtrisé).
Taille du cercle croît avec l’état. **Aucune affiche, aucun bitmap de
film.**

Le texte utilise `nativeCanvas.drawText` (Paint Android) : le `DrawScope`
Compose ne pose pas de Text composable.

------

## 8.10. Données et navigation

`cinemaMap(layer, focusMovieCode)` relit les relations déjà en mémoire.
Focus par défaut : dernier film Vu, sinon un titre d’Initiation.

Tap film (vue autour, pas le centre) → la constellation **se reconstruit**
autour de lui. Tap territoire → `ModalBottomSheet` (liste + ouvrir la fiche).
Fiche film : « Voir sur la carte ».

------

## 8.11. Fichiers

| Fichier | Rôle |
| --- | --- |
| `domain/map/CinemaMap.kt` | `MapLayer` (dont `AROUND_FILM`), `buildAround`, caméra, hit-test |
| `ui/map/InteractiveMapScreen.kt` | Canvas, gestes, chips, FAB, feuille |
| `app/MainViewModel.kt` | `cinemaMap`, `defaultSkyMovieCode`, `mapNodeUi`, `constellationSeeds` |
| `ui/UrbinemaApp.kt` | Onglet `atlas` = ciel ; `atlas/list` = Atlas |
| `ui/model/UiModels.kt` | Contrat + preview |
| `domain/map/CinemaMapTest.kt` | Tests JVM (dont distance liée, zoom > 6,5) |

------

## 8.12. Tests JVM (sans émulateur)

`CinemaMapTest` : continents, frise, co-occurrence, hit-test, caméra,
**constellation** (film lié plus près qu’un film peu lié), pinch au-delà de 6,5.

Le Canvas (pixels, gestes) n’a pas de test UI Compose en 0.2.1.

------

## 8.13. Garde-fous

- Labels, pas de bitmaps d’affiches (mémoire + lecture).
- Atlas **équivalent** : TalkBack, paysage, tablette.
- Un calque à la fois.
- Positions **déterministes** (pas un chaos à chaque ouverture).
- Carte toujours sombre, indépendante du thème app.

------


# 9. Navigation et UI

- Compose Navigation dès le départ, routes aussi **typées** que possible (sérialisation des arguments).
- Écrans attendus : onboarding court, **carte du ciel** (`atlas`), **Atlas
  listes** (`atlas/list`), exploration par dimension, collection, fiche film
  (validation vu + « Voir sur la carte »), quêtes, profil / stats / badges,
  réglages (pseudo).
- Material 3 comme base ; la carte du ciel a sa palette propre (IHM §10.4).

------

# 10. Réseau et APIs externes

**V1 : pas de réseau obligatoire.** L’app doit fonctionner **offline** une fois installée avec son catalogue.

TMDb (ou autre) n’est **pas** la source de vérité. Le catalogue Urbinema l’est.
Les affiches éventuellement téléchargées via `batchPosters/` sont ensuite
des fichiers `assets/` ; l’app n’embarque aucune clé API.

Piste **facultative, pas V1, peut ne jamais exister** : demander l’ajout d’un film absent → ligne dans une table « demandes » à traiter **à la main** ; automatisation API beaucoup plus tard. À n’introduire que si ça ne transforme pas Urbinema en base personnelle exhaustive.

Ktor n’entre dans le Gradle que le jour où un client HTTP existe vraiment.

------

# 11. Build

- Kotlin DSL + Version Catalogs + KSP : obligatoire.
- R8 : à activer avant toute distribution APK un peu sérieuse.
- Pas de CI imposée jour 1 ; un build Gradle reproductible oui.
- Clés API : aucune en V1. Le jour d’une API, **pas** de secret en dur dans le repo public.

------

# 12. Tests et qualité

Minimum utile (parce que le métier est un moteur de règles, pas parce qu’on scale) :

- tests JVM du **domain** (valider un film → collections / badges / quêtes /
  XP / niveau / rang) ;
- le **moteur de rang** est le morceau qui justifie le plus les tests : il est pur, entièrement spécifié, et une erreur y est invisible à l’œil nu ;
- tests de la courbe XP sur les 50 seuils, de l'unicité de récompense et du
  renouvellement lundi 02:00 ;
- tests Room des FK, de l'index partiel `isPrimary` et des transactions d'import ;
- tests JVM du **layout carte** (`CinemaMapTest` : grappes, frise, co-occurrence,
  hit-test, caméra fit / zoomAround / focus) ;
- pas d’obligation de tests UI Compose au premier commit.

Ces tests tournent dans `app/src/test`, exécutables depuis Android Studio comme en ligne de commande, **sans émulateur**.

Lint / detekt : optionnels, pas bloquants pour démarrer.

------

# 13. Évolutivité (sans overkill)

Quand (si) l’app n’est plus « un user, un téléphone » :

| Évolution | Impact prévu |
| --------- | ------------ |
| 2e–30e utilisateur, APK | Même binaire, chacun sa Room sur son device. Rien à « scaler » |
| Play Store | targetSdk, signing, privacy policy si besoin ; pas une réécriture métier |
| Pseudo déjà là | Un vrai compte s’ajouterait **au-dessus** (userId), pas à la place des tables catalogue |
| Demande d’ajout de film | Table `FilmRequest` + traitement manuel |
| TMDb | Client HTTP + matching d’ids, catalogue éditorial **reste** la brique des parcours |
| Sync cloud | Couche data supplémentaire ; domain inchangé si les use cases parlent déjà « un profil » |

On n’implémente **aucune** de ces lignes en V1 « pour plus tard » au-delà d’IDs propres et d’un domain indépendant de l’UI.

------

# 14. Hors stack V1 / plus tard

- Ktor, TMDb, Coil comme pipeline d’affiches distantes.
- WorkManager / notifications push (le renouvellement des quêtes est évalué
  paresseusement à l'ouverture à partir de l'heure locale).
- Firebase, Hilt (Koin reste).
- Lib de graphe.
- Compose Multiplatform.
- CMS web.

------

# 15. Décisions techniques encore ouvertes

Déjà tranchées : projet Gradle Android standard ouvert dans Android Studio,
minSdk 26, Atlas listes + Canvas ciel **0.2.3**, aucune affiche sur la carte, Room,
Paging 3 pour les listes de nœuds, pas TMDb dans l'app, Navigation Compose, téléphone
d'abord, portrait avant paysage, 1 profil local, catalogue N croissant, images
locales packagées en V1, XP et 50 niveaux indépendants du rang.

Encore à caler :

- épreuve du merge catalogue sur une grosse delta (retrait de films) ;
- production des binaires `assets/media/` (voir `ASSETS.md`).
