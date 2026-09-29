# Cahier des charges fonctionnel

### Urbinema

------

## Spécification fonctionnelle du produit

**Version :** 0.14
**Statut :** Cadrage fonctionnel aligné sur **0.3.0** (catalogue v3, pack 29, 1542 films, 28 collections, parcours 1)
**Périmètre :** Fonctionnel
**Technologie :** Voir `CahierDesCharges_Technique.md` (hors détail d’implémentation ici)
**Décisions actées :** `DECISIONS_ACTEES.txt` — en cas de conflit, les décisions actées priment, puis le code
**Feuille de route :** `ROADMAP_V2_V3.md`

**0.3 — catalogue :** Urbinema n’est pas un journal de films vus. Catalogue fermé V1, de taille N croissante. Pas d’import Letterboxd. **Pas de TMDb dans l’app** (tout est local). Un script hors-app (`batchPosters/`) peut télécharger des affiches TMDB pour les **embarquer** ensuite. Voir §5.0 et `ASSETS.md`.

**0.4 — identité cinéphile :** le **rang** est le cœur du produit (10 rangs, évolution lente, état d’esprit et non volume). Les **badges** en sont clairement distingués (nombreux, cumulables, conditionnels). Voir §9.

**0.5 — modèle initial et calcul du rang :** première version du poids et des 50 caractéristiques éditoriales. La cardinalité « un mouvement par film » de cette version est remplacée en 0.7 par une relation N–N.

**0.6 — historique, remplacé par 0.7 :** retrait temporaire de l'XP et des niveaux. Cette décision n'est plus applicable.

**0.8 — livrable 0.1.6 :** V1 jouable (catalogue démo, Atlas listes, quêtes
hebdo). Le découpage a depuis bougé : avatars, badges, affiches packagées
et catalogue élargi sont **V1** ; la **carte interactive Canvas** est la **V2**.
Voir `ROADMAP_V2_V3.md`.

**0.9 — livrable 0.1.7 :** collection **Initiation** (10 classiques publics),
cadenas Initiation, cinq groupes de difficulté, progression **uniquement si
suivie**, 100 %, historique, onboarding, grain, Aide. Catalogue pack v8
à l’époque.

**0.10 — livrable 0.1.10 :** cadenas **entre groupes** (2 collections commencées
= 2 films vus chacune, suivi non exigé pour *rester* ouvert) + **cliquet**
(un groupe ouvert ne se recadenasse plus). Profil : 3 badges max, choix depuis
Tous les badges, non obtenus en N&B, ordre difficulté puis code. XP : 40 par
film unique **et** quêtes 100/250/500. Grain allégé (~3,2 %). À propos :
Léo Barroux, Flaticon, Avatar Maker, TMDB. Room v6, pack JSON **v9**,
app `0.1.10` / `versionCode` 18.

**0.11 — livrable 0.1.11 :** avatars packagés à l’onboarding et dans Réglages
(10 visuels `AVATAR_01`…`10`, carrousel coulissant). Profil : avatar à
gauche du pseudo, au-dessus du rang. Cadenas : Initiation reste obligatoire
après reset (le cliquet ne contourne plus la porte). Dialogues de cadenas
résolus dans la locale Compose. Comment calculer H/A/R/C :
`FORMULE_MATHEMATIQUE.txt` §1.bis. Room v7, app `0.1.11` / `versionCode` 19.

**0.12 — close V1 (prêt 0.1.12) :** pack JSON **v11**, ~405 films, 42 pays,
50 quêtes types. Avatars packagés, badges, affiches par code : **V1**.
Carte Canvas : **V2**. App encore `0.1.11` jusqu’à la release APK.

**0.13 — livrable 0.2.1 :** carte du ciel = icône étoiles (onglet **Atlas**
= listes). Vue ciel : constellation **autour d’un film**. XP film =
**10** (essai). Voir §7.2 et §11.

**0.14 — livrable 0.2.3 :** ciel **coloré par type** (films blancs / vus
dorés, pays, réal, genres, courants, décennies, collections) + légende.
Pas de doublon de libellé (réal vs collection homonyme). Pop-up badge
une seule fois (DataStore), chaînes FR/EN. Historique Accueil limité à
50 + écran complet. Tiroir : un peu plus d’air sous le logo.

> **Vision du produit**
>
> *Une application qui transforme l'histoire et la diversité du cinéma en un immense terrain d'exploration, où le spectateur développe progressivement sa culture, ses connaissances et sa capacité d'analyse.*

------

# Sommaire

1. Vision et objectifs
2. Positionnement du produit
3. Public cible
4. Principes directeurs
5. Architecture fonctionnelle du contenu
6. Système utilisateur
7. Système de progression
8. Système de collections
9. **Identité cinéphile : rangs et badges**
10. Système de quêtes
11. Carte cinématographique
12. Statistiques et suivi de progression
13. Recherche et navigation
14. Onboarding et première expérience
15. Administration et gestion éditoriale
16. Règles éditoriales
17. Règles de cohérence et anti-abus
18. UX et principes d'interface
19. Priorisation fonctionnelle
20. Fonctionnalités futures
21. Boucles d'utilisation
22. Vision à long terme
23. Glossaire fonctionnel
24. Questions et décisions à prendre

Documents liés :

- `SPECIFICATION_DEVELOPPEUR.md` — ce que le code 0.2.3 fait vraiment
- `CahierDesCharges_Technique.md` — stack et architecture
- `CahierDesCharges_IHM.md` — interface, affichage, charte graphique
- `DECISIONS_ACTEES.txt` — décisions qui priment en cas de conflit
- `ROADMAP_V2_V3.md` — V1 close, V2 Canvas
- `ASSETS.md` — dossiers et branchement des médias
- `FAQ_CAHIER_FONCTIONNEL.txt` — questions encore ouvertes
- `Listes_Fonctionnelles/` — rangs, badges, caractéristiques cinématographiques et genres
- `FORMULE_MATHEMATIQUE.txt` — formulation du calcul du rang (v0.3)
- `FORMULE_NIVEAUX_XP.txt` — formulation des niveaux et de la courbe d'XP
- `RETOUR_FORMULE_RANG.txt` — analyse et justification de cette formule

Tous ces documents vivent dans le répertoire `specs/`.

------

# 1. Vision et objectifs

## 1.1. Contexte

Les plateformes cinématographiques existantes permettent principalement :

- de référencer des films ;
- de rechercher des œuvres ;
- de consulter des informations ;
- de noter des films ;
- de rédiger des critiques ;
- de suivre des utilisateurs ;
- de recevoir des recommandations.

Ces plateformes répondent principalement à une logique de **catalogue, de notation ou de communauté**.

Urbinema propose une approche différente.

L'application considère le cinéma comme un **territoire culturel à explorer**.

L'utilisateur ne cherche pas uniquement à savoir :

> « Quels films ai-je vus ? »

Il cherche également à savoir :

> « Quelles parties du cinéma ai-je explorées ? »

et :

> « Qu'est-ce que je pourrais découvrir ensuite ? »

------

## 1.2. Objectif principal

L'objectif d'Urbinema est d'encourager les utilisateurs à :

- découvrir davantage de films ;
- diversifier leurs cinématographies ;
- explorer différentes périodes ;
- découvrir des mouvements cinématographiques ;
- sortir progressivement de leur zone de confort ;
- construire une culture cinématographique plus large ;
- visualiser leur progression.

------

## 1.3. Objectifs secondaires

Urbinema doit également :

- donner une représentation ludique de la culture cinématographique ;
- créer une sensation de progression durable ;
- donner des objectifs concrets aux utilisateurs ;
- permettre de visualiser les zones encore inexplorées ;
- valoriser la découverte de cinéma moins connu ;
- créer une expérience de collection ;
- transformer la curiosité en parcours de découverte.

------

## 1.4. Ce que le produit doit provoquer

À terme, un utilisateur doit pouvoir ouvrir Urbinema et se dire :

> « Je n'ai jamais vraiment exploré le cinéma japonais des années 1940. »

Puis :

> « Il y a une collection de 20 films essentiels. »

Puis :

> « J'en ai vu 4. »

Puis :

> « Encore 6 et je débloque quelque chose. »

Puis :

> « Tiens, ce mouvement est relié à celui que je viens de découvrir. »

La boucle recherchée est donc celle de la **curiosité → découverte → progression → nouvelle curiosité**.

------

# 2. Positionnement du produit

## 2.1. Urbinema est

Urbinema est :

- une carte interactive du cinéma ;
- un système de progression culturelle ;
- un outil de découverte ;
- un système de collections ;
- un système de badges ;
- un système de quêtes ;
- un profil de progression cinéphile.

------

## 2.2. Urbinema n'est pas

Urbinema n'a pas vocation à devenir :

- un clone de Letterboxd ;
- un clone de SensCritique ;
- un site de critiques ;
- une plateforme de notation ;
- un réseau social cinéphile classique ;
- un classement des « meilleurs cinéphiles » ;
- un cours universitaire de cinéma.

------

## 2.3. Absence de notation

La première version ne nécessite pas de système de notation des films.

L'utilisateur n'a pas besoin de renseigner :

- une note ;
- un avis ;
- une critique ;
- un commentaire.

L'information principale associée à l'utilisateur est :

> **Film vu / film non vu**

Cette distinction permet de conserver une identité propre face aux plateformes existantes.

------

# 3. Public cible

## 3.1. Public principal

Urbinema cible notamment :

- les cinéphiles ;
- les spectateurs curieux ;
- les personnes souhaitant développer leur culture cinématographique ;
- les utilisateurs appréciant les systèmes de progression ;
- les personnes souhaitant diversifier leurs goûts ;
- les amateurs de quêtes et de collections.

------

## 3.2. Profils d'utilisateurs

### Spectateur curieux

Possède une culture limitée et souhaite découvrir les grands classiques.

### Cinéphile intermédiaire

A déjà vu de nombreux films mais souhaite structurer et élargir ses connaissances.

### Cinéphile confirmé

Connaît les grands classiques et souhaite explorer des œuvres moins connues.

### Cinéphile avancé

Cherche des cinématographies, périodes et mouvements plus spécialisés.

------

# 4. Principes directeurs

## 4.1. Explorer sans obligation

Urbinema doit **encourager** l'exploration sans imposer un parcours unique.

L'utilisateur doit pouvoir choisir librement :

- un pays ;
- une époque ;
- une décennie ;
- un mouvement ;
- un genre ;
- une collection ;
- une quête.

------

## 4.2. La diversité plutôt que le volume

Le nombre de films vus ne doit pas être l'unique indicateur de progression.

Le système doit valoriser :

- la diversité géographique ;
- la diversité temporelle ;
- la diversité des mouvements ;
- la diversité des genres ;
- la découverte d'œuvres moins connues.

------

## 4.3. Le cinéma n'est pas une compétition

Les rangs existent pour matérialiser une progression personnelle.

Ils ne doivent pas nécessairement servir à établir un classement entre utilisateurs.

Le produit doit favoriser :

> **la comparaison avec soi-même plutôt qu'avec les autres.**

------

## 4.4. Le contenu est la récompense

Les mécanismes de gamification doivent servir la découverte.

