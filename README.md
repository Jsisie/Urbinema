# Urbinema

Application Android locale de découverte et de progression cinématographique.

## Démarrage

1. Ouvrir la racine dans Android Studio.
2. Laisser Gradle synchroniser le projet.
3. Sélectionner un appareil Android API 26 ou supérieur.
4. Exécuter la configuration `app`.

Au premier lancement, l’app importe `app/src/main/assets/catalog/catalog.json`
dans Room (`urbinema.db`) si le pack est plus récent. Les lancements suivants
ne réécrasent pas la progression. Une pop-up demande pseudo, âge et avatar tant qu’aucun
profil local n’existe, ou tant que la date de naissance manque.

Le mode d’emploi complet (code **0.1.11**, prêt **0.1.12**) est dans
`specs/SPECIFICATION_DEVELOPPEUR.md`.
V2 (carte Canvas, GO requis) : `specs/ROADMAP_V2_V3.md`. Médias : `specs/ASSETS.md`.
Décisions : `specs/DECISIONS_ACTEES.txt`.

## Vérification

```powershell
.\gradlew.bat :urbinema:testDebugUnitTest
.\gradlew.bat :urbinema:assembleDebug
```

Les tests Room nécessitant Android :

```powershell
.\gradlew.bat :urbinema:connectedDebugAndroidTest
```

## Documentation

- cahier fonctionnel : `specs/CahierDesCharges_Fonctionnel_v2.md` ;
- architecture visuelle : `specs/CahierDesCharges_IHM.md` ;
- décisions techniques : `specs/CahierDesCharges_Technique.md` ;
- décisions actées : `specs/DECISIONS_ACTEES.txt` ;
- implémentation : `specs/SPECIFICATION_DEVELOPPEUR.md` ;
- batch TMDB (affiches et fiches JSON) : `batchPosters/README.md`.

Le catalogue éditorial V1 est local. Aucun compte distant, service cloud ou
appel TMDB n’est requis **dans l’app**.
