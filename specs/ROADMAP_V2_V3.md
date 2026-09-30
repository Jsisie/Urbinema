# Feuille de route — V1 close, V2 = carte

**Date :** 2026-09-19  
**Livrable de référence :** catalogue et code prêts pour la release **0.1.12**
(Léo bumpera `versionName` / `versionCode` au moment de l’APK).  
**En cas de conflit :** le code et les tests font foi ; `DECISIONS_ACTEES.txt`
prime sur les cahiers plus anciens. Le mode d’emploi du code :
`SPECIFICATION_DEVELOPPEUR.md`.

La **V2, c’est surtout la carte interactive**. Jouable en **0.2.3** :
ciel = icône étoiles depuis l’Atlas, constellation autour d’un film,
couleurs par type, calques en option. XP film = **10** (essai).

Comment ça marche (à lire pendant le test) :

- métier / utilisateur : `CahierDesCharges_Fonctionnel_v2.md` §11
- Canvas, caméra, monde/écran, hit-test : `CahierDesCharges_Technique.md` §8
- gestes, couleurs, feuille, wireframes : `CahierDesCharges_IHM.md` §10

---

## 0. Ce que la V1 livre (jouable, close)

Moteur, persistence, IHM des cinq onglets, onboarding, quêtes, rang, badges,
avatars packagés, affiches par code, catalogue démo élargi.

- App locale, un profil Room, pas de compte.
- Onboarding : pseudo + âge + **avatar packagé** (10 visuels, carrousel).
- Avatar sur le Profil et changeable dans Réglages (même carrousel).
- Badges : 30 définitions, vitrine Profil (3), N&B si non obtenus, liste
  complète, rareté Figurant / Second rôle / Tête d’affiche. Visuels par
  `{CODE}` dans `assets/media/badges/`.
- Affiches / portraits : convention `{CODE}.webp|png|jpg|jpeg` dans
  `assets/media/…`. Batch hors-app `batchPosters/` (clé TMDB dans `.env`).
- Cadenas Initiation (suivie + ≥ 1 Vu) **et** cadenas entre groupes + cliquet.
- Pack JSON **v11** : ~405 films, 15 collections (Initiation inchangée,
  les 14 autres alimentées), 50 quêtes types (16/17/17), 42 pays.
- Quêtes hebdo lundi 02:00 : une tirée au hasard par palier, éligibilité
  `remainingCapacity`.
- XP 1–50, rang formule lissée v0.3.1, **25 XP** si le film est dans une collection suivie + quêtes 100/250/500.
- Atlas = **listes** (icône liste, TalkBack).
- **0.2.1 :** première carte du ciel (autour d’un film).
- **0.2.3 :** couleurs par type + légende, pas de doublons de libellé,
  pop-up badges persistés, historique Accueil 30 + tout voir.
- Thème, langue, grain persistés. Aide. À propos.

Photothèque (photo perso depuis la galerie du téléphone) : **pas** en V1.

---

## 1. V2 — carte interactive

C’est le livrable. Compose **Canvas custom**. Vue par défaut : constellation
autour d’un film. Calques territoires en puces. Atlas listes = icône liste.

Hors V2 : constellation de films, acteurs / compositeurs sur le graphe,
moteur de jeu, lib de graphe tierce.

Métaphore exacte (ciel vs autre) : ouverte, à juger sur prototype.

Confort éventuellement dans le même train, **après** la carte, si Léo le
demande : photothèque, bios réalisateurs, recherche continents, plus de
collections / caractéristiques, export CSV. Ce n’est pas le cœur de la V2.

---

## 2. V3+ 

Culture / analyse, reco, social, cloud, TMDb **dans l’app**, CMS web : pas
avant, et plusieurs de ces lignes **peuvent ne jamais exister**.

**Collections — ordre des films (noté 2026-09-21).** Aujourd’hui chaque
collection liste ses films par **année de sortie croissante**. En V3,
remplacer cet ordre chronologique par un ordre **éditorial**, du plus
accessible au plus complexe à voir (Initiation déjà un peu dans cet esprit).
Le `displayOrder` de `collections_movies` est le bon levier : pas besoin
d’un second champ. L’Atlas (pays, courants, etc.) garde son tri utilisateur.

---

## 3. Réglé par le code (ne plus rouvrir)

- Stack AGP 8.13.2 / Gradle 8.13 / Kotlin 2.0.21 / minSdk 26.
- Module Gradle `:urbinema` (dossier `app/`).
- Merge de catalogue : upsert par `version` de pack, codes stables, `user_*`
  intacts.
- Explorer = Collections. Carte V1 = Atlas listes.
- Quêtes : pool 50, tirage hebdo éligible.
- Langue / thème / grain persistés.
- Cadenas Initiation, groupes, cliquet, suivi → %, titres dorés, 100 % UI.
- 10 avatars packagés, carrousel. Badges packagés par code.
- **25 XP** si collection suivie. Crédits À propos + page Sources.
