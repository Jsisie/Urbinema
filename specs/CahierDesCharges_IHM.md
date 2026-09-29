# Cahier des charges IHM / Charte graphique

### Urbinema

**Version :** 1.5 — 0.3.0 : splash logo, guide, sources, index lettres, appui long Vu, célébration de rang
**Statut :** Direction de travail validée ; carte du ciel = maquette jouable (0.2.3+)
**Lié à :** `CahierDesCharges_Fonctionnel_v2.md`, `CahierDesCharges_Technique.md`, `DECISIONS_ACTEES.txt`

> La direction artistique, la navigation et les traitements proposés en v0.2
> sont validés comme base de maquettage. Ils seront corrigés après visualisation,
> pas avant.
>
> Les éléments **imposés par Léo** sont signalés par la mention **[imposé]**. Le reste relève de ma proposition.
>
> **0.3.0 —** Pendant le chargement du catalogue, fond blanc plein écran et icône de l’app (plus le texte « Votre aventure commence ici »). Après le pseudo, un guide de 6 pages (intro, Accueil, Atlas, Collections, futur Parcours, Profil) dans un panneau d’environ 60 % de l’écran, le reste fortement flouté. Rejouable dans Réglages (« Revoir le guide »). « Voir toutes les sources » sous les crédits. Index A–Z blanc (couleur du texte, pas l’or) sur pays, courants, genres et réalisateurs. Appui long sur un film d’une liste → confirmer Vu. La chaîne des rangs s’ouvre sur le rang courant. Un nouveau rang ouvre un dialogue avec confettis. Chaque liste de films affiche son effectif en petit. La fiche réalisateur montre un portrait (plus petit qu’une affiche) et la biographie au-dessus de la liste de films, avec un espace sous le titre « Biographie ». La biographie suit la langue de l’app. Le grain argentique est à peine plus visible en thème sombre. L'onglet Parcours liste des lectures (une grande carte par parcours, pas une carte de collection). Le fil est vertical : une bulle par courant, un trait, un point d'interrogation qui ouvre une petite fenêtre avec seulement la phrase de transition. La fiche courant est une feuille qui laisse voir le fil au-dessus.

------

# Sommaire

