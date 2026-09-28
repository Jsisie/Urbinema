# Spec v0.3.1 Urbinema

Le fichier de spec est découpé en 3 parties, une partie "Retour" qui correspond à fixe des bugs de la version 0.2.7 en cours. Une partie "Ajouts" qui correspond à des nouvelles fonctionnalités/amélioration de l'application etc.. Et une partie "Ajout data" qui correspond à un ajout de films, de collections, etc etc...

Tout ce qui va être données/catalog etc.. Dès le début, crée un "catalog_v3.json" à partir du catalog_v2.json, qui sera la prochaine version des bases.

Ca va sans dire qu'à CHAQUE fois que tu traites un tiret (donc un sujet à part entière, qu'il soit court ou long), tu vérifies tous les CAHIERS et toutes les specs et listes fonctionnelles que tout est toujours corrects, cohérent, que tout est écrit, tout est vrai dans les specs et cahier des charges techniques/fonctionelles/IHM/Dev.

### Retour  0.2.7 (livré en 0.2.8) :

- [x] Créer un catalog_v3.json copie de catalog_v2.json
- [x] Supprimer tous les doublons dans catalog_v3.json (même titre, même année, même réal)
- [x] Ciné-club : vérifié — bug réel (chevauchement Initiation ∩ Nouvel Hollywood) ; le palier demande maintenant **suivre** + 2 films
- [x] Démarrage / fluidité : snapshot catalogue unique + debounce des refresh UI
- [x] Limite de 10 collections en cours (`MAX_IN_PROGRESS_COLLECTIONS`) + popup
- [x] Carte du ciel en light theme : fond papier + liste aux tokens du thème  

### Ajouts 0.3.1 :

- [ ] Gagner de l'xp quand on regarde un film SEULEMENT quand on regarde un film d'une collection qu'on suit (mais gagner plus, genre 20 ou 30xp). J'ai essayé d'ajouter une variable currentMovie dans la function rewardForFilm(), mais je n'ai pas trouvé comment savoir si on avait vu le film ou non une fois la variable en paramètre de la fonction. Donc à faire.
- [ ] Ça serait tellement bien dans une collection (collection, liste de pays, liste de genres etc... Tout ce qui contient une liste de films) de pouvoir rester appuyer sur un film et ça te propose de le marquer en Vu.  
- [ ] Je veux le truc des lettres sur le côté droit pour la liste des courants, pays, genres et réalisateurs aussi. Sans lettre en doré etc.. Juste en blanc simple partout. 
- [ ] Rangs beaucoup trop souples, on devient rang 3 ultra rapidement avec seulement 9 films. Voir comment on peut solutionner ça... Mettre un peu plus de poids sur le nombre de films vu je pense, pour commencer. Qualité > Quantité je suis 100% d'accord, mais il faut pas non plus gagner 2 rangs en ayant juste vu 5 films de 5 pays et 5 époques différentes quoi. Mais là avec 129 films je suis rang 6, ça me paraît un peu trop. 
- [ ] Ajouter une page quand on ouvre l'appli pour la première fois (comme il y a actuellement pour choisir le pseudo etc.. Juste après avoir choisir photo/pseudo/age) pour expliquer rapidement comment fonctionne l'appli, ce qu'on peut trouver sur chaque onglet etc..), en mode carroussel, 1er page du caroussel une explication rapide, 2ème page la page home, 3ème page la page atlas, 4eme page la page collections, 5eme page la future page parcours, 6eme page la page profile. Et ce petit "tuto" doit être visible dans les settings dans un bouton aide ou autre.
- [ ] Ajouter une page "source" genre œuvre/sites/articles etc. Dans les settings, peut-être un mini bouton discret sous les crédits actuels ou un texte cliquable même pas un bouton (genre "Voir toutes les sources"). L'idée est de citer toutes les sources utilisées pour la partie histoire/choix de films etc... Avec déjà pour commencer : 
  - Livres : 
    - "Le Cinéma Muet" de Pierre Allard. 
    - "100 classiques du cinéma" de Jurgen Muller. 
    - "100 films pour une cinémathèque idéale" de Claude Jean Philippe. 
  - Ajouter une phrase explicative. Découpé les sources en catégories "livres" / sites/etc.. Ajouter les sites que j'ai utilisé la dernière fois pour faire le catalog v3 (le top letterbox, le top roger ebbert, les sites que tu as utilisé etc etc...)