Le produit ne doit pas devenir une mécanique de récompenses artificielles où :

> récompense → badge → récompense → badge

devient l'objectif principal.

L'objectif reste :

> **découvrir du cinéma.**

------

## 4.5. Respect de la subjectivité

Urbinema ne doit pas chercher à déterminer si l'utilisateur :

- a « bien compris » un film ;
- possède la « bonne » interprétation ;
- a aimé un film ;
- a eu une mauvaise réaction à une œuvre.

L'application peut transmettre des connaissances.

Elle ne doit pas imposer une opinion.

------

# 5. Architecture fonctionnelle du contenu

Le contenu constitue le socle d'Urbinema.

Il doit être organisé selon plusieurs dimensions complémentaires.

------

## 5.0. Nature du catalogue (V1)

Urbinema **n'est pas un journal de films vus**. C'est un **parcours cinématographique guidé et gamifié**.

Un catalogue initial de quelques centaines de films éditorialisés est largement suffisant pour démarrer. Les films sont **pré-enregistrés** et constituent les briques des parcours, collections, mouvements, pays, décennies, badges, quêtes et rangs.

L'utilisateur **ne renseigne pas tout ce qu'il voit dans sa vie**. Il **valide les films que l'application lui propose** au fil de son exploration.

Les quêtes du type « voir 5 films asiatiques dans le mois » reposent sur **ces films proposés et validés**.

En V1 :

- usage d'abord **personnel** ;
- déclarations **non contrôlées** (pas de police du visionnage) ;
- **uniquement** les films du catalogue Urbinema ;
- le catalogue compte **N films**, et ce N grandit en continu : sans doute une centaine au lancement, puis 500, puis 1000, puis davantage. Horizon de travail : quelques milliers de titres. Aucune valeur ne doit être écrite en dur, ni dans le contenu ni dans les calculs — y compris des films moins connus s'ils sont importants pour un parcours — **sans** prétendre à l'exhaustivité type Letterboxd ;
- **aucune importation** d'historique (Letterboxd, SensCritique, etc.) : cela irait contre cette philosophie ;
- alimentation du catalogue **en base**, notamment via batch / script.

Hors V1 (facultatif, **peut ne jamais être développé** s'il dénature le projet) :

- demander l'ajout d'un film absent, d'abord comme simple entrée/alerte à traiter à la main, plus tard éventuellement via TMDb ou une autre API ;
- onboarding enrichi : sélection de films déjà connus, plus variés géographiquement, culturellement et historiquement (davantage d'anciens) pour identifier les zones déjà explorées et personnaliser le départ.

L'âme du projet : **proposer des parcours et faire découvrir progressivement du cinéma**, pas devenir une base personnelle exhaustive de films vus.

------

## 5.1. Film

Le film constitue l'unité fondamentale de **validation** dans le catalogue Urbinema (pas « n'importe quelle œuvre jamais vue hors app »).

### Cardinalités

| Dimension | Règle |
| --- | --- |
| Année de référence | **une seule** |
| Décennie, époque | **dérivées** de l'année |
| Caractéristiques cinématographiques | **zéro à plusieurs** (§5.7) |
| Genres | **zéro à plusieurs** (§5.6) |
| Pays | **un à plusieurs**, avec exactement un pays principal (§5.2) |
| Collections | plusieurs |
| Réalisateurs | **un à plusieurs** (§5.9) |
| Poids | **une seule valeur** — voir ci-dessous |

### Données principales

Chaque film possède au minimum :

- un identifiant technique ;
- un code éditorial stable ;
- un titre original, affiché en premier ;
- un titre français facultatif, affiché en second ;
- une année de référence ;
- une durée en minutes ;
- un synopsis ;
- un média d'affiche local facultatif en V0.1, prévu dès la V1 ;
- les quatre composantes de son poids cinéphile ;
- des propriétés calculables ou explicites nécessaires aux badges : muet, noir et blanc, expérimental, format.

Le format est stocké explicitement comme `SHORT`, `MEDIUM`, `FEATURE` ou
`EXTENDED`. Il ne doit pas être recalculé à chaque affichage depuis la durée :
les frontières éditoriales peuvent évoluer indépendamment de la valeur brute.

### Poids du film

Chaque film porte un **poids**, qui traduit ce qu'il représente dans le parcours cinéphile. Un blockbuster récent pèse peu ; une œuvre ancienne, exigeante ou issue d'une cinématographie peu représentée pèse beaucoup plus.

Ce poids alimente le calcul du rang (§9.4).

### Formats acceptés

- **longs métrages** : le format dominant du catalogue ;
- **courts métrages** : surtout pour les décennies 1880 à 1920, où le court est le format normal du cinéma ;
- **animation** : bien sûr, c'est du cinéma ;
- **documentaire** : accepté — c'est un **genre**, pas un mouvement (sauf courant documentaire identifié comme tel, par exemple l'École britannique documentaire).

------

## 5.2. Pays

Les pays constituent une dimension géographique majeure.

Exemples :

- France ;
- Allemagne ;
- Italie ;
- Japon ;
- États-Unis ;
- Corée du Sud ;

Les **libellés affichés** des pays sont sans accent (Egypte, Etats-Unis) afin
que le tri alphabétique de l’Atlas ne sépare pas « E » et « É ». Le code
ISO / éditorial reste inchangé (`EGYPT`, `USA`, etc.).
- Inde ;
- etc.

Un film peut être associé à plusieurs pays dans le cas des coproductions.
**Exactement un** de ces pays est désigné comme principal lors de l'import.

Le pays principal sert :

- à l'état « exploré » d'un pays sur l'Atlas ;
- aux quêtes qui demandent d'explorer plusieurs pays ;
- aux statistiques qui ne doivent pas compter une coproduction plusieurs fois.

Les pays secondaires restent visibles et peuvent alimenter les recherches et
les badges dont la règle accepte explicitement les coproductions.

La normalisation historique relève de l'import : URSS → Russie,
RFA/RDA → Allemagne. Hong Kong demeure une entrée distincte. La liste complète
des pays sera maintenue dans les données éditoriales, pas dans une enum du code.

------

## 5.3. Continents

Les pays sont regroupés par continent au moyen d'une relation explicite.
Un pays peut techniquement être lié à plusieurs continents afin de traiter les
cas transcontinentaux sans modifier le schéma.

Exemples :

- Europe ;
- Asie ;
- Afrique ;
- Amérique du Nord ;
- Amérique du Sud ;
- Océanie.

Les continents servent notamment aux objectifs de grande exploration géographique.

Le rattachement exact des cas ambigus (Russie, Turquie, Israël, Égypte) est une
décision éditoriale du pack d'import. Les badges utilisent ces relations et non
une liste codée en dur.

------

## 5.4. Année et décennie

Chaque film porte **une année de référence unique**.

Le choix de cette année (sortie nationale, sortie internationale, présentation en festival, œuvre restaurée, date contestée) est un **problème d'import**, pas un problème d'application : il se tranche au moment où le film entre en base. Une fois stockée, l'année ne bouge plus.

L'année permet de déterminer :

- la décennie ;
- l'époque ;
- les statistiques temporelles ;
- les collections historiques.

Exemple :

> 1947 → années 1940.

------

## 5.5. Époques

Classification temporelle plus large que la décennie.

Exemple :

- cinéma des origines ;
- cinéma muet ;
- cinéma classique ;
- cinéma moderne ;
- cinéma contemporain.

**Les époques seront définies avec des bornes de dates précises**, dans un fichier dédié de `Listes_Fonctionnelles/`. Ce fichier est en cours de rédaction ; il sera intégré ici une fois validé.

------

## 5.6. Genres

Un film peut avoir **plusieurs genres**.

Exemples :

- drame ;
- comédie ;
- horreur ;
- science-fiction ;
- western ;
- thriller ;
- documentaire ;
- animation ;
- etc.

Les genres servent notamment aux statistiques, aux quêtes et aux badges.

La liste V1 complète est définie dans
`Listes_Fonctionnelles/Liste_Des_Genres.txt`. Elle contient 34 genres et reste
extensible par les données, sans migration du schéma.

### Ne pas confondre genre et mouvement

C'est une distinction **structurante** du modèle :

| | Genre | Mouvement |
| --- | --- | --- |
| Exemples | aventure, thriller, comédie, documentaire, animation | Nouvelle Vague française, Nouvel Hollywood, Néoréalisme italien |
| Nombre par film | zéro à plusieurs | zéro à plusieurs |
| Nature | catégorie de récit ou de forme | courant historique, esthétique ou national |

Un documentaire est un **genre**. *Cinéma-vérité* est un **mouvement**. Les deux ne vivent pas dans la même table et ne se mélangent jamais.

------

## 5.7. Caractéristiques cinématographiques

Urbinema intègre une taxonomie éditoriale unifiée nommée
**caractéristique cinématographique**.

Une caractéristique peut être typée `MOVEMENT`, `CURRENT`, `STYLE`, `PERIOD`,
`SCHOOL` ou `WAVE`. Cette liste de types est extensible : elle décrit la nature
éditoriale de l'entrée sans modifier la relation avec les films.

Le type `PERIOD` désigne une période éditoriale comme « Âge d'or hollywoodien ».
Il ne remplace pas l'**époque** chronologique dérivée de l'année (§5.5). Les
deux peuvent coexister et alimenter deux axes différents du rang ; ce
chevauchement est assumé.

La V1 importe les **50 premières** entrées de la liste éditoriale (jusqu'à
*Slow Cinema* inclus). Les suivantes constituent la réserve V2+.

Liste complète et à jour : `Listes_Fonctionnelles/Liste_Des_Courants_Cinematographiques.txt`

### Mouvements traités en V1

| # | Mouvement | # | Mouvement |
| --- | --- | --- | --- |
| 1 | Hollywood classique | 26 | Nouvelle Vague sud-coréenne |
| 2 | Montage soviétique | 27 | Cinquième génération chinoise |
| 3 | Néoréalisme italien | 28 | Réalisme poétique français |
| 4 | Nouvelle Vague française | 29 | Cinéma expérimental américain / New American Cinema |
| 5 | Expressionnisme allemand | 30 | Troisième Cinéma |
| 6 | Nouvel Hollywood | 31 | Nouvelle vague iranienne |
| 7 | Surréalisme cinématographique | 32 | Sixième génération chinoise |
| 8 | Film noir | 33 | École britannique documentaire |
| 9 | Impressionnisme français | 34 | Free Cinema britannique |
| 10 | Nouvelle Vague japonaise (Nūberu Bāgu) | 35 | Nouvelle Vague britannique / Kitchen Sink |
| 11 | Nouveau cinéma allemand | 36 | Commedia all'italiana |
| 12 | Âge d'or du cinéma japonais | 37 | Nouvelle génération iranienne |
| 13 | Nouvelle Vague taïwanaise | 38 | Cinéma québécois moderne |
| 14 | Cinéma Novo brésilien | 39 | Australian New Wave |
| 15 | Cinéma soviétique / russe moderne | 40 | Cinéma afro-américain indépendant / L.A. Rebellion |
| 16 | Cinéma classique italien | 41 | Dogme 95 |
| 17 | Nouvelle Vague hongkongaise | 42 | New Queer Cinema |
| 18 | Cinéma politique italien | 43 | Nouveau cinéma roumain / Romanian New Wave |
| 19 | Cinéma parallèle indien (Parallel Cinema) | 44 | Nouvelle Vague hongroise |
| 20 | Cinéma indépendant américain | 45 | Black Wave yougoslave |
| 21 | École polonaise du cinéma | 46 | Cinéma politique latino-américain |
| 22 | Cinéma-vérité | 47 | Nouvelle Vague philippine |
| 23 | Nouvelle Vague tchécoslovaque | 48 | Cinéma du look français |
| 24 | Cinéma direct | 49 | New French Extremity |
| 25 | Spaghetti Western | 50 | Slow Cinema |

