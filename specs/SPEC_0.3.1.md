# Spec v0.3.1 Urbinema

Le fichier de spec est découpé en 3 parties, une partie "Retour" qui correspond à fixe des bugs de la version 0.2.7 en cours. Une partie "Ajouts" qui correspond à des nouvelles fonctionnalités/amélioration de l'application etc.. Et une partie "Ajout data" qui correspond à un ajout de films, de collections, etc etc...

Tout ce qui va être données/catalog etc.. Dès le début, crée un "catalog_v3.json" à partir du catalog_v2.json, qui sera la prochaine version des bases.

Ca va sans dire qu'à CHAQUE fois que tu traites un tiret (donc un sujet à part entière, qu'il soit court ou long), tu vérifies tous les CAHIERS et toutes les specs et listes fonctionnelles que tout est toujours corrects, cohérent, que tout est écrit, tout est vrai dans les specs et cahier des charges techniques/fonctionnelles/IHM/Dev.

### Retour  0.2.7 (livré en 0.2.8) :

- [x] Créer un catalog_v3.json copie de catalog_v2.json
- [x] Supprimer tous les doublons dans catalog_v3.json (même titre, même année, même réal) — pack **20**, 1429 → **1383** films, 46 alias (OLDBOY_2003 → OLD_BOY_2003). La Condition de l’homme II est conservée. catalog_v2.json n’a pas été modifié.
- [x] Ciné-club : vérifié — bug réel (chevauchement Initiation ∩ Nouvel Hollywood) ; le palier demande maintenant **suivre** + 2 films
- [x] Démarrage / fluidité : snapshot catalogue unique + debounce des refresh UI
- [x] Limite de 10 collections en cours (`MAX_IN_PROGRESS_COLLECTIONS`) + popup
- [x] Carte du ciel en light theme : fond papier + liste aux tokens du thème  

### Ajouts 0.3.1 :

- [x] Gagner de l'xp quand on regarde un film SEULEMENT quand on regarde un film d'une collection qu'on suit (25 XP, au moment du marquage, sans rattrapage).
- [x] Ça serait tellement bien dans une collection (collection, liste de pays, liste de genres etc... Tout ce qui contient une liste de films) de pouvoir rester appuyer sur un film et ça te propose de le marquer en Vu.  
- [x] Je veux le truc des lettres sur le côté droit pour la liste des courants, pays, genres et réalisateurs aussi. Sans lettre en doré etc.. Juste en blanc simple partout. 
- [x] Rangs beaucoup trop souples au démarrage : formule v0.3.1 lissée après un test réel jusqu'au rang 10. Le volume devient `1,02 × ln(1 + Vw / 25)` et la diversité effective `Dmax × (D / Dmax)^1,2`. Les premiers films ne captent plus l'essentiel du score, tandis que le volume vers 1 100 films et la valeur d'une diversité complète sont conservés. Le score commence strictement à zéro film = zéro point. Seuils 2→10 recalibrés : `1,80 / 3,00 / 4,20 / 5,40 / 6,60 / 7,80 / 9,20 / 10,80 / 12,50`. Implémentation et tests dans `RankEngine`, détail dans `FORMULE_MATHEMATIQUE.txt`.
- [x] Films courts dans le rang : la durée pondère les trois axes pour éviter qu'une vue primitive d'une minute rapporte 171 points. Ancrages centralisés dans `RankDurationDefaults` : `1–10 min ×0,10`, `15 min ×0,15`, `20 min ×0,20`, interpolation jusqu'à `30 min ×1`, puis plein tarif. L'exposition cumulée remplace le comptage entier pour diversité et profondeur.
- [x] Sécuriser « Réinitialiser les données » : dialogue FR/EN explicite et irréversible, confirmation désactivée pendant 10 secondes avec compteur `(10)` → `(1)`, puis « Confirmer » / “Confirm”.
- [x] Retour 0.3.3 — félicitation de badge : afficher la petite illustration du badge sous le message.
- [x] Retour 0.3.3 — cartes film : afficher jusqu'à deux réalisateurs, un par ligne, puis `...`, sans écraser le titre.
- [x] Retour 0.3.3 — badges vitrine du Profil : un appui long affiche la condition d'obtention.
- [x] Retour 0.3.3 — titres : pack 42. Titres FR/VO tranchés ; 014 et 015 en titre unique (`Vérités et mensonges`, `Je, tu, il, elle`). Les derniers cas (Jeanne Dielman, Twin Peaks FWWM, Doom Generation, El club) conservent VO et VF. Le batch refuse les titres alternatifs `BE` / `CH`.
- [x] Ajouter une page quand on ouvre l'appli pour la première fois (comme il y a actuellement pour choisir le pseudo etc.. Juste après avoir choisir photo/pseudo/age) pour expliquer rapidement comment fonctionne l'appli, ce qu'on peut trouver sur chaque onglet etc..), en mode carroussel, 1er page du caroussel une explication rapide, 2ème page la page home, 3ème page la page atlas, 4eme page la page collections, 5eme page la future page parcours, 6eme page la page profile. Et ce petit "tuto" doit être visible dans les settings dans un bouton aide ou autre. Le panneau est à la taille du texte (environ un tiers de l’écran), le reste est fortement flouté.
- [x] Ajouter une page "source" genre œuvre/sites/articles etc. Dans les settings, peut-être un mini bouton discret sous les crédits actuels ou un texte cliquable même pas un bouton (genre "Voir toutes les sources"). L'idée est de citer toutes les sources utilisées pour la partie histoire/choix de films etc... Avec déjà pour commencer : 
  - Livres : 
    - "Le Cinéma Muet" de Pierre Allard. 
    - "100 classiques du cinéma" de Jurgen Muller. 
    - "100 films pour une cinémathèque idéale" de Claude Jean Philippe. 
  - Ajouter une phrase explicative. Découpé les sources en catégories "livres" / sites/etc.. Ajouter les sites que j'ai utilisé la dernière fois pour faire le catalog v3 (le top letterbox, le top roger ebbert, les sites que tu as utilisé etc etc...). Ajoutées ensuite : Sadoul et Breton, Karthala (cinéma africain), Ginsberg et Lippard, Pinel (Larousse), Thon 2008, KMDb, Cahiers du cinéma et Positif, dossiers BFI / liste CNN du cinéma asiatique, IMDb et SensCritique. Letterboxd et les archives de festivals y étaient déjà, le libellé les cite comme sources à part entière.