1. [Périmètre](#1-périmètre)
2. [Principes d'interface](#2-principes-dinterface)
3. [Direction artistique](#3-direction-artistique)
4. [Couleurs](#4-couleurs)
5. [Typographie](#5-typographie)
6. [Formes, élévation, densité](#6-formes-élévation-densité)
7. [Iconographie et états](#7-iconographie-et-états)
8. [Navigation](#8-navigation)
9. [Écran Accueil](#9-écran-accueil)
10. [Écran Carte](#10-écran-carte)
11. [Écran Progression](#11-écran-progression)
12. [Écran Profil](#12-écran-profil)
13. [Rang — traitement visuel](#13-rang--traitement-visuel)
14. [Badges — traitement visuel](#14-badges--traitement-visuel)
15. [Collections et parcours](#15-collections-et-parcours)
16. [Fiche film](#16-fiche-film)
17. [Réglages](#17-réglages)
18. [Inventaire d'écrans](#18-inventaire-décrans)
19. [Mouvement et animation](#19-mouvement-et-animation)
20. [Accessibilité](#20-accessibilité)
21. [Implémentation](#21-implémentation)
22. [Questions ouvertes](#22-questions-ouvertes)

------

# 1. Périmètre

Application Android, **téléphone d'abord**, tablette acceptable, pas de TV ni de PC.

**Portrait** en priorité, **paysage** dans un second temps (cahier technique §3).

Un seul utilisateur, profil local, pas de dimension sociale : l'interface n'a pas à prévoir de vues « autres utilisateurs », de flux, ni de partage.

------

# 2. Principes d'interface

## 2.1. Vocabulaire affiché

Le modèle de données parle de **mouvements** (table unique regroupant mouvements, styles, courants, manifestes, écoles). C'est un terme technique.

**L'interface évite ce mot.** L'utilisateur voit des **collections**, des parcours, des territoires à explorer — pas une taxonomie universitaire.

Même logique pour les autres termes internes : *poids*, *diversité*, *profondeur*, *score*, *rareté* n'apparaissent jamais tels quels à l'écran.

| Interne | Affiché |
| --- | --- |
| mouvement | collection, courant |
| poids du film | (jamais affiché) |
| diversité | étendue, territoires parcourus |
| profondeur | approfondissement |
| score | (jamais affiché) |
| caractéristique | territoire, zone |

## 2.2. Principes repris du fonctionnel §18

- **Compréhension immédiate** — ce qui a été exploré, ce qui reste, comment progresser.
- **Progression visible** — rang, badges, collections en cours, quêtes du moment.
- **Découverte** — les zones inconnues doivent rester visibles, pas cachées.
- **Gamification mesurée** — ludique, jamais un jeu mobile agressif. Pas de confettis, pas de badge qui hurle toutes les trois minutes. Une **seule** boîte de félicitations à 100 % d’une collection suivie.
- **Identité cinéphile** — culturelle et exploratoire. Material 3 par défaut ne donnera **pas** ce ton : il faut un habillage complet.

## 2.3. La règle du cul-de-sac

Aucun écran ne doit être une impasse. Depuis n'importe quelle fiche, il doit toujours exister au moins une **piste suivante** : un film du même courant, un pays voisin, une collection adjacente.

C'est le principe d'exploration du produit traduit en règle d'interface.

------

# 3. Direction artistique

## 3.1. Intention

> **La salle obscure, pas la bobine.**

Le cinéma visuellement, c'est d'abord **le noir** — celui de la salle avant la projection — et **une source de lumière chaude** qui le traverse. Tout part de là.

Trois qualités recherchées, dans cet ordre :

1. **Élégant** — l'application doit donner l'impression d'un objet soigné, pas d'un tableau de bord.
2. **Sombre** — noir profond par défaut **[imposé]**, thème clair disponible.
3. **Moderne** — contemporain, pas rétro. Voir §3.2.

## 3.2. La référence Artly, et ce qu'on en garde

Artly sert de référence déclarée. Ce qu'on en retient et ce qu'on en écarte :

| On garde | On écarte |
| --- | --- |
| Les collections d'œuvres organisées par **mouvement** et par **époque** | Le côté légèrement daté du traitement graphique |
| L'idée de collections progressivement ouvertes, conservée pour plus tard | Les ornements, dorures, textures « musée » |
| L'idée que la culture se parcourt comme un territoire | La densité de vignettes qui transforme l'art en catalogue |

**« Plus moderne qu'Artly »** se traduit concrètement par : moins d'ornement, plus d'espace blanc (enfin, d'espace noir), une typographie qui porte l'élégance à la place des décorations, et des aplats francs plutôt que des dégradés et des ombres portées.

## 3.3. Ce qu'on s'interdit

Le cinéma a un imaginaire visuel usé jusqu'à la corde. Sont **proscrits** :

- la bobine de film, le clap, la caméra manivelle, le fauteuil rouge, le pop-corn ;
- les perforations de pellicule utilisées comme bordure décorative ;
- le rideau de velours rouge ;
- l'or clinquant des récompenses (statuettes, lauriers) ;
- les dégradés violets Material 3 par défaut.

Ces éléments diraient « cinéma » immédiatement, et diraient aussi « fait vite ». Urbinema doit plutôt évoquer **un beau livre d'histoire du cinéma** qu'un multiplexe.

## 3.4. Le grain

Une **texture de grain argentique** discrète, overlay Compose plein écran,
unifie l'ensemble. En 0.1.10 le voile est **un peu plus léger** qu’en 0.1.9 :
fond noir à ~3,2 % d’opacité, points espacés de 5 dp, specks ~7–9 % d’alpha.
Texture **statique**, jamais animée.

Contraintes : désactivable dans les Réglages (défaut **désactivé**), persisté
dans DataStore. Ce n’est qu’un effet visuel : il ne touche ni au catalogue ni
à la progression.

Le grain est livré ; le calibrage actuel (0.1.10) est le voile ~3,2 %.
On ne le renforce plus sans nouvel essai visuel.

------

# 4. Couleurs

## 4.1. Principe

Deux thèmes complets **[imposé]** : **sombre par défaut**, clair disponible. Chaque thème vit dans son propre fichier de configuration (§21.2) **[imposé]**.

Aucune couleur n'est écrite en dur dans un Composable. On passe **toujours** par un jeton sémantique.

## 4.2. Thème sombre — « Salle obscure » (défaut)

| Jeton | Hex | Usage |
| --- | --- | --- |
| `background` | `#0A0A0C` | Fond général. Presque noir, très légèrement bleuté — un noir pur serait dur et écraserait le grain |
| `surface` | `#131317` | Cartes, listes, feuilles |
| `surfaceElevated` | `#1C1C22` | Dialogues, menu latéral, barre basse |
| `surfacePressed` | `#26262E` | État pressé, survol |
| `outline` | `#2E2E37` | Séparateurs, contours discrets |
| `onBackground` | `#F4EFE6` | Texte principal — **ivoire, jamais blanc pur**. Le blanc pur sur noir vibre et fatigue |
| `onBackgroundMuted` | `#F4EFE6` à 62 % | Texte secondaire |
| `onBackgroundFaint` | `#F4EFE6` à 38 % | Texte tertiaire, non exploré |
| `accent` | `#E8C68A` | **La lumière du projecteur.** Ambre pâle et chaud. Progression, complétion, éléments actifs |
| `accentMuted` | `#A8895A` | Accent en retrait |
| `cool` | `#6E8FA8` | Bleu-gris froid — « nitrate ». En cours, liens de la carte, informations neutres |
| `rare` | `#C9D6E3` | Argent froid. Réservé à la rareté et aux rangs 8 à 10 (§13.3) |
| `danger` | `#B4635A` | Retrait d'un film, action destructive. Terre cuite, pas rouge vif |

Le contraste `onBackground` / `background` atteint environ 17:1, très au-delà des 4,5:1 exigés.

## 4.3. Thème clair — « Salle éclairée »

Le thème clair **n'est pas l'inverse mécanique** du sombre. Il change de métaphore : on passe de la salle obscure au **papier** — programme de cinémathèque, page de livre.

| Jeton | Hex | Usage |
| --- | --- | --- |
| `background` | `#F5F1E8` | Blanc cassé chaud. Un blanc pur serait clinique |
| `surface` | `#FBF8F1` | Cartes |
| `surfaceElevated` | `#FFFFFF` | Dialogues |
| `surfacePressed` | `#EBE5D8` | État pressé |
| `outline` | `#DCD4C4` | Séparateurs |
| `onBackground` | `#17171B` | Texte principal |
| `onBackgroundMuted` | `#17171B` à 66 % | Texte secondaire |
| `onBackgroundFaint` | `#17171B` à 42 % | Texte tertiaire |
| `accent` | `#8A6A2F` | Ambre assombri — l'ambre clair du thème sombre serait illisible sur fond clair |
| `accentMuted` | `#B39B6E` | Accent en retrait |
| `cool` | `#3E5A70` | Bleu-gris assombri |
| `rare` | `#5A6B7A` | Argent assombri |
| `danger` | `#8E3F36` | Action destructive |

**Piège classique à éviter :** reprendre les mêmes accents dans les deux thèmes. `#E8C68A` sur `#F5F1E8` donne un contraste de 1,6:1 — invisible. D'où deux valeurs distinctes par rôle.

## 4.4. Couleur et signification

La couleur ne porte **jamais seule** une information (§20). Les cinq états de la carte se distinguent par la couleur **et** par le trait, l'opacité et la forme (§7.3).

------

# 5. Typographie

## 5.1. Deux familles, deux rôles

| Rôle | Police | Justification |
| --- | --- | --- |
| **Display** — rang, titres d'écran, noms de collections | **Bodoni Moda** | Didone à fort contraste. C'est la typographie des affiches et des cartons de générique. Elle porte à elle seule l'élégance, ce qui permet de supprimer tout ornement ailleurs |
| **Texte** — tout le reste | **Inter** | Grotesque neutre, variable, excellente en petit corps. L'application est très textuelle (§22 du technique) : la lisibilité prime |

Les deux sont sur Google Fonts, licence libre, embarquables en local — cohérent avec une application qui doit fonctionner hors ligne.

**Alternatives** si Bodoni Moda paraît trop marquée : *Newsreader*, *Instrument Serif*, *Libre Caslon Display*. À arbitrer sur maquette.

## 5.2. Échelle

| Style | Police | Taille | Graisse | Usage |
| --- | --- | --- | --- | --- |
| `rankDisplay` | Bodoni Moda | 44 sp | 500 | Le nom du rang sur le profil. Le plus gros texte de l'application |
| `displayLarge` | Bodoni Moda | 32 sp | 500 | Titre d'écran |
| `displayMedium` | Bodoni Moda | 24 sp | 500 | Nom de collection, de courant |
| `titleLarge` | Inter | 20 sp | 600 | Titre de section |
| `titleMedium` | Inter | 16 sp | 600 | Titre de carte, de ligne |
| `body` | Inter | 15 sp | 400 | Texte courant, interligne 1,5 |
| `bodySmall` | Inter | 13 sp | 400 | Métadonnées : année, pays, durée |
| `label` | Inter | 12 sp | 600 | Barre basse, puces, majuscules espacées |
| `numeric` | Inter | variable | 500 | Statistiques — **chiffres tabulaires obligatoires**, sinon les colonnes dansent |

## 5.3. Règles

- Longueur de ligne maximale d'environ 70 caractères sur les textes éditoriaux.
- Interligne généreux (1,5) sur le corps de texte : l'application se lit posément.
- **Pas de texte en capitales** au-delà des micro-libellés — illisible en Bodoni.
- Respecter la taille de police système : pas de `sp` figés en `dp`.

------

# 6. Formes, élévation, densité

## 6.1. Formes

Rayons volontairement **faibles** : les grands arrondis font « application mobile grand public », l'inverse du ton recherché.

| Élément | Rayon |
| --- | --- |
| Cartes, vignettes | 8 dp |
| Feuilles, dialogues | 16 dp (haut uniquement pour les feuilles) |
| Puces, badges textuels | complet |
| Champs de saisie | 8 dp |
| Emblème de rang | forme dédiée (§13.2) |

## 6.2. Élévation

**Pas d'ombres portées.** Sur un fond presque noir, une ombre ne se voit pas ; elle salit. L'élévation se lit par la **valeur de surface** (`surface` → `surfaceElevated`) et, si nécessaire, par un contour `outline` d'un pixel.

C'est aussi ce qui distingue le plus visiblement Urbinema d'une application Material 3 par défaut.

## 6.3. Densité et espacement

Grille de **4 dp**. Espacements standards : 4, 8, 12, 16, 24, 32, 48.

Marge latérale d'écran : **20 dp** (et non 16, plus courant) — un peu plus d'air, cohérent avec le ton posé.

Densité **moyenne à faible**. Urbinema n'est pas une application de productivité : on préfère quatre éléments respirants à huit comprimés.

------

# 7. Iconographie et états

## 7.1. Style d'icônes

Icônes **linéaires**, trait de 1,5 dp, coins nets, jamais pleines sauf pour signaler un état actif.

Material Symbols en variante *Outlined* couvre 90 % des besoins. Les 10 %
restants — états de la carte et emblèmes de rang — sont dessinés sur mesure.

## 7.2. Cadenas des collections (0.1.10)

Hors **Initiation**, une collection encore verrouillée s’affiche en niveaux de
gris (~42 % d’opacité) avec une **icône cadenas**. Un tap n’ouvre pas la fiche :
il affiche une boîte (`setLocales`) :

- titre : « Collection verrouillée »
- Initiation pas encore ouverte : « Suivre la collection et marquer un film comme vu »
- palier suivant : « commence au moins N collection(s) de {groupe précédent}
  et marque au moins 2 films dans chacune »

Une fois un palier ouvert, il **reste** ouvert (cliquet). Une collection
**terminée** (suivie et 100 %) replace le cadenas par une **icône check**.

Les territoires de l’Atlas (pays, courants, etc.) n’ont **pas** de cadenas :
contour pointillé et faible opacité pour le non exploré.

## 7.3. Les cinq états de progression

Ces états s'appliquent à toute entité explorable : pays, décennie, courant, collection, époque. Ils doivent être lisibles **sans couleur**.

| État | Couleur | Trait | Opacité | Signe |
| --- | --- | --- | --- | --- |
| Non exploré | `onBackgroundFaint` | pointillé | 40 % | cercle vide |
| En cours | `cool` | plein 1 dp | 100 % | arc de progression partiel |
| Exploré | `onBackground` | plein 1 dp | 100 % | aucun |
| Complété | `accent` | plein 2 dp | 100 % | anneau fermé |
| Maîtrisé | `accent` | plein 2 dp + halo | 100 % | anneau fermé + point central |

Quatre variables redondantes pour une seule information : c'est volontaire, et c'est ce qui rend l'interface utilisable en daltonisme comme en plein soleil.

------

# 8. Navigation

## 8.1. Structure générale **[imposé]**

```text
┌─────────────────────────────────────────┐
│  ☰     [logo Accueil]            ? / ⚙  │  ← ☰ sur chaque onglet ; ⚙ sur Profil ; ? si aide
│                                          │
│              CONTENU                     │
│                                          │
├─────────────────────────────────────────┤
│   ⌂        ▦      ((●))      ◈      ☺    │  ← barre basse, 5 entrées
│ Accueil  Collections  CARTE  Parcours  Profil│
└─────────────────────────────────────────┘
```

## 8.2. Barre basse — cinq entrées

Léo a imposé : une page principale, **la carte au milieu**, un onglet de suivi (rangs, quêtes), et **le profil tout à droite**.

Cinq entrées permettent que la carte tombe **exactement au centre** — avec quatre, elle serait décalée.

| # | Entrée | Contenu | Statut |
| --- | --- | --- | --- |
| 1 | **Accueil** | Point d'entrée quotidien (§9) | **[imposé]** |
| 2 | **Collections** | Liste groupée par difficulté. Initiation ouverte ; cadenas Initiation (≥ 1 Vu) puis entre groupes. Suivies en or, 0 % si non suivie, 100 % or + check. Libellé barre basse **une ligne** (11 sp). | **[imposé]** |
| 3 | **Atlas** | Listes filtrables (§10.2) ; carte du ciel via l’icône étoiles (§10.3) | **[imposé]** — position centrale imposée |
| 4 | **Parcours** | Liste des parcours pédagogiques, puis fil vertical de courants. L'ancien écran (rang, quêtes, collections en cours) reste dans le code, hors barre. | **[imposé]** |
| 5 | **Profil** | Pseudo, rang, badges (§12) | **[imposé]** — position à droite imposée |

### Traitement de l'entrée centrale

La carte est le seul onglet **surélevé** : cercle légèrement plus grand, en `accent`, débordant sur le bord supérieur de la barre.

Justification : la carte est l'objet le plus spectaculaire du produit et mérite d'attirer l'œil — mais **elle n'est pas le cœur** (le rang l'est, fonctionnel §9.2). La surélever visuellement sans lui donner plus de poids fonctionnel est exactement le bon dosage.

### Détails

- Libellés **toujours visibles**, **une seule ligne**, jamais seulement au survol. Cinq icônes muettes sont indéchiffrables. « Collections » ne passe pas à la ligne.
- Onglet actif : icône pleine + libellé en `accent`. Onglet inactif : icône linéaire + libellé en `onBackgroundMuted`.
- **Pas de badge de notification** sur les onglets. Contraire au principe « gamification mesurée ».
- Chaque onglet conserve sa propre pile de navigation. Retaper l'onglet actif remonte en haut de la pile.

## 8.3. Menu latéral **[imposé]**

Un **menu burger en haut à gauche** de l'écran d'accueil, ouvrant un tiroir latéral.

### Une réserve à formuler

Cohabiter un tiroir et une barre basse est généralement considéré comme redondant : deux systèmes de navigation pour un même produit, et l'utilisateur ne sait plus où chercher. C'est d'ailleurs ce qui date le plus une interface Android.

**La solution retenue** conserve le tiroir demandé mais lui donne un rôle **qui ne recoupe pas** la barre basse :

> La barre basse contient les **cinq modes d'usage**. Le tiroir contient **les index exhaustifs** — les endroits où l'on va chercher quelque chose de précis, rarement, pas ceux où l'on navigue au quotidien.

| Barre basse — modes | Tiroir — index |
| --- | --- |
| Accueil | Tous les badges |
| Collections | Toutes les collections |
| Carte | Recherche |
| Parcours | Statistiques détaillées |
| Profil | Tous les rangs |

L'Accueil affiche un résumé des quêtes, collections en cours et événements.
Les écrans détaillés vivent dans **Parcours** ; les index exhaustifs dans le
tiroir. Ce n'est pas un doublon de navigation : une carte de résumé ouvre sa
destination unique.

Le tiroir est accessible **depuis chaque onglet** (☰ dans la barre haute).
Un peu plus d’air entre le logo, le titre « Index d’exploration » et le
premier item (Tous les rangs) — padding logo `md`, titre `xxs` en dessous.

## 8.4. Barre haute et réglages **[imposé]**

Sur **tous les onglets** : à gauche, **☰** (tiroir des index).

Sur l’**Accueil** : logo Urbinema au centre de la barre ; le rang / niveau / XP
vit **sous** la barre, dans l’en-tête cliquable (ouvre le Profil).

Sur le **Profil** : à droite, **⚙** roue des réglages (§17).

Sur Parcours (et les écrans d’aide thématiques) : **?** ouvre l’aide.

Sur l’**onglet Atlas** : ☰, **?** aide, icône **étoiles** (carte du ciel).

Sur la **carte du ciel** : flèche retour, titre « Carte du ciel », **?**.
Fond nuit en salle obscure ; **papier** (salle éclairée) en thème clair.

Les autres écrans hors onglet : flèche de retour + titre.

## 8.5. Ce qu'on ne fait pas

- Pas de menu à trois points. Tout ce qui mériterait d'y être doit être visible ou dans le tiroir.
- Pas de bouton d'action flottant **global**. Exception 0.2.1 : le FAB
  **recentrer** de la carte du ciel (cible, bas droite), local à cet écran.
- Pas d'onglets horizontaux en haut **et** d'une barre en bas sur le même écran
  (les puces de calque du ciel sont des filtres, pas une deuxième nav).

------

# 9. Écran Accueil

L'écran le plus souvent vu, et le seul qui n'était spécifié nulle part.

## 9.1. Intention

> **Voir immédiatement où j'en suis et reprendre mon parcours.**

L'Accueil est un tableau de progression personnel. Il ne recommande aucun film
en V1 : Urbinema propose déjà ses films à travers les collections et parcours.

## 9.2. Structure validée

```text
┌────────────────────────────────────────────┐
│ ☰  [logo]                                   │
│ EXPLORATEUR                        NIV. 12  │ ← zone fixe, ouvre le Profil
│ ━━━━━━━━━━━━━━━━━━━━━━━━░░░  380 / 500 XP │
├────────────────────────────────────────────┤
│ QUÊTES DE LA SEMAINE                        │
│ Bronze · Un film muet              ✓ 100 XP│
│ Argent · Trois pays d'Asie       2 / 3 ▰▰▱ │
│ Or · Cinq films avant 1950       1 / 5 ▰▱▱ │
│                                            │
│ COLLECTIONS EN COURS                       │
│   (image)      (image)      (image)        │
│     35 %         18 %         62 %         │
│ Néoréalisme   Nouvelle V.   Âge d'or japonais│
│                                            │
│ HISTORIQUE                                 │
│ Aujourd'hui · Le Roi Lion                  │
│ Hier · Badge obtenu                        │
│ Lundi · Quête Bronze terminée              │
│ ...                                        │
├────────────────────────────────────────────┤
│  Accueil  Collections  CARTE  Parcours Profil │
└────────────────────────────────────────────┘
```

## 9.3. Répartition

- **Premier tiers** : en-tête rang/niveau/XP et trois quêtes.
- **Deuxième tiers** : **collections en cours** = suivies, **pas** à 100 %,
  **pas** cadenassées. Vignettes circulaires et pourcentage. Une collection
  terminée ou encore verrouillée n’y figure pas.
- **Dernier tiers** : historique chronologique, **titres de films lisibles**
  (jamais `LE_ROI_LION_1994`).

Cette répartition décrit le premier écran visible. En défilant, l'historique
prend progressivement la majorité puis toute la hauteur disponible.

## 9.4. Comportement fixe et défilement

Seul l'en-tête **rang + niveau + barre XP** reste fixé. Les quêtes, parcours et
événements défilent. Fixer aussi les quêtes consommerait trop d'espace sur les
petits écrans.

Chaque vignette de parcours ouvre sa fiche complète. L'historique Accueil
montre les **50** événements les plus récents ; au-delà, un bouton ouvre
l’écran complet (`history`).

## 9.5. Premier lancement

Les trois quêtes et **Initiation** (seule collection ouverte au départ)
fournissent immédiatement du contenu. Les autres collections restent
cadenassées. L'historique vide affiche une phrase courte au ton de compagnon :
« Ton voyage commence ici. »

------

# 10. Écran Carte

Deux surfaces. L’onglet bas **Carte** ouvre toujours l’**Atlas**. La
**carte du ciel** est un écran au-dessus, pas un sixième onglet.

------

## 10.1. Intention

> **Atlas :** trouver un territoire. Le nombre de films est à droite de la ligne ; le pourcentage de vus n’y est pas.
> **Ciel :** sentir l’étendue, voyager, voir ce qui s’allume.

Même modèle (cinq états, mêmes codes). Le ciel n’ajoute pas de règle métier.

------

## 10.2. Atlas listes (onglet)

Toujours là pour TalkBack et pour chercher un nom. C’est l’onglet **Atlas**.
L’icône **étoiles** en haut à droite ouvre le ciel.

```text
┌─────────────────────────────────────────┐
│  ☰              Atlas            ?  ✦   │
└─────────────────────────────────────────┘
│  ( Courants ) ( Pays ) ( Décennies ) …  │
│  France                         48 films │
│  …                                      │
```

Le nombre de films du catalogue est affiché en petit, à droite de chaque
ligne d’Atlas (pays, courant, décennie, genre, réalisateur). Pas de
pourcentage de films vus sur ces lignes. La liste des collections ne
répète pas ce nombre : il apparaît sur la fiche, « Films · 24 ».

------

## 10.3. Carte du ciel — structure 0.2.3

S’ouvre depuis l’icône étoiles de l’Atlas. Vue par défaut : un film au centre.

```text
┌─────────────────────────────────────────┐
│  ←          Carte du ciel          ?    │
├─────────────────────────────────────────┤
│  Le film au centre, autour ce qui le lie│
│  (Autour du film) (Pays) (Courants) …   │
│                                         │
│              KUROSAWA  (cyan)           │
│                 ●                       │
│        JAPON ────★──── 1950            │  ★ = film focus (or)
│        (corail)  │    (orange)          │
│            Rashomon  ·                  │  plus loin = moins lié
│                                         │
│  Or au centre…  ● Films ● Vus ● Réals   │
│                 ● Pays ● Genres …  [ ◎ ]│
└─────────────────────────────────────────┘
│   ⌂     ▦    ((●))    ◈     ☺           │
```

Le **Canvas occupe tout** sous la barre haute. Les chips et le hint sont
**superposés**. En salle obscure le ciel reste `#07060D` ; en salle éclairée
il reprend le papier du thème pour que la liste de films (titres vus compris)
reste lisible.

------

## 10.4. Palette du ciel (hors thème Material)

| Rôle | Hex | Usage |
| --- | --- | --- |
| Nuit | `#07060D` | fond |
| Halo | `#1B1430` | dégradé radial |
| Film | `#F4EFE6` | nœud film non vu, hint |
| Film vu / centre | `#E8C68A` | focus, films validés, chip actif, FAB |
| Réalisateur | `#5EC8D8` | nœuds + labels réal |
| Pays | `#E07A5F` | nœuds pays |
| Genre | `#D489C0` | nœuds genres |
| Courant / violet | `#7A5CB8` | nœuds courants, liens, labels continent |
| Décennie | `#E0A45C` | nœuds décennies |
| Collection | `#6EA8FF` | nœuds collections |
| Lien | `#8B7AC7` | traits, alpha 0.10–0.28 selon le poids |
| Non exploré | même teinte, **cercle pointillé** | territoire pas encore commencé |
| Feuille | `#12101A` | `ModalBottomSheet` |
| FAB | `#16141F` | disque recentrer |

Légende colorée en bas à gauche (avec le hint de distance). Un libellé
homonyme n’est dessiné qu’une fois.

Ce n’est pas la palette Material des autres onglets. C’est une **salle
obscure** dédiée.

------

## 10.5. Gestes

| Geste | Effet |
| --- | --- |
| Pincer | zoom autour des doigts, jusqu’à ×14 |
| Un doigt glissé | déplacement |
| Tap un **film** (vue autour) | la carte se reconstruit autour de lui |
| Tap un **territoire** | feuille : liste + ouvrir la fiche |
| Tap le film **centre** | feuille : ouvrir la fiche film |
| FAB cible | recadre |
| Chip | remplace le dessin, recadre |
| Icône liste | Atlas scrollable |

Pas de rotation à deux doigts. Pas de double-tap zoom en 0.2.1.

------

## 10.6. Calques (chips)

Un seul allumé. Chip inactif : fond blanc 6 %, bordure 12 %, label ivoire.
Chip actif : fond or 22 %, bordure or, label or.

Changer de calque = **nouvelle constellation**, caméra qui recadre (spring),
sélection perdue. Première puce : **Autour du film**. Puis Courants, Pays,
Décennies, Genres, Réalisateurs, Collections.

Pays / réalisateurs : libellés de **continent** en petites capitales
violettes, au-dessus des grappes.

------

## 10.7. Dessin d’une étoile

| État | Forme | Couleur | Taille relative |
| --- | --- | --- | --- |
| Non exploré | anneau pointillé, pas de halo | gris `#6A6480` | plus petit |
| En cours | disque + halo | violet | |
| Exploré | disque + halo | ivoire | |
| Complété | disque + halo | or | plus grand |
| Maîtrisé | disque or + **point sombre** au centre | or | le plus grand |
| Sélectionné | + anneau or, pulse lent (~1,7 s) | | |

**Labels :**

- toujours si sélectionné, ou déjà exploré, ou calque peu peuplé (≤ 24) ;
- sinon à partir d’un zoom confortable ;
- réalisateurs : zoom plus fort (sinon 200 noms illisibles).

Police labels : serif, centrée sous le point. Groupes : sans-serif
11 sp, capitales.

Légende bas gauche : *Or au centre : film choisi. Plus c’est loin, moins
c’est lié* (vue autour) ; sur un calque territoires, les cinq états.

------

## 10.8. Feuille d’un nœud

`ModalBottomSheet` sombre, on **reste sur la carte**.

1. Nom (display, or). Sous-titre si film (réal · année).
2. Pour un territoire : état + `n %` + barre or.
3. Bouton **Ouvrir la fiche** / **Ouvrir ce territoire**.
4. Si territoire : liste des films. Tap → fiche.

------

## 10.9. Garde-fous

- Tout territoire du ciel existe dans l’Atlas.
- Cibles : le hit-test élargit le rayon quand on dézoome ; le FAB et les
  chips restent à 48 dp.
- TalkBack : le Canvas n’est pas un graphe d’accessibilité. L’Atlas + la
  feuille (liste Compose) portent le lecteur d’écran.
- La couleur n’est pas seule : pointillé / plein / point central.
- Aide dédiée (`HelpTopic.InteractiveMap`) : pinch, tap, autour du film,
  listes Atlas.

------

## 10.10. Hors 0.2.1

Pas d’affiches sur le ciel. Pas les 405 films d’un coup (12 voisins max).
Pas de mini-map. Pas de mode jour pour cet écran.

------


# 11. Écran Parcours

Regroupe ce que Léo a décrit comme « suivre les rangs, quêtes, etc. » **[imposé]**.

## 11.1. Structure

```text
┌─────────────────────────────────────────┐
│  Parcours                                │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │        EXPLORATEUR                 │  │  ← rang actuel, en Bodoni
│  │        rang 5 sur 10               │  │
│  │                                    │  │
│  │  Ce qui progresse                  │  │  ← lecture du rang (§13.4)
│  │  → ton étendue géographique        │  │
│  │                                    │  │
│  │  Ce qui stagne                     │  │
│  │  → l'approfondissement des         │  │
│  │    filmographies                   │  │
│  └────────────────────────────────────┘  │
│                                          │
│  QUÊTES EN COURS                         │
│  ┌────────────────────────────────────┐  │
│  │ ◈ Trois pays d'Amérique du Sud     │  │
│  │   ●●○                    difficile │  │
│  └────────────────────────────────────┘  │
│                                          │
│  COLLECTIONS EN COURS                    │
│  (suivies, pas à 100 %, pas cadenassées)                  │
│  Néoréalisme italien       ▰▰▰▱▱▱▱  35 %│
│  Cinéma japonais           ▰▰▱▱▱▱▱  27 %│
│                                          │
└─────────────────────────────────────────┘
```

## 11.2. Le rang ici et sur le Profil

Le rang apparaît à deux endroits, avec deux traitements différents — ce n'est pas une redite :

| Écran | Traitement |
| --- | --- |
| **Profil** | Le rang comme **identité**. Grand, statique, contemplatif. Aucune explication mécanique |
| **Parcours** | Le rang comme **progression**. Ce qui avance, ce qui stagne, où aller |

## 11.3. Difficulté des quêtes

Trois paliers décidés : **Bronze**, **Argent**, **Or**, respectivement
100, 250 et 500 XP. Le libellé et la récompense sont affichés ensemble.
Pas d'étoiles : elles évoquent une note, or Urbinema ne note aucun film.

------

# 12. Écran Profil

## 12.1. Hiérarchie **[imposé]**

```text
┌──────────────────────────────┐
│  (avatar)   PSEUDO           │   ← identité : avatar à gauche du pseudo
│                              │
│      ╭──────────────╮        │
│      │              │        │   ← emblème de rang, **cliquable**
│      │   NOVICE     │        │     → écran des 10 rangs (actuel en accent/or)
│      ╰──────────────╯        │
│      Niv. 1                  │   ← barre d'XP juste sous le rang
│      0 / 115 XP              │
│                              │
│  jusqu’à 3 badges (centrés)  │  ← choisis depuis Tous les badges
│        voir tous             │
│                              │
│  stats non cliquables        │   → listes via le tiroir
└──────────────────────────────┘
```

Ordre : **Avatar + pseudo → Rang → niveau/XP → Badges → statistiques**.

Cliquer le rang ouvre l'échelle 1→10, flèches entre les rangs, rang actuel
en `accent`, et **sous le nom de ce rang uniquement** la description détaillée
(`rankings.longDescription`, issue de `Liste_Des_Rangs.txt`). Même écran
accessible depuis le tiroir Accueil.

L'en-tête Accueil (rang / niveau / XP) **ouvre le Profil**.

## 12.2. Un écran volontairement statique

Le niveau et l'XP existent à nouveau, mais restent **secondaires** sur le
Profil : une ligne compacte **sous le rang**, jamais une seconde carte héroïque.
Leur affichage principal est l'en-tête de l'Accueil.

Le rang étant presque immobile, le Profil est **délibérément contemplatif**. C'est l'inverse de la plupart des applications gamifiées, où tout bouge en permanence. C'est assumé : la progression fréquente se lit sur *Accueil* et *Parcours*.

------

# 13. Rang — traitement visuel

Le rang est le cœur du produit (fonctionnel §9.2). Il doit être **l'élément le plus fort de toute l'application**.

## 13.1. Contraintes

- un seul rang affiché à la fois (1 à 10) sur Profil / Accueil / Parcours ;
- l'échelle complète 1→10 est un écran dédié, pas une liste concurrente du profil ;
- le rang actuel y est doré (`accent`) ; les autres restent en `onBackground` ;
- il se lit comme un **titre**, jamais comme un score ;
- aucun chiffre brut, aucune barre de progression vers le rang suivant — le rang évolue sur des années, une barre quasi immobile serait déprimante ;
- le rang ne redescend jamais (fonctionnel §9.4) : aucun cas de « perte de rang » à gérer à l'écran.

## 13.2. Représentation

**Typographie d'abord, emblème ensuite.** Le nom du rang en Bodoni Moda 44 sp est déjà une image ; un emblème trop travaillé entrerait en concurrence avec lui.

Les visuels packagés se déposent dans `assets/media/rankings/` sous le code
Room (`RANK_01.webp` … `RANK_10.webp`, aussi png/jpg/jpeg). Dès qu’un fichier
est présent, il s’affiche dans le cadre du Profil, sur Parcours et dans
l’échelle des 10 rangs ; **le nom reste sous l’image**. Sans fichier, le nom
reste seul dans le cadre. Voir `ASSETS.md`.

## 13.3. La rupture au rang 8

Le fonctionnel (§9.3) annonce un **changement de nature** au rang 8 : il ne s'agit plus d'une culture qui s'élargit mais d'un rapport différent au médium.

Traduction visuelle proposée : **inversion du registre chromatique**. Les rangs 1 à 7 vivent en `accent` (ambre chaud, la lumière). Les rangs 8 à 10 basculent en `rare` (argent froid) — et la carte de rang du Profil s'inverse, fond clair sur application sombre.

L'effet est immédiat, se lit sans explication, et ne coûte qu'un jeu de jetons.

## 13.4. Expliquer le rang sans le dévoiler

Le calcul combine trois axes pondérés (fonctionnel §9.4). C'est puissant mais **opaque** : l'utilisateur ne peut pas deviner pourquoi il a progressé, et le cœur du produit ne peut pas être une boîte noire.

La formule v0.3 se prête bien à une lecture littéraire, parce que ses trois axes sont indépendants et nommables :

> « Ce qui te fait progresser en ce moment : ton **étendue géographique**.
> Ce qui stagne : l'**approfondissement** — tu as vu beaucoup de premiers films, peu de filmographies. »

Règles absolues : aucun score chiffré, aucun pourcentage vers le rang suivant, aucun nom de variable. Des phrases.

## 13.5. Le changement de rang

C'est **le seul moment spectaculaire de l'application**, et il arrivera peut-être une fois par an. Il mérite donc un traitement complet, et l'excès est ici permis — c'est le seul endroit où il l'est.

Proposition : un **écran plein**, noir, où le nom du nouveau rang apparaît en fondu lent, sans son, sans confetti, sans bouton immédiat. Trois secondes de rien, puis le titre. Un « continuer » discret apparaît ensuite.

La retenue produit plus d'effet que l'explosion — et c'est cohérent avec un produit qui se parcourt sur des années.

------

# 14. Badges — traitement visuel

## 14.1. Contraintes

Les badges sont **nombreux** (30 en V1, potentiellement des centaines) et cumulables. L'interface doit tenir ce volume sans devenir un tableau Excel.

## 14.2. Forme

Vignette carrée à coins peu arrondis, contenant un **pictogramme linéaire** sur fond `surface`.

Un badge obtenu : pictogramme en couleur.
Un badge non obtenu : **niveaux de gris** (saturation 0), condition affichée
sous le nom. Aucun cadenas.

## 14.3. Badges non obtenus : visibles

**Décision : tous les montrer.** Les conditions sont visibles sous les badges.
Les badges obtenus sont colorés ; les autres sont en noir et blanc. Aucun
badge surprise en V1.

## 14.4. Illustrations

Pictogrammes packagés dans `assets/media/badges/{code}.jpeg` (source Flaticon,
créditée dans À propos).

## 14.5. Galerie

L'écran « Tous les badges » (tiroir + bouton Profil) découpe d’abord par
**rareté / difficulté** : Figurant (difficulté 1–2), Second rôle (3),
Tête d’affiche (4–5), puis trie par `code` dans un même palier (`001` avant
`002`). Filtre « obtenus ».
Roue en haut à droite : choisir jusqu’à 3 badges débloqués pour le Profil.

------

# 15. Collections et parcours

## 15.1. Liste groupée et cadenas

L’onglet Collections groupe les fiches sous les cinq intitulés de `track`
(Premières séances, Ciné-club, Salle obscure, Cinémathèque, Hors-champ).
Le pack 24 en compte 27. **Initiation** est toujours en tête, toujours ouverte.

Collections verrouillées : niveaux de gris + cadenas, non ouvrables, dialogue
§7.2 (Initiation : ≥ 1 Vu ; palier suivant : 2 collections commencées).
Collections suivies : titre et barre en `accent` (or). Collections
non suivies (déjà déverrouillées) : **0 %** et **0 / N**, titres de films **sans**
dorure même s’ils sont Vu. Collections **terminées** : titre + % en or, icône
check, plus dans « en cours ».

## 15.2. Présentation d'une collection

```text
┌─────────────────────────────────────────┐
│  ← Initiation                            │
│                                          │
│  Premières séances · 10 films            │
│                                          │
│  ▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱          3 / 10   │  ← seulement si suivie
│                                     30 % │
│                                          │
│  [ Suivre cette collection ]             │
│  ou, si 100 % :                          │
│  Vous avez terminé cette collection      │  ← grisé, non cliquable
│                                          │
│  Texte long d’intention.                 │
│                                          │
│  ☑ Le Roi Lion                  1994     │  ← or si collection suivie
│  ☐ Titanic                      1997     │
│                                          │
└─────────────────────────────────────────┘
```

Les paliers s’affichent en **pourcentage** (fonctionnel §8.7). La barre et le
compteur restent à 0 tant que la collection n’est pas suivie.

À 100 % d’une collection **suivie** : boîte « Collection terminée / Félicitations,
vous avez terminé la collection « … ». » Puis l’écran reste sur la fiche
terminée.

Au déblocage d’un badge : même type de boîte, FR/EN
« Félicitations ! Vous avez débloqué le badge « … » ! ». Si plusieurs badges
tombent d’un coup, ils s’enchaînent. Si une collection se termine en même
temps, la collection s’affiche d’abord.

------

# 16. Fiche film

## 16.1. Contenu

La fiche film affiche :

- affiche locale dès la V1 — la V0.1 peut utiliser un placeholder textuel ;
- titre original en grand et en gras ;
- titre français plus petit juste dessous ;
- année, durée, réalisateurs ;
- pays principal puis coproductions ;
- genres, caractéristiques et collections ;
- synopsis ;
- état vu/non vu et date de visionnage.

Le texte éditorial « pourquoi ce film est dans Urbinema » reste une amélioration
possible, mais ne bloque pas la première fiche.

## 16.3. Structure

```text
┌─────────────────────────────────────────┐
│  ←                                       │
│                                          │
│           [ AFFICHE LOCALE ]             │
│                                          │
│  七人の侍                                 │  ← titre original, grand
│  Les Sept Samouraïs                      │  ← titre français, plus petit
│  Akira Kurosawa · 1954                   │
│  Japon · 3 h 27                          │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │      ✓  Marquer comme vu           │  │  ← action unique, franche
│  └────────────────────────────────────┘  │
│                                          │
│  SYNOPSIS                                │
│  Description importée du catalogue.      │
│                                          │
│  TERRITOIRES                             │
│  ( France )  ( 1950s )  ( Thriller )     │  ← puces cliquables
│                                          │
│  DANS CE COURANT                         │  ← la piste suivante (§2.3)
│  Trois autres films proposés             │
│                                          │
└─────────────────────────────────────────┘
```

Les puces de territoire sont **cliquables** : chacune mène à sa fiche. C'est ce qui transforme le catalogue en réseau parcourable, sans aucune carte.

« Marquer comme vu » enregistre **la date du jour du téléphone** (fuseau
appareil). Pas de calendrier en 0.1.7. Les dates futures sont interdites
(comparaison dans le même fuseau). La confirmation valide le film et
déclenche atomiquement rang, badges, quêtes, XP, collections et historique.

------

# 17. Réglages **[imposé]**

Accessibles par la **roue en haut à droite du Profil**.

| Réglage | Options | Défaut |
| --- | --- | --- |
| **Avatar** | 10 visuels packagés, carrousel coulissant | demandé à l'onboarding, changeable ensuite |
| **Pseudo** | texte libre | demandé à l'onboarding |
| **Âge** | entier 8–120 | demandé à l'onboarding, modifiable ensuite |
| **Thème** | Sombre · Clair · Système | **Sombre** |
| **Langue** | Système · Français · English | **Système** (switch réel, immédiat) |
| Grain argentique | activé · désactivé | **désactivé** — overlay persisté, voir §3.4 |
| Titres | VO principale + français secondaire | fixé |
| Aide | écran d’aide (collections, carte, courants, rang, badges, XP) | aussi `?` sur Parcours |
| Comprendre les rangs | inclus dans Aide | — |
| Données | réinitialisation de la progression | — |
| À propos | version, auteur (Léo Barroux), crédits TMDB / Flaticon / Avatar Maker | — |

Le changement de thème et de langue s'applique **immédiatement**, sans redémarrage.

L'explication des rangs est volontairement rangée ici derrière une entrée
« Comprendre les rangs » et un bouton `?` près du rang. Elle décrit simplement
volume pondéré, étendue et approfondissement, sans exposer la formule brute.

------

# 18. Inventaire d'écrans

| Écran | Accès | Priorité |
| --- | --- | --- |
| Onboarding | premier lancement | V1 |
| Accueil | barre basse 1 | V1 |
| Collections | barre basse 2 | V1 |
| Carte (ciel) | barre basse 3 | **0.2.1** |
| Atlas listes | onglet Atlas | V1 / TalkBack |
| Parcours | barre basse 4 | V1 |
| Profil | barre basse 5 | V1 |
| Réglages | roue, depuis Profil | V1 |
| Aide | Réglages « Ouvrir l’aide » et `?` Parcours | V1 |
| Tous les rangs | clic sur le rang du Profil, ou tiroir Accueil | V1 |
| Statistiques détaillées | tiroir Accueil, ou stats du Profil | V1 |
| Tiroir latéral | burger, depuis Accueil | V1 |
| Fiche film | depuis partout | V1 |
| Fiche collection | depuis Collections, Carte, Accueil, tiroir | V1 |
| Fiche pays / décennie / courant / genre | depuis Carte | V1 |
| Tous les badges | tiroir | V1 |
| Toutes les collections | tiroir | V1 |
| Statistiques détaillées | tiroir | V1 |
| Recherche | tiroir | V1 |
| Historique | section scrollable de l'Accueil | V1 |
| Changement de rang | événement | V1 |

------

# 19. Mouvement et animation

## 19.1. Un vocabulaire emprunté au montage

Plutôt que les ressorts et rebonds habituels, Urbinema emprunte son vocabulaire de transition au **montage cinématographique** :

| Nom | Usage | Durée |
| --- | --- | --- |
| **Coupe** | navigation entre onglets de la barre basse | instantané |
| **Fondu** | apparition de contenu, chargement | 200 ms |
| **Spring caméra** | recadrage ciel (changement de calque, tap, FAB) | ~400 ms, damping 0.86 |
| **Pulse** | étoile sélectionnée | 1,7 s aller-retour |
| **Fondu au noir** | changement de rang | 3 s |

Le pinch / pan du ciel suit le doigt **sans** interpolation (caméra live).
Le spring ne concerne que les recadrages déclenchés par l’UI. Exception
volontaire au « jamais de rebond » : un ressort *sous-amorti très léger*
(damping 0.86), pas un bounce Material.

## 19.2. Retenue

Le fonctionnel impose une gamification mesurée. Concrètement :

- **jamais de confetti**, ni de son, ni de vibration festive ;
- un badge obtenu se signale par une **bannière discrète** en bas d'écran, qui disparaît seule ;
- **100 % collection** : une boîte de dialogue de félicitations, pas une animation ;
- une exception plus solennelle : le changement de rang (§13.5).

## 19.3. Respect des préférences système

Si l'utilisateur a réduit les animations dans les réglages Android, **toutes** les transitions deviennent instantanées, y compris le changement de rang.

------

# 20. Accessibilité

Non négociable, et peu coûteux si c'est prévu dès le départ :

- **contraste** minimum 4,5:1 sur le texte, 3:1 sur les éléments graphiques porteurs de sens. Les palettes du §4 le respectent ;
- **la couleur ne porte jamais seule une information** — les cinq états combinent couleur, trait, opacité et signe (§7.3) ;
- **cibles tactiles** de 48 dp minimum, y compris les nœuds de la carte ;
- **description pour lecteur d'écran** sur chaque icône, chaque nœud, chaque badge ;
- **la carte du ciel a une alternative en liste** (Atlas, §10.9) — un Canvas n'est pas explorable au lecteur d'écran ;
- **taille de police système respectée** : tout doit survivre à un agrandissement de 200 %.

------

# 21. Implémentation

## 21.1. Attentes générales de code **[imposé]**

Ces exigences valent pour tout le projet, pas seulement pour l'interface. Elles sont rappelées ici parce que le thème et les traductions en sont l'application la plus visible.

- **code propre, moderne, découpé** — responsabilités claires, fonctions courtes, pas de Composable de 400 lignes ;
- **commenté au niveau des méthodes** : chaque fonction publique porte une KDoc qui explique *ce qu'elle fait et pourquoi*, pas qui paraphrase son corps ;
- **patrons de conception** appliqués là où ils servent, jamais pour la forme ;
- **bonnes pratiques Kotlin et Compose** : état remonté, Composables sans effet de bord, aperçus (`@Preview`) sur les composants réutilisables, aucune logique métier dans l'interface ;
- **rien en dur** : ni couleur, ni dimension, ni chaîne de caractères dans un Composable.

## 21.2. Un fichier de configuration par thème **[imposé]**

```text
ui/theme/
├── UrbinemaTheme.kt        // point d'entrée, choisit le schéma
├── ColorTokens.kt          // définition des jetons sémantiques
├── ThemeSalleObscure.kt    // ← un fichier : le thème sombre
├── ThemeSalleEclairee.kt   // ← un fichier : le thème clair
├── Typography.kt
├── Shapes.kt
└── Dimens.kt
```

Chaque fichier de thème ne contient **que** des valeurs : aucune logique. Ajouter un troisième thème doit se réduire à créer un fichier et l'enregistrer.

Le reste de l'application ne connaît que les **jetons sémantiques** (`accent`, `surfaceElevated`), jamais les valeurs. Une couleur écrite en dur dans un écran est un défaut.

**Exception 0.2.1 :** la carte du ciel (`InteractiveMapScreen`) a sa propre
palette nuit (`SkyNight`, `SkyGold`, …). Elle ne suit **pas** le thème
salle éclairée : c’est une salle obscure dédiée, documentée au §10.4.

## 21.3. Un fichier par langue **[imposé]**

Internationalisation en place **dès le premier écran**, selon le mécanisme standard d'Android :

```text
res/
├── values/strings.xml        // français — langue par défaut
└── values-en/strings.xml     // anglais
```

Conséquences à tenir dès le début, faute de quoi la reprise coûte cher :

- **aucune chaîne de caractères en dur** dans un Composable ;
- pluriels gérés par `plurals`, jamais par des conditions dans le code ;
- **aucune phrase construite par concaténation** — les langues n'ont pas le même ordre de mots. On utilise des paramètres de formatage ;
- dates et nombres formatés selon la locale ;
- prévoir que les textes allemands ou anglais sont 30 % plus longs : pas de largeur figée sur un libellé.

Les **contenus éditoriaux** (descriptions de films, de courants) ne sont pas des ressources : ils vivent en base. Leur traduction éventuelle est un sujet de modèle de données, pas d'interface — et n'est pas un sujet V1.

## 21.4. Contraintes techniques d'affichage

Rappels du cahier technique qui contraignent le design :

- **pas d'images distantes en V1**, pas de TMDb : affiches et illustrations
  viennent des assets locaux ;
- la V0.1 peut rester textuelle ; la V1 active les images locales ;
- catalogue de N films, N croissant : les listes deviendront longues, prévoir filtres et recherche partout ;
- portrait d'abord, paysage ensuite : ne pas concevoir de maquette qui ne survit qu'en portrait.

------

# 22. Questions ouvertes

La direction v0.2 est validée afin de passer au prototype. Les choix suivants
seront jugés **sur écran**, pas davantage théorisés avant de coder :

- taille réelle de l'en-tête fixe rang / niveau / XP sur petits téléphones ;
- équilibre du premier tiers entre en-tête et trois quêtes ;
- nombre de collections circulaires visibles avant défilement ;
- traitement des rangs non atteints sur le Profil ;
- inversion chromatique au rang 8 ;
- **carte du ciel 0.2.1** : densité des labels, hit-test, lisibilité
  Réalisateurs — calibrage après le test de Léo.

Le grain 0.1.10, le cadenas Initiation **et** le chaînage entre groupes sont
**réglés**. La première carte du ciel est **livrée** (décision 68) ; son
réglage fin attend le retour d’usage.
