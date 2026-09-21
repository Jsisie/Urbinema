# Architecture des médias — Urbinema

**Statut :** affiches, badges, avatars et rangs packagés testables (png / jpg / jpeg / webp).
**Lié à :** `MediaPaths.kt`, `EditorialImage`, éventuellement `mediaAssets` plus tard.

Les images ne sont **pas** distantes. L’app n’appelle **pas** TMDB et n’a
aucune URL. Tout fichier éditorial est embarqué ; la photo choisie par
l’utilisateur reste privée. Un script hors-app (`batchPosters/`) peut
télécharger des affiches TMDB pour les **copier** ensuite dans
`assets/media/posters/`. Crédit TMDB dans À propos.

---

## 1. Deux familles

| Famille | Stockage | `storageType` | Exemple |
| --- | --- | --- | --- |
| Éditorial (affiches, plus tard drapeaux, portraits, badges…) | APK `assets/media/…` | `ASSET` | `media/posters/TITANIC_1997.jpg` |
| Utilisateur (photo de profil choisie) | `filesDir/media/users/` | `FILE` | `media/users/avatar.webp` |

Le JSON catalogue ne pointe **jamais** vers un fichier utilisateur.

---

## 2. Dossiers packagés

```text
app/src/main/assets/media/
├── posters/         affiches de films          {MOVIE_CODE}.webp|png|jpg
├── collections/     couvertures de collections {COLLECTION_CODE}…
├── directors/       portraits de réalisateurs  {DIRECTOR_CODE}…
├── countries/       drapeaux / visuels pays    {COUNTRY_CODE}…
├── continents/      visuels continents         {CONTINENT_CODE}…
├── avatars/         portraits proposés         AVATAR_01…
├── badges/          pictogrammes de badges     {BADGE_CODE}…
└── rankings/        visuels de rangs           {RANK_CODE}…
```

Convention de nom : **le code éditorial déjà en Room** (`movies.code`), ASCII,
plus l’extension. Formats acceptés : **`.webp`**, **`.png`**, **`.jpg`**, **`.jpeg`**
(casse indifférente). Si plusieurs fichiers existent pour le même code, l’ordre
de préférence est webp → png → jpg → jpeg.

Pour tester une affiche **sans toucher au JSON** :

1. Lire le `code` du film dans Room (`TITANIC_1997`).
2. Déposer `TITANIC_1997.jpg` (ou png / webp) dans `app/src/main/assets/media/posters/`.
3. Relancer l’app (Rebuild si Android Studio n’a pas recopié les assets).
4. Ouvrir la fiche du film : l’affiche remplace le placeholder.

Pour un badge, même convention avec `badges.code` :

1. Lire le `code` (`001` pour Premier Rideau).
2. Déposer `001.jpeg` (ou png / jpg / webp) dans `app/src/main/assets/media/badges/`.
3. Relancer : le visuel apparaît sur le Profil (badges obtenus, nom en dessous)
   et dans la liste Tous les badges (visuel à gauche, nom à côté).

Pour un rang, même convention avec `rankings.code` (`RANK_01` … `RANK_10`) :

1. Déposer `RANK_01.webp` (ou png / jpg / jpeg) dans
   `app/src/main/assets/media/rankings/`.
2. Relancer : le visuel remplace le placeholder sur le Profil (dans le cadre),
   sur Parcours et dans l’échelle des 10 rangs. **Le nom du rang reste affiché**
   sous l’image. Sans fichier, le nom reste seul dans le cadre, comme avant.

Pour un avatar packagé (onboarding + Réglages + Profil) :

1. Déposer `AVATAR_01.png` (ou jpg / webp) dans `app/src/main/assets/media/avatars/`.
2. Codes livrés : `AVATAR_01` … `AVATAR_10`. Choix en carrousel coulissant
   à l’onboarding et dans Réglages.
3. `users.avatarCode` pointe vers ce code. Pas de JSON.

Le JSON `mediaAssets` / `posterMediaCode` reste optionnel. Il servira plus tard
si on veut un chemin différent du code, pas pour le cas normal.

---

## 3. Branchement JSON (optionnel, plus tard)

Dans `catalog.json` :

1. Déclarer l’asset dans `mediaAssets` :
   `{ "code": "POSTER_TITANIC_1997", "storageType": "ASSET", "path": "media/posters/TITANIC_1997.jpg" }`
2. Le référencer : `movies[].posterMediaCode`, `collections[].coverMediaCode`,
   `directors[].portraitMediaCode`, `countries[].imageMediaCode`, etc.

Sans fichier correspondant, l’UI garde le placeholder. L’import ne
doit pas échouer : le validateur vérifie que le **code** existe dans
`mediaAssets`, pas que le binaire est présent sur disque.

---

## 4. Photo de profil utilisateur — V2

L’onboarding 0.1.11 demande déjà un **avatar packagé**. La photothèque
(fichier privé) reste V2.

Flux prévu, déjà cadré dans `MediaPaths` :

1. L’utilisateur choisit une image (photothèque) **ou** un avatar packagé.
2. Si photothèque : copie redimensionnée vers
   `filesDir/media/users/avatar.webp` (`USER_AVATAR_RELATIVE`).
3. Une ligne `media_assets` `storageType=FILE` est upsertée, code
   `USER_AVATAR_{userId}`.
4. `users.avatarMediaId` pointe vers cet asset.
5. Désinstall = perte de la photo, comme le reste du profil.

Aucun fichier utilisateur n’est lu depuis `assets/`.

---

## 5. Ce qu’il ne faut pas faire

- Mettre des JPEG 4K : viser ~200–400 px de côté pour les portraits,
  ~600 px de large pour les affiches.
- Nommer par titre français (`titanic.jpg`) : le code Room casse au
  premier accent. Toujours `{CODE}.ext`.
- Servir depuis internet « en attendant » (l’app doit rester offline).
- Mettre une clé TMDB dans l’APK : `batchPosters/` lit `.env` **en local**.
- Stocker la photo user dans le JSON catalogue.