- [ ] Ajouter pour les quêtes une colonne boolean qui dit si la quête est possible ou non. Réfléchir à quand et comment l'alimenter (on ne peut pas check toutes les quêtes à chaque film vu), et peut-être un compteur pour que les quêtes qui tombent souvent aient moins de chance de tomber justement. **Reporté** : pas implémenté en 0.3.0. Le tirage hebdomadaire filtre déjà l’impossible une fois par semaine. Un scan à chaque film vu, et un compteur de fréquence, restent une idée pour plus tard (cahier fonctionnel + décision 78).
- [x] Sur la page Profil quand on appuie sur le logo de notre rang et que ça amène à la page où on voit tous les rangs en chaîne, il faudrait que ça amène direct à la position de notre rang 
- [x] Ajouter bien sûr un message qui dit quand a gagné un rang avec des confettis etc !
- [x] Splash au démarrage : logo de l’app sur fond blanc plein écran pendant le chargement du catalogue (plus « Votre aventure commence ici »). En thème sombre le fond suit le thème.
- [ ] Logo de splash plus propre (PNG détouré) pour qu’il tienne aussi bien sur fond sombre que sur fond clair.  
- [x] Préparer les fiches réalisateur. Fait, pack **26**. La fiche montre le nom, un portrait (120 dp, plus petit qu’une affiche) et la biographie, puis les collections et les films. Portraits dans `assets/media/directors/{CODE}.jpg`. Batch `batchsData/batchReals` (et `batchPosters` déplacé dans `batchsData/`). 742 photos, 728 bios, sur 804 réalisateurs. Room v8, colonne `directors.biography`. (actuellement sur un réal on voit sa liste de films, ajouter maintenant une bio pour chaque réalisateur/réalisatrice, ainsi qu'un petit emplacement (un peu plus petit que les affiches) pour les photos des réals. Aussi, bien évidemment, il faut ABSOLUMENT un moyen de télécharger une image pour TOUS les réalisateurs. Si possible avec l'API TMDB parfait ! Sinon, une autre façon. Crées un répertoire "batchsData", où tu vas mettre dedans le batchPosters, et tu créeras maintenant un batchReals, qui comme tu t'en doutes, à partir d'une liste de nom/prénom de réal, va venir télécharger une image de chacun d'entre eux (fichier input) et les mettre comme dab dans le dossier output. Ecris ce batch, teste le et mets les photos des reals de output dans le bon endroit dans le projet "media/directors" j'imagine un truc comme ça, pour qu'ils s'affichent sur l'appli.
- [x] Collection « Cinéma des premiers temps ». Fait, pack **27**, groupe Premières séances, 17 films (1892–1906). Onze films et leurs affiches ajoutés ; les films déjà au catalogue sont seulement reliés. La Fée aux choux est la fiche 1896 d’Alice Guy ; la fiche 1900, simple remaster, a été retirée.
- [ ] Il faudrait vraiment un moyen de lier des collections entre elles ! Par exemple, pour voir "post-nouvel hollywood", il faudrait avoir vu 5 films dans "nouvel hollywood" ET 5 films de "âge d'Or Hollywood" ! Des trucs comme ça ! Ou pour débloquer "cinéma muet" avoir vu 7 films dans "Cinéma des premiers temps". Ou pour âge d'or japonais et japon - 70s. A tester, essaye d'implémenter quelque chose comme ça ! Pouvoir mettre des conditions sur chaque collections d'autres collections etc.. J'imagine qu'il faudra sûrement ajouter une colonne en base, sauf s'il y a une autre façon de le faire. Une classe "CollectionsRule" qui implémente toutes les règles des collections de l'appli. Et pense dès maintenant que peut-être plus tard on voudra bloquer une collection si on a pas vu UN film précis en particulier (pas d'idées pour l'instant mais soyons fous !). Je te laisse implémenter ça de la meilleure façon possible, et surtout tu mettras bien dans les SPECS tout ce que tu as fais, dans la spec DEV tu expliqueras en détail comment tu as implémenté ça et comment ajouter/modifier les règles. Et notamment là il y a 2 nouvelles collections sur le ciné expérimental, je veux que la collection "Cinéma Expérimental et Formel" se débloque après avoir vu 5 films de la catégorie "Cinéma Surréaliste et Onirique". 
- [x] Nouveauté principale : Nouvelle page "Parcours" (parcours 1, pack 38, Room 10). L'ancien écran rang/quêtes est commenté dans `UrbinemaApp.kt`. Mode d'emploi : spec dev §6.4. L'onglet parcours actuel "4ème onglet" pourra peut-être mixé avec les pages Home et Profile, à voir plus tard, pour l'instant garde le en commentaire quelque part (et bien commenter genre ancien onglet parcours etc..) pour ne pas qu'on perde tout (si tu as une idée de nouvel affichage d'ailleurs GO hein, j'aimerais bien que tu proposes, tant que tu peux revenir en arrière sur l'état actuel si je n'aime pas ça me va). L'objectif de cet onglet est purement pédagogique, théorique. Le but n'est pas de marquer de nouveaux films en "Vu", mais simplement d'en apprendre plus sur des pans du cinéma. L'idée va donc être de faire des "parcours", qui vont être basés sur les courants (courants et pas collection !) de l'appli, et qui vont ajouter du contexte historique. Pour voir la liste de parcours à implémenter, voir le fichier "Liste_Des_Parcours" dans le sous-répertoire "Listes fonctionnelles" de "spec". Pour le moment, implémenter uniquement le parcours 1 ("comment le cinéma est devenu un art" un truc comme ça). Comme tu le verras, un parcours est constitué tout d'abord d'une description détaillée du parcours. Ensuite, une liste de courants qui seront des genres de bulles, liées entre elles comme dans Artly par un simple trait, ou pas des flèches. Au niveau de ces flèches il y aura soit du texte (Transitions), soit une icone point d'interrogation (?), et quand on clique dessus le texte de la Transition apparaît. Le parcours fléchés ou similaire sera bien sûr scrollable, de haut en bas, pour défiler les bulles (courants) de la première à la dernière (donc pour le parcours 1 par exemple, la première sera bien sûr "cinéma muet" et la dernière sera "Cinéma contemporain"). Pour les bulles (courants), on aura un rond avec un dessin représentant le courant, et le nom du courant juste en-dessous. Un dessin exemple est enregistré dans "specs\assets" au nom de "parcours_1_flow.png". Le rendu sera bien sûr très différent, avec un scroll de haut en bas, sûrement une seule bulle par niveau etc... Mais c'est pour avoir une idée de la représentation des bulles, avec des dessins pour les bulles qui ressembleront à ça. De plus, il faudra du coup créer dans les assets/medias/ un nouveau dossier pour les courants. Tout ça tu le mettras bien dans toutes les SPECS hein, fonctionnelles techniques ihm dev etc.... Ensuite, en cliquant sur un courant/une bulle, une nouvelle fiche s'affiche, une pop-up (donc qui ne recouvre pas tout l'écran, une bonne partie mais pas tout). Cette nouvelle fiche courant affichera une période (année début et année fin), à afficher en-dessous du titre du courant, une description, et ensuite une liste de "A savoir" (2-3 max en général, petite liste à afficher), et ensuite quelques figures clés et films clés, qui quand on clique sur eux renvoi vers la page réal s'il existe ou la page film de l'application (si le film n'existe pas le créer). Point TRES important également, à chaque fois que dans les films des courants je cite un film qui n'existe PAS dans l'appli, ajoute le direct dans le fichier input des films à télécharger. Tu trouveras également dans "Transitions" le texte de toutes les transitions entre les bulles/courants. Et évidemment, avant de cliquer sur le parcours 1 il faut un écran qui répertorie les différents parcours, mais je veux que ça fasse plus stylé et moderne que pour les collections actuelles, genre pas des trucs simples rectangulaires comme pour les collections actuelles.

### Ajouts data :

-  [x] Ajouter des quêtes de "courant" (ex : "Voir 1 Giallo"). De courant je dis bien, pas de collection. Fait : 9 quêtes (bronze Giallo, Dogme 95, jidai-geki ; argent néoréalisme, expressionnisme, western spaghetti ; or surréalisme, âge d'or japonais, cinéma soviétique). Pack 21, 59 quêtes (19 / 20 / 20).

-  [x] Nombre de films discret : à droite des lignes Atlas (pays, courant, décennie, genre, réalisateur), sans le pourcentage de vus. Section Films d’une fiche (territoire, collection, réalisateur, feuille de la carte). Pas sur les cartes de la liste Collections.

-  [x] Ajout de films par pays dans les pays avec peu de films. Fait jusqu’à l’Éthiopie, pack **23**, **1453** films. Pas de doublon quand l’œuvre était déjà là (Véronique, Trois couleurs : Rouge, et avant ça Quartier Mozart, Timbuktu, Soleil Ô). « Quand la Saint-Jean arrive » est enregistré sous « Quand viendra le mois d’octobre ». Synopsis : les vides ont été remplis quand la fiche TMDB est le même film ; 11 restent vides. 

   -  France :
      -  *Cœur fidèle* (1923) – Jean Epstein
      -  *La Glace à trois faces* (1927) – Jean Epstein
   -  Norvège :
      -    Le Rescapé - 1957 - Arne Skouen
      -    La Chasse - 1959 - Erik Løchen
      -    La Faim - 1966 - Henning Carlsen
      -    Edvard Munch - 1974 - Peter Watkins
      -    Grand Prix Pignon-sur-Roc - 1975 - Ivo Caprino
      -    Le Passeur - 1987 - Nils Gaup
      -    Insomnia - 1997 - Erik Skjoldbjærg
   -  Autriche :
      -  Sissi - 1955 - Ernst Marischka
      -  Angst - 1983 - Gerald Kargl
      -  Le Septième Continent - 1989 - Michael Haneke
      -  Benny's Video - 1992 - Michael Haneke
      -  Dog Days - 2001 - Ulrich Seidl
   -  Belge :
      -  Je vous parle d'un temps... - 1934 - Henri Storck et Joris Ivens
      -  Malpertuis - 1971 - Harry Kümel
      -  Les Lèvres rouges - 1971 - Harry Kümel
      -  Vase de noces - 1974 - Thierry Zéno
   -  Cameroun :
      -  Muna Moto - 1975 - Jean-Pierre Dikongué Pipa
      -  Quartier Mozart - 1992 - Jean-Pierre Bekolo
      -  Sango Malo - 1991 - Bassek Ba Kobhio
      -  Chef ! - 1999 - Jean-Marie Teno
      -  Les Saignantes - 2005 - Jean-Pierre Bekolo
   -  Corée du Sud :
      -  Sweet Dream - 1936 - Yang Ju-nam
      -  Aimless Bullet - 1961 - Yoo Hyun-mok
      -  Ieodo - 1977 - Kim Ki-young
      -  Pourquoi Bodhi-Dharma est-il parti vers l'Orient ? - 1989 - Bae Yong-kyun
      -  3-Iron - 2004 - Kim Ki-duk
   -  Egypte :
      -  La Volonté - 1939 - Kamal Selim
      -  La Terre - 1969 - Youssef Chahine
   -  Estonie :
      -  The Last Relic - 1969 - Grigori Kromanov
      -  November - 2017 - Rainer Sarnet
   -  Cambodge :
      -  La Joie de vivre - 1969 - Norodom Sihanouk
   -  Bolivie :
      -  La Nation clandestine - 1989 - Jorge Sanjinés
      -  Chuquiago - 1977 - Antonio Eguino
   -  Angola :
      -  Nelisita - 1982 - Ruy Duarte de Carvalho
      -  O Herói - 2005 - Zézé Gamboa
      -  Air Conditioner - 2020 - Fradique
   -  Finlande :
      -  Le Renne blanc - 1952 - Erik Blomberg
      -  Les Indignes - 1982 - Mika Kaurismäki
      -  Ombres au paradis - 1986 - Aki Kaurismäki
   -  Grèce :
      -  L'Ogre d'Athènes - 1956 - Nikos Koundouros
      -  Stella - 1955 - Michael Cacoyannis
   -  Lettonie :
      -  Quatre chemises blanches - 1967 - Rolands Kalniņš
      -  Flow - 2024 - Gints Zilbalodis
   -  Liban :
      -  Vers l'inconnu ? - 1957 - Georges Nasser
      -  Beyrouth ô Beyrouth - 1975 - Maroun Bagdadi
      -  Hors la vie - 1991 - Maroun Bagdadi
   -  Lituanie :
      -  La Fille à l'écho - 1964 - Arūnas Žebriūnas
      -  Personne ne voulait mourir - 1965 - Vytautas Žalakevičius
      -  Corridor - 1995 - Šarūnas Bartas
      -  The Excursionist - 2013 - Audrius Juzėnas
   -  Mauritanie :
      -  Soleil Ô - 1969 - Med Hondo
      -  Timbuktu - 2014 - Abderrahmane Sissako
   -  Nouvelle-Zélande :
      -  Utu - 1983 - Geoff Murphy
      -  Vigil - 1984 - Vincent Ward
   -  Pays-Bas :
      -  L'Agression - 1962 - Paul Rotha
      -  L'Homme qui voulait savoir - 1988 - George Sluizer
   -  Pologne :
      -  La Double Vie de Véronique - 1991 - Krzysztof Kieślowski
      -  Trois Couleurs : Blanc - 1994 - Krzysztof Kieślowski
      -  Trois Couleurs : Rouge - 1994 - Krzysztof Kieślowski
      -  Ida - 2013 - Paweł Pawlikowski
   -  Roumanie :
      -  La Forêt des pendus - 1965 - Liviu Ciulei
      -  Baccalauréat - 2016 - Cristian Mungiu
   -  Tchad :
      -  Bye Bye Africa - 1999 - Mahamat-Saleh Haroun
      -  Daratt - 2006 - Mahamat-Saleh Haroun
      -  Lingui, les liens sacrés - 2021 - Mahamat-Saleh Haroun
   -  Tunisie :
      -  L'Homme de cendres - 1986 - Nouri Bouzid
      -  Les Filles d'Olfa - 2023 - Kaouther Ben Hania
   -  Ukraine :
      -  Le Syndrome asthénique - 1989 - Kira Mouratova
      -  The Tribe - 2014 - Myroslav Slaboshpytsky
   -  Vietnam :
      -  Quand la Saint-Jean arrive - 1984 - Đặng Nhật Minh
      -  L'Arbre aux papillons d'or - 2023 - Phạm Thiên Ân
   -  Zimbabwe :
      -  Jit - 1990 - Michael Raeburn
      -  Neria - 1991 - Godwin Mawuru
   -  Ethiopie :
      -  Qui est le père d'Hirut ? - 1965 - Ilala Ibsa
      -  Crumbs - 2015 - Miguel Llansó

-  [x] Ajouter plusieurs collections et ajouter les films des collections qui ne sont actuellement pas dans le catalog_v3. Fait, pack **24**, **1527** films, **27** collections. Les œuvres déjà au catalogue ont été reliées, pas dupliquées. Cinéma muet : films ≤ 1906 retirés de la collection seulement ; Fantômas (1913) et Les Vampires ajoutés ; texte long réécrit sans Méliès. Hitchcockiens s’appelle déjà « Hitchcock — Le suspense comme forme ». Neuf collections ajoutées sous le titre de Liste_Collections&Films.md (Âge d’or hongkongais, pas le surnom « Nouvelle Vague hongkongaise »), films par année croissante. Les mauvaises fiches TMDB (autre Secret, autre Club, autre Nomad, La Chute de l’Empire romain) n’ont pas été prises ; Empire de Warhol a le code EMPIRE_WARHOL_1964. Courant ajouté : Cinéma documentaire (style), distinct du genre Documentaire. Pas de règles de déblocage entre collections. TOUT est listé dans le fichier "Liste_Collections&Films.md". ALORS, point important avant de se retrouver avec 1000 doublons, ce fichier "Liste_Collections&Films.md" liste TOUTES les collections et leurs films associés. Donc évidemment une grande partie existent déjà, TOUTEFOIS, certains collections ont été modifées (le "rang" (difficulté), ou même certains films en plus/en moins). Je vais quand même essayer de tout te lister en-dessous pour te faciliter le taff, mais fais quand même un deuxième check après entre le fichier et le catalog_v3 (copie de catalog_v2 je rappelle). Ensuite, évidemment tu vas créer tous ces nouveaux films en base (dans le catalog_v3 quoi), mais tu penseras BIEN aussi à jouer le batchPosters sur ces films, en les ajoutant dans le input à ceux déjà présents, en faisant tourner le batch, une fois le batch terminé en copiant TOUTES les affiches de "output" dans media/posters comme dab, à vider le fichier "input" SAUF pour les films où l'affiche n'a pas été trouvé, n'a pas été récupéré etc.. Bref comme dab quoi. Liste des collecs :

  - Collections modifiées :

    - Cinéma muet : Supprimer les films en/avant 1906. Modifier également la description pour ne plus faire référence à Melies et la lune (car il n'y a plus "un voyager vers la lune") et les années. Ajout de "Les Vampires" et "Fantomas".
    - Hitchcockiens : Renommer la collection en "Hitchcock — Le suspense comme forme", ça a plus de sens.
  
- [x] Collections à ajouter :
  
  *(PS: pour les nouvelles collections, il y a tout d'abord le titre de la collection, une description courte pour la données "description" et une description plus longue pour la données "longDescription". Et ensuite bien sûr la liste des films. Pour connaître le rang/difficulté de la collection, je les ai rangé dedans à chaque fois, donc "premières séances", toutes les collections de rang 1, puis "ciné-club", toutes les collections de rang 2 etc...)*
    *(PS2: Pour chaque film j'ai mis le réal pour t'aider à trouver les films, mais une fois tous les films ajoutés/créés tu peux retirer les noms de réals pour garder les mêmes format des autres collections)*
  
  *(PS3: Des fois les titres sont en VF, d'autres fois en VO, de toute façon tu ajouteras bien les titres en français et en VO comme dab)*
  
  - Post-néoréalisme Italien, rang : Cinémathèque
  
  - Nouvelle Vague Tchécoslovaque, rang : Cinémathèque
  
  - Cinéma Chinois - Cinquième Génération : rang : Cinémathèque
  
  - Nouvelle Vague hongkongaise : rang : "Salle Obscure"
  
  - Free Cinema Britannique : rang : "Ciné-Club"
  
  - Cinéma Documentaire : rang : "Cinémathèque"
  
  - post-Nouvel Hollywood : rang : "Salle Obscure"
  
  - Cinéma Surréaliste et onirique : rang : "Salle Obscure"
  
  - Cinéma Expérimentale et formel : rang "Hors-champ"
  
- [x] Note Importante pour les nouvelles Collections (et les autres aussi d'ailleurs) : Bien vérifier que la liste de films et la description (courte et surtout longue) sont en adéquation ! Les textes des neuf collections citaient encore des réalisateurs présents dans les listes. Seul le texte long du cinéma muet a été réécrit.



Rappel, mettre à jour TOUTES LES SPECS A CHAQUE MODIFS !! ET INCREMENTER LE NUMERO DE VERSION !!!