### Cardinalité

Un film peut posséder **zéro, une ou plusieurs** caractéristiques. Il n'existe
donc aucune colonne `movement` dans le film et aucune valeur artificielle
« Hors mouvement ».

Exemple : un même film peut être rattaché à *Nouvelle Vague française*,
*Surréalisme* et *Cinéma direct* si l'éditorial le justifie.

### Vocabulaire

Le nom technique générique est `cinemaCharacteristic`. L'interface peut
afficher le type exact lorsque cela aide à comprendre, ou employer
« courant », « collection » ou « territoire » selon le contexte.

### Précision de nature

Plusieurs entrées ne sont pas des mouvements au sens académique strict
(*Hollywood classique*, *Film noir*, *Spaghetti Western*, *Cinéma indépendant
américain*). Le champ `type` rend désormais cette nuance explicite sans
fragmenter le modèle.

------

## 5.8. Collections

Les collections sont des regroupements éditoriaux de films.

Exemples :

- 20 films essentiels de l'Expressionnisme allemand ;
- 20 films majeurs de la Nouvelle Vague ;
- 20 classiques du cinéma japonais ;
- 20 films majeurs des années 1940.

Une collection possède :

- un nom ;
- une description ;
- un code stable ;
- un numéro d'ordre éditorial distinct de son identifiant technique ;
- une image locale facultative ;
- une liste ordonnée de films (aujourd’hui : année de sortie croissante ;
  **V3** : ordre éditorial du plus accessible au plus complexe) ;
- des objectifs de progression ;
- éventuellement un badge associé.

Une collection peut être libre ou associée à une ou plusieurs cibles :

- caractéristique cinématographique ;
- pays ;
- continent ;
- époque.

Ces associations sont indépendantes : aucune relation polymorphe fragile n'est
stockée sous la forme `type + id`.

La cible éditoriale reste **20 collections**. Le livrable 0.1.10 en embarque
**15**, dont **Initiation** (10 classiques, tête de liste). D'autres seront
ajoutées dans l'ordre éditorial.

Le numéro d'ordre et le **groupe de difficulté** (`track`) structurent la
liste. **Cadenas 0.1.10 :**

1. **Initiation** toujours ouverte. Les autres collections du catalogue
   restent verrouillées tant qu’au moins **un film d’Initiation** n’est pas Vu
   (le suivi n’est plus exigé pour *garder* l’ouverture).
2. **Entre groupes** : un palier plus exigeant s’ouvre quand le palier
   précédent a assez de collections **commencées** (2 films vus dans la
   collection, suivie ou non ; s’il n’y en a qu’une, celle-là suffit).
3. **Cliquet** : une fois un palier ouvert, il **reste** ouvert même si on
   unfollow les collections qui l’ont débloqué (`users.unlockedTrackOrdinal`).

Une collection complétée ne donne pas automatiquement un badge en V1. Cette
récompense systématique est conservée comme piste V2+. La complétion 100 %
a en revanche un traitement d'interface dédié (§8.6).

------

## 5.9. Réalisateurs

Les réalisateurs constituent une entité éditoriale à part entière.

Un réalisateur possède notamment un identifiant, un code stable, un prénom,
un nom et une photographie locale facultative.

Un film peut avoir plusieurs réalisateurs et un réalisateur plusieurs films.
Les co-réalisations sont donc prises en charge sans traitement spécial.

------

## 5.10. Médias locaux

Toute entité affichable peut référencer un média local : films, réalisateurs,
badges, collections, caractéristiques, pays, continents, genres, époques,
rangs et profils.

- affiche de film ;
- portrait de réalisateur ;
- illustration de badge ;
- couverture de collection ou de caractéristique ;
- avatar proposé par l'application.

La V0.1 de développement peut fonctionner en texte seul. La V1 prévoit les
images locales et ne dépend d'aucune URL distante. TMDB n’est pas appelé
par l’app : un script hors-app (`batchPosters/`) peut préparer des affiches
à **embarquer**. Crédit TMDB dans À propos.

------

# 6. Système utilisateur

## 6.1. Profil local (pas de compte)

Pas d'inscription, pas d'authentification.

Un seul profil sur l'appareil en V1. Le profil peut contenir :

- pseudo obligatoire ;
- adresse e-mail facultative — donnée de profil uniquement, jamais utilisée
  pour s'authentifier en V1 ;
- prénom et nom facultatifs ;
- date de naissance facultative ;
- pays facultatif ;
- avatar choisi dans une galerie d'images fournies par l'application ;
- rang courant ;
- niveau courant et XP cumulée.

L'âge n'est pas stocké directement : il deviendrait faux chaque année. Une date
de naissance facultative permet de le calculer si l'information devient utile.

Voir `DECISIONS_ACTEES.txt`.

------

## 6.2. Profil

Le profil s'organise autour de trois éléments, dans cet ordre : **pseudo**, puis **rang**, puis **badges** (voir §9 et `CahierDesCharges_IHM.md`).

Il affiche notamment :

- pseudo ;
- rang ;
- niveau et progression XP ;
- badges ;
- nombre de films vus ;
- pays explorés ;
- mouvements explorés ;
- décennies explorées ;
- collections complétées.

------

## 6.3. Film vu (validé)

L'utilisateur peut marquer un **film du catalogue** comme :

> **Vu** (validé)

Cette action déclenche les mécanismes de progression associés.

Cela ne signifie pas « j'ajoute n'importe quel titre de ma vie réelle ». En V1, seuls les titres proposés par Urbinema sont validables.