- [ ] Ajouter pour les quêtes une colonne boolean qui dit si la quête est possible ou non. Réfléchir à quand et comment l'alimenter (on ne peut pas check toutes les quêtes à chaque film vu), et peut-être un compteur pour que les quêtes qui tombent souvent aient moins de chance de tomber justement
- [ ] Il faudrait vraiment un moyen de lier des collections entre elles ! Par exemple, pour voir "post-nouvel hollywood", il faudrait avoir vu 5 films dans "nouvel hollywood" ET 5 films de "âge d'Or Hollywood" ! Des trucs comme ça ! Ou pour débloquer "cinéma muet" avoir vu 7 films dans "Cinéma des premiers temps". Ou pour âge d'or japonais et japon - 70s. A tester, essaye d'implémenter quelque chose comme ça ! Pouvoir mettre des conditions sur chaque collections d'autres collections etc.. J'imagine qu'il faudra sûrement ajouter une colonne en base, sauf s'il y a une autre façon de le faire. Une classe "CollectionsRule" qui implémente toutes les règles des collections de l'appli. Et pense dès maintenant que peut-être plus tard on voudra bloquer une collection si on a pas vu UN film précis en particulier (pas d'idées pour l'instant mais soyons fous !). Je te laisse implémenter ça de la meilleure façon possible, et surtout tu mettras bien dans les SPECS tout ce que tu as fais, dans la spec DEV tu expliqueras en détail comment tu as implémenté ça et comment ajouter/modifier les règles. Et notamment là il y a 2 nouvelles collections sur le ciné expérimental, je veux que la collection "Cinéma Expérimental et Formel" se débloque après avoir vu 5 films de la catégorie "Cinéma Surréaliste et Onirique". 
- [ ] Nouveauté principale : Nouvelle page "Parcours". L'onglet parcours actuel "4ème onglet" pourra peut-être mixé avec les pages Home et Profile, à voir plus tard, pour l'instant garde le en commentaire quelque part (et bien commenter genre ancien onglet parcours etc..) pour ne pas qu'on perde tout (si tu as une idée de nouvel affichage d'ailleurs GO hein, j'aimerais bien que tu proposes, tant que tu peux revenir en arrière sur l'état actuel si je n'aime pas ça me va). L'objectif de cet onglet est purement pédagogique, théorique. Le but n'est pas de marquer de nouveaux films en "Vu", mais simplement d'en apprendre plus sur des pans du cinéma. L'idée va donc être de faire des "parcours", qui vont être basés sur les courants (courants et pas collection !) de l'appli, et qui vont ajouter du contexte historique. Pour voir la liste de parcours à implémenter, voir le fichier "Liste_Des_Parcours" dans le sous-répertoire "Listes fonctionnelles" de "spec". Pour le moment, implémenter uniquement le parcours 1 ("comment le cinéma est devenu un art" un truc comme ça). Comme tu le verras, un parcours est constitué tout d'abord d'une description détaillée du parcours. Ensuite, une liste de courants qui seront des genres de bulles, liées entre elles comme dans Artly par un simple trait, ou pas des flèches. Au niveau de ces flèches il y aura soit du texte (Transitions), soit une icone point d'interrogation (?), et quand on clique dessus le texte de la Transition apparaît. Le parcours fléchés ou similaire sera bien sûr scrollable, de haut en bas, pour défiler les bulles (courants) de la première à la dernière (donc pour le parcours 1 par exemple, la première sera bien sûr "cinéma muet" et la dernière sera "Cinéma contemporain"). Pour les bulles (courants), on aura un rond avec un dessin représentant le courant, et le nom du courant juste en-dessous. Un dessin exemple est enregistré dans "specs\assets" au nom de "parcours_1_flow.png". Le rendu sera bien sûr très différent, avec un scroll de haut en bas, sûrement une seule bulle par niveau etc... Mais c'est pour avoir une idée de la représentation des bulles, avec des dessins pour les bulles qui ressembleront à ça. De plus, il faudra du coup créer dans les assets/medias/ un nouveau dossier pour les courants. Tout ça tu le mettras bien dans toutes les SPECS hein, fonctionnelles techniques ihm dev etc.... Ensuite, en cliquant sur un courant/une bulle, une nouvelle fiche s'affiche, une pop-up (donc qui ne recouvre pas tout l'écran, une bonne partie mais pas tout). Cette nouvelle fiche courant affichera une période (année début et année fin), à afficher en-dessous du titre du courant, une description, et ensuite une liste de "A savoir" (2-3 max en général, petite liste à afficher), et ensuite quelques figures clés et films clés, qui quand on clique sur eux renvoi vers la page réal s'il existe ou la page film de l'application (si le film n'existe pas le créer). Point TRES important également, à chaque fois que dans les films des courants je cite un film qui n'existe PAS dans l'appli, ajoute le direct dans le fichier input des films à télécharger. Tu trouveras également dans "Transitions" le texte de toutes les transitions entre les bulles/courants. Et évidemment, avant de cliquer sur le parcours 1 il faut un écran qui répertorie les différents parcours, mais je veux que ça fasse plus stylé et moderne que pour les collections actuelles, genre pas un
- [ ] Sur la page Profil quand on appuie sur le logo de notre rang et que ça amène à la page où on voit tous les rangs en chaîne, il faudrait que ça amène direct à la position de notre rang 
- [ ] Ajouter bien sûr un message qui dit quand a gagné un rang avec des confettis etc !  
- [ ] Préparer les fiches réalisateur (actuellement sur un réal on voit sa liste de films, ajouter maintenant une bio pour chaque réalisateur/réalisatrice, ainsi qu'un petit emplacement (un peu plus petit que les affiches) pour les photos des réals. Aussi, bien évidemment, il faut ABSOLUMENT un moyen de télécharger une image pour TOUS les réalisateurs. Si possible avec l'API TMDB parfait ! Sinon, une autre façon. Crées un répertoire "batchsData", où tu vas mettre dedans le batchPosters, et tu créeras maintenant un batchReals, qui comme tu t'en doutes, à partir d'une liste de nom/prénom de réal, va venir télécharger une image de chacun d'entre eux (fichier input) et les mettre comme dab dans le dossier output. Ecris ce batch, teste le

### Ajouts data :

-  [ ] Ajouter des quêtes de "courant" (ex : "Voir 1 Giallo"). De courant je dis bien, pas de collection.

-  [ ] Ajouter de films par pays dans les pays avec peu de films : 

   -  France :
      -  *Cœur fidèle* (1923) – Jean Epstein
      -  *La Glace à trois faces* (1927) – Jean Epstein
   -  Norvège :
      -    

-  [ ] Ajouter plusieurs collections et ajouter les films des collections qui ne sont actuellement pas dans le catalog_v3. TOUT est listé dans le fichier "Liste_Collections&Films.md". ALORS, point important avant de se retrouver avec 1000 doublons, ce fichier "Liste_Collections&Films.md" liste TOUTES les collections et leurs films associés. Donc évidemment une grande partie existent déjà, TOUTEFOIS, certains collections ont été modifées (le "rang" (difficulté), ou même certains films en plus/en moins). Je vais quand même essayer de tout te lister en-dessous pour te faciliter le taff, mais fais quand même un deuxième check après entre le fichier et le catalog_v3 (copie de catalog_v2 je rappelle). Ensuite, évidemment tu vas créer tous ces nouveaux films en base (dans le catalog_v3 quoi), mais tu penseras BIEN aussi à jouer le batchPosters sur ces films, en les ajoutant dans le input à ceux déjà présents, en faisant tourner le batch, une fois le batch terminé en copiant TOUTES les affiches de "output" dans media/posters comme dab, à vider le fichier "input" SAUF pour les films où l'affiche n'a pas été trouvé, n'a pas été récupéré etc.. Bref comme dab quoi. Liste des collecs :

  - Collections modifiées :

    - Cinéma muet : Supprimer les films en/avant 1906. Modifier également la description pour ne plus faire référence à Melies et la lune (car il n'y a plus "un voyager vers la lune") et les années. Ajout de "Les Vampires" et "Fantomas".
    - Hitchcockiens : Renommer la collection en "Hitchcock — Le suspense comme forme", ça a plus de sens.
    - 

  - [ ] Collections à ajouter :

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

  - [ ] Note Importante pour les nouvelles Collections (et els autres aussi d'ailleurs) : Bien vérifier que la liste de films et la description (courte et surtout longue) sont en adéquation ! Car des fois j'ai modifié la liste des films et donc peut-être qu'un réal cité dans la description ne fais plur partie de la collection ! Donc bien vérifier à chaque fois, et adapter/refaire la description si besoin.



Rappel, mettre à jour TOUTES LES SPECS A CHAQUE MODIFS !! ET INCREMENTER LE NUMERO DE VERSION !!!