En 0.1.7, marquer Vu enregistre **la date du jour du téléphone** (`LocalDate`
dans le fuseau de l'appareil, pas UTC). Il n'y a pas encore de calendrier
pour choisir une autre date. Cette date est stockée dans la relation
utilisateur–film et sert aux quêtes temporelles. Un `watchedOn` ne peut pas
être dans le futur **selon ce même fuseau**. L'édition a posteriori d'une date
déjà enregistrée reste hors V1.

------

## 6.4. Film non vu

Les films non vus restent visibles afin de permettre l'exploration et la planification.

Il n'existe **aucune watchlist utilisateur en V1**. Les seules listes à
parcourir sont celles proposées par Urbinema : collections, caractéristiques,
pays, réalisateurs et quêtes.

------

## 6.5. Annulation

L'utilisateur doit pouvoir retirer un film de sa liste des films vus.

Le retrait déclenche un recalcul complet de la progression, sans jamais faire redescendre le rang affiché (§17.3).

------

## 6.6. Historique

Une trace des actions importantes pourra être conservée :

- film ajouté ;
- badge débloqué ;
- collection complétée ;
- quête réalisée ;
- gain d'XP et passage de niveau ;
- changement de rang — événement rare, donc marquant.

L'écran Accueil affiche ce flux avec le **titre français (ou original) du film**,
jamais le code éditorial (`LE_ROI_LION_1994`). Le libellé est résolu après
chargement du catalogue ; un code n'est un filet de sécurité que si le film
est introuvable.

L'historique détaillé pourra être enrichi ultérieurement.

------

# 7. Système de progression

## 7.1. Les cinq piliers de la V1

La progression repose sur cinq éléments complémentaires :

| Élément | Rythme | Rôle |
| --- | --- | --- |
| **Rang** | des années | identité cinéphile — cœur du produit (§9) |
| **Niveau / XP** | quotidien à mensuel | progression ludique régulière |
| **Badges** | régulier | jalons collectionnables (§9.5) |
| **Quêtes** | hebdomadaire | objectifs du moment (§10) |
| **Atlas / carte** | continu | représentation du territoire parcouru (§11) |

Le rang et le niveau sont **strictement indépendants**. Un immense cinéphile
qui installe Urbinema commence niveau 1 comme tout le monde, même si son parcours
le conduit rapidement à un rang élevé.

------

## 7.2. XP

Deux sources, à calibrer après usage :

| Source | XP |
| --- | ---: |
| **Film vu** (une fois, et seulement s’il est dans une collection suivie à cet instant) | **25** |
| **Quête Bronze** | 100 |
| **Quête Argent** | 250 |
| **Quête Or** | 500 |

Les quêtes restent la grosse source d’assiduité. Un film hors collection suivie ne donne pas d’XP. 25 XP, seulement au moment où on le marque Vu, évite de noyer le niveau. Les films déjà vus ne sont pas recalculés. Badges et collections ne donnent **pas** d’XP.

Pas de colonne « quête possible » ni de compteur de fréquence en 0.3.0 : le tirage de la semaine filtre déjà les quêtes devenues impossibles, une fois, sur le catalogue. Refaire ce contrôle à chaque film vu ralentirait l’app. L’idée (flag + moins de chances pour les quêtes qui tombent souvent) reste ouverte pour plus tard.

Une quête expirée ou inachevée ne donne aucune XP. Une quête n'est jamais
rétroactive : seuls les films validés après son activation et dont la date de
visionnage appartient à sa période peuvent la faire progresser.

------

## 7.3. Niveaux

- niveau initial : **1** ;
- niveau maximum : **50** ;
- XP initiale : **0** ;
- le niveau ne redescend jamais ;
- atteindre le niveau 50 n'a aucun effet sur le rang.

Les premiers niveaux sont rapides, puis le coût augmente avant d'atteindre un
coût stable proche de 3 200 XP par niveau. La table complète et la formule sont
définies dans `FORMULE_NIVEAUX_XP.txt`.

Tous les seuils, récompenses et paramètres sont centralisés dans une
configuration métier dédiée. Aucun seuil n'est dispersé dans les ViewModels ou
les écrans. Ils seront ajustés après tests réels.

------

## 7.4. Rangs

Le rang **ne se traite pas ici**. C'est le cœur du produit, et il obéit à une logique propre.

Voir **§9 — Identité cinéphile : rangs et badges**.

------

## 7.5. Déblocages

La carte (Atlas) reste **entièrement observable** : aucun pays, courant,
décennie ou genre n'est cadenassé.

Les **collections** ont deux verrous, puis un cliquet :

- **Initiation** est toujours ouverte ;
- les autres collections sont grisées et cadenassées tant qu’aucun film
  d’Initiation n’est Vu ;
- un tap sur une collection verrouillée affiche un message expliquant
  soit Initiation, soit le palier précédent (2 collections commencées,
  2 films vus chacune) ;
- une fois un palier ouvert, il **ne se recadenasse plus** (unfollow
  d’une collection « commencée » ne referme pas le groupe suivant).

La philosophie générale reste :

> **La carte doit rester largement observable et l'utilisateur doit rester libre.**

Les groupes de difficulté (Premières séances, Ciné-club, Salle obscure,
Cinémathèque, Hors-champ) **se cadenassent en chaîne** depuis 0.1.10
(§8.3). L’Atlas n’a aucun cadenas.

------

# 8. Système de collections

## 8.1. Objectif

Les collections permettent de structurer l'exploration autour d'un ensemble cohérent de films. Elles ne sont pas un simple index : **suivre** une collection en fait un parcours personnel (or, Accueil, pourcentage, titres dorés).

------

## 8.2. Collection Initiation

**Initiation** est la première collection du catalogue, toujours en tête de liste, toujours déverrouillée. Dix classiques largement connus du public (Titanic, Avatar, Seven, Le Roi Lion, Forrest Gump, etc.).

Texte d’intention (résumé) : une porte d’entrée, pas un palmarès. Le cinéphile confirmé peut la parcourir rapidement ; le novice y trouve des films déjà vus ou facilement trouvables. La valider n’est pas un examen : elle ouvre le reste des collections.

Règle de déverrouillage des **autres** collections (0.1.10) :

1. au moins **un** film d’Initiation est marqué Vu ;
2. **et**, pour un groupe plus exigeant que Premières séances, le groupe
   précédent a assez de collections **suivies** et commencées (2 films vus,
   ou toutes s’il y en a moins de 2).

Le **suivi** d’Initiation n’est plus une condition pour *rester* ouvert.
Unfollow d’une collection déjà commencée ne referme pas le palier suivant.

------

## 8.3. Groupes de difficulté

Les collections sont regroupées sous cinq intitulés (registre « aller au cinéma », pas scolaire) :

| Code `track` | Libellé FR | Intention |
| --- | --- | --- |
| `GATEWAY` | Premières séances | Initiation |
| `CLUB` | Ciné-club | Courants accessibles (dont expressionnisme allemand) |
| `DARKROOM` | Salle obscure | Un cran plus exigeant |
| `CINEMATHEQUE` | Cinémathèque | Corpus plus austère |
| `OFFSCREEN` | Hors-champ | Formats / expérimentations |

Les groupes **se cadenassent en chaîne** depuis 0.1.10 : ouvrir Ciné-club
demande d’avoir **suivi** et commencé au moins 2 collections de Premières
séances (2 films vus dans chacune ; s’il n’y en a qu’une, celle-là suffit).
Sans le suivi, les films partagés (ex. Initiation ∩ Nouvel Hollywood) ne
doivent pas débloquer le palier suivant. Même logique pour Salle obscure,
Cinémathèque, Hors-champ. Cliquet : un palier ouvert reste ouvert.

Au plus **10** collections en cours (suivies et non terminées) à la fois
(`FunctionalLimits.MAX_IN_PROGRESS_COLLECTIONS`). Un 11e suivi affiche
une alerte ; il faut en terminer une ou ne plus en suivre une.

------

## 8.4. Suivre, progression affichée, films dorés

- **Suivre** une collection : elle passe en or, remonte en tête des suivies, apparaît dans « Collections en cours » (Accueil / Parcours) **tant qu’elle n’est pas à 100 %**.
- **Ne plus suivre** : possible seulement si la collection n’est **pas** complétée.
- **Pourcentage et compteur X / N** : calculés et affichés **uniquement si la collection est suivie**. Si elle n’est pas suivie, l’interface affiche **0 %** et **0 / N**, même si des films de la collection sont déjà marqués Vu (films vus ailleurs, quêtes, etc.).
- **Titres en or** dans la fiche : un film déjà Vu n’est doré **que** si la collection est suivie. Sinon le titre reste au style normal (le Vu existe toujours en base).

------

## 8.5. Collections essentielles

Une collection majeure pourra comporter environ 20 films essentiels, mais la taille peut varier librement : les paliers étant en pourcentage (§8.7), aucune contrainte de format ne pèse sur la sélection éditoriale. Initiation en a 10. Le pack 0.1.10 en comptait 15. Le pack 24 en compte 27.

------

## 8.6. Complétion 100 %

Lorsque le dernier film d’une **collection suivie** est marqué Vu :

- une **boîte de félicitations** s’affiche (titre + nom de la collection). Ce n’est pas une pluie de confettis ni une animation pleine page ;
- la collection **sort** des listes « collections en cours » (Accueil et Parcours) ;
- elle reste dans l’onglet Collections : titre et pourcentage **en or**, icône de **validation** (check) à la place du cadenas / de l’état courant ;
- le bouton Suivre / Ne plus suivre est **remplacé** par un libellé grisé non actionnable : « Vous avez terminé cette collection ».

La collection reste `followed` en base (on ne force pas un unfollow). On ne peut plus la retirer du suivi.

------

## 8.7. Paliers

Les paliers sont exprimés en **pourcentage**, jamais en nombre absolu de films.

| Progression | Palier |
| --- | --- |
| 0 % | Non explorée |
| 25 % | Découverte |
| 50 % | Exploration |
| 75 % | Avancée |
| 100 % | Complétée |

Raison : les collections n'ont pas toutes la même taille. Des seuils fixes (5, 10, 15, 20) seraient incohérents dès qu'une collection compte 12 ou 35 films — le palier « 15 » n'existerait même pas dans la première.

Avec des pourcentages, une seule règle couvre toutes les collections, quelle que soit leur taille.

Les appellations définitives restent à travailler. En 0.1.7, l'interface affiche surtout le pourcentage et l'état complété (§8.6), pas encore ces libellés de palier.

------

# 9. Identité cinéphile : rangs et badges

## 9.1. Quatre notions à ne pas confondre

| Notion | Rôle | Quantité | Rythme |
| ------ | ---- | -------- | ------ |
| **Rang** | Identité cinéphile à un instant T : un état d'esprit, une façon de voir et de concevoir le cinéma | 10, un seul à la fois | Bouge très lentement — des années |
| **Niveau / XP** | Progression ludique (quêtes + **25 XP** si le film est dans une collection suivie) | 1 à 50 | Régulier |
| **Badge** | Accomplissement ponctuel une fois une condition remplie | Des dizaines, voire des centaines, cumulables | Dès que la condition tombe |
| **Quête** | Objectif à court terme, avec une difficulté | Trois par semaine | Hebdomadaire |

Le rang **n'est pas** un compteur de films et ne se déduit ni du niveau, ni des
badges, ni des quêtes. Inversement, le niveau dépend de l'XP (quêtes + 25 XP
pour un film d'une collection suivie, une seule fois) et jamais du rang.

------

## 9.2. Le rang est le cœur de l'application

Le rang est l'élément central du produit — davantage que la carte interactive, aussi séduisante soit-elle.

Il ne représente pas un nombre de films vus. Il représente **un état d'esprit**.

Le rang évolue lentement. Il est tout à fait normal qu'un cinéphile ne gagne pas deux rangs en deux ou trois ans.

Différence entre un rang 8 et un rang 10 : ce n'est pas le volume. Un rang 8 peut connaître la filmographie complète de Bergman, Ozu, Tarkovski ou Kurosawa. Un rang 10 ne regarde plus le cinéma de la même manière — il tient six heures sur une œuvre contemplative obscure sans fermer l'œil, et trouve encore que le troisième acte manquait de peps.

**10 rangs** au total. Les noms et le nombre restent modifiables.

------

## 9.3. Les 10 rangs

| # | Rang | Description |
| --- | --- | --- |
| 1 | **Novice** | Découvre encore le cinéma. Culture très limitée ou principalement composée de films populaires / contemporains. |
| 2 | **Amateur** | Commence à avoir des références, des réalisateurs favoris, quelques classiques. Le cinéma devient un intérêt régulier. |
| 3 | **Initié** | A dépassé le simple cinéma populaire. Commence à explorer les classiques, les cinématographies étrangères, certains réalisateurs importants. |
| 4 | **Passionné** | On commence à parler de vraie cinéphilie. Connaît très bien plusieurs filmographies, explore des décennies différentes, possède ses propres goûts et repères. |
| 5 | **Explorateur** | La curiosité devient structurée. Ne se contente plus d'enchaîner les « grands films » : explore des pays, des mouvements, des genres, des périodes et des cinématographies moins connues. |
| 6 | **Connaisseur** | Culture très solide. Nombreuses références, filmographies conséquentes, bonne connaissance de plusieurs pans de l'histoire du cinéma. |
| 7 | **Érudit** | Culture cinématographique exceptionnelle. Grande diversité historique et géographique, connaissance approfondie de nombreux cinéastes et mouvements, capacité à faire des connexions entre eux. |
| 8 | **Spécialiste** | Compréhension approfondie du cinéma comme **langage** et comme **histoire** : mise en scène, montage, son, esthétique, écoles, filiations, contexte historique. |
| 9 | **Expert** | Culture et capacité d'analyse extrêmement poussées. Très grande maîtrise de l'histoire du cinéma, capacité à analyser une œuvre dans ses dimensions formelles, historiques et esthétiques. |
| 10 | **Maître** | Le sommet. Connaissance exceptionnellement vaste et profonde du médium — périodes, régions, formes, traditions — accompagnée d'une capacité d'analyse avancée. |

Les dix définitions vivent dans le catalogue `rankings`, avec un code et un
ordre stables distincts de leur identifiant technique. Le profil référence son
rang courant ; les noms restent provisoires et peuvent évoluer ou être traduits
sans migration du schéma.

### Changement de nature au rang 8

Les rangs 1 à 7 décrivent une **culture qui s'élargit**.

À partir du rang 8, il ne s'agit plus de « j'ai vu énormément de films » mais d'un **rapport différent au médium** : le cinéma comme langage et comme histoire, pas seulement comme catalogue d'œuvres vues.

------

## 9.4. Calcul du rang

La formule est **arrêtée** et implémentable en l'état. Cette section en donne la lecture fonctionnelle ; la formulation complète est dans `FORMULE_MATHEMATIQUE.txt` (v0.3), et la justification des choix dans `RETOUR_FORMULE_RANG.txt`.

### Principe retenu

Le rang ne se calcule pas sur un compteur de films. Il combine **trois axes**, dont deux dominent volontairement le troisième :

| Axe | Ce qu'il mesure | Comportement | Poids |
| --- | --- | --- | --- |
| **Volume pondéré** | combien de films validés, chacun compté à hauteur de son exigence | croît toujours | faible — mais non nul |
| **Diversité** | combien de territoires différents touchés au moins une fois | **sature** | fort |
| **Profondeur** | à quel point ces territoires ont été creusés | croît sans limite | fort |

> Voir beaucoup de films proches ne suffit pas. Voir un film de chaque zone non plus. Le rang élevé demande les deux : **étendue et approfondissement**.

### Séparation stricte découverte / approfondissement

C'est la mécanique centrale. Un territoire — un pays, un réalisateur, un mouvement — alimente **soit** la diversité, **soit** la profondeur. Jamais les deux.

| Films vus d'un même territoire | Diversité | Profondeur |
| --- | --- | --- |
| 0 | 0 | 0 |
| 1 | **acquise, définitivement** | 0 |
| 2 | acquise | commence |
| 10 | acquise | élevée |
| 50 | acquise | très élevée |

Le premier film japonais ouvre le territoire « Japon ». Le deuxième n'apporte plus aucune diversité — il commence à apporter de la profondeur. Un utilisateur qui voit un seul film par pays aura une diversité maximale et une profondeur nulle ; celui qui voit cinquante films japonais aura l'inverse. Les deux profils sont distingués, ce qui était tout l'objectif.

### Poids intrinsèque du film

Chaque film du catalogue porte un **poids**, calculé à partir de quatre critères : éloignement historique, exigence, importance dans l'histoire du cinéma, rareté culturelle.

Ce poids intervient sur l'axe **volume** : cent films exigeants pèsent environ 2,4 fois cent blockbusters. Un film au maximum d'exigence vaut au plus **3,16 fois** un film au minimum — l'écart est volontairement borné, pour que quelques films obscurs ne puissent pas remplacer une vraie culture générale.

### Le catalogue comme référentiel

Les valeurs ne sont pas absolues. La rareté d'un territoire se mesure **par rapport au catalogue** : si seulement huit films viennent d'un pays donné, ce pays est une zone rare, et le toucher rapporte davantage.

Le catalogue est donc la carte du territoire, et le rang mesure la portion réellement parcourue.

### Équilibre entre les axes d'exploration

Le catalogue comptera des centaines de réalisateurs mais seulement six continents. Sans correction, le rang serait devenu un compteur de réalisateurs déguisé.

Chaque dimension reçoit donc une **part cible** du parcours — le mouvement pèse un quart, le réalisateur un cinquième, le pays un peu moins, et ainsi de suite jusqu'à cent pour cent. Couvrir entièrement une dimension rapporte exactement sa part, quel que soit le nombre de valeurs qu'elle contient.

### Rien ne peut être perdu

Le catalogue partira de zéro et grandira pendant des années. Trois protections garantissent qu'un enrichissement du catalogue ne dégrade jamais un acquis :

- la rareté de chaque territoire est figée par version de catalogue, et conservée à sa valeur historique la plus favorable ;
- les poids de dimension suivent la même règle ;
- le rang affiché ne redescend jamais sous le maximum déjà atteint.

Ce dernier point couvre aussi le retrait accidentel d'un film et les corrections éditoriales.

### Conversion en rang

Le score global est converti par une **table de neuf seuils**, et non par une courbe. C'est plus lisible, ajustable rang par rang, et cela rend le rang 10 réellement atteignable.

En V1, les rangs 8 à 10 restent attribués aux scores les plus élevés. Le rang
10 correspond à un parcours presque exhaustif : couverture de la quasi-totalité
des pays, caractéristiques, époques et autres dimensions du catalogue. Cette
approximation quantitative est acceptée pour démarrer ; les seuils seront
affinés sur des données réelles.

### Points encore ouverts

- **Calibrage** : vingt valeurs, dont neuf seuils qui demandent un vrai arbitrage cinéphile. À faire par simulation sur des profils types, pas à l'intuition.
- **Attribution du poids** : quatre notes par film sur plusieurs milliers de films, c'est le coût caché de la formule. Deux des quatre sont dérivables automatiquement ; les deux autres demandent un jugement. Piste : un seul curseur manuel de 1 à 5 par film.

------

## 9.5. Badges — principe

Un badge se débloque dès que sa condition est remplie. Rien d'autre.

L'utilisateur peut en cumuler autant qu'il le souhaite : les badges ne sont pas en concurrence, et ils ne déterminent pas le rang.

La liste a vocation à **grossir librement** au fil du développement.

Toutes les conditions portent sur les films du **catalogue Urbinema** validés.

Un badge obtenu est **définitivement acquis**. Le retrait ou la correction
ultérieure d'un film ne supprime jamais une date d'obtention existante.

------

## 9.6. Structure d'un badge

Chaque badge possède idéalement :

- un identifiant technique auto-généré ;
- un code métier stable (`001`, `002`, `003`...) utilisé par le moteur de
  règles — jamais l'identifiant technique ;
- nom ;
- description ;
- catégorie ;
- difficulté de 1 à 5 ;
- rareté ;
- illustration locale ;
- état actif/inactif.

Le badge **est** la récompense. Il n'en accorde pas d'autre.

La condition n'est pas une expression dynamique stockée en base. Les règles
V1 sont implémentées dans un registre de code typé, indexé par le code stable
du badge. La base stocke la définition éditoriale et l'obtention ; le domaine
porte la logique vérifiable et testable.

------

## 9.7. Noms des badges

Les noms évitent d'être purement descriptifs lorsque c'est pertinent : l'objectif est une identité ludique et cinéphile (*Dolce Vita*, *Fantômes du Muet*, *Nuits américaines*).

------

## 9.8. Liste des badges — première fournée

Liste de travail : `Listes_Fonctionnelles/Liste_Des_Badges.txt`

### Volume

| Badge | Condition |
| --- | --- |
| Premier Rideau | voir son premier film |
| Deuxième Séance | voir 20 films |
| Accro au Ciné | voir 100 films |
| Collectionneur | voir 300 films |

### Géographie

| Badge | Condition |
| --- | --- |
| Passeport Cinéma | voir des films de 15 pays différents |
| Globe-Trotter | voir des films de 30 pays différents |
| Cartographe du Cinéma | voir des films de 50 pays différents |
| Tour d'Europe | voir des films de 10 pays européens différents |
| Au-delà des Frontières | voir au moins 5 films provenant de chacun de 5 continents |
| Mappemonde | voir au moins un film de chaque pays du catalogue |

### Pays et cinématographies

| Badge | Condition |
| --- | --- |
| Dolce Vita | voir 20 films italiens |
| Made in USA | voir 50 films américains |
| Rising Sun | voir 20 films japonais |
| Lumière sur la France | voir 20 films français |
| Made in Asia | voir 50 films asiatiques |

### Temps

| Badge | Condition |
| --- | --- |
| Au-delà du Canon | voir 40 films sortis avant 1950 |
| Archéologue du Cinéma | voir 100 films sortis avant 1960 |
| Mémoire du Septième Art | voir 300 films sortis avant 1980 |
| Fantômes du Muet | voir 20 films muets |
| Retour aux Sources | voir des films de 5 décennies différentes |
| À Travers les Âges | voir un film de chaque décennie, des années 1890 aux années 2020 |

### Mouvements et genres

| Badge | Condition |
| --- | --- |
| Enfant de la Nouvelle Vague | voir 15 films de réalisateurs associés à la Nouvelle Vague française |
| La Dolce Commedia | voir 15 films de la comédie italienne |
| L'Œil soviétique | voir 10 films issus du cinéma soviétique |
| Nuits américaines | voir 20 films noirs |
| Western Spaghetti | voir 15 westerns italiens |
| Cabinet des Frayeurs | voir 30 films d'horreur |

### Formes exigeantes

| Badge | Condition |
| --- | --- |
| La Forme avant le Fond | voir 10 films particulièrement expérimentaux ou non narratifs |
| Le Temps suspendu | voir 20 films de plus de 3 heures |
| La Grande Traversée | voir 5 films de plus de 5 heures |

### Panorama

| Badge | Condition |
| --- | --- |
| Bibliothèque de Pellicule | voir au moins 10 films de 20 réalisateurs différents |
| Encyclopédie Vivante | voir au moins 10 films appartenant à 30 mouvements cinématographiques différents |

------

## 9.9. Ce que les badges exigent du catalogue

### Atteignabilité : non-sujet

Plusieurs badges sont hors d'atteinte tant que le catalogue est petit. **Ce n'est pas un problème et ce n'est pas une priorité.** La base compte aujourd'hui zéro film : tout est inatteignable, et les titres s'ajouteront progressivement. La priorité est le cœur, l'algorithme et l'application, pas l'équilibrage du contenu.

### Données requises : ça, c'est structurant

En revanche, une condition de badge n'est **calculable** que si le film porte la donnée correspondante. C'est une contrainte de modèle, pas de volume :

| Donnée | Badges concernés |
| --- | --- |
| durée | Le Temps suspendu, La Grande Traversée |
| muet (oui/non) | Fantômes du Muet |
| expérimental / non narratif | La Forme avant le Fond |
| réalisateur | Bibliothèque de Pellicule, Enfant de la Nouvelle Vague |
| pays et continent | tous les badges géographiques |
| mouvements | L'Œil soviétique, Encyclopédie Vivante |
| genre | Nuits américaines, Western Spaghetti, La Dolce Commedia |

Le **réalisateur devient donc une donnée du film dès la V1** — il est requis par deux badges et par le calcul de profondeur du rang (§9.4). Cela ne remet pas en cause son statut d'entité de la carte, qui reste en V2.

Pour mémoire, les volumes impliqués (100 films d'avant 1980, 50 pays, 20 réalisateurs à 10 films, 30 mouvements à 10 films) supposent un catalogue de plusieurs milliers de titres. Il sera atteint progressivement. Urbinema n'est pas pensée pour être terminée en deux mois, mais parcourue sur des années.

------

## 9.10. Affichage

Sur le profil, la hiérarchie est : **Pseudo → Rang → niveau/XP → jusqu’à 3
badges vitrine → statistiques**.

Le rang est l'élément identitaire principal. Les badges se placent en dessous,
en sélection (3 max, choisis depuis Tous les badges).

Détail d'interface : voir `CahierDesCharges_IHM.md`.

------

# 10. Système de quêtes

## 10.1. Objectif

Les quêtes créent des objectifs temporaires et constituent la principale
source d'XP.

Elles se distinguent des collections par leur caractère :

- transversal ;
- court ;
- temporaire ;
- indépendant d'une seule caractéristique.

------

## 10.2. Quêtes de découverte

Exemples :

> Regarder 3 films en noir et blanc ce mois-ci.

> Regarder 3 films provenant de 3 pays différents.

> Regarder un film de trois décennies différentes.

> Regarder un film sorti avant 1950.

------

## 10.3. Difficulté et récompense

Trois difficultés sont retenues en V1 :

| Difficulté | Récompense | Forme habituelle |
| --- | ---: | --- |
| **Bronze** | 100 XP | un objectif simple |
| **Argent** | 250 XP | plusieurs films ou plusieurs critères |
| **Or** | 500 XP | objectif long ou exigeant |

Les quêtes Argent et Or peuvent demander plusieurs films. Elles affichent alors
une progression `réalisé / objectif` et une barre de progression.

------

## 10.4. Cycle hebdomadaire

La V1 propose **trois quêtes simultanées par semaine** : une Bronze, une Argent
et une Or.

- activation : lundi à 02:00, heure locale de l'appareil ;
- expiration : lundi suivant à 02:00 ;
- une quête terminée reste affichée comme telle jusqu'au renouvellement ;
- qu'elle soit terminée ou non, elle disparaît à l'expiration ;
- aucune nouvelle quête n'est attribuée avant le cycle suivant ;
- aucune validation rétroactive avant l'heure d'activation.

Le décalage à 02:00 permet de terminer un film commencé le dimanche soir et de
l'enregistrer avant le renouvellement.

Les quêtes sont écrites manuellement dans le catalogue. Le pack 21 embarque
**59 quêtes types** (19 Bronze, 20 Argent, 20 Or), dont des quêtes de courant
(`WATCH_CHARACTERISTIC_*`, par exemple « Voir 1 Giallo »), pas de collection.
Chaque lundi 02:00, l'app
tire **au hasard une quête par palier** parmi celles encore faisables (assez de films
non vus pour atteindre la cible). Une quête devenue impossible en cours de
semaine est remplacée. La génération automatique de nouveaux énoncés est
reportée.

Une quête mensuelle éventuelle suit le mois civil, du premier jour à 00:00 au
premier jour du mois suivant à 00:00. Elle n'est pas activée en V1.

------

## 10.5. Quêtes avancées d'analyse

Fonctionnalité future.

Exemples :

- comparer deux mises en scène ;
- observer le montage ;
- identifier des utilisations du hors-champ ;
- observer le travail du son ;
- comparer deux approches narratives.

Cette fonctionnalité nécessite une conception éditoriale importante et n'est donc pas prioritaire.

------

# 11. Carte cinématographique

## 11.1. Rôle (métier)

Le **rang** dit *qui tu es* comme cinéphile. Les **collections** et les
**quêtes** disent *par où passer*. La **carte** dit *où tu as mis les pieds*
dans le cinéma : quels pays, quelles décennies, quels courants, quels
auteurs.

Ce n’est pas un GPS, ni une liste Letterboxd dessinée. C’est un **territoire
d’exploration**. Chaque point est un *type* de chose (la France, les années
1960, le néoréalisme, Kurosawa), pas un film posé comme une punaise.

Les films restent le moyen d’allumer le territoire : tu marques un film Vu,
et les nœuds qui le concernent s’éclairent.

------

## 11.2. Deux surfaces, un même modèle

Depuis 0.1.6, l’onglet **Atlas** montre des **listes** filtrables
(courants, pays, décennies, genres, réalisateurs). C’est l’accès sobre,
lisible, compatible TalkBack.

La **carte du ciel** s’ouvre depuis l’icône étoiles en haut à droite.
Vue par défaut de la carte : un **film au centre**, ses territoires tout
près, d’autres films plus loin s’ils sont moins liés. Les puces Pays /
Courants… gardent l’ancienne vue calques.

| | Atlas | Carte du ciel |
| --- | --- | --- |
| Où | Onglet Atlas (défaut) | Icône étoiles en haut à droite |
| Forme | Lignes + pastilles d’état | Constellation autour d’un film, ou calques |
| Usage | Trouver, comparer, TalkBack | Voyager, recentrer, ouvrir les fiches |
| Données | Room, mêmes territoires | + films comme nœuds dans la vue « Autour du film » |

Tout ce qui est tapable sur le ciel l’est aussi dans l’Atlas. La carte
visuelle est un **plaisir**, pas un passage obligé.

------

## 11.3. Parcours utilisateur (0.2.1)

1. Onglet **Carte** → constellation autour d’un film (dernier Vu, sinon
   Initiation).
2. **Pincer** pour zoomer (jusqu’à ×14), **glisser**, **cible** en bas à
   droite pour recadrer.
3. **Tap un film** autour du centre → la carte se **reconstruit** autour
   de lui. **Tap un territoire** → feuille (liste de films + ouvrir la
   fiche pays / réal / genre…).
4. Puce **Autour du film** vs **Pays / Courants / …** : l’ancienne vue
   calques.
5. Icône **étoiles** (depuis l’Atlas) → carte du ciel. Fiche film → **Voir sur la carte**.

Le bas de l’app reste visible. L’onglet Atlas reste sélectionné.

------

## 11.4. Calques — pourquoi un seul à la fois

Mettre 42 pays, 50 courants, 14 décennies, les genres, 200 réalisateurs
et 15 collections **en même temps** saturait l’écran. Un calque = une
question :

| Calque | Question | Disposition 0.2.1 |
| --- | --- | --- |
| **Autour du film** (défaut) | Qu’est-ce qui entoure *ce* film ? | Centre = film, anneau 1 = réal/pays/genres…, anneau 2 = films liés |
| Courants | Quels mouvements as-tu touchés ? | Constellation |
| Pays | Où as-tu voyagé ? | Grappes par **continent** |
| Décennies | Quelles années ? | Frise de gauche à droite |
| Genres | Quels langages ? | Constellation |
| Réalisateurs | Quels auteurs ? | Grappes par continent du pays le plus fréquent |
| Collections | Quels parcours éditoriaux ? | Constellation |

Changer de calque **remplace** le dessin (ce n’est pas un calque Photoshop
superposé). Les positions d’un calque sont **stables** pour un catalogue
donné : ce n’est pas un chaos à chaque ouverture.

------

## 11.5. Nœuds et liens (ce que ça *veut dire*)

**Nœud** = un territoire (`FRANCE`, `NOUVELLE_VAGUE_FRANCAISE`, `1960`,
`DRAME`, `AKIRA_KUROSAWA`, `COLLECTION_001`…) **ou**, en vue « Autour du
film », un titre du catalogue. Jamais une affiche. Jamais les 405 films
d’un coup.

**Lien** = « ces deux territoires apparaissent ensemble sur au moins un
film » (co-production, deux genres sur la même fiche, deux courants, deux
réalisateurs, deux collections qui partagent un titre). Pour les
**décennies**, le lien est simplement le voisin chronologique
(1950—1960—1970).

Un trait n’est **jamais inventé** pour faire joli. S’il est visible, on
peut l’expliquer par Room.

Les films **ont** des coordonnées dans la vue « Autour du film » (centre
et anneau 2, au plus 12 voisins). Ils n’apparaissent pas tous à la fois.

------

## 11.6. États des étoiles (0.2.3)

La **couleur** dit d’abord **ce que c’est** :

| Type | Couleur |
| --- | --- |
| Film | Ivoire `#F4EFE6` |
| Film vu / centre | Or `#E8C68A` |
| Réalisateur | Cyan `#5EC8D8` |
| Pays | Corail `#E07A5F` |
| Genre | Rose `#D489C0` |
| Courant | Violet `#7A5CB8` |
| Décennie | Orange `#E0A45C` |
| Collection | Bleu `#6EA8FF` |

L’**état d’exploration** reste lisible : non exploré = cercle **pointillé**
de la couleur du type ; commencé / avancé = disque plein ; maîtrisé = disque
+ point sombre au centre. Un même nom n’apparaît **qu’une fois** (le
réalisateur gagne face à une collection homonyme).

Les types du premier anneau sont **séparés** (secteurs + rayons un peu
différents), pas tous mélangés sur le même cercle.

Légende en bas à gauche de la carte. L’intensité dit *où tu as vécu*, pas
un score de rang. Le rang continue de se calculer ailleurs.

------

## 11.7. Navigation depuis un nœud

La feuille du ciel liste les **films** du territoire (titre or si Vu).

L’Atlas, lui, ouvre encore l’écran liste (films + collections liées).
Les deux chemins mènent aux mêmes objets.

Chaîne métier typique :

```text
Carte du ciel, calque Pays → tap France
  → feuille : films français
    → tap Les 400 coups
      → Marquer comme vu
        → la France (et la Nouvelle Vague, 1950, etc.) s’allument au retour
```

------

## 11.8. Ce que la carte n’est pas (0.2.1)

- Pas les **405 films** posés d’un coup : seulement le focus + 12 voisins.
- Pas des **acteurs / compositeurs / scénaristes**.
- Pas un moteur de jeu, pas de physique, pas de mini-map Google.
- L’Atlas listes **est** l’écran d’entrée de l’onglet ; le ciel est l’icône étoiles.

------

## 11.9. Suite possible

Affiner la métaphore après usage. Plus tard, si Léo le veut : nœuds-films,
autres métiers du générique, influences. Ce n’est pas le jour 1.

------

# 12. Statistiques et suivi de progression

## 12.1. Statistiques générales

Le profil doit notamment afficher :

- rang ;
- films vus ;
- collections complétées ;
- badges ;
- quêtes réalisées.

------

## 12.2. Statistiques géographiques

- pays explorés ;
- continents explorés ;
- progression par continent ;
- pays les plus représentés.

------

## 12.3. Statistiques temporelles

- décennies explorées ;
- périodes explorées ;
- progression historique.

------

## 12.4. Statistiques de genres

- genres explorés ;
- genres peu explorés ;
- diversité des genres.

------

## 12.5. Statistiques de mouvements

- mouvements découverts ;
- progression par mouvement ;
- collections complétées.

------

## 12.6. Statistique de diversité

Une représentation synthétique doit permettre de comprendre rapidement l'étendue du parcours.

Exemple :

```text
Films vus              487
Pays explorés           31
Continents                5
Décennies                 12
Mouvements                18
Collections complétées   23
Quêtes réalisées          47
Badges obtenus            38
```

------

# 13. Recherche et navigation

## 13.1. Recherche globale

L'utilisateur doit pouvoir rechercher notamment :

- films ;
- pays ;
- mouvements ;
- collections ;
- décennies ;
- genres.

------

## 13.2. Filtres

Les contenus peuvent être filtrés selon :

- vu / non vu ;
- pays ;
- décennie ;
- mouvement ;
- genre ;
- collection ;
- difficulté ;
- progression.

------

## 13.3. Navigation exploratoire

L'utilisateur doit pouvoir passer naturellement d'un élément à un autre.

Exemple :

> Mouvement → pays → décennie → collection → film.

------

# 14. Onboarding et première expérience

## 14.1. Objectif

La première expérience doit permettre à l'utilisateur de comprendre immédiatement :

- ce qu'est Urbinema ;
- comment progresser ;
- comment déclarer des films vus ;
- comment explorer la carte ;
- comment fonctionnent les collections et badges.

------

## 14.2. Premier lancement V1 (0.1.7)

Pop-up bloquante dès qu'il n'y a **aucun utilisateur** **ou** que l'utilisateur
existant n'a **pas de date de naissance** (cas des installs 0.1.6 qui avaient
créé un profil `Léo` sans âge) : **pseudo** (obligatoire, pas de valeur par
défaut), **âge** (8–120, stocké comme année de naissance approximative) et
**avatar packagé** (10 visuels en carrousel, changeable ensuite dans Réglages). Pas de
photothèque. Pas de choix de films déjà vus. Tout le monde commence Novice,
niveau 1, 0 XP.

Si un profil existe déjà avec un pseudo mais sans `birthDate`, la pop-up
propose de le compléter (mise à jour, pas une seconde ligne `users`).

Une V2 **possible** pourra proposer, plus tard, une sélection de films du
catalogue déjà susceptibles d'être connus — toujours **dans** le catalogue
Urbinema, pas via un dump Letterboxd.

------

## 14.3. Import tiers

**Pas en V1.** Letterboxd, SensCritique et équivalents iraient à l'encontre du parcours guidé.

Non anticipé comme exigence de modèle V1.

------

## 14.4. Évaluation initiale

Pas de rang déclaré qui court-circuite le parcours.

Le rang découle **uniquement** des validations réelles dans l'application. Tout le monde commence Novice.

------

# 15. Administration et gestion éditoriale

## 15.1. Importance

Le contenu constitue une partie essentielle de la valeur d'Urbinema.

Un système d'administration est donc indispensable.

------

## 15.2. Gestion des films

L'administrateur doit pouvoir :

- créer un film ;
- modifier un film ;
- désactiver un film ;
- corriger ses métadonnées ;
- associer ses catégories.

------

## 15.3. Gestion des caractéristiques

L'administrateur doit pouvoir :

- créer une caractéristique ;
- choisir son type ;
- modifier sa description ;
- modifier sa période ;
- modifier ses pays associés ;
- associer des films ;
- définir sa difficulté.

------

## 15.4. Gestion des collections

L'administrateur doit pouvoir :

- créer une collection ;
- modifier une collection ;
- ajouter/supprimer des films ;
- modifier l'ordre ;
- publier/dépublier une collection ;
- associer pays, continent, époque ou caractéristique ;
- définir le badge associé.

------

## 15.5. Gestion des badges

L'administrateur doit pouvoir :

- créer un badge ;
- attribuer son code stable ;
- définir sa description ;
- définir sa difficulté de 1 à 5 ;
- modifier son illustration ;
- activer/désactiver un badge.

La condition métier reste implémentée dans le code et testée séparément.

------

## 15.6. Gestion des quêtes

L'administrateur doit pouvoir :

- créer une quête ;
- définir sa condition ;
- définir sa durée ;
- définir sa difficulté Bronze, Argent ou Or ;
- définir sa récompense XP correspondante ;
- publier/dépublier une quête.

------

## 15.7. Gestion des fiches

Fonctionnalité future.

L'administration devra permettre de gérer :

- les fiches pédagogiques ;
- les concepts ;
- les contenus associés.

------

## 15.8. Parcours pédagogiques (0.3.0, pack 29)

L'onglet Parcours n'est pas une collection et ne marque aucun film Vu. Il
propose des lectures : pour l'instant le parcours « Comment le cinéma est
devenu un art », onze courants du muet au cinéma contemporain.

Chaque courant est une bulle. Entre deux bulles, un point d'interrogation
ouvre une petite fenêtre qui contient seulement la phrase de transition. La bulle ouvre une fiche (période, description, à savoir,
figures, films). Une figure ouvre la fiche réalisateur quand elle existe.
Un film ouvre la fiche film. Les personnes sans fiche (acteur, théoricien)
restent du texte.

Le mode d'emploi pour modifier un parcours, une transition ou un courant est
dans la spec développeur, §6.4. Le texte source est
`Listes_Fonctionnelles/Listes_Des_Parcours.txt` ; l'app lit la clé `paths`
du catalogue.

------

# 16. Règles éditoriales

## 16.1. Importance

Urbinema ne doit pas être uniquement une application techniquement fonctionnelle.

La qualité de son **référentiel cinématographique** est fondamentale.

------

## 16.2. Définition d'une caractéristique cinématographique

Il faudra définir précisément :

- ce qui constitue un mouvement ;
- ce qui constitue un courant ;
- ce qui constitue un style ;
- les périodes ;
- les zones géographiques.

------

## 16.3. Définition d'un film essentiel

Une collection de films essentiels doit reposer sur une méthodologie éditoriale.

Les critères pourront inclure :

- importance historique ;
- influence ;
- représentativité ;
- reconnaissance critique ;
- importance culturelle ;
- diversité ;
- accessibilité.

La méthode exacte reste à définir.

------

## 16.4. Cas ambigus

Les cas suivants doivent être traités explicitement :

- film appartenant à plusieurs caractéristiques de types différents ;
- coproduction internationale ;
- film à cheval entre deux périodes ;
- genre hybride ;
- mouvement dont les frontières sont discutées.

------

## 16.5. Diversité géographique

Le catalogue doit éviter une vision excessivement centrée sur :

- Hollywood ;
- Europe occidentale.

Le cinéma mondial doit être représenté progressivement.

------

## 16.6. Équilibre entre canon et découverte

Urbinema doit commencer par des films largement reconnus afin d'être accessible.

Mais la progression doit progressivement introduire :

- des films moins connus ;
- des œuvres de niche ;
- des cinématographies moins représentées ;
- des mouvements moins populaires.

------

# 17. Règles de cohérence et anti-abus

## 17.1. Objectif

Le système de gamification doit éviter que l'utilisateur puisse facilement « farmer » la progression.

------

## 17.2. Visionnage répété

Un film est **validé ou non** : il n'existe pas de compteur de visionnages en V1.

Revoir un film ne produit donc aucun effet sur la progression. C'est cohérent avec le calcul du rang, qui raisonne sur un **ensemble** de films validés et non sur une suite d'événements.

------

## 17.3. Suppression d'un film

Le retrait d'un film déclenche un **recalcul complet** de la progression depuis l'ensemble des films validés — rang, badges, collections, statistiques, états de la carte.

Le rang affiché, lui, **ne redescend jamais** sous le maximum déjà atteint (effet cliquet, §9.4). Un retrait accidentel ne peut donc pas faire perdre une identité acquise.

Un badge déjà obtenu reste **définitivement acquis**, même si une correction
éditoriale ou le retrait d'une validation fait ensuite disparaître sa condition.

------

## 17.4. Ajout massif / import

**Hors V1.** On ne prévoit pas de cocher 400 films d'un coup depuis un historique externe.

Si, plus tard, l'onboarding propose une sélection du catalogue à valider rapidement, les règles de badges et de quêtes associées devront être définies à ce moment (risque : terminer la progression en une soirée).

------

## 17.5. Cohérence des collections

Un film appartenant à plusieurs collections ne doit pas générer artificiellement plusieurs fois la récompense correspondant à sa découverte.

Exemple :

```text
Film X
 ├── Collection A
 ├── Collection B
 └── Collection C
```

La découverte du film reste une action unique.

La progression dans les trois collections est néanmoins mise à jour.

------

# 18. UX et principes d'interface

## 18.1. Compréhension immédiate

L'utilisateur doit comprendre rapidement :

> ce qu'il a exploré.

> ce qu'il peut explorer.

> comment progresser.

------

## 18.2. Progression visible

Les éléments de progression doivent être constamment lisibles :

- rang actuel ;
- niveau actuel et barre d'XP ;
- collections en cours ;
- badges ;
- quêtes en cours.

Le rang s'affiche comme un **état**, pas comme une barre de chargement vers le palier suivant : il évolue trop lentement pour être présenté comme un objectif immédiat.

------

## 18.3. Structure de l'accueil

La page d'accueil est organisée en trois zones :

1. **En-tête fixe** — rang en haut à gauche, niveau en haut à droite, barre
   d'XP sur presque toute la largeur juste dessous.
2. **Quêtes puis parcours** — trois quêtes hebdomadaires avec leurs barres de
   progression ; ensuite les **collections en cours** : suivies **et non
   complétées**. Une collection à 100 % disparaît de cette zone. Vignettes
   circulaires illustrées, avec leur pourcentage. Au premier lancement cette
   zone est vide.
3. **Historique** — flux chronologique des actions, **titres de films lisibles**
   (pas les codes), occupant le bas de l'écran puis l'essentiel de l'espace à
   mesure que l'on défile.

L'en-tête rang / niveau / XP reste fixé pendant le défilement. Les quêtes et
collections défilent avec le contenu.

La V1 ne met **aucune recommandation de film** sur l'accueil. La future
dimension sociale pourra mêler l'activité des amis à l'historique personnel,
mais la V1 n'affiche que celle de l'utilisateur local.

------

## 18.4. Découverte

L'interface doit constamment rendre visibles les zones inconnues.

Exemple :

> **Vous avez exploré 31 pays.**
>
> **42 restent à découvrir.**

------

## 18.5. Gamification modérée

L'interface doit être ludique sans ressembler à un jeu mobile agressivement gamifié.

L'identité doit rester :

> **cinéphile + culturelle + exploratoire.**

Le ton est le **tutoiement**, agréable et encourageant. Urbinema se présente
comme un compagnon de route vers la cinéphilie, jamais comme un professeur qui
juge ni comme un jeu qui met la pression.

**Exception 0.1.7 :** à 100 % d'une collection suivie, une **seule** boîte de
dialogue de félicitations. Pas de confettis, pas d'animation pleine page, pas
de série de toasts.

------

# 19. Priorisation fonctionnelle

## 19.1. MVP / V1

Le MVP doit contenir :

### Utilisateur

- pseudo local ;
- profil ;
- film du catalogue validé / non validé.

### Contenu

- catalogue fermé (~500, jusqu'à ~5000) ;
- films ;
- pays ;
- continents ;
- décennies ;
- genres ;
- 50 mouvements (§5.7).

### Progression

- rangs (10, voir §9) ;
- XP et 50 niveaux (§7) ;
- trois quêtes hebdomadaires Bronze / Argent / Or.

### Identité

- rang affiché ;
- badges (première fournée, §9.8).

### Collections

- 28 collections dans le pack 27 (dont Cinéma des premiers temps, groupe Premières séances) ;
- Initiation + cadenas Initiation **et** cadenas entre groupes, avec cliquet ;
- suivi obligatoire pour afficher la progression (0 % si non suivie) ;
- progression et complétion 100 % (§8).

### Badges

- badges de collections ;
- badges géographiques ;
- badges de mouvements ;
- badges temporels.

### Quêtes

- trois quêtes hebdomadaires ;
- progression et récompenses XP.

### Statistiques

- films ;
- pays ;
- continents ;
- décennies ;
- mouvements ;
- collections ;
- badges ;
- quêtes.

### Carte

- Atlas scrollable avec filtres (onglet Atlas, TalkBack) ;
- **carte du ciel** = icône étoiles (**0.2.1**, §11) : autour d’un film par
  défaut, calques en option, zoom/pan, fiches.

### Administration

- pas de back-office web en V1 ;
- chargement du catalogue en base (batch / script).

------

# 20. Fonctionnalités futures

## 20.1. Suite de la carte du ciel

La **première** carte interactive est livrée en **0.2.1** (§11). Ce qui
reste, si Léo le veut après usage :

- affiner le layout (trop serré, trop vide, labels) ;
- acteurs, scénaristes, compositeurs, producteurs ;
- influences historiques entre courants.

Les films comme nœuds (constellation **autour d’un titre**, 12 voisins)
sont **déjà** la vue par défaut. L’Atlas liste **reste** (icône liste).
Pas d’affiches sur le ciel.

## 20.2. Après la carte (confort, pas le cœur)

Si Léo le demande une fois la carte en place : photothèque, bios,
plus de collections, export CSV. Les avatars, badges et affiches packagés
sont déjà en V1.

------

## 20.3. V4 — Culture et analyse

- fiches pédagogiques avancées ;
- notions de cinéma ;
- quêtes d'analyse ;
- comparaison de films ;
- parcours pédagogiques ;
- outils d'observation.

------

## 20.4. V5+

### Personnalisation

- analyse du parcours ;
- recommandations ;
- zones sous-explorées ;
- parcours personnalisés.

### Profil avancé

- profil cinéphile détaillé ;
- spécialisations ;
- statistiques avancées.

### Intelligence

- recommandations intelligentes ;
- analyse des habitudes ;
- génération de parcours personnalisés.

------

# 21. Boucles d'utilisation

## 21.1. Boucle principale

```text
                 EXPLORER
                    ↓
              Choisir un film
                    ↓
                VOIR
                    ↓
             Marquer comme vu
                    ↓
        Collection / Badge / Quête
                    ↓
            Nouvelle progression
                    ↓
              Nouvelle piste
                    ↓
                 EXPLORER
```

------

## 21.2. Boucle de diversification

```text
        FILMS DÉJÀ VUS
               ↓
        CARTE DU CINÉMA
               ↓
       ZONES INEXPLORÉES
               ↓
       Nouvelle curiosité
               ↓
          Nouveau film
               ↓
       Nouvelle zone explorée
               ↓
              ...
```

------

## 21.3. Boucle de collection

```text
       Collection 3 / 20
               ↓
         Voir un film
               ↓
       Collection 4 / 20
               ↓
          Progression
               ↓
       Collection 20 / 20
               ↓
             BADGE
```

------

# 22. Vision à long terme

## 22.1. La carte comme cœur du produit

À terme, Urbinema doit pouvoir représenter une partie importante de l'histoire et de la diversité du cinéma mondial.

Un utilisateur pourrait commencer par :

> 🇫🇷 France

puis :

> 🎞️ Années 1960

puis :

> 🎥 Nouvelle Vague

puis :

> 🎬 Réalisateur

puis :

> 🎞️ Film

et découvrir ensuite des connexions vers d'autres mouvements ou pays.

------

## 22.2. Réseau cinématographique

La carte pourra représenter des relations telles que :

```text
Mouvement
   ↓
Pays
   ↓
Période
   ↓
Réalisateur
   ↓
Film
   ↓
Influence
   ↓
Autre mouvement
```

Elle pourrait ainsi devenir progressivement une **cartographie relationnelle du cinéma**.

------

## 22.3. Profil cinéphile

À terme, le profil pourra représenter non seulement :

> « combien de films as-tu vus ? »

mais :

> « quel territoire cinématographique as-tu exploré ? »

------

## 22.4. Journal de progression

Une future fonctionnalité pourra construire automatiquement une chronologie :

```text
Septembre 2026
    ↓
Découverte du cinéma japonais
    ↓
Collection complétée
    ↓
Badge obtenu
    ↓
Nouveau mouvement exploré
    ↓
Nouvelle zone de la carte ouverte
```

Cette chronologie constituera progressivement une représentation de la relation de l'utilisateur au cinéma.

------

# 23. Glossaire fonctionnel

| Terme             | Définition                                                   |
| ----------------- | ------------------------------------------------------------ |
| **Film**          | Œuvre du catalogue éditorial Urbinema                        |
| **Film vu**       | Film du catalogue validé (proposé puis marqué vu)            |
| **Pays**          | Origine géographique associée à une œuvre                    |
| **Continent**     | Regroupement géographique de pays                            |
| **Décennie**      | Période de dix années déterminée à partir de l'année du film |
| **Époque**        | Regroupement temporel plus large                             |
| **Genre**         | Catégorie de récit ou de forme. Un film en a zéro à plusieurs |
| **Caractéristique cinématographique** | Mouvement, courant, style, période, école ou vague éditoriale. Un film en a zéro à plusieurs |
| **Poids**         | Valeur intrinsèque d'un film dans le parcours cinéphile, utilisée par le calcul du rang |
| **Diversité**     | Étendue des territoires parcourus |
| **Profondeur**    | Degré d'approfondissement d'un même territoire |
| **Collection**    | Ensemble éditorialisé de films autour d'un thème             |
| **Quête**         | Objectif hebdomadaire Bronze, Argent ou Or donnant de l'XP   |
| **XP**            | Expérience : 10 par film unique (essai) + quêtes 100/250/500 |
| **Niveau**        | Progression ludique de 1 à 50, indépendante du rang          |
| **Rang**          | Identité cinéphile de l'utilisateur à un instant T (1 à 10) : un état d'esprit, pas un volume de films. Évolue très lentement. Cœur du produit |
| **Badge**         | Accomplissement débloqué dès qu'une condition précise est remplie. Cumulable, potentiellement des centaines |
| **Exploration**   | Progression de l'utilisateur dans une catégorie              |
| **Atlas**         | Listes filtrables des territoires (icône liste, TalkBack)    |
| **Carte**         | Onglet central : ciel interactif (autour d’un film / calques) |
| **Zone explorée** | Élément pour lequel l'utilisateur a satisfait la condition minimale d'exploration |

------

# 24. Questions et décisions à prendre

Cette section regroupe volontairement les éléments qui doivent être décidés avant la rédaction des cas d'utilisation détaillés.

## 24.1. Modèle de contenu

**Tranché :**

- catalogue V1 fermé, de taille **N** croissante (centaine au départ, puis milliers), pas de TMDb **dans l’app**, pas journal de visionnage personnel (§5.0) ;
- zéro à plusieurs caractéristiques cinématographiques par film, avec un type éditorial (§5.7) ;
- zéro à plusieurs genres par film, liste V1 définie (§5.6) ;
- un à plusieurs pays par film, avec exactement un pays principal (§5.2) ;
- réalisateurs en relation N–N (§5.9) ;
- **une seule année de référence**, choisie à l'import et figée ensuite (§5.4) ;
- époques définies par bornes de dates, dans un fichier dédié à venir (§5.5) ;
- durée en minutes et format explicite SHORT / MEDIUM / FEATURE / EXTENDED ;
- titres original et français, synopsis, images locales ;
- chaque film porte un **poids** (§5.1, §9.4).

Encore ouvert :

- règles précises d'attribution des quatre composantes du poids d'un film ;
- bornes des époques ;
- choix éditoriaux de rattachement des pays transcontinentaux.

------

## 24.2. Collections

**Tranché (0.1.10) :** pack actuel **15 collections** (cible 20), ordonnées par
un numéro éditorial et un `track`. **Initiation** en tête, toujours ouverte.
Cadenas Initiation : collection **suivie** et ≥ 1 film Vu. Cadenas **entre groupes** :
2 collections commencées (2 films vus) dans le palier précédent. **Cliquet** :
un palier ouvert reste ouvert. Progression affichée et titres dorés **seulement
si la collection est suivie**. À 100 % : félicitations, sortie des « en cours »,
bouton figé, check. Pas de badge automatique à la complétion.

Encore ouvert : règles éditoriales des collections restantes jusqu’à 20.

------

## 24.3. Progression

**Tranché :** 10 rangs, nommés provisoirement et décrits (§9.3). La formule est
arrêtée et paramétrable (§9.4). Les rangs 8 à 10 restent quantitatifs en V1 et
le rang 10 demande un parcours quasi exhaustif. Le rang ne redescend jamais.

XP et niveaux : 50 niveaux, indépendants du rang, obtenus par les quêtes
**et 25 XP** quand le film marqué Vu appartient à une collection suivie. Courbe : `FORMULE_NIVEAUX_XP.txt`.

Encore ouvert :

- calibrage des seuils du rang sur des profils réels ;
- ajustement de la courbe XP après usage.

------

## 24.4. Badges

**Tranché :** liste plate, cumulable, sans lien avec le rang. Première fournée
de 32 badges. Code métier stable, difficulté 1 à 5, règle dans le code, image
locale. Tous les badges sont visibles (non obtenus en N&B) et un badge obtenu
ne se perd jamais. Liste triée par difficulté puis `code`. Profil : jusqu’à
**3 badges** choisis. La V1 affiche sa difficulté éditoriale, pas une rareté
statistique entre utilisateurs.

------

## 24.5. Quêtes

**Tranché :** trois quêtes hebdomadaires — Bronze 100 XP, Argent 250 XP,
Or 500 XP. Pool de **50** types (16 Bronze, 17 Argent, 17 Or). Tirage
aléatoire parmi les quêtes encore faisables. Renouvellement lundi 02:00,
aucune rétroactivité.

Encore ouvert : enrichir le pool ; calibrer après usage.

------

## 24.6. Atlas et carte

**Tranché :** l’onglet **Atlas** ouvre les **listes** (décision 72, amende 70).
Carte du ciel = icône étoiles. Vue ciel : constellation autour d’un film.
Puces = calques territoires. Zoom max 14. Tap film = recentrer ; tap
territoire = feuille + fiche. XP film = **25**, seulement si une collection suivie contient ce film (0.3.0).

Encore ouvert : calibrage après test (labels, densité, 25 XP en collection suivie vs quêtes).

------

## 24.7. Historique

**Tranché :** pas d'import Letterboxd / SensCritique / historique externe en V1.
L'historique Accueil affiche des **titres de films**, jamais les codes
éditoriaux. `watchedOn` = date locale du téléphone.

Encore ouvert :

- modification a posteriori d'une date de visionnage déjà enregistrée ;
- calendrier au moment du Vu (aujourd'hui : date du jour uniquement).

------

## 24.8. Administration

**Tranché V1 :** pas de CMS web. Source JSON versionnée, validée par un outil
d'import qui produit une base Room préchargée dans les assets.
« Admin » = auteur du catalogue.

Encore ouvert :

- Comment pousser un nouveau pack sur un téléphone déjà en progression ?
- Comment gérer une modification d'une collection déjà complétée ?
- Comment corriger une erreur éditoriale sans casser la progression passée ?

------

## 24.9. Produit

**Tranché V1 :** un utilisateur, profil local privé, pas de social, pas de classement. Gratuit pour soi (APK). Pas de pub.

Encore ouvert (seulement si un jour store / amis payants) :

- modèle économique éventuel beaucoup plus tard.

------

# Conclusion

Urbinema a pour ambition de transformer le cinéma en **territoire d'exploration**.

L'utilisateur ne cherche pas simplement à accumuler des films vus. Il construit progressivement une carte personnelle de ses découvertes :

- des pays ;
- des continents ;
- des décennies ;
- des genres ;
- des caractéristiques cinématographiques ;
- des collections ;
- des œuvres.

La progression est matérialisée par :

> **les quêtes et le niveau/XP** (progression régulière), **les collections et
> les badges** (accomplissements), et, au-dessus de tout, **le rang** (identité
> cinéphile)

et représentée visuellement par :

> **une carte cinématographique progressivement explorée.**

Le système doit toujours rester au service d'un objectif fondamental :

> **donner envie de découvrir ce que l'on ne connaît pas encore.**

À court terme, Urbinema doit rester suffisamment simple pour être réalisable :
films, catégories, progression, collections, badges, quêtes, statistiques et
premier Atlas.

À long terme, le produit peut évoluer vers une véritable **cartographie interactive du cinéma mondial**, intégrant les mouvements, les périodes, les pays, les réalisateurs, les artistes, les films et les relations qui les unissent, puis vers des fonctionnalités de transmission culturelle, d'analyse et de personnalisation.

L'ambition finale n'est pas de déterminer qui est le meilleur cinéphile.

Elle est de permettre à chaque utilisateur de visualiser et d'étendre **son propre voyage à travers le cinéma**.