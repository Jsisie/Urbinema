#!/usr/bin/env python3
"""Generate a CatalogPack JSON for Urbinema (catalog_v1.json)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "app" / "src" / "main" / "assets" / "catalog" / "catalog_v1.json"

VERSION = 11
GENERATED_AT = "2026-09-19T18:50:00Z"
REQUIRED_MOVIE_COUNT = 405
REQUIRED_MOVIE_CODES = {
    "SEPT_SAMOURAIS_1954",
    "ROMA_CITTA_APERTA_1945",
    "CLEO_DE_5_A_7_1962",
}
SCORE_OVERRIDES = {
    "SEPT_SAMOURAIS_1954": (0.72, 0.55, 0.95, 0.90),
    "ROMA_CITTA_APERTA_1945": (0.82, 0.48, 0.96, 0.86),
    "CLEO_DE_5_A_7_1962": (0.62, 0.50, 0.87, 0.82),
}
SYNOPSIS_OVERRIDES = {
    "SEPT_SAMOURAIS_1954": (
        "Des villageois engagent sept samouraïs pour protéger leur récolte. "
        "Une fresque sur la solidarité, le courage et le prix de la victoire."
    ),
    "ROMA_CITTA_APERTA_1945": (
        "Dans la Rome occupée, plusieurs destins se croisent autour de la Résistance."
    ),
    "CLEO_DE_5_A_7_1962": (
        "Deux heures dans la vie d'une chanteuse qui attend les résultats d'un examen médical."
    ),
}

CHARACTERISTIC_TYPES = [
    ("MOVEMENT", "Mouvement"),
    ("CURRENT", "Courant"),
    ("STYLE", "Style"),
    ("PERIOD", "Période"),
    ("SCHOOL", "École"),
    ("WAVE", "Vague"),
]

CONTINENTS = [
    ("EUROPE", "Europe"),
    ("ASIA", "Asie"),
    ("NORTH_AMERICA", "Amérique du Nord"),
    ("SOUTH_AMERICA", "Amérique du Sud"),
    ("AFRICA", "Afrique"),
    ("OCEANIA", "Océanie"),
]

COUNTRIES = [
    ("FRANCE", "France", "FR", ["EUROPE"]),
    ("ITALY", "Italie", "IT", ["EUROPE"]),
    ("JAPAN", "Japon", "JP", ["ASIA"]),
    ("USA", "Etats-Unis", "US", ["NORTH_AMERICA"]),
    ("UK", "Royaume-Uni", "GB", ["EUROPE"]),
    ("GERMANY", "Allemagne", "DE", ["EUROPE"]),
    ("RUSSIA", "Russie", "RU", ["EUROPE"]),
    ("SWEDEN", "Suède", "SE", ["EUROPE"]),
    ("IRAN", "Iran", "IR", ["ASIA"]),
    ("SENEGAL", "Sénégal", "SN", ["AFRICA"]),
    ("SOUTH_KOREA", "Corée du Sud", "KR", ["ASIA"]),
    ("INDIA", "Inde", "IN", ["ASIA"]),
    ("CHINA", "Chine", "CN", ["ASIA"]),
    ("BRAZIL", "Brésil", "BR", ["SOUTH_AMERICA"]),
    ("MEXICO", "Mexique", "MX", ["NORTH_AMERICA"]),
    ("SPAIN", "Espagne", "ES", ["EUROPE"]),
    ("POLAND", "Pologne", "PL", ["EUROPE"]),
    ("DENMARK", "Danemark", "DK", ["EUROPE"]),
    ("CZECH", "Tchéquie", "CZ", ["EUROPE"]),
    ("HUNGARY", "Hongrie", "HU", ["EUROPE"]),
    ("ARGENTINA", "Argentine", "AR", ["SOUTH_AMERICA"]),
    ("EGYPT", "Egypte", "EG", ["AFRICA"]),
    ("AUSTRALIA", "Australie", "AU", ["OCEANIA"]),
    ("CANADA", "Canada", "CA", ["NORTH_AMERICA"]),
    ("BELGIUM", "Belgique", "BE", ["EUROPE"]),
    ("GREECE", "Grèce", "GR", ["EUROPE"]),
    ("TURKEY", "Turquie", "TR", ["EUROPE", "ASIA"]),
    ("HONG_KONG", "Hong Kong", "HK", ["ASIA"]),
    ("TAIWAN", "Taïwan", "TW", ["ASIA"]),
    ("ALGERIA", "Algérie", "DZ", ["AFRICA"]),
    ("MALI", "Mali", "ML", ["AFRICA"]),
    ("CUBA", "Cuba", "CU", ["NORTH_AMERICA"]),
    ("AUSTRIA", "Autriche", "AT", ["EUROPE"]),
    ("PORTUGAL", "Portugal", "PT", ["EUROPE"]),
    ("CHILE", "Chili", "CL", ["SOUTH_AMERICA"]),
    ("NEW_ZEALAND", "Nouvelle-Zélande", "NZ", ["OCEANIA"]),
    ("UKRAINE", "Ukraine", "UA", ["EUROPE"]),
    ("FINLAND", "Finlande", "FI", ["EUROPE"]),
    ("THAILAND", "Thaïlande", "TH", ["ASIA"]),
    ("PHILIPPINES", "Philippines", "PH", ["ASIA"]),
    ("BURKINA_FASO", "Burkina Faso", "BF", ["AFRICA"]),
    ("ANGOLA", "Angola", "AO", ["AFRICA"]),
]

GENRES = [
    ("DRAME", "Drame"),
    ("GUERRE", "Guerre"),
    ("HISTORIQUE", "Historique"),
    ("POLICIER", "Policier"),
    ("DOCUMENTAIRE", "Documentaire"),
    ("COMEDIE", "Comédie"),
    ("WESTERN", "Western"),
    ("HORREUR", "Horreur"),
    ("SCIENCE_FICTION", "Science-fiction"),
    ("ROMANCE", "Romance"),
    ("THRILLER", "Thriller"),
    ("MUSICAL", "Musical"),
    ("ANIMATION", "Animation"),
    ("AVENTURE", "Aventure"),
    ("FILM_NOIR", "Film noir"),
]

ERAS = [
    ("CINEMA_MUET", "Cinéma muet", 1895, 1929),
    ("CINEMA_CLASSIQUE", "Cinéma classique", 1930, 1959),
    ("CINEMA_MODERNE", "Cinéma moderne", 1960, 1979),
    ("CINEMA_CONTEMPORAIN", "Cinéma contemporain", 1980, 2028),
]

CHARACTERISTICS = [
    ("NEOREALISME_ITALIEN", "Néoréalisme italien", "MOVEMENT",
     "Un cinéma d'après-guerre tourné dans la rue, avec des non-professionnels et le réel social pour matière."),
    ("NOUVELLE_VAGUE_FRANCAISE", "Nouvelle Vague française", "WAVE",
     "Une génération de critiques devenus cinéastes, caméra légère, rupture de découpage et liberté de récit."),
    ("AGE_OR_CINEMA_JAPONAIS", "Âge d'or du cinéma japonais", "PERIOD",
     "Les studios japonais des années 1930-1960, de Mizoguchi et Ozu à Kurosawa."),
    ("HOLLYWOOD_CLASSIQUE", "Hollywood classique", "PERIOD",
     "Le système des studios américains, ses genres, sa continuité invisible et ses stars."),
    ("MONTAGE_SOVIETIQUE", "Montage soviétique", "MOVEMENT",
     "Le choc des plans comme pensée politique, d'Eisenstein à Vertov."),
    ("CINEMA_SOVIETIQUE", "Cinéma soviétique", "PERIOD",
     "L'histoire du cinéma d'URSS, de l'avant-garde muette au dégel et à l'auteurisme tardif."),
    ("EXPRESSIONNISME_ALLEMAND", "Expressionnisme allemand", "MOVEMENT",
     "Décors distendus, ombres portées et psyché visuelle du cinéma de Weimar."),
    ("FILM_NOIR_STYLE", "Film noir", "STYLE",
     "Fatalité urbaine, éclairages contrastés et moralité trouble de l'après-guerre."),
    ("WESTERN_CLASSIQUE", "Western classique", "STYLE",
     "La frontière américaine comme mythe, paysage et conflit moral."),
    ("CINEMA_MUET_MOUVEMENT", "Cinéma muet", "PERIOD",
     "L'âge du cinéma avant la parole synchronisée, du trick film au mélodrame monumental."),
    ("NOUVEAU_CINEMA_ALLEMAND", "Nouveau cinéma allemand", "WAVE",
     "Le renouveau ouest-allemand des années 1960-1980, d'Oberhausen à Fassbinder, Herzog et Wenders."),
    ("NOUVELLE_VAGUE_IRANIENNE", "Nouvelle vague iranienne", "WAVE",
     "Un cinéma de la vie quotidienne, de l'enfance et du hors-champ, de Kiarostami à Farhadi."),
    ("COMMEDIA_ALL_ITALIANA", "Comédie à l'italienne", "CURRENT",
     "Satire sociale, amertume et virtuoses du jeu, de Monicelli à Scola."),
    ("SPAGHETTI_WESTERN", "Western spaghetti", "CURRENT",
     "Le western européen, violent et baroque, recentré sur l'Italie des années 1960."),
    ("SURREALISME", "Surréalisme", "MOVEMENT",
     "Le rêve, le choc d'images et la subversion de la logique narrative."),
    ("CINEMA_EXPERIMENTAL", "Cinéma expérimental", "STYLE",
     "Films qui travaillent la matière, le temps et la perception hors du récit classique."),
    ("NEW_HOLLYWOOD", "Nouvel Hollywood", "PERIOD",
     "La rupture américaine 1967-1980 : auteurs, contre-culture et fin du code Hays."),
    ("REALISME_POETIQUE", "Réalisme poétique", "CURRENT",
     "Le lyrisme populaire français des années 1930, de Carné à Renoir."),
    ("BRITISH_NEW_WAVE", "Free Cinema / British New Wave", "WAVE",
     "Le réalisme social britannique, de Saturday Night and Sunday Morning à Kes."),
    ("CINEMA_NOVO", "Cinema Novo", "MOVEMENT",
     "L'esthétique de la faim brésilienne, entre allégorie et urgences politiques."),
    ("DOGME_95", "Dogme 95", "SCHOOL",
     "Le manifeste danois de 1995 : caméra portée, lumière naturelle, rejet du cosmétique."),
    ("HONG_KONG_NEW_WAVE", "Nouvelle Vague hongkongaise", "WAVE",
     "Modernité urbaine, polar et mélancolie, de Wong Kar-wai à John Woo."),
    ("TAIWAN_NEW_CINEMA", "Nouveau cinéma taïwanais", "WAVE",
     "Mémoire, plans-séquences et histoire nationale, de Hou Hsiao-hsien à Edward Yang."),
    ("KOREAN_NEW_WAVE", "Nouvelle vague coréenne", "WAVE",
     "Le cinéma sud-coréen contemporain, entre genre virtuose et critique sociale."),
    ("INDIAN_PARALLEL", "Cinéma parallèle indien", "CURRENT",
     "L'alternative au studio hindi, de Satyajit Ray au réalisme bengali."),
    ("THIRD_CINEMA", "Troisième cinéma", "MOVEMENT",
     "Un cinéma de décolonisation, contre Hollywood et l'auteurisme européen."),
    ("MELODRAME", "Mélodrame", "STYLE",
     "L'excès émotionnel comme forme : Sirk, Mizoguchi, Almodóvar."),
    ("CINEMA_D_AUTEUR", "Cinéma d'auteur", "CURRENT",
     "La mise en scène comme signature, héritée de la politique des auteurs."),
    ("IMPRESSIONNISME_FRANCAIS", "Impressionnisme français", "MOVEMENT",
     "Rythme, superpositions et états d'âme du cinéma français des années 1920."),
    ("DOCUMENTAIRE_POETIQUE", "Documentaire poétique", "STYLE",
     "Le réel travaillé comme matière lyrique plutôt que comme reportage."),
    ("NEO_NOIR", "Néo-noir", "STYLE",
     "L'héritage du film noir après 1960, de Chinatown à Oldboy."),
    ("ROAD_MOVIE", "Road movie", "STYLE",
     "La route comme forme : errance, paysage et identité."),
    ("ECOLE_POLONAISE", "École polonaise", "SCHOOL",
     "La mémoire de la guerre et du stalinisme dans le cinéma polonais d'après 1956."),
    ("NOUVELLE_VAGUE_TCHEQUE", "Nouvelle Vague tchèque", "WAVE",
     "L'ironie et la liberté formelle du cinéma tchécoslovaque des années 1960."),
    ("CINEMA_DIRECT", "Cinéma direct", "CURRENT",
     "Prise de vue légère, son synchrone et observation du présent."),
    ("LEFT_BANK", "Rive gauche", "CURRENT",
     "Le versant littéraire et moderne de la Nouvelle Vague : Resnais, Marker, Varda."),
    ("JIDAIGEKI", "Jidai-geki", "STYLE",
     "Le film d'époque japonais, samouraïs, codes et violence cérémonielle."),
    ("GIALLO", "Giallo", "STYLE",
     "Polar-horreur italien, couleur saturée et mise en scène du crime."),
    ("ANIMATION_DAUTEUR", "Animation d'auteur", "STYLE",
     "Le dessin et l'animation comme cinéma d'auteur, de McLaren à Ghibli."),
    ("CINEMA_AFRICAIN", "Cinémas d'Afrique", "CURRENT",
     "Les cinématographies africaines, de Sembène à Cissé, entre fable et politique."),
]

# firstName, lastName, characteristicCodes
DIRECTORS: dict[str, tuple[str | None, str, list[str]]] = {
    "AKIRA_KUROSAWA": ("Akira", "Kurosawa", ["AGE_OR_CINEMA_JAPONAIS", "JIDAIGEKI", "CINEMA_D_AUTEUR"]),
    "YASUJIRO_OZU": ("Yasujirō", "Ozu", ["AGE_OR_CINEMA_JAPONAIS", "CINEMA_D_AUTEUR"]),
    "KENJI_MIZOGUCHI": ("Kenji", "Mizoguchi", ["AGE_OR_CINEMA_JAPONAIS", "MELODRAME", "CINEMA_D_AUTEUR"]),
    "MIKIO_NARUSE": ("Mikio", "Naruse", ["AGE_OR_CINEMA_JAPONAIS", "MELODRAME"]),
    "MASAKI_KOBAYASHI": ("Masaki", "Kobayashi", ["AGE_OR_CINEMA_JAPONAIS", "JIDAIGEKI"]),
    "TEINOSUKE_KINUGASA": ("Teinosuke", "Kinugasa", ["CINEMA_MUET_MOUVEMENT", "CINEMA_EXPERIMENTAL"]),
    "ISHIRO_HONDA": ("Ishirō", "Honda", ["AGE_OR_CINEMA_JAPONAIS"]),
    "NAGISA_OSHIMA": ("Nagisa", "Ōshima", ["CINEMA_D_AUTEUR"]),
    "HIROSHI_TESHIGAHARA": ("Hiroshi", "Teshigahara", ["CINEMA_D_AUTEUR"]),
    "SHOHEI_IMAMURA": ("Shōhei", "Imamura", ["CINEMA_D_AUTEUR"]),
    "HAYAO_MIYAZAKI": ("Hayao", "Miyazaki", ["ANIMATION_DAUTEUR"]),
    "KATSUHIRO_OTOMO": ("Katsuhiro", "Ōtomo", ["ANIMATION_DAUTEUR"]),
    "SATOSHI_KON": ("Satoshi", "Kon", ["ANIMATION_DAUTEUR"]),
    "TAKESHI_KITANO": ("Takeshi", "Kitano", ["CINEMA_D_AUTEUR"]),
    "HIROKAZU_KOREEDA": ("Hirokazu", "Kore-eda", ["CINEMA_D_AUTEUR"]),
    "KIYOSHI_KUROSAWA": ("Kiyoshi", "Kurosawa", ["CINEMA_D_AUTEUR"]),
    "SEIJUN_SUZUKI": ("Seijun", "Suzuki", ["CINEMA_D_AUTEUR"]),
    "SHINYA_TSUKAMOTO": ("Shinya", "Tsukamoto", ["CINEMA_EXPERIMENTAL"]),
    "BONG_JOON_HO": ("Joon-ho", "Bong", ["KOREAN_NEW_WAVE"]),
    "PARK_CHAN_WOOK": ("Chan-wook", "Park", ["KOREAN_NEW_WAVE", "NEO_NOIR"]),
    "LEE_CHANG_DONG": ("Chang-dong", "Lee", ["KOREAN_NEW_WAVE"]),
    "KIM_KI_YOUNG": ("Ki-young", "Kim", ["KOREAN_NEW_WAVE"]),
    "SATYAJIT_RAY": ("Satyajit", "Ray", ["INDIAN_PARALLEL", "CINEMA_D_AUTEUR"]),
    "RITWIK_GHATAK": ("Ritwik", "Ghatak", ["INDIAN_PARALLEL"]),
    "GURU_DUTT": ("Guru", "Dutt", ["MELODRAME"]),
    "RAJ_KAPOOR": ("Raj", "Kapoor", ["MELODRAME"]),
    "ZHANG_YIMOU": ("Yimou", "Zhang", ["MELODRAME", "CINEMA_D_AUTEUR"]),
    "CHEN_KAIGE": ("Kaige", "Chen", ["CINEMA_D_AUTEUR"]),
    "JIA_ZHANGKE": ("Zhangke", "Jia", ["CINEMA_D_AUTEUR"]),
    "FEI_MU": ("Mu", "Fei", ["CINEMA_D_AUTEUR"]),
    "KING_HU": ("Hu", "King", ["JIDAIGEKI"]),
    "WONG_KAR_WAI": ("Kar-wai", "Wong", ["HONG_KONG_NEW_WAVE", "CINEMA_D_AUTEUR"]),
    "JOHN_WOO": ("Woo", "John", ["HONG_KONG_NEW_WAVE"]),
    "HOU_HSIAO_HSIEN": ("Hsiao-hsien", "Hou", ["TAIWAN_NEW_CINEMA", "CINEMA_D_AUTEUR"]),
    "EDWARD_YANG": ("Edward", "Yang", ["TAIWAN_NEW_CINEMA", "CINEMA_D_AUTEUR"]),
    "WANG_BING": ("Bing", "Wang", ["DOCUMENTAIRE_POETIQUE", "CINEMA_DIRECT"]),
    "ABBAS_KIAROSTAMI": ("Abbas", "Kiarostami", ["NOUVELLE_VAGUE_IRANIENNE", "CINEMA_D_AUTEUR"]),
    "FOROUGH_FARROKHZAD": ("Forough", "Farrokhzad", ["NOUVELLE_VAGUE_IRANIENNE", "DOCUMENTAIRE_POETIQUE"]),
    "MOHSEN_MAKHMALBAF": ("Mohsen", "Makhmalbaf", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "ASGHAR_FARHADI": ("Asghar", "Farhadi", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "JAFAR_PANAHI": ("Jafar", "Panahi", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "GEORGES_MELIES": ("Georges", "Méliès", ["CINEMA_MUET_MOUVEMENT", "CINEMA_EXPERIMENTAL"]),
    "ABEL_GANCE": ("Abel", "Gance", ["CINEMA_MUET_MOUVEMENT", "IMPRESSIONNISME_FRANCAIS"]),
    "RENE_CLAIR": ("René", "Clair", ["CINEMA_MUET_MOUVEMENT", "SURREALISME"]),
    "FERNAND_LEGER": ("Fernand", "Léger", ["CINEMA_EXPERIMENTAL"]),
    "JEAN_VIGO": ("Jean", "Vigo", ["CINEMA_D_AUTEUR"]),
    "JEAN_RENOIR": ("Jean", "Renoir", ["REALISME_POETIQUE", "CINEMA_D_AUTEUR"]),
    "MARCEL_CARNE": ("Marcel", "Carné", ["REALISME_POETIQUE"]),
    "JULIEN_DUVIVIER": ("Julien", "Duvivier", ["REALISME_POETIQUE"]),
    "HENRI_GEORGES_CLOUZOT": ("Henri-Georges", "Clouzot", ["CINEMA_D_AUTEUR"]),
    "ROBERT_BRESSON": ("Robert", "Bresson", ["CINEMA_D_AUTEUR"]),
    "JACQUES_TATI": ("Jacques", "Tati", ["CINEMA_D_AUTEUR"]),
    "JEAN_COCTEAU": ("Jean", "Cocteau", ["SURREALISME", "CINEMA_D_AUTEUR"]),
    "JEAN_LUC_GODARD": ("Jean-Luc", "Godard", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "FRANCOIS_TRUFFAUT": ("François", "Truffaut", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "AGNES_VARDA": ("Agnès", "Varda", ["NOUVELLE_VAGUE_FRANCAISE", "LEFT_BANK", "CINEMA_D_AUTEUR"]),
    "ALAIN_RESNAIS": ("Alain", "Resnais", ["NOUVELLE_VAGUE_FRANCAISE", "LEFT_BANK", "CINEMA_D_AUTEUR"]),
    "ERIC_ROHMER": ("Éric", "Rohmer", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "JACQUES_RIVETTE": ("Jacques", "Rivette", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "CLAUDE_CHABROL": ("Claude", "Chabrol", ["NOUVELLE_VAGUE_FRANCAISE"]),
    "JACQUES_DEMY": ("Jacques", "Demy", ["NOUVELLE_VAGUE_FRANCAISE"]),
    "CHRIS_MARKER": ("Chris", "Marker", ["LEFT_BANK", "DOCUMENTAIRE_POETIQUE", "CINEMA_EXPERIMENTAL"]),
    "JEAN_PIERRE_MELVILLE": ("Jean-Pierre", "Melville", ["NEO_NOIR", "CINEMA_D_AUTEUR"]),
    "LOUIS_MALLE": ("Louis", "Malle", ["NOUVELLE_VAGUE_FRANCAISE"]),
    "LUIS_BUNUEL": ("Luis", "Buñuel", ["SURREALISME", "CINEMA_D_AUTEUR"]),
    "CLAIRE_DENIS": ("Claire", "Denis", ["CINEMA_D_AUTEUR"]),
    "LEOS_CARAX": ("Leos", "Carax", ["CINEMA_D_AUTEUR"]),
    "CELINE_SCIAMMA": ("Céline", "Sciamma", ["CINEMA_D_AUTEUR"]),
    "MATHIEU_KASSOVITZ": ("Mathieu", "Kassovitz", []),
    "MICHAEL_HANEKE": ("Michael", "Haneke", ["CINEMA_D_AUTEUR"]),
    "CLAUDE_LANZMANN": ("Claude", "Lanzmann", ["DOCUMENTAIRE_POETIQUE"]),
    "PETER_WATKINS": ("Peter", "Watkins", ["CINEMA_D_AUTEUR", "DOCUMENTAIRE_POETIQUE"]),
    "ROBERTO_ROSSELLINI": ("Roberto", "Rossellini", ["NEOREALISME_ITALIEN", "CINEMA_D_AUTEUR"]),
    "VITTORIO_DE_SICA": ("Vittorio", "De Sica", ["NEOREALISME_ITALIEN", "COMMEDIA_ALL_ITALIANA"]),
    "LUCHINO_VISCONTI": ("Luchino", "Visconti", ["NEOREALISME_ITALIEN", "CINEMA_D_AUTEUR", "MELODRAME"]),
    "FEDERICO_FELLINI": ("Federico", "Fellini", ["CINEMA_D_AUTEUR"]),
    "MICHELANGELO_ANTONIONI": ("Michelangelo", "Antonioni", ["CINEMA_D_AUTEUR"]),
    "PIER_PAOLO_PASOLINI": ("Pier Paolo", "Pasolini", ["CINEMA_D_AUTEUR"]),
    "SERGIO_LEONE": ("Sergio", "Leone", ["SPAGHETTI_WESTERN"]),
    "SERGIO_CORBUCCI": ("Sergio", "Corbucci", ["SPAGHETTI_WESTERN"]),
    "SERGIO_SOLLIMA": ("Sergio", "Sollima", ["SPAGHETTI_WESTERN"]),
    "TONINO_VALERII": ("Tonino", "Valerii", ["SPAGHETTI_WESTERN"]),
    "ENZO_BARBONI": ("Enzo", "Barboni", ["SPAGHETTI_WESTERN"]),
    "GIULIO_PETRONI": ("Giulio", "Petroni", ["SPAGHETTI_WESTERN"]),
    "ENZO_G_CASTELLARI": ("Enzo G.", "Castellari", ["SPAGHETTI_WESTERN"]),
    "DUCCIO_TESSARI": ("Duccio", "Tessari", ["SPAGHETTI_WESTERN"]),
    "GIULIO_QUESTI": ("Giulio", "Questi", ["SPAGHETTI_WESTERN"]),
    "DAMIANO_DAMIANI": ("Damiano", "Damiani", ["SPAGHETTI_WESTERN"]),
    "MARIO_MONICELLI": ("Mario", "Monicelli", ["COMMEDIA_ALL_ITALIANA"]),
    "PIETRO_GERMI": ("Pietro", "Germi", ["COMMEDIA_ALL_ITALIANA"]),
    "DINO_RISI": ("Dino", "Risi", ["COMMEDIA_ALL_ITALIANA"]),
    "ETTORE_SCOLA": ("Ettore", "Scola", ["COMMEDIA_ALL_ITALIANA"]),
    "LINA_WERTMULLER": ("Lina", "Wertmüller", ["COMMEDIA_ALL_ITALIANA"]),
    "LUIGI_COMENCINI": ("Luigi", "Comencini", ["COMMEDIA_ALL_ITALIANA"]),
    "FRANCO_BRUSATI": ("Franco", "Brusati", ["COMMEDIA_ALL_ITALIANA"]),
    "BERNARDO_BERTOLUCCI": ("Bernardo", "Bertolucci", ["CINEMA_D_AUTEUR"]),
    "GILLO_PONTECORVO": ("Gillo", "Pontecorvo", ["THIRD_CINEMA"]),
    "GIUSEPPE_TORNATORE": ("Giuseppe", "Tornatore", []),
    "PAOLO_SORRENTINO": ("Paolo", "Sorrentino", ["CINEMA_D_AUTEUR"]),
    "ERMANNO_OLMI": ("Ermanno", "Olmi", ["CINEMA_D_AUTEUR"]),
    "DW_GRIFFITH": ("D. W.", "Griffith", ["CINEMA_MUET_MOUVEMENT"]),
    "LOUIS_FEUILLADE": ("Louis", "Feuillade", ["CINEMA_MUET_MOUVEMENT"]),
    "CHARLIE_CHAPLIN": ("Charlie", "Chaplin", ["CINEMA_MUET_MOUVEMENT", "CINEMA_D_AUTEUR"]),
    "BUSTER_KEATON": ("Buster", "Keaton", ["CINEMA_MUET_MOUVEMENT"]),
    "HAROLD_LLOYD": ("Harold", "Lloyd", ["CINEMA_MUET_MOUVEMENT"]),
    "KING_VIDOR": ("King", "Vidor", ["HOLLYWOOD_CLASSIQUE", "CINEMA_MUET_MOUVEMENT"]),
    "ERICH_VON_STROHEIM": ("Erich", "von Stroheim", ["CINEMA_MUET_MOUVEMENT", "HOLLYWOOD_CLASSIQUE"]),
    "ORSON_WELLES": ("Orson", "Welles", ["HOLLYWOOD_CLASSIQUE", "CINEMA_D_AUTEUR", "FILM_NOIR_STYLE"]),
    "ALFRED_HITCHCOCK": ("Alfred", "Hitchcock", ["HOLLYWOOD_CLASSIQUE", "CINEMA_D_AUTEUR"]),
    "JOHN_FORD": ("John", "Ford", ["HOLLYWOOD_CLASSIQUE", "WESTERN_CLASSIQUE", "CINEMA_D_AUTEUR"]),
    "HOWARD_HAWKS": ("Howard", "Hawks", ["HOLLYWOOD_CLASSIQUE", "WESTERN_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "BILLY_WILDER": ("Billy", "Wilder", ["HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "FRITZ_LANG": ("Fritz", "Lang", ["EXPRESSIONNISME_ALLEMAND", "FILM_NOIR_STYLE", "HOLLYWOOD_CLASSIQUE"]),
    "FW_MURNAU": ("F. W.", "Murnau", ["EXPRESSIONNISME_ALLEMAND", "CINEMA_MUET_MOUVEMENT", "HOLLYWOOD_CLASSIQUE"]),
    "STANLEY_KUBRICK": ("Stanley", "Kubrick", ["CINEMA_D_AUTEUR", "NEW_HOLLYWOOD"]),
    "FRANCIS_FORD_COPPOLA": ("Francis Ford", "Coppola", ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR"]),
    "MARTIN_SCORSESE": ("Martin", "Scorsese", ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR", "NEO_NOIR"]),
    "STEVEN_SPIELBERG": ("Steven", "Spielberg", ["NEW_HOLLYWOOD"]),
    "QUENTIN_TARANTINO": ("Quentin", "Tarantino", ["NEO_NOIR"]),
    "DAVID_LYNCH": ("David", "Lynch", ["CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR", "NEO_NOIR"]),
    "JOHN_CASSAVETES": ("John", "Cassavetes", ["CINEMA_D_AUTEUR", "NEW_HOLLYWOOD"]),
    "ELIA_KAZAN": ("Elia", "Kazan", ["HOLLYWOOD_CLASSIQUE"]),
    "NICHOLAS_RAY": ("Nicholas", "Ray", ["HOLLYWOOD_CLASSIQUE"]),
    "STANLEY_DONEN": ("Stanley", "Donen", ["HOLLYWOOD_CLASSIQUE"]),
    "GENE_KELLY": ("Gene", "Kelly", ["HOLLYWOOD_CLASSIQUE"]),
    "MICHAEL_CURTIZ": ("Michael", "Curtiz", ["HOLLYWOOD_CLASSIQUE"]),
    "JOHN_HUSTON": ("John", "Huston", ["HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "JOSEPH_L_MANKIEWICZ": ("Joseph L.", "Mankiewicz", ["HOLLYWOOD_CLASSIQUE"]),
    "PRESTON_STURGES": ("Preston", "Sturges", ["HOLLYWOOD_CLASSIQUE"]),
    "ERNST_LUBITSCH": ("Ernst", "Lubitsch", ["HOLLYWOOD_CLASSIQUE"]),
    "FRANK_CAPRA": ("Frank", "Capra", ["HOLLYWOOD_CLASSIQUE"]),
    "VICTOR_FLEMING": ("Victor", "Fleming", ["HOLLYWOOD_CLASSIQUE"]),
    "MERIAN_C_COOPER": ("Merian C.", "Cooper", ["HOLLYWOOD_CLASSIQUE"]),
    "ERNEST_B_SCHOEDSACK": ("Ernest B.", "Schoedsack", ["HOLLYWOOD_CLASSIQUE"]),
    "JAMES_WHALE": ("James", "Whale", ["HOLLYWOOD_CLASSIQUE"]),
    "CHARLES_LAUGHTON": ("Charles", "Laughton", ["HOLLYWOOD_CLASSIQUE"]),
    "SIDNEY_LUMET": ("Sidney", "Lumet", ["CINEMA_D_AUTEUR"]),
    "FRED_ZINNEMANN": ("Fred", "Zinnemann", ["HOLLYWOOD_CLASSIQUE", "WESTERN_CLASSIQUE"]),
    "GEORGE_STEVENS": ("George", "Stevens", ["HOLLYWOOD_CLASSIQUE", "WESTERN_CLASSIQUE"]),
    "WILLIAM_WYLER": ("William", "Wyler", ["HOLLYWOOD_CLASSIQUE"]),
    "OTTO_PREMINGER": ("Otto", "Preminger", ["HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "JACQUES_TOURNEUR": ("Jacques", "Tourneur", ["HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "EDWARD_DMYTRYK": ("Edward", "Dmytryk", ["FILM_NOIR_STYLE"]),
    "JOHN_FARROW": ("John", "Farrow", ["FILM_NOIR_STYLE"]),
    "HENRY_HATHAWAY": ("Henry", "Hathaway", ["FILM_NOIR_STYLE"]),
    "ROBERT_SIODMAK": ("Robert", "Siodmak", ["FILM_NOIR_STYLE"]),
    "SAMUEL_FULLER": ("Samuel", "Fuller", ["FILM_NOIR_STYLE", "NEW_HOLLYWOOD"]),
    "ROBERT_ALDRICH": ("Robert", "Aldrich", ["FILM_NOIR_STYLE", "NEW_HOLLYWOOD"]),
    "ARTHUR_PENN": ("Arthur", "Penn", ["NEW_HOLLYWOOD"]),
    "MIKE_NICHOLS": ("Mike", "Nichols", ["NEW_HOLLYWOOD"]),
    "DENNIS_HOPPER": ("Dennis", "Hopper", ["NEW_HOLLYWOOD", "ROAD_MOVIE"]),
    "SAM_PECKINPAH": ("Sam", "Peckinpah", ["NEW_HOLLYWOOD", "WESTERN_CLASSIQUE"]),
    "ROBERT_ALTMAN": ("Robert", "Altman", ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR"]),
    "WILLIAM_FRIEDKIN": ("William", "Friedkin", ["NEW_HOLLYWOOD"]),
    "PETER_BOGDANOVICH": ("Peter", "Bogdanovich", ["NEW_HOLLYWOOD"]),
    "WOODY_ALLEN": ("Woody", "Allen", ["NEW_HOLLYWOOD"]),
    "GEORGE_LUCAS": ("George", "Lucas", ["NEW_HOLLYWOOD"]),
    "SPIKE_LEE": ("Spike", "Lee", ["CINEMA_D_AUTEUR"]),
    "JOEL_COEN": ("Joel", "Coen", ["NEO_NOIR"]),
    "ETHAN_COEN": ("Ethan", "Coen", ["NEO_NOIR"]),
    "PAUL_THOMAS_ANDERSON": ("Paul Thomas", "Anderson", ["CINEMA_D_AUTEUR"]),
    "TERRENCE_MALICK": ("Terrence", "Malick", ["NEW_HOLLYWOOD", "CINEMA_D_AUTEUR"]),
    "JORDAN_PEELE": ("Jordan", "Peele", []),
    "BARRY_JENKINS": ("Barry", "Jenkins", ["CINEMA_D_AUTEUR"]),
    "DAVID_FINCHER": ("David", "Fincher", ["NEO_NOIR"]),
    "LANA_WACHOWSKI": ("Lana", "Wachowski", []),
    "LILLY_WACHOWSKI": ("Lilly", "Wachowski", []),
    "GEORGE_A_ROMERO": ("George A.", "Romero", []),
    "JOHN_CARPENTER": ("John", "Carpenter", []),
    "MAYA_DEREN": ("Maya", "Deren", ["CINEMA_EXPERIMENTAL"]),
    "ALEXANDER_HAMMID": ("Alexander", "Hammid", ["CINEMA_EXPERIMENTAL"]),
    "MICHAEL_SNOW": ("Michael", "Snow", ["CINEMA_EXPERIMENTAL"]),
    "GODFREY_REGGIO": ("Godfrey", "Reggio", ["CINEMA_EXPERIMENTAL", "DOCUMENTAIRE_POETIQUE"]),
    "STANLEY_KRAMER": ("Stanley", "Kramer", ["HOLLYWOOD_CLASSIQUE"]),
    "JOSEPH_LOSEY": ("Joseph", "Losey", ["CINEMA_D_AUTEUR"]),
    "NICHOLAS_RAY": ("Nicholas", "Ray", ["HOLLYWOOD_CLASSIQUE"]),
    "ELIA_KAZAN": ("Elia", "Kazan", ["HOLLYWOOD_CLASSIQUE"]),
    "SIDNEY_LUMET": ("Sidney", "Lumet", ["CINEMA_D_AUTEUR"]),
    "ROMAN_POLANSKI": ("Roman", "Polanski", ["CINEMA_D_AUTEUR", "NEO_NOIR"]),
    "MILOS_FORMAN": ("Miloš", "Forman", ["NOUVELLE_VAGUE_TCHEQUE", "NEW_HOLLYWOOD"]),
    "DAVID_LEAN": ("David", "Lean", ["CINEMA_D_AUTEUR"]),
    "MICHAEL_POWELL": ("Michael", "Powell", ["CINEMA_D_AUTEUR"]),
    "EMERIC_PRESSBURGER": ("Emeric", "Pressburger", ["CINEMA_D_AUTEUR"]),
    "CAROL_REED": ("Carol", "Reed", ["FILM_NOIR_STYLE"]),
    "ROBERT_HAMER": ("Robert", "Hamer", []),
    "KEN_LOACH": ("Ken", "Loach", ["BRITISH_NEW_WAVE"]),
    "LINDSAY_ANDERSON": ("Lindsay", "Anderson", ["BRITISH_NEW_WAVE"]),
    "TONY_RICHARDSON": ("Tony", "Richardson", ["BRITISH_NEW_WAVE"]),
    "NICOLAS_ROEG": ("Nicolas", "Roeg", ["CINEMA_D_AUTEUR"]),
    "RIDLEY_SCOTT": ("Ridley", "Scott", ["NEO_NOIR"]),
    "ROBERT_WIENE": ("Robert", "Wiene", ["EXPRESSIONNISME_ALLEMAND", "CINEMA_MUET_MOUVEMENT"]),
    "GW_PABST": ("G. W.", "Pabst", ["EXPRESSIONNISME_ALLEMAND"]),
    "WERNER_HERZOG": ("Werner", "Herzog", ["NOUVEAU_CINEMA_ALLEMAND", "CINEMA_D_AUTEUR"]),
    "RAINER_WERNER_FASSBINDER": ("Rainer Werner", "Fassbinder", ["NOUVEAU_CINEMA_ALLEMAND", "MELODRAME", "CINEMA_D_AUTEUR"]),
    "WIM_WENDERS": ("Wim", "Wenders", ["NOUVEAU_CINEMA_ALLEMAND", "ROAD_MOVIE", "CINEMA_D_AUTEUR"]),
    "VOLKER_SCHLONDORFF": ("Volker", "Schlöndorff", ["NOUVEAU_CINEMA_ALLEMAND"]),
    "WOLFGANG_PETERSEN": ("Wolfgang", "Petersen", []),
    "SERGEI_EISENSTEIN": ("Sergueï", "Eisenstein", ["MONTAGE_SOVIETIQUE", "CINEMA_SOVIETIQUE"]),
    "DZIGA_VERTOV": ("Dziga", "Vertov", ["MONTAGE_SOVIETIQUE", "CINEMA_SOVIETIQUE", "CINEMA_EXPERIMENTAL", "DOCUMENTAIRE_POETIQUE"]),
    "ALEXANDER_DOVZHENKO": ("Alexandre", "Dovjenko", ["MONTAGE_SOVIETIQUE", "CINEMA_SOVIETIQUE"]),
    "ANDREI_TARKOVSKY": ("Andreï", "Tarkovski", ["CINEMA_SOVIETIQUE", "CINEMA_D_AUTEUR"]),
    "MIKHAIL_KALATOZOV": ("Mikhaïl", "Kalatozov", ["CINEMA_SOVIETIQUE"]),
    "ELEM_KLIMOV": ("Elem", "Klimov", ["CINEMA_SOVIETIQUE"]),
    "SERGEI_PARAJANOV": ("Sergueï", "Paradjanov", ["CINEMA_SOVIETIQUE", "CINEMA_EXPERIMENTAL", "CINEMA_D_AUTEUR"]),
    "SERGEI_BONDARCHUK": ("Sergueï", "Bondartchouk", ["CINEMA_SOVIETIQUE"]),
    "INGMAR_BERGMAN": ("Ingmar", "Bergman", ["CINEMA_D_AUTEUR"]),
    "VICTOR_SJOSTROM": ("Victor", "Sjöström", ["CINEMA_MUET_MOUVEMENT"]),
    "CARL_THEODOR_DREYER": ("Carl Theodor", "Dreyer", ["CINEMA_D_AUTEUR", "CINEMA_MUET_MOUVEMENT"]),
    "LARS_VON_TRIER": ("Lars", "von Trier", ["DOGME_95", "CINEMA_D_AUTEUR"]),
    "THOMAS_VINTERBERG": ("Thomas", "Vinterberg", ["DOGME_95"]),
    "PEDRO_ALMODOVAR": ("Pedro", "Almodóvar", ["MELODRAME", "CINEMA_D_AUTEUR"]),
    "VICTOR_ERICE": ("Víctor", "Erice", ["CINEMA_D_AUTEUR"]),
    "CARLOS_SAURA": ("Carlos", "Saura", ["CINEMA_D_AUTEUR"]),
    "ANDRZEJ_WAJDA": ("Andrzej", "Wajda", ["ECOLE_POLONAISE", "CINEMA_D_AUTEUR"]),
    "KRZYSZTOF_KIESLOWSKI": ("Krzysztof", "Kieślowski", ["CINEMA_D_AUTEUR"]),
    "WOJCIECH_HAS": ("Wojciech", "Has", ["ECOLE_POLONAISE"]),
    "JIRI_MENZEL": ("Jiří", "Menzel", ["NOUVELLE_VAGUE_TCHEQUE"]),
    "VERA_CHYTILOVA": ("Věra", "Chytilová", ["NOUVELLE_VAGUE_TCHEQUE"]),
    "FRANTISEK_VLACIL": ("František", "Vláčil", ["NOUVELLE_VAGUE_TCHEQUE"]),
    "JAN_SVANKMAJER": ("Jan", "Švankmajer", ["CINEMA_EXPERIMENTAL", "ANIMATION_DAUTEUR", "SURREALISME"]),
    "BELA_TARR": ("Béla", "Tarr", ["CINEMA_D_AUTEUR"]),
    "ISTVAN_SZABO": ("István", "Szabó", ["CINEMA_D_AUTEUR"]),
    "LASZLO_NEMES": ("László", "Nemes", []),
    "CHANTAL_AKERMAN": ("Chantal", "Akerman", ["CINEMA_D_AUTEUR", "CINEMA_EXPERIMENTAL"]),
    "JEAN_PIERRE_DARDENNE": ("Jean-Pierre", "Dardenne", ["CINEMA_D_AUTEUR"]),
    "LUC_DARDENNE": ("Luc", "Dardenne", ["CINEMA_D_AUTEUR"]),
    "THEO_ANGELOPOULOS": ("Théo", "Angelopoulos", ["CINEMA_D_AUTEUR"]),
    "YORGOS_LANTHIMOS": ("Yorgos", "Lanthimos", ["CINEMA_D_AUTEUR"]),
    "NURI_BILGE_CEYLAN": ("Nuri Bilge", "Ceylan", ["CINEMA_D_AUTEUR"]),
    "YILMAZ_GUNEY": ("Yılmaz", "Güney", ["CINEMA_D_AUTEUR"]),
    "SERIF_GOREN": ("Şerif", "Gören", []),
    "GLAUBER_ROCHA": ("Glauber", "Rocha", ["CINEMA_NOVO", "THIRD_CINEMA"]),
    "NELSON_PEREIRA_DOS_SANTOS": ("Nelson", "Pereira dos Santos", ["CINEMA_NOVO"]),
    "FERNANDO_MEIRELLES": ("Fernando", "Meirelles", []),
    "KATIA_LUND": ("Kátia", "Lund", []),
    "WALTER_SALLES": ("Walter", "Salles", []),
    "MARIO_PEIXOTO": ("Mário", "Peixoto", ["CINEMA_MUET_MOUVEMENT", "CINEMA_EXPERIMENTAL"]),
    "ALFONSO_CUARON": ("Alfonso", "Cuarón", ["CINEMA_D_AUTEUR"]),
    "ALEJANDRO_GONZALEZ_INARRITU": ("Alejandro González", "Iñárritu", []),
    "GUILLERMO_DEL_TORO": ("Guillermo", "del Toro", []),
    "LUCRECIA_MARTEL": ("Lucrecia", "Martel", ["CINEMA_D_AUTEUR"]),
    "JUAN_JOSE_CAMPANELLA": ("Juan José", "Campanella", []),
    "FERNANDO_SOLANAS": ("Fernando", "Solanas", ["THIRD_CINEMA"]),
    "OCTAVIO_GETINO": ("Octavio", "Getino", ["THIRD_CINEMA"]),
    "OUSMANE_SEMBENE": ("Ousmane", "Sembène", ["CINEMA_AFRICAIN", "THIRD_CINEMA", "CINEMA_D_AUTEUR"]),
    "DJIBRIL_DIOP_MAMBETY": ("Djibril Diop", "Mambéty", ["CINEMA_AFRICAIN", "CINEMA_D_AUTEUR"]),
    "SOULEYMANE_CISSE": ("Souleymane", "Cissé", ["CINEMA_AFRICAIN"]),
    "MOHAMMED_LAKHDAR_HAMINA": ("Mohammed", "Lakhdar-Hamina", ["CINEMA_AFRICAIN"]),
    "YOUSSEF_CHAHINE": ("Youssef", "Chahine", ["CINEMA_AFRICAIN", "CINEMA_D_AUTEUR"]),
    "SHADI_ABDEL_SALAM": ("Shadi", "Abdel Salam", ["CINEMA_AFRICAIN"]),
    "ABDERRAHMANE_SISSAKO": ("Abderrahmane", "Sissako", ["CINEMA_AFRICAIN"]),
    "PETER_WEIR": ("Peter", "Weir", []),
    "GEORGE_MILLER": ("George", "Miller", ["ROAD_MOVIE"]),
    "JANE_CAMPION": ("Jane", "Campion", ["CINEMA_D_AUTEUR"]),
    "DAVID_CRONENBERG": ("David", "Cronenberg", ["CINEMA_D_AUTEUR"]),
    "DENIS_VILLENEUVE": ("Denis", "Villeneuve", []),
    "TOMAS_GUTIERREZ_ALEA": ("Tomás", "Gutiérrez Alea", ["THIRD_CINEMA"]),
    "MANOEL_DE_OLIVEIRA": ("Manoel", "de Oliveira", ["CINEMA_D_AUTEUR"]),
    "RAOUL_RUIZ": ("Raoul", "Ruiz", ["CINEMA_D_AUTEUR"]),
    "HU_BO": ("Bo", "Hu", ["CINEMA_D_AUTEUR"]),
    "ANDRZEJ_WAJDA": ("Andrzej", "Wajda", ["ECOLE_POLONAISE", "CINEMA_D_AUTEUR"]),
    "KRZYSZTOF_KIESLOWSKI": ("Krzysztof", "Kieślowski", ["CINEMA_D_AUTEUR"]),
    "JACQUES_BECKER": ("Jacques", "Becker", ["CINEMA_D_AUTEUR"]),
    "JEAN_PIERRE_MELVILLE": ("Jean-Pierre", "Melville", ["NEO_NOIR", "CINEMA_D_AUTEUR"]),
    "FRANCOIS_TRUFFAUT": ("François", "Truffaut", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "ROBERT_BRESSON": ("Robert", "Bresson", ["CINEMA_D_AUTEUR"]),
    "JEAN_EPSTEIN": ("Jean", "Epstein", ["IMPRESSIONNISME_FRANCAIS", "CINEMA_MUET_MOUVEMENT"]),
    "MARCEL_L_HERBIER": ("Marcel", "L'Herbier", ["IMPRESSIONNISME_FRANCAIS"]),
    "ANTHONY_MANN": ("Anthony", "Mann", ["WESTERN_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "DOUGLAS_SIRK": ("Douglas", "Sirk", ["HOLLYWOOD_CLASSIQUE", "MELODRAME"]),
    "VINCENTE_MINNELLI": ("Vincente", "Minnelli", ["HOLLYWOOD_CLASSIQUE"]),
    "GEORGE_CUKOR": ("George", "Cukor", ["HOLLYWOOD_CLASSIQUE"]),
    "BILLY_WILDER": ("Billy", "Wilder", ["HOLLYWOOD_CLASSIQUE", "FILM_NOIR_STYLE"]),
    "NICHOLAS_RAY": ("Nicholas", "Ray", ["HOLLYWOOD_CLASSIQUE"]),
    "ELIA_KAZAN": ("Elia", "Kazan", ["HOLLYWOOD_CLASSIQUE"]),
    "SIDNEY_LUMET": ("Sidney", "Lumet", ["CINEMA_D_AUTEUR"]),
    "ANDRZEJ_WAJDA": ("Andrzej", "Wajda", ["ECOLE_POLONAISE", "CINEMA_D_AUTEUR"]),
    "KRZYSZTOF_KIESLOWSKI": ("Krzysztof", "Kieślowski", ["CINEMA_D_AUTEUR"]),
    "JEAN_PIERRE_MELVILLE": ("Jean-Pierre", "Melville", ["NEO_NOIR", "CINEMA_D_AUTEUR"]),
    "ROBERT_BRESSON": ("Robert", "Bresson", ["CINEMA_D_AUTEUR"]),
    "FRANCOIS_TRUFFAUT": ("François", "Truffaut", ["NOUVELLE_VAGUE_FRANCAISE", "CINEMA_D_AUTEUR"]),
    "MICHAEL_CIMINO": ("Michael", "Cimino", ["NEW_HOLLYWOOD"]),
    "SERGIO_LEONE": ("Sergio", "Leone", ["SPAGHETTI_WESTERN"]),
    "KIM_KI_DUK": ("Ki-duk", "Kim", ["KOREAN_NEW_WAVE"]),
    "HONG_SANG_SOO": ("Sang-soo", "Hong", ["KOREAN_NEW_WAVE"]),
    "TSAI_MING_LIANG": ("Ming-liang", "Tsai", ["TAIWAN_NEW_CINEMA"]),
    "ANURAG_KASHYAP": ("Anurag", "Kashyap", ["INDIAN_PARALLEL"]),
    "KLEBER_MENDONCA_FILHO": ("Kleber", "Mendonça Filho", ["CINEMA_D_AUTEUR"]),
    "PATRICIO_GUZMAN": ("Patricio", "Guzmán", ["DOCUMENTAIRE_POETIQUE", "THIRD_CINEMA"]),
    "PETER_JACKSON": ("Peter", "Jackson", []),
    "ATOM_EGOYAN": ("Atom", "Egoyan", ["CINEMA_D_AUTEUR"]),
    "XAVIER_DOLAN": ("Xavier", "Dolan", []),
    "MICHAEL_CACOYANNIS": ("Michael", "Cacoyannis", []),
    "LUIS_GARCIA_BERLANGA": ("Luis García", "Berlanga", []),
    "EMILIO_FERNANDEZ": ("Emilio", "Fernández", []),
    "ARTURO_RIPSTEIN": ("Arturo", "Ripstein", []),
    "RAJ_KAPOOR": ("Raj", "Kapoor", ["MELODRAME"]),
    "MIRA_NAIR": ("Mira", "Nair", []),
    "KATIA_LUND": ("Kátia", "Lund", []),
    "OCTAVIO_GETINO": ("Octavio", "Getino", ["THIRD_CINEMA"]),
    "GIOVANNI_PASTRONE": ("Giovanni", "Pastrone", ["CINEMA_MUET_MOUVEMENT"]),
    "GERMAINE_DULAC": ("Germaine", "Dulac", ["IMPRESSIONNISME_FRANCAIS", "SURREALISME"]),
    "JOSEF_VON_STERNBERG": ("Josef", "von Sternberg", ["HOLLYWOOD_CLASSIQUE"]),
    "MAX_OPHULS": ("Max", "Ophüls", ["MELODRAME", "CINEMA_D_AUTEUR"]),
    "LEO_MCCAREY": ("Leo", "McCarey", ["HOLLYWOOD_CLASSIQUE"]),
    "RAOUL_WALSH": ("Raoul", "Walsh", ["HOLLYWOOD_CLASSIQUE", "WESTERN_CLASSIQUE"]),
    "WILLIAM_WELLMAN": ("William", "Wellman", ["HOLLYWOOD_CLASSIQUE"]),
    "TOD_BROWNING": ("Tod", "Browning", ["HOLLYWOOD_CLASSIQUE"]),
    "ALEXANDER_MACKENDRICK": ("Alexander", "Mackendrick", []),
    "ROBERT_WISE": ("Robert", "Wise", ["HOLLYWOOD_CLASSIQUE"]),
    "JEROME_ROBBINS": ("Jerome", "Robbins", ["HOLLYWOOD_CLASSIQUE"]),
    "JOHN_FRANKENHEIMER": ("John", "Frankenheimer", []),
    "HAL_ASHBY": ("Hal", "Ashby", ["NEW_HOLLYWOOD"]),
    "JAMES_CAMERON": ("James", "Cameron", []),
    "ROBERT_ZEMECKIS": ("Robert", "Zemeckis", []),
    "ROGER_ALLERS": ("Roger", "Allers", ["ANIMATION_DAUTEUR"]),
    "KATHRYN_BIGELOW": ("Kathryn", "Bigelow", []),
    "CHRISTOPHER_NOLAN": ("Christopher", "Nolan", []),
    "ALEJANDRO_JODOROWSKY": ("Alejandro", "Jodorowsky", ["CINEMA_EXPERIMENTAL", "SURREALISME"]),
    "DON_SIEGEL": ("Don", "Siegel", []),
    "ALAN_J_PAKULA": ("Alan J.", "Pakula", ["NEW_HOLLYWOOD"]),
    "JOHN_STURGES": ("John", "Sturges", ["WESTERN_CLASSIQUE"]),
    "BUDD_BOETTICHER": ("Budd", "Boetticher", ["WESTERN_CLASSIQUE"]),
    "IDA_LUPINO": ("Ida", "Lupino", ["FILM_NOIR_STYLE"]),
    "JULES_DASSIN": ("Jules", "Dassin", ["FILM_NOIR_STYLE"]),
    "CHARLES_VIDOR": ("Charles", "Vidor", ["FILM_NOIR_STYLE"]),
    "EDGAR_G_ULMER": ("Edgar G.", "Ulmer", ["FILM_NOIR_STYLE"]),
    "JOSEPH_H_LEWIS": ("Joseph H.", "Lewis", ["FILM_NOIR_STYLE"]),
    "WALTER_RUTTMANN": ("Walter", "Ruttmann", ["CINEMA_EXPERIMENTAL", "DOCUMENTAIRE_POETIQUE"]),
    "PAUL_WEGENER": ("Paul", "Wegener", ["EXPRESSIONNISME_ALLEMAND", "CINEMA_MUET_MOUVEMENT"]),
    "BENJAMIN_CHRISTENSEN": ("Benjamin", "Christensen", ["CINEMA_MUET_MOUVEMENT"]),
    "MAURITZ_STILLER": ("Mauritz", "Stiller", ["CINEMA_MUET_MOUVEMENT"]),
    "JEAN_ROUCH": ("Jean", "Rouch", ["CINEMA_DIRECT"]),
    "JEAN_EUSTACHE": ("Jean", "Eustache", ["CINEMA_D_AUTEUR"]),
    "MAURICE_PIALA": ("Maurice", "Pialat", ["CINEMA_D_AUTEUR"]),
    "NANNI_MORETTI": ("Nanni", "Moretti", ["CINEMA_D_AUTEUR"]),
    "PAOLO_TAVIANI": ("Paolo", "Taviani", ["CINEMA_D_AUTEUR"]),
    "VITTORIO_TAVIANI": ("Vittorio", "Taviani", ["CINEMA_D_AUTEUR"]),
    "STAN_BRAKHAGE": ("Stan", "Brakhage", ["CINEMA_EXPERIMENTAL"]),
    "KENNETH_ANGER": ("Kenneth", "Anger", ["CINEMA_EXPERIMENTAL"]),
    "JONAS_MEKAS": ("Jonas", "Mekas", ["CINEMA_EXPERIMENTAL"]),
    "LARISA_SHEPITKO": ("Larissa", "Chepitko", ["CINEMA_SOVIETIQUE"]),
    "RENE_CLEMENT": ("René", "Clément", []),
    "GEORGES_FRANJU": ("Georges", "Franju", []),
    "CLAUDE_SAUTET": ("Claude", "Sautet", []),
    "OLIVIER_ASSAYAS": ("Olivier", "Assayas", ["CINEMA_D_AUTEUR"]),
    "SOFIA_COPPOLA": ("Sofia", "Coppola", []),
    "RICHARD_LINKLATER": ("Richard", "Linklater", []),
    "WES_ANDERSON": ("Wes", "Anderson", []),
    "JONATHAN_DEMME": ("Jonathan", "Demme", []),
    "FABIAN_BIELINSKY": ("Fabián", "Bielinsky", ["NEO_NOIR"]),
    "PABLO_LARRAIN": ("Pablo", "Larraín", []),
    "JACQUES_FEYDER": ("Jacques", "Feyder", ["REALISME_POETIQUE"]),
    "JEAN_GREMILLION": ("Jean", "Grémillon", ["REALISME_POETIQUE"]),
    "DOROTHY_ARZNER": ("Dorothy", "Arzner", ["HOLLYWOOD_CLASSIQUE"]),
    "ROBERT_ENRICO": ("Robert", "Enrico", []),
    "FREDERICK_WISEMAN": ("Frederick", "Wiseman", ["CINEMA_DIRECT"]),
    "GIAN_FRANCO_DALLA_CASSA": ("Gian Franco", "Dallamano", ["SPAGHETTI_WESTERN"]),
    "GIANFRANCO_PAROLINI": ("Gianfranco", "Parolini", ["SPAGHETTI_WESTERN"]),
    "LUCIO_FULCI": ("Lucio", "Fulci", ["SPAGHETTI_WESTERN"]),
    "LUIS_PUENZO": ("Luis", "Puenzo", []),
    "MOHSEN_MAKHMALBAF": ("Mohsen", "Makhmalbaf", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "ALICE_GUY": ("Alice", "Guy", ["CINEMA_MUET_MOUVEMENT"]),
    "LOUIS_LUMIERE": ("Louis", "Lumière", ["CINEMA_MUET_MOUVEMENT", "DOCUMENTAIRE_POETIQUE"]),
    "EDWIN_S_PORTER": ("Edwin S.", "Porter", ["CINEMA_MUET_MOUVEMENT"]),
    "OSCAR_MICHEAUX": ("Oscar", "Micheaux", ["CINEMA_MUET_MOUVEMENT"]),
    "VSEVOLOD_PUDOVKIN": ("Vsevolod", "Poudovkine", ["MONTAGE_SOVIETIQUE", "CINEMA_SOVIETIQUE"]),
    "PAUL_LENI": ("Paul", "Leni", ["EXPRESSIONNISME_ALLEMAND", "CINEMA_MUET_MOUVEMENT"]),
    "JOE_MAY": ("Joe", "May", ["EXPRESSIONNISME_ALLEMAND"]),
    "KON_ICHIKAWA": ("Kon", "Ichikawa", ["AGE_OR_CINEMA_JAPONAIS"]),
    "DARIUS_MEHRJUI": ("Dariush", "Mehrjui", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "AMIR_NADERI": ("Amir", "Naderi", ["NOUVELLE_VAGUE_IRANIENNE"]),
    "SARAH_MALDOROR": ("Sarah", "Maldoror", ["CINEMA_AFRICAIN", "THIRD_CINEMA"]),
    "IDRISSA_OUEDRAOGO": ("Idrissa", "Ouédraogo", ["CINEMA_AFRICAIN"]),
    "GASTON_KABORE": ("Gaston", "Kaboré", ["CINEMA_AFRICAIN"]),
    "HUMBERTO_SOLAS": ("Humberto", "Solás", ["THIRD_CINEMA"]),
    "HECTOR_BABENCO": ("Héctor", "Babenco", []),
    "MIGUEL_LITTIN": ("Miguel", "Littin", ["THIRD_CINEMA"]),
    "AKI_KAURISMAKI": ("Aki", "Kaurismäki", ["CINEMA_D_AUTEUR"]),
    "APICHATPONG_WEERASETHAKUL": ("Apichatpong", "Weerasethakul", ["CINEMA_D_AUTEUR"]),
    "LINO_BROCKA": ("Lino", "Brocka", ["CINEMA_D_AUTEUR"]),
    "KIDLAT_TAHIMIK": ("Kidlat", "Tahimik", ["THIRD_CINEMA", "CINEMA_EXPERIMENTAL"]),
    "PEDRO_COSTA": ("Pedro", "Costa", ["CINEMA_D_AUTEUR"]),
}

# Remove accidental invalid characteristic on Tati if any slipped through — cleaned above.

BADGES = [
    ("001", "Premier Rideau", "Voir son premier film.", 1, "VOLUME"),
    ("002", "Deuxième Séance", "Voir 10 films.", 1, "VOLUME"),
    ("003", "Accro au Ciné", "Voir 50 films.", 2, "VOLUME"),
    ("004", "Collectionneur", "Voir 100 films.", 3, "VOLUME"),
    ("005", "Passeport Cinéma", "Explorer 15 pays.", 2, "GEOGRAPHY"),
    ("006", "Globe-Trotter", "Explorer 30 pays.", 3, "GEOGRAPHY"),
    ("007", "Cartographe du Cinéma", "Explorer 50 pays.", 5, "GEOGRAPHY"),
    ("008", "Tour d'Europe", "Explorer 10 pays européens.", 3, "GEOGRAPHY"),
    ("009", "Au-delà des Frontières", "Voir cinq films sur cinq continents.", 4, "GEOGRAPHY"),
    ("010", "Dolce Vita", "Voir 20 films italiens.", 3, "COUNTRY"),
    ("011", "Made in USA", "Voir 50 films américains.", 3, "COUNTRY"),
    ("012", "Rising Sun", "Voir 20 films japonais.", 3, "COUNTRY"),
    ("013", "Lumière sur la France", "Voir 20 films français.", 3, "COUNTRY"),
    ("014", "Made in Asia", "Voir 50 films asiatiques.", 4, "COUNTRY"),
    ("015", "Au-delà du Canon", "Voir 10 films sortis avant 1950.", 2, "TIME"),
    ("016", "Archéologue du Cinéma", "Voir 30 films sortis avant 1960.", 3, "TIME"),
    ("017", "Mémoire du Septième Art", "Voir 100 films sortis avant 1980.", 5, "TIME"),
    ("018", "Fantômes du Muet", "Voir 10 films muets.", 3, "TIME"),
    ("019", "Retour aux Sources", "Explorer 5 décennies.", 2, "TIME"),
    ("020", "À Travers les Âges", "Explorer 8 décennies.", 4, "TIME"),
    ("021", "Enfant de la Nouvelle Vague", "Voir 15 films de cinéastes associés à la Nouvelle Vague.", 4, "CURRENT"),
    ("022", "La Dolce Commedia", "Voir 15 films de la comédie italienne.", 3, "CURRENT"),
    ("023", "L'Œil soviétique", "Voir 10 films du cinéma soviétique.", 3, "CURRENT"),
    ("024", "Nuits américaines", "Voir 20 films noirs.", 3, "GENRE"),
    ("025", "Western Spaghetti", "Voir 15 westerns italiens.", 3, "CURRENT"),
    ("026", "La Forme avant le Fond", "Voir 10 films expérimentaux.", 4, "FORM"),
    ("027", "Le Temps suspendu", "Voir 10 films de plus de trois heures.", 4, "FORM"),
    ("028", "La Grande Traversée", "Voir 5 films de plus de cinq heures.", 5, "FORM"),
    ("029", "Bibliothèque de Pellicule", "Voir 10 films de 20 réalisateurs.", 5, "PANORAMA"),
    ("030", "Encyclopédie Vivante", "Voir 10 films de 30 courants.", 5, "PANORAMA"),
]

QUESTS = [
    ("QUEST_BRONZE_SILENT", "Le silence est d'or", "Voir 1 film muet", "BRONZE", "WATCH_SILENT", 1),
    ("QUEST_BRONZE_FRANCE", "Une séance française", "Voir 1 film français", "BRONZE", "WATCH_COUNTRY_FRANCE", 1),
    ("QUEST_BRONZE_BW", "Nuances de gris", "Voir 1 film en noir et blanc", "BRONZE", "WATCH_BLACK_AND_WHITE", 1),
    ("QUEST_BRONZE_DRAMA", "Le drame d'abord", "Voir 1 drame", "BRONZE", "WATCH_GENRE_DRAMA", 1),
    ("QUEST_BRONZE_COMEDY", "Un éclat de rire", "Voir 1 comédie", "BRONZE", "WATCH_GENRE_COMEDIE", 1),
    ("QUEST_BRONZE_WESTERN", "Poussière et horizon", "Voir 1 western", "BRONZE", "WATCH_GENRE_WESTERN", 1),
    ("QUEST_BRONZE_HORROR", "Une peur courte", "Voir 1 film d'horreur", "BRONZE", "WATCH_GENRE_HORREUR", 1),
    ("QUEST_BRONZE_UK", "Une soirée britannique", "Voir 1 film britannique", "BRONZE", "WATCH_COUNTRY_UK", 1),
    ("QUEST_BRONZE_GERMANY", "Une séance allemande", "Voir 1 film allemand", "BRONZE", "WATCH_COUNTRY_GERMANY", 1),
    ("QUEST_BRONZE_EXPERIMENTAL", "Hors du récit", "Voir 1 film expérimental", "BRONZE", "WATCH_EXPERIMENTAL", 1),
    ("QUEST_BRONZE_1930S", "Retour en 1930", "Voir 1 film sorti dans les années 1930", "BRONZE", "WATCH_DECADE_1930", 1),
    ("QUEST_BRONZE_FROM_1980", "Après 1980", "Voir 1 film sorti en 1980 ou après", "BRONZE", "WATCH_FROM_1980", 1),
    ("QUEST_BRONZE_NEW_WAVE", "Un souffle de Vague", "Voir 1 film de la Nouvelle Vague française", "BRONZE", "WATCH_CHARACTERISTIC_NOUVELLE_VAGUE_FRANCAISE", 1),
    ("QUEST_BRONZE_NOIR", "Une ruelle sombre", "Voir 1 film noir", "BRONZE", "WATCH_GENRE_FILM_NOIR", 1),
    ("QUEST_BRONZE_ANIMATION", "Un dessin qui bouge", "Voir 1 film d'animation", "BRONZE", "WATCH_GENRE_ANIMATION", 1),
    ("QUEST_BRONZE_DOCUMENTARY", "Un regard sur le réel", "Voir 1 documentaire", "BRONZE", "WATCH_GENRE_DOCUMENTAIRE", 1),
    ("QUEST_SILVER_ASIA", "Trois regards d'Asie", "Voir 3 films asiatiques", "SILVER", "WATCH_CONTINENT_ASIA", 3),
    ("QUEST_SILVER_ITALY", "Voyage en Italie", "Voir 3 films italiens", "SILVER", "WATCH_COUNTRY_ITALY", 3),
    ("QUEST_SILVER_JAPAN", "Trois regards du Japon", "Voir 3 films japonais", "SILVER", "WATCH_COUNTRY_JAPAN", 3),
    ("QUEST_SILVER_1960S", "Les années 1960", "Voir 3 films sortis dans les années 1960", "SILVER", "WATCH_DECADE_1960", 3),
    ("QUEST_SILVER_DRAMA_2", "Deux drames", "Voir 2 drames", "SILVER", "WATCH_GENRE_DRAMA", 2),
    ("QUEST_SILVER_COMEDY", "Deux comédies", "Voir 2 comédies", "SILVER", "WATCH_GENRE_COMEDIE", 2),
    ("QUEST_SILVER_GERMANY", "Trois Allemagnes", "Voir 3 films allemands", "SILVER", "WATCH_COUNTRY_GERMANY", 3),
    ("QUEST_SILVER_UK", "Trois Albions", "Voir 3 films britanniques", "SILVER", "WATCH_COUNTRY_UK", 3),
    ("QUEST_SILVER_1950S", "Les années 1950", "Voir 3 films sortis dans les années 1950", "SILVER", "WATCH_DECADE_1950", 3),
    ("QUEST_SILVER_1970S", "Les années 1970", "Voir 3 films sortis dans les années 1970", "SILVER", "WATCH_DECADE_1970", 3),
    ("QUEST_SILVER_1930S", "Les années 1930", "Voir 3 films sortis dans les années 1930", "SILVER", "WATCH_DECADE_1930", 3),
    ("QUEST_SILVER_NEW_HOLLYWOOD", "Nouvel Hollywood", "Voir 3 films du Nouvel Hollywood", "SILVER", "WATCH_CHARACTERISTIC_NEW_HOLLYWOOD", 3),
    ("QUEST_SILVER_NOIR", "Trois nuits noires", "Voir 3 films noirs", "SILVER", "WATCH_GENRE_FILM_NOIR", 3),
    ("QUEST_SILVER_WESTERN", "Trois frontières", "Voir 3 westerns", "SILVER", "WATCH_GENRE_WESTERN", 3),
    ("QUEST_SILVER_BW", "Trois gris", "Voir 3 films en noir et blanc", "SILVER", "WATCH_BLACK_AND_WHITE", 3),
    ("QUEST_SILVER_SOUTH_AMERICA", "Trois Amériques du Sud", "Voir 3 films sud-américains", "SILVER", "WATCH_CONTINENT_SOUTH_AMERICA", 3),
    ("QUEST_SILVER_AUTEUR", "Trois signatures", "Voir 3 films de cinéma d'auteur", "SILVER", "WATCH_CHARACTERISTIC_CINEMA_D_AUTEUR", 3),
    ("QUEST_GOLD_BEFORE_1950", "Avant 1950", "Voir 5 films sortis avant 1950", "GOLD", "WATCH_BEFORE_1950", 5),
    ("QUEST_GOLD_USA", "Cinq Amériques", "Voir 5 films américains", "GOLD", "WATCH_COUNTRY_USA", 5),
    ("QUEST_GOLD_EUROPE", "Grand tour d'Europe", "Voir 5 films européens", "GOLD", "WATCH_CONTINENT_EUROPE", 5),
    ("QUEST_GOLD_DIRECTORS", "Cinq auteurs", "Voir 5 films de 5 réalisateurs différents", "GOLD", "DISTINCT_DIRECTORS", 5),
    ("QUEST_GOLD_FRANCE", "Cinq séances françaises", "Voir 5 films français", "GOLD", "WATCH_COUNTRY_FRANCE", 5),
    ("QUEST_GOLD_1960S", "Plein 1960", "Voir 5 films sortis dans les années 1960", "GOLD", "WATCH_DECADE_1960", 5),
    ("QUEST_GOLD_FROM_1980", "Cinq regards contemporains", "Voir 5 films sortis en 1980 ou après", "GOLD", "WATCH_FROM_1980", 5),
    ("QUEST_GOLD_COUNTRIES", "Cinq drapeaux", "Voir des films de 5 pays différents", "GOLD", "DISTINCT_COUNTRIES", 5),
    ("QUEST_GOLD_GENRES", "Quatre genres", "Voir des films de 4 genres différents", "GOLD", "DISTINCT_GENRES", 4),
    ("QUEST_GOLD_DECADES", "Quatre décennies", "Voir des films de 4 décennies différentes", "GOLD", "DISTINCT_DECADES", 4),
    ("QUEST_GOLD_NOIR", "Cinq nuits noires", "Voir 5 films noirs", "GOLD", "WATCH_GENRE_FILM_NOIR", 5),
    ("QUEST_GOLD_AUTEUR", "Cinq signatures", "Voir 5 films de cinéma d'auteur", "GOLD", "WATCH_CHARACTERISTIC_CINEMA_D_AUTEUR", 5),
    ("QUEST_GOLD_HOLLYWOOD", "Cinq studios", "Voir 5 films d'Hollywood classique", "GOLD", "WATCH_CHARACTERISTIC_HOLLYWOOD_CLASSIQUE", 5),
    ("QUEST_GOLD_RUNTIME", "Cinq longues séances", "Voir 5 films de plus de 2 heures", "GOLD", "WATCH_RUNTIME_OVER_120", 5),
    ("QUEST_GOLD_WESTERN", "Cinq chevauchées", "Voir 5 westerns", "GOLD", "WATCH_GENRE_WESTERN", 5),
    ("QUEST_GOLD_COMEDY", "Cinq éclats", "Voir 5 comédies", "GOLD", "WATCH_GENRE_COMEDIE", 5),
    ("QUEST_GOLD_NEW_WAVE", "Cinq Vagues", "Voir 5 films de la Nouvelle Vague française", "GOLD", "WATCH_CHARACTERISTIC_NOUVELLE_VAGUE_FRANCAISE", 5),
]

RANK_SHORT = {
    "RANK_01": "Tu commences à tracer ta carte du cinéma.",
    "RANK_02": "Ta curiosité prend forme.",
    "RANK_03": "Tu reconnais les premiers territoires.",
    "RANK_04": "Le cinéma accompagne régulièrement ton regard.",
    "RANK_05": "Tu parcours des cinématographies variées.",
    "RANK_06": "Tu relies les œuvres, les auteurs et les époques.",
    "RANK_07": "Ta culture est large et approfondie.",
    "RANK_08": "Tu maîtrises de vastes pans de l'histoire du cinéma.",
    "RANK_09": "Ton parcours couvre presque tout le territoire proposé.",
    "RANK_10": "Tu as parcouru presque intégralement le catalogue Urbinema.",
}

RANKINGS = [
    (
        "RANK_01", 1, "Novice",
        "Tu entres dans le catalogue comme on pousse une première porte de salle. "
        "Quelques films suffisent à poser un point sur la carte, sans encore dessiner un territoire. "
        "Ce rang enregistre un contact inaugural avec l'histoire du cinéma, pas une culture déjà formée. "
        "Chaque séance suivante élargit simplement l'espace que tu commences à habiter.",
    ),
    (
        "RANK_02", 2, "Amateur",
        "Ta curiosité n'est plus un accident : tu reviens vers les films par choix. "
        "Les titres s'accumulent et les premiers échos apparaissent entre les époques. "
        "Tu n'as pas encore de méthode, mais tu as un goût qui commence à se formuler. "
        "Le cinéma cesse d'être un divertissement isolé pour devenir une habitude de regard.",
    ),
    (
        "RANK_03", 3, "Initié",
        "Tu reconnais désormais quelques territoires : un pays, une décennie, un nom d'auteur. "
        "Les films cessent d'arriver un par un ; ils s'inscrivent dans des familles. "
        "Tu sais situer une œuvre sans encore pouvoir en raconter toute la généalogie. "
        "L'initiation, ici, c'est moins le savoir encyclopédique que le passage d'un regard passif à un regard orienté.",
    ),
    (
        "RANK_04", 4, "Passionné",
        "Le cinéma accompagne régulièrement tes semaines, plus comme une pratique que comme une liste. "
        "Tu acceptes des films difficiles, longs, anciens, parce que le plaisir s'est déplacé vers la découverte. "
        "Les conversations que tu pourrais avoir sur un plan, un acteur ou une époque s'étoffent. "
        "Ce rang marque l'instant où le catalogue n'est plus un défi : il devient un appétit.",
    ),
    (
        "RANK_05", 5, "Explorateur",
        "Tu quittes les sentiers les plus balisés pour parcourir des cinématographies éloignées. "
        "L'Asie, l'Afrique, l'Amérique latine ou le muet ne sont plus des exceptions, mais des directions. "
        "Explorer, c'est accepter de se perdre : un film peut déplacer tout ce que tu croyais établi. "
        "Ta carte s'agrandit moins par accumulation que par écarts volontairement cherchés.",
    ),
    (
        "RANK_06", 6, "Connaisseur",
        "Tu relies désormais les œuvres, les auteurs et les époques avec une mémoire active. "
        "Un plan de Mizoguchi appelle Renoir ; un polar italien réveille Hollywood ; un muet éclaire un film contemporain. "
        "Le connaisseur ne cite pas pour briller : il compare pour comprendre. "
        "Ton parcours commence à avoir une cohérence, même s'il reste inachevé par nature.",
    ),
    (
        "RANK_07", 7, "Érudit",
        "Ta culture s'est élargie sans se diluer : tu tiens ensemble le canon et ses marges. "
        "Les mouvements, les écoles et les chronologies ne sont plus des étiquettes, mais des outils. "
        "L'érudition, dans Urbinema, se mesure à la diversité réelle de ce que tu as vu, pas à la pose du specialist. "
        "Tu peux traverser un siècle de cinéma et encore pointer ce qui te manque.",
    ),
    (
        "RANK_08", 8, "Spécialiste",
        "Tu maîtrises de vastes pans de l'histoire du cinéma, assez pour y discerner des lignes de force. "
        "Certains territoires te sont devenus familiers au point que tu y repères les exceptions. "
        "Le spécialiste n'est pas celui qui s'enferme : c'est celui qui peut approfondir sans perdre le panorama. "
        "À ce stade, chaque nouveau film se lit contre une bibliothèque intérieure déjà dense.",
    ),
    (
        "RANK_09", 9, "Expert",
        "Ton parcours couvre presque tout le territoire proposé, des premiers muets aux formes contemporaines. "
        "Tu as croisé assez de pays, de formats et de courants pour que les hasards du catalogue deviennent rares. "
        "L'expertise se voit moins à la vitesse qu'à la justesse : tu sais ce que tu as vu et ce que cela ouvre. "
        "Il reste des zones d'ombre, mais elles sont choisies, plus subies.",
    ),
    (
        "RANK_10", 10, "Maître",
        "Tu as parcouru presque intégralement le catalogue Urbinema, non comme une collection fermée, mais comme une carte habitée. "
        "Le titre de maître n'arrête pas le regard : il constate une traversée longue, diverse et tenace. "
        "Les films se répondent désormais d'eux-mêmes, d'un continent à l'autre, d'une décennie à la suivante. "
        "Revenir à un titre déjà vu, dès lors, n'est plus une répétition : c'est une relecture.",
    ),
]


def clamp01(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 2)


def movie_format(minutes: int) -> str:
    if minutes < 40:
        return "SHORT"
    if minutes < 60:
        return "MEDIUM"
    if minutes >= 180:
        return "EXTENDED"
    return "FEATURE"


def scores_for(code: str, year: int, silent: bool, experimental: bool, demand: float) -> tuple[float, float, float, float]:
    if code in SCORE_OVERRIDES:
        return SCORE_OVERRIDES[code]
    digest = hashlib.md5(code.encode("utf-8")).hexdigest()
    jitter = int(digest[:4], 16) / 65535.0
    age = (2028 - year) / float(2028 - 1880)
    historical_distance = clamp01(0.16 + 0.72 * age + 0.08 * jitter)
    artistic_demand = clamp01(
        0.30 + 0.42 * demand + (0.08 if silent else 0.0) + (0.16 if experimental else 0.0) + 0.06 * jitter
    )
    historical_richness = clamp01(0.48 + 0.38 * age + 0.12 * demand)
    cultural_richness = clamp01(0.46 + 0.30 * demand + 0.14 * (1.0 - jitter) + (0.06 if year < 1960 else 0.0))
    return historical_distance, artistic_demand, historical_richness, cultural_richness


def split_codes(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def is_black_and_white(year: int, flags: str) -> bool:
    if "c" in flags:
        return False
    if "b" in flags or "s" in flags:
        return True
    return year <= 1954


def film(
    code: str,
    original: str,
    french: str,
    year: int,
    minutes: int,
    synopsis: str,
    countries: str,
    directors: str,
    genres: str,
    chars: str = "",
    flags: str = "",
    demand: float = 0.7,
) -> dict:
    country_codes = split_codes(countries)
    director_codes = split_codes(directors)
    silent = "s" in flags
    experimental = "e" in flags
    hd, ad, hr, cr = scores_for(code, year, silent, experimental, demand)
    item = {
        "code": code,
        "originalTitle": original,
        "frenchTitle": french,
        "releaseYear": year,
        "durationMinutes": minutes,
        "format": movie_format(minutes),
        "synopsis": SYNOPSIS_OVERRIDES.get(code, synopsis),
        "historicalDistance": hd,
        "artisticDemand": ad,
        "historicalRichness": hr,
        "culturalRichness": cr,
        "countries": [
            {"code": country_code, "isPrimary": index == 0}
            for index, country_code in enumerate(country_codes)
        ],
        "directors": [
            {"code": director_code, "billingOrder": index}
            for index, director_code in enumerate(director_codes)
        ],
        "genreCodes": split_codes(genres),
        "characteristicCodes": split_codes(chars),
    }
    if silent:
        item["isSilent"] = True
    if is_black_and_white(year, flags):
        item["isBlackAndWhite"] = True
    if experimental:
        item["isExperimental"] = True
    return item


def parse_film_table(blob: str) -> list[dict]:
    movies: list[dict] = []
    for raw_line in blob.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 12:
            raise SystemExit(f"Bad film row ({len(parts)} fields): {line[:120]}")
        code, original, french, year, minutes, countries, directors, genres, chars, flags, demand, synopsis = parts
        movies.append(
            film(
                code,
                original,
                french,
                int(year),
                int(minutes),
                synopsis,
                countries,
                directors,
                genres,
                chars,
                flags,
                float(demand),
            )
        )
    return movies


# code|original|french|year|minutes|countries|directors|genres|chars|flags|demand|synopsis
FILM_TABLE = r"""
# --- Required ---
SEPT_SAMOURAIS_1954|七人の侍|Les Sept Samouraïs|1954|207|JAPAN|AKIRA_KUROSAWA|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI,CINEMA_D_AUTEUR|b|0.88|Des villageois engagent sept samouraïs pour protéger leur récolte.
ROMA_CITTA_APERTA_1945|Roma città aperta|Rome, ville ouverte|1945|103|ITALY|ROBERTO_ROSSELLINI|DRAME,GUERRE|NEOREALISME_ITALIEN|b|0.80|Dans la Rome occupée, plusieurs destins se croisent autour de la Résistance.
CLEO_DE_5_A_7_1962|Cléo de 5 à 7|Cléo de 5 à 7|1962|90|FRANCE|AGNES_VARDA|DRAME|NOUVELLE_VAGUE_FRANCAISE,LEFT_BANK| |0.78|Deux heures dans la vie d'une chanteuse qui attend les résultats d'un examen médical.
# --- Silent ---
VOYAGE_DANS_LA_LUNE_1902|Le Voyage dans la Lune|Le Voyage dans la Lune|1902|14|FRANCE|GEORGES_MELIES|AVENTURE,SCIENCE_FICTION|CINEMA_MUET_MOUVEMENT,CINEMA_EXPERIMENTAL|se|0.55|Un obus chargé de savants atterrit dans l'œil de la Lune.
INTOLERANCE_1916|Intolerance|Intolérance|1916|197|USA|DW_GRIFFITH|DRAME,HISTORIQUE|CINEMA_MUET_MOUVEMENT,HOLLYWOOD_CLASSIQUE|s|0.82|Quatre époques croisent leurs récits d'injustice et de fanatisme.
LES_VAMPIRES_1915|Les Vampires|Les Vampires|1915|417|FRANCE|LOUIS_FEUILLADE|POLICIER,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.70|Un journaliste traque une bande criminelle qui règne sur Paris.
CABIRIA_1914|Cabiria|Cabiria|1914|181|ITALY|GIOVANNI_PASTRONE|HISTORIQUE,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.72|Une enfant enlevée durant les guerres puniques traverse le monde antique.
CABINET_DU_DOCTEUR_CALIGARI_1920|Das Cabinet des Dr. Caligari|Le Cabinet du docteur Caligari|1920|76|GERMANY|ROBERT_WIENE|HORREUR,THRILLER|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.86|Un hypnotiseur et son somnambule sèment le crime dans une ville déformée.
NOSFERATU_1922|Nosferatu, eine Symphonie des Grauens|Nosferatu|1922|94|GERMANY|FW_MURNAU|HORREUR|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.84|Un vampire quitte les Carpates pour contaminer une ville hanséatique.
LE_GOLEM_1920|Der Golem, wie er in die Welt kam|Le Golem|1920|85|GERMANY|PAUL_WEGENER|HORREUR,HISTORIQUE|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.70|Un rabbin de Prague façonne une créature d'argile pour protéger son peuple.
DOCTEUR_MABUSE_LE_JOUEUR_1922|Dr. Mabuse, der Spieler|Docteur Mabuse le joueur|1922|270|GERMANY|FRITZ_LANG|POLICIER,THRILLER|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.80|Un criminel aux mille visages manipule la république de Weimar.
LA_ROUE_1923|La Roue|La Roue|1923|273|FRANCE|ABEL_GANCE|DRAME,ROMANCE|IMPRESSIONNISME_FRANCAIS,CINEMA_MUET_MOUVEMENT|s|0.78|Un mécanicien élève l'orpheline d'un accident et voit le désir détruire sa famille.
MONTEUR_DE_SECURITE_1923|Safety Last!|Monte là-dessus !|1923|73|USA|HAROLD_LLOYD|COMEDIE|CINEMA_MUET_MOUVEMENT|s|0.58|Un employé de magasin grimpe une façade pour sauver sa place et son amour.
LES_RAPACES_1924|Greed|Les Rapaces|1924|140|USA|ERICH_VON_STROHEIM|DRAME|CINEMA_MUET_MOUVEMENT,HOLLYWOOD_CLASSIQUE|s|0.80|Un gain à la loterie empoisonne un couple jusqu'à la vallée de la Mort.
SHERLOCK_JUNIOR_1924|Sherlock Jr.|Sherlock Junior|1924|45|USA|BUSTER_KEATON|COMEDIE,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.72|Un projectionniste entre dans l'écran pour résoudre un crime et reconquérir sa fiancée.
LE_DERNIER_DES_HOMMES_1924|Der letzte Mann|Le Dernier des hommes|1924|90|GERMANY|FW_MURNAU|DRAME|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.83|Un portier d'hôtel déchu perd son uniforme et sa dignité.
ENTR_ACTE_1924|Entr'acte|Entr'acte|1924|22|FRANCE|RENE_CLAIR|COMEDIE|SURREALISME,CINEMA_EXPERIMENTAL,CINEMA_MUET_MOUVEMENT|se|0.88|Un ballet d'images absurdes interrompt un spectacle dadaïste.
BALLET_MECANIQUE_1924|Ballet mécanique|Ballet mécanique|1924|16|FRANCE|FERNAND_LEGER|ANIMATION|CINEMA_EXPERIMENTAL,CINEMA_MUET_MOUVEMENT|se|0.90|Objets, visages et machines dansent dans un rythme cubiste.
LE_CUIRASSE_POTEMKINE_1925|Броненосец Потёмкин|Le Cuirassé Potemkine|1925|75|RUSSIA|SERGEI_EISENSTEIN|GUERRE,HISTORIQUE,DRAME|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.92|La mutinerie d'un cuirassé et le massacre d'Odessa deviennent un choc de plans.
LA_RUEE_VERS_LOR_1925|The Gold Rush|La Ruée vers l'or|1925|95|USA|CHARLIE_CHAPLIN|COMEDIE,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.70|Charlot cherche fortune au Klondike, entre famine, danse des petits pains et précipice.
LA_GREVE_1925|Стачка|La Grève|1925|82|RUSSIA|SERGEI_EISENSTEIN|DRAME,HISTORIQUE|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.85|Une révolte ouvrière est écrasée, montée comme une démonstration politique.
FAUST_1926|Faust|Faust|1926|107|GERMANY|FW_MURNAU|DRAME,HORREUR|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.84|Un savant vend son âme et traverse un monde d'ombres monumentales.
LE_MECANICIEN_DE_LA_GENERAL_1926|The General|Le Mécano de la General|1926|78|USA|BUSTER_KEATON|COMEDIE,GUERRE,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.68|Un mécanicien récupère sa locomotive et sa fiancée derrière les lignes ennemies.
UNE_PAGE_FOLLE_1926|狂った一頁|Une page folle|1926|70|JAPAN|TEINOSUKE_KINUGASA|HORREUR,DRAME|CINEMA_EXPERIMENTAL,CINEMA_MUET_MOUVEMENT,AGE_OR_CINEMA_JAPONAIS|se|0.90|Un homme se fait embaucher dans l'asile où sa femme a été internée.
METROPOLIS_1927|Metropolis|Metropolis|1927|153|GERMANY|FRITZ_LANG|SCIENCE_FICTION,DRAME|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.88|Dans une ville verticale, un fils de maître descend vers les ouvriers de l'enfer industriel.
L_AURORE_1927|Sunrise: A Song of Two Humans|L'Aurore|1927|94|USA|FW_MURNAU|DRAME,ROMANCE|HOLLYWOOD_CLASSIQUE,CINEMA_MUET_MOUVEMENT|s|0.90|Un paysan tenté par le meurtre retrouve le chemin de l'amour conjugal.
NAPOLEON_1927|Napoléon|Napoléon|1927|333|FRANCE|ABEL_GANCE|HISTORIQUE,GUERRE,DRAME|IMPRESSIONNISME_FRANCAIS,CINEMA_MUET_MOUVEMENT|s|0.86|La jeunesse de Bonaparte jusqu'à la campagne d'Italie, en polyvision monumentale.
OCTOBRE_1928|Октябрь|Octobre|1928|104|RUSSIA|SERGEI_EISENSTEIN|HISTORIQUE,DRAME|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.88|La révolution de 1917 racontée par le choc des masses et des symboles.
LA_PASSION_DE_JEANNE_DARC_1928|La Passion de Jeanne d'Arc|La Passion de Jeanne d'Arc|1928|82|FRANCE|CARL_THEODOR_DREYER|HISTORIQUE,DRAME|CINEMA_D_AUTEUR,CINEMA_MUET_MOUVEMENT|s|0.95|Le procès de Jeanne, collé aux visages, jusqu'au bûcher.
STEAMBOAT_BILL_JR_1928|Steamboat Bill, Jr.|Steamboat Bill Jr.|1928|71|USA|BUSTER_KEATON|COMEDIE|CINEMA_MUET_MOUVEMENT|s|0.64|Un fils fluet doit sauver le bateau de son père au milieu d'une tornade.
LA_FOULE_1928|The Crowd|La Foule|1928|98|USA|KING_VIDOR|DRAME|HOLLYWOOD_CLASSIQUE,CINEMA_MUET_MOUVEMENT|s|0.78|Un employé anonyme de New York voit le rêve américain se diluer dans la masse.
L_HOMME_A_LA_CAMERA_1929|Человек с киноаппаратом|L'Homme à la caméra|1929|68|RUSSIA|DZIGA_VERTOV|DOCUMENTAIRE|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_EXPERIMENTAL,DOCUMENTAIRE_POETIQUE,CINEMA_MUET_MOUVEMENT|se|0.93|Une ville soviétique saisie par l'œil mécanique du ciné-œil.
LA_BOITE_DE_PANDORE_1929|Die Büchse der Pandora|Lulu|1929|109|GERMANY|GW_PABST|DRAME|CINEMA_MUET_MOUVEMENT|s|0.80|Lulu attire et détruit ceux qui l'aiment, jusqu'à Jack l'Éventreur.
UN_CHIEN_ANDALOU_1929|Un chien andalou|Un chien andalou|1929|16|FRANCE|LUIS_BUNUEL|HORREUR|SURREALISME,CINEMA_EXPERIMENTAL,CINEMA_MUET_MOUVEMENT|se|0.95|Une suite de chocs oniriques, de l'œil tranché au piano chargé de ânes.
LES_LUMIERES_DE_LA_VILLE_1931|City Lights|Les Lumières de la ville|1931|87|USA|CHARLIE_CHAPLIN|COMEDIE,ROMANCE|CINEMA_MUET_MOUVEMENT|s|0.72|Charlot aide une fleuriste aveugle et affronte un millionnaire lunatique.
JE_SUIS_NE_MAIS_1932|大人の見る絵本 生れてはみたけれど|Je suis né, mais...|1932|100|JAPAN|YASUJIRO_OZU|COMEDIE,DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_MUET_MOUVEMENT|s|0.80|Deux frères découvrent la lâcheté sociale de leur père.
LES_TEMPS_MODERNES_1936|Modern Times|Les Temps modernes|1936|87|USA|CHARLIE_CHAPLIN|COMEDIE,DRAME|CINEMA_MUET_MOUVEMENT|s|0.74|Charlot est avalé par l'usine, puis par la crise, sans jamais parler.
# --- Japan ---
RASHOMON_1950|羅生門|Rashōmon|1950|88|JAPAN|AKIRA_KUROSAWA|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI,CINEMA_D_AUTEUR|b|0.90|Un crime dans la forêt est raconté par quatre voix incompatibles.
VIVRE_1952|生きる|Vivre|1952|143|JAPAN|AKIRA_KUROSAWA|DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_D_AUTEUR|b|0.82|Un bureaucrate mourant décide de laisser un parc derrière lui.
LE_CHATEAU_DE_L_ARAIGNEE_1957|蜘蛛巣城|Le Château de l'araignée|1957|110|JAPAN|AKIRA_KUROSAWA|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI|b|0.84|Macbeth transplanté dans le Japon féodal, entre brume et trahison.
YOJIMBO_1961|用心棒|Yojimbo|1961|110|JAPAN|AKIRA_KUROSAWA|AVENTURE,COMEDIE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI|b|0.70|Un rōnin joue deux clans l'un contre l'autre dans une ville pourrie.
ENTRE_LE_CIEL_ET_L_ENFER_1963|天国と地獄|Entre le ciel et l'enfer|1963|143|JAPAN|AKIRA_KUROSAWA|POLICIER,DRAME|AGE_OR_CINEMA_JAPONAIS|b|0.78|Un industriel doit choisir entre payer la rançon d'un enfant qui n'est pas le sien et ruiner son emprise.
KAGEMUSHA_1980|影武者|Kagemusha, l'ombre du guerrier|1980|180|JAPAN|AKIRA_KUROSAWA|HISTORIQUE,DRAME,GUERRE|JIDAIGEKI,CINEMA_D_AUTEUR|c|0.82|Un voleur est forcé de jouer le double d'un seigneur mourant.
RAN_1985|乱|Ran|1985|162|JAPAN|AKIRA_KUROSAWA|DRAME,HISTORIQUE,GUERRE|JIDAIGEKI,CINEMA_D_AUTEUR|c|0.88|Un seigneur divise son domaine entre ses fils et contemple la ruine du monde.
VOYAGE_A_TOKYO_1953|東京物語|Voyage à Tokyo|1953|136|JAPAN|YASUJIRO_OZU|DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_D_AUTEUR|b|0.90|Des parents visitent leurs enfants à Tokyo et mesurent la tiédeur des liens.
PRINTEMPS_TARDIF_1949|晩春|Printemps tardif|1949|108|JAPAN|YASUJIRO_OZU|DRAME|AGE_OR_CINEMA_JAPONAIS|b|0.84|Une fille s'occupe de son père veuf jusqu'à ce que le mariage vienne rompre l'équilibre.
HERBES_FLOTTANTES_1959|浮草|Herbes flottantes|1959|119|JAPAN|YASUJIRO_OZU|DRAME|AGE_OR_CINEMA_JAPONAIS|c|0.80|Une troupe de kabuki de province réveille d'anciennes amours et un fils caché.
LE_GOUT_DU_SAKE_1962|秋刀魚の味|Le Goût du saké|1962|113|JAPAN|YASUJIRO_OZU|DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_D_AUTEUR|c|0.82|Un veuf marier sa fille et se retrouve seul avec ses habitudes de bureau et de bar.
LES_CONTES_DE_LA_LUNE_VAGUE_1953|雨月物語|Les Contes de la lune vague après la pluie|1953|96|JAPAN|KENJI_MIZOGUCHI|DRAME,HORREUR,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI,CINEMA_D_AUTEUR|b|0.92|Deux potiers quittent leur village en guerre et croisent fantômes et convoitises.
L_INTENDANT_SANSHO_1954|山椒大夫|L'Intendant Sansho|1954|124|JAPAN|KENJI_MIZOGUCHI|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI,MELODRAME|b|0.90|Une famille déchue est réduite en esclavage et cherche à retrouver sa dignité.
LA_VIE_D_OHARU_1952|西鶴一代女|La Vie d'Oharu femme galante|1952|136|JAPAN|KENJI_MIZOGUCHI|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,MELODRAME|b|0.88|La descente d'une dame de cour vers la prostitution, racontée sans consolation.
LA_RUE_DE_LA_HONTE_1956|赤線地帯|La Rue de la honte|1956|85|JAPAN|KENJI_MIZOGUCHI|DRAME|AGE_OR_CINEMA_JAPONAIS|b|0.76|Plusieurs femmes d'une maison close de Tokyo voient approcher l'interdiction de leur métier.
HARA_KIRI_1962|切腹|Hara-kiri|1962|133|JAPAN|MASAKI_KOBAYASHI|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI|b|0.90|Un rōnin vient demander le droit de se tuer et démonte l'honneur d'un clan.
LA_CONDITION_DE_L_HOMME_1959|人間の條件 第1部|La Condition de l'homme|1959|208|JAPAN|MASAKI_KOBAYASHI|GUERRE,DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS|b|0.86|Un pacifiste est envoyé en Mandchourie et voit l'armée dévorer toute morale.
LA_FEMME_DES_SABLES_1964|砂の女|La Femme des sables|1964|147|JAPAN|HIROSHI_TESHIGAHARA|DRAME,THRILLER|CINEMA_D_AUTEUR|b|0.88|Un entomologiste se retrouve prisonnier d'une fosse de sable avec une inconnue.
GODZILLA_1954|ゴジラ|Godzilla|1954|96|JAPAN|ISHIRO_HONDA|SCIENCE_FICTION,HORREUR|AGE_OR_CINEMA_JAPONAIS|b|0.60|Une créature née des essais nucléaires ravage Tokyo.
LE_VOYAGE_DE_CHIHIRO_2001|千と千尋の神隠し|Le Voyage de Chihiro|2001|125|JAPAN|HAYAO_MIYAZAKI|ANIMATION,AVENTURE,DRAME|ANIMATION_DAUTEUR|c|0.70|Une fillette doit travailler dans un monde d'esprits pour sauver ses parents.
PRINCESSE_MONONOKE_1997|もののけ姫|Princesse Mononoké|1997|134|JAPAN|HAYAO_MIYAZAKI|ANIMATION,AVENTURE,DRAME|ANIMATION_DAUTEUR|c|0.72|Un prince maudit s'interpose entre la forge humaine et les dieux de la forêt.
QUAND_UNE_FEMME_MONTE_L_ESCALIER_1960|女が階段を上る時|Quand une femme monte l'escalier|1960|111|JAPAN|MIKIO_NARUSE|DRAME|AGE_OR_CINEMA_JAPONAIS,MELODRAME|b|0.78|Une hôtesse de bar de Ginza tente de rester indépendante sans s'offrir tout à fait.
# --- France ---
L_ATALANTE_1934|L'Atalante|L'Atalante|1934|89|FRANCE|JEAN_VIGO|DRAME,ROMANCE|CINEMA_D_AUTEUR,REALISME_POETIQUE|b|0.88|Un couple de péniche dérive entre le désir, la ville et le brouillard de la Seine.
LA_GRANDE_ILLUSION_1937|La Grande Illusion|La Grande Illusion|1937|114|FRANCE|JEAN_RENOIR|GUERRE,DRAME|REALISME_POETIQUE,CINEMA_D_AUTEUR|b|0.90|Des officiers prisonniers traversent les classes sociales plus sûrement que les frontières.
LA_REGLE_DU_JEU_1939|La Règle du jeu|La Règle du jeu|1939|110|FRANCE|JEAN_RENOIR|COMEDIE,DRAME|REALISME_POETIQUE,CINEMA_D_AUTEUR|b|0.95|Une partie de campagne tourne au massacre mondain des sentiments et des conventions.
LE_QUAI_DES_BRUMES_1938|Le Quai des brumes|Le Quai des brumes|1938|91|FRANCE|MARCEL_CARNE|DRAME,ROMANCE|REALISME_POETIQUE|b|0.78|Un déserteur croise une orpheline dans le brouillard du Havre.
LE_JOUR_SE_LEVE_1939|Le Jour se lève|Le Jour se lève|1939|93|FRANCE|MARCEL_CARNE|DRAME,POLICIER|REALISME_POETIQUE|b|0.80|Un ouvrier retranché raconte la nuit qui l'a mené au meurtre.
LES_ENFANTS_DU_PARADIS_1945|Les Enfants du paradis|Les Enfants du paradis|1945|190|FRANCE|MARCEL_CARNE|DRAME,ROMANCE,HISTORIQUE|REALISME_POETIQUE|b|0.88|Le boulevard du Crime, ses acteurs et une femme que tous désirent.
LE_SALAIRE_DE_LA_PEUR_1953|Le Salaire de la peur|Le Salaire de la peur|1953|153|FRANCE|HENRI_GEORGES_CLOUZOT|THRILLER,AVENTURE|CINEMA_D_AUTEUR|b|0.74|Quatre hommes convoyent de la nitroglycérine sur une piste pourrie.
LES_DIABOLIQUES_1955|Les Diaboliques|Les Diaboliques|1955|117|FRANCE|HENRI_GEORGES_CLOUZOT|THRILLER,HORREUR|CINEMA_D_AUTEUR|b|0.70|Deux femmes noient un tyran, puis le cadavre refuse de rester à sa place.
UN_CONDAMNE_A_MORT_S_EST_ECHAPPE_1956|Un condamné à mort s'est échappé|Un condamné à mort s'est échappé|1956|101|FRANCE|ROBERT_BRESSON|DRAME,GUERRE|CINEMA_D_AUTEUR|b|0.90|Un résistant prépare son évasion avec une précision de rituel.
PICKPOCKET_1959|Pickpocket|Pickpocket|1959|75|FRANCE|ROBERT_BRESSON|DRAME,POLICIER|CINEMA_D_AUTEUR|b|0.88|Un jeune homme fait du vol à la tire une vocation solitaire.
AU_HASARD_BALTHAZAR_1966|Au hasard Balthazar|Au hasard Balthazar|1966|95|FRANCE|ROBERT_BRESSON|DRAME|CINEMA_D_AUTEUR|b|0.92|La vie d'un âne passe de main en main, entre grâce et cruauté.
MOUCHETTE_1967|Mouchette|Mouchette|1967|81|FRANCE|ROBERT_BRESSON|DRAME|CINEMA_D_AUTEUR|b|0.86|Une adolescente de campagne encaisse les coups jusqu'au bord de l'eau.
LES_QUATRE_CENTS_COUPS_1959|Les Quatre Cents Coups|Les Quatre Cents Coups|1959|99|FRANCE|FRANCOIS_TRUFFAUT|DRAME|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|b|0.80|Antoine Doinel fuit l'école, la famille et finit face à la mer.
A_BOUT_DE_SOUFFLE_1960|À bout de souffle|À bout de souffle|1960|90|FRANCE|JEAN_LUC_GODARD|POLICIER,DRAME,ROMANCE|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|b|0.86|Un petit voyou et une Américaine improvisent l'amour et la fuite à Paris.
LE_MEPRIS_1963|Le Mépris|Le Mépris|1963|103|FRANCE|JEAN_LUC_GODARD|DRAME,ROMANCE|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|c|0.84|Un couple se défait sur le tournage d'une Odyssée à Capri.
PIERROT_LE_FOU_1965|Pierrot le fou|Pierrot le fou|1965|110|FRANCE|JEAN_LUC_GODARD|DRAME,AVENTURE,ROMANCE|NOUVELLE_VAGUE_FRANCAISE|c|0.82|Ferdinand et Marianne prennent la route jusqu'à l'explosion.
JULES_ET_JIM_1962|Jules et Jim|Jules et Jim|1962|105|FRANCE|FRANCOIS_TRUFFAUT|DRAME,ROMANCE|NOUVELLE_VAGUE_FRANCAISE|b|0.78|Deux amis et Catherine inventent une liberté qui les blesse.
LA_NUIT_AMERICAINE_1973|La Nuit américaine|La Nuit américaine|1973|115|FRANCE|FRANCOIS_TRUFFAUT|COMEDIE,DRAME|NOUVELLE_VAGUE_FRANCAISE|c|0.70|Un tournage devient le vrai sujet du film, entre accidents et tendresse.
HIROSHIMA_MON_AMOUR_1959|Hiroshima mon amour|Hiroshima mon amour|1959|90|FRANCE|ALAIN_RESNAIS|DRAME,ROMANCE,GUERRE|NOUVELLE_VAGUE_FRANCAISE,LEFT_BANK|b|0.90|Une actrice et un Japonais superposent Nevers et Hiroshima.
L_ANNEE_DERNIERE_A_MARIENBAD_1961|L'Année dernière à Marienbad|L'Année dernière à Marienbad|1961|94|FRANCE|ALAIN_RESNAIS|DRAME,ROMANCE|LEFT_BANK,CINEMA_EXPERIMENTAL,CINEMA_D_AUTEUR|be|0.95|Dans un palace, un homme affirme qu'une femme lui a déjà promis de partir.
MON_ONCLE_1958|Mon oncle|Mon oncle|1958|117|FRANCE|JACQUES_TATI|COMEDIE|CINEMA_D_AUTEUR|c|0.72|M. Hulot dérègle la villa moderne de sa sœur et répare le vieux quartier.
PLAYTIME_1967|PlayTime|Playtime|1967|124|FRANCE|JACQUES_TATI|COMEDIE|CINEMA_D_AUTEUR|c|0.88|Hulot se perd dans un Paris de verre où les gags naissent de l'architecture.
ORPHEE_1950|Orphée|Orphée|1950|95|FRANCE|JEAN_COCTEAU|DRAME,AVENTURE|SURREALISME,CINEMA_D_AUTEUR|b|0.80|Un poète suit la Mort à travers les miroirs.
LA_BELLE_ET_LA_BETE_1946|La Belle et la Bête|La Belle et la Bête|1946|93|FRANCE|JEAN_COCTEAU|ROMANCE,AVENTURE|SURREALISME|b|0.76|Belle accepte le château d'une bête pour sauver son père.
LA_JETEE_1962|La Jetée|La Jetée|1962|28|FRANCE|CHRIS_MARKER|SCIENCE_FICTION,DRAME|LEFT_BANK,CINEMA_EXPERIMENTAL|b|0.92|Un homme est renvoyé dans le temps à partir d'une image de jetée.
SANS_SOLEIL_1983|Sans soleil|Sans soleil|1983|100|FRANCE|CHRIS_MARKER|DOCUMENTAIRE|LEFT_BANK,DOCUMENTAIRE_POETIQUE,CINEMA_EXPERIMENTAL|c|0.90|Lettres filmées du Japon, de Guinée-Bissau et de la mémoire.
LE_SAMOURAI_1967|Le Samouraï|Le Samouraï|1967|105|FRANCE|JEAN_PIERRE_MELVILLE|POLICIER,THRILLER|NEO_NOIR,CINEMA_D_AUTEUR|c|0.80|Un tueur à gages solitaire voit son rituel se fissurer après un contrat.
PORTRAIT_DE_LA_JEUNE_FILLE_EN_FEU_2019|Portrait de la jeune fille en feu|Portrait de la jeune fille en feu|2019|122|FRANCE|CELINE_SCIAMMA|DRAME,ROMANCE|CINEMA_D_AUTEUR|c|0.74|Une peintre et sa modèle s'aiment en secret sur une île bretonne.
# --- Italy auteurs / neorealism ---
PAISA_1946|Paisà|Paisà|1946|120|ITALY|ROBERTO_ROSSELLINI|GUERRE,DRAME|NEOREALISME_ITALIEN|b|0.82|Six épisodes suivent la remontée des Alliés dans l'Italie libérée.
LE_VOLEUR_DE_BICYCLETTE_1948|Ladri di biciclette|Le Voleur de bicyclette|1948|89|ITALY|VITTORIO_DE_SICA|DRAME|NEOREALISME_ITALIEN|b|0.90|Un chômeur et son fils cherchent la bicyclette sans laquelle le travail s'évapore.
UMBERTO_D_1952|Umberto D.|Umberto D.|1952|89|ITALY|VITTORIO_DE_SICA|DRAME|NEOREALISME_ITALIEN|b|0.86|Un retraité et sa chienne tiennent contre l'expulsion et l'indifférence.
LA_STRADA_1954|La strada|La Strada|1954|108|ITALY|FEDERICO_FELLINI|DRAME|CINEMA_D_AUTEUR,NEOREALISME_ITALIEN|b|0.80|Gelsomina suit un hercule de foire sur les routes et y laisse son âme.
LA_DOLCE_VITA_1960|La dolce vita|La Dolce Vita|1960|174|ITALY|FEDERICO_FELLINI|DRAME|CINEMA_D_AUTEUR|b|0.82|Un journaliste dérive de fête en fête dans la Rome mondaine.
HUIT_ET_DEMI_1963|8½|Huit et demi|1963|138|ITALY|FEDERICO_FELLINI|DRAME,COMEDIE|CINEMA_D_AUTEUR|b|0.90|Un metteur en scène en panne se réfugie dans souvenirs, fantasmes et plateau.
L_AVVENTURA_1960|L'avventura|L'Avventura|1960|143|ITALY|MICHELANGELO_ANTONIONI|DRAME|CINEMA_D_AUTEUR|b|0.88|Une femme disparaît sur une île et le désir des autres continue sans elle.
LE_GUEPARD_1963|Il Gattopardo|Le Guépard|1963|186|ITALY|LUCHINO_VISCONTI|DRAME,HISTORIQUE|CINEMA_D_AUTEUR,MELODRAME|c|0.88|Un prince sicilien voit 1860 emporter sa classe tout en dansant encore.
LE_CONFORMISTE_1970|Il conformista|Le Conformiste|1970|113|ITALY|BERNARDO_BERTOLUCCI|DRAME,THRILLER|CINEMA_D_AUTEUR|c|0.84|Un homme cherche l'ordre fasciste pour étouffer une faute d'enfance.
LA_BATAILLE_D_ALGER_1966|La battaglia di Algeri|La Bataille d'Alger|1966|121|ITALY,ALGERIA|GILLO_PONTECORVO|GUERRE,HISTORIQUE,DRAME|THIRD_CINEMA|b|0.88|La casbah organise l'insurrection pendant que l'armée française répond par la torture.
NOVECENTO_1976|Novecento|1900|1976|317|ITALY|BERNARDO_BERTOLUCCI|DRAME,HISTORIQUE|CINEMA_D_AUTEUR|c|0.80|Deux enfants nés le même jour, l'un padrone, l'autre paysan, traversent le siècle italien.
# --- Spaghetti western ---
POUR_UNE_POIGNEE_DE_DOLLARS_1964|Per un pugno di dollari|Pour une poignée de dollars|1964|99|ITALY|SERGIO_LEONE|WESTERN|SPAGHETTI_WESTERN|c|0.62|Un étranger joue deux familles l'une contre l'autre dans un village de la frontière.
ET_POUR_QUELQUES_DOLLARS_DE_PLUS_1965|Per qualche dollaro in più|Et pour quelques dollars de plus|1965|132|ITALY|SERGIO_LEONE|WESTERN|SPAGHETTI_WESTERN|c|0.64|Deux chasseurs de primes poursuivent le même bandit.
LE_BON_LA_BRUTE_ET_LE_TRUAND_1966|Il buono, il brutto, il cattivo|Le Bon, la Brute et le Truand|1966|178|ITALY|SERGIO_LEONE|WESTERN|SPAGHETTI_WESTERN|c|0.70|Trois hommes courent après un trésor enfoui pendant la guerre de Sécession.
IL_ETAIT_UNE_FOIS_DANS_L_OUEST_1968|C'era una volta il West|Il était une fois dans l'Ouest|1968|165|ITALY|SERGIO_LEONE|WESTERN,DRAME|SPAGHETTI_WESTERN|c|0.78|Le chemin de fer, une veuve et un homme à l'harmonica attendent un règlement de comptes.
IL_ETAIT_UNE_FOIS_LA_REVOLUTION_1971|Giù la testa|Il était une fois la révolution|1971|157|ITALY|SERGIO_LEONE|WESTERN,GUERRE|SPAGHETTI_WESTERN|c|0.72|Un voleur et un dynamiteur irlandais se heurtent à la révolution mexicaine.
DJANGO_1966|Django|Django|1966|91|ITALY|SERGIO_CORBUCCI|WESTERN|SPAGHETTI_WESTERN|c|0.60|Un homme traîne un cercueil dans la boue et en sort une mitrailleuse.
LE_GRAND_SILENCE_1968|Il grande silenzio|Le Grand Silence|1968|105|ITALY|SERGIO_CORBUCCI|WESTERN,DRAME|SPAGHETTI_WESTERN|c|0.80|Dans la neige, un pistolero muet affronte des chasseurs de primes.
LE_MERCENAIRE_1968|Il mercenario|Le Mercenaire|1968|105|ITALY|SERGIO_CORBUCCI|WESTERN|SPAGHETTI_WESTERN|c|0.58|Un Polonais cynique et un révolutionnaire mexicain font alliance pour de l'or.
COMPANEROS_1970|Vamos a matar, compañeros|Compañeros|1970|118|ITALY|SERGIO_CORBUCCI|WESTERN,COMEDIE|SPAGHETTI_WESTERN|c|0.55|Un trafiquant d'armes et un paysan se retrouvent malgré eux dans la révolution.
COLORADO_1966|La resa dei conti|Colorado|1966|105|ITALY|SERGIO_SOLLIMA|WESTERN|SPAGHETTI_WESTERN|c|0.66|Un chasseur de primes poursuit un suspect et découvre une autre injustice.
FACE_A_FACE_1967|Faccia a faccia|Face à face|1967|112|ITALY|SERGIO_SOLLIMA|WESTERN,DRAME|SPAGHETTI_WESTERN|c|0.68|Un professeur se radicalise au contact d'un hors-la-loi.
LA_MORT_ETAIT_AU_RENDEZ_VOUS_1967|Da uomo a uomo|La Mort était au rendez-vous|1967|120|ITALY|GIULIO_PETRONI|WESTERN|SPAGHETTI_WESTERN|c|0.60|Un jeune homme et un tueur d'élite traquent le même massacreur.
KEOMA_1976|Keoma|Keoma|1976|101|ITALY|ENZO_G_CASTELLARI|WESTERN|SPAGHETTI_WESTERN|c|0.58|Un métis revient dans une ville de peste et affronte ses demi-frères.
MON_NOM_EST_PERSONNE_1973|Il mio nome è Nessuno|Mon nom est Personne|1973|116|ITALY|TONINO_VALERII|WESTERN,COMEDIE|SPAGHETTI_WESTERN|c|0.56|Un jeune admirateur pousse un vieux gunfighter vers une dernière légende.
ON_L_APPELLE_TRINITE_1970|Lo chiamavano Trinità|On l'appelle Trinità|1970|113|ITALY|ENZO_BARBONI|WESTERN,COMEDIE|SPAGHETTI_WESTERN|c|0.48|Deux frères paresseux défont une bande sans presque se lever.
# --- Commedia all'italiana ---
LE_PIGEON_1958|I soliti ignoti|Le Pigeon|1958|111|ITALY|MARIO_MONICELLI|COMEDIE,POLICIER|COMMEDIA_ALL_ITALIANA|b|0.70|Un casse amateur à Rome tourne à la catastrophe joyeuse.
LA_GRANDE_GUERRE_1959|La grande guerra|La Grande Guerre|1959|137|ITALY|MARIO_MONICELLI|COMEDIE,GUERRE|COMMEDIA_ALL_ITALIANA|b|0.72|Deux tirailleurs tentent d'éviter le front et y trouvent une autre bravoure.
L_ARMEE_BRANCALEONE_1966|L'armata Brancaleone|L'Armée Brancaleone|1966|120|ITALY|MARIO_MONICELLI|COMEDIE,AVENTURE,HISTORIQUE|COMMEDIA_ALL_ITALIANA|c|0.64|Un chevalier médiocre mène une troupe de miséreux à travers l'Italie du Moyen Âge.
MES_CHERS_AMIS_1975|Amici miei|Mes chers amis|1975|140|ITALY|MARIO_MONICELLI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.66|Des bourgeois toscans se vengent de l'âge par des farces cruelles.
DIVORCE_A_L_ITALIENNE_1961|Divorzio all'italiana|Divorce à l'italienne|1961|105|ITALY|PIETRO_GERMI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|b|0.74|En Sicile, un baron préfère le crime d'honneur au divorce impossible.
SEDUITE_ET_ABANDONNEE_1964|Sedotta e abbandonata|Séduite et abandonnée|1964|115|ITALY|PIETRO_GERMI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|b|0.72|Une famille sicilienne veut laver l'honneur d'une fille en forçant le mariage.
LE_FANFARON_1962|Il sorpasso|Le Fanfaron|1962|105|ITALY|DINO_RISI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA,ROAD_MOVIE|b|0.78|Un beau parleur entraîne un étudiant dans une virée qui va trop vite.
UNE_VIE_DIFFICILE_1961|Una vita difficile|Une vie difficile|1961|118|ITALY|DINO_RISI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|b|0.70|Un résistant devient journaliste et se perd dans l'Italie du miracle économique.
PARFUM_DE_FEMME_1974|Profumo di donna|Parfum de femme|1974|103|ITALY|DINO_RISI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.62|Un capitaine aveugle et son ordonnance descendent vers Naples et une épreuve.
UNE_JOURNEE_PARTICULIERE_1977|Una giornata particolare|Une journée particulière|1977|106|ITALY|ETTORE_SCOLA|DRAME|COMMEDIA_ALL_ITALIANA,CINEMA_D_AUTEUR|c|0.80|Le jour de la visite d'Hitler, une ménagère et un voisin ostracisé se parlent enfin.
NOUS_NOUS_SOMMES_TANT_AIMES_1974|C'eravamo tanto amati|Nous nous sommes tant aimés|1974|124|ITALY|ETTORE_SCOLA|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.74|Trois amis de la Résistance se retrouvent trente ans plus tard, aigris et complices.
MIMI_METALLO_BLESSE_DANS_SON_HONNEUR_1972|Mimì metallurgico ferito nell'onore|Mimì métallo blessé dans son honneur|1972|108|ITALY|LINA_WERTMULLER|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.66|Un ouvrier sicilien émigré à Turin croise syndicat, honneur et jalousie.
PAIN_ET_CHOCOLAT_1973|Pane e cioccolata|Pain et chocolat|1973|111|ITALY|FRANCO_BRUSATI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.64|Un émigré italien en Suisse accumule les humiliations pour rester.
L_ARGENT_DE_LA_VIEILLE_1972|Lo scopone scientifico|L'Argent de la vieille|1972|121|ITALY|LUIGI_COMENCINI|COMEDIE,DRAME|COMMEDIA_ALL_ITALIANA|c|0.68|Une milliardaire américaine défie un couple pauvre au scopone.
LES_MONSTRES_1963|I mostri|Les Monstres|1963|115|ITALY|DINO_RISI|COMEDIE|COMMEDIA_ALL_ITALIANA|b|0.70|Une mosaïque de sketches dresse le portrait féroce de l'Italie bourgeoise.
# --- USA ---
CITIZEN_KANE_1941|Citizen Kane|Citizen Kane|1941|119|USA|ORSON_WELLES|DRAME|HOLLYWOOD_CLASSIQUE,CINEMA_D_AUTEUR|b|0.95|Un magnat de la presse meurt en murmurant Rosebud, et l'enquête reconstitue un empire vide.
CASABLANCA_1942|Casablanca|Casablanca|1942|102|USA|MICHAEL_CURTIZ|DRAME,ROMANCE,GUERRE|HOLLYWOOD_CLASSIQUE|b|0.62|Dans un café de Maroc, un Américain revoit celle qu'il a perdue à Paris.
AUTANT_EN_EMPORTE_LE_VENT_1939|Gone with the Wind|Autant en emporte le vent|1939|238|USA|VICTOR_FLEMING|DRAME,ROMANCE,HISTORIQUE,GUERRE|HOLLYWOOD_CLASSIQUE,MELODRAME|c|0.55|Scarlett O'Hara traverse la guerre de Sécession en refusant de céder.
LE_MAGICIEN_D_OZ_1939|The Wizard of Oz|Le Magicien d'Oz|1939|102|USA|VICTOR_FLEMING|AVENTURE,MUSICAL|HOLLYWOOD_CLASSIQUE|c|0.50|Dorothy est emportée au-dessus de l'arc-en-ciel et veut seulement rentrer.
KING_KONG_1933|King Kong|King Kong|1933|100|USA|MERIAN_C_COOPER,ERNEST_B_SCHOEDSACK|AVENTURE,HORREUR|HOLLYWOOD_CLASSIQUE|b|0.58|Une expédition ramène un grand singe de l'île et le montre à New York.
NEW_YORK_MIAMI_1934|It Happened One Night|New York-Miami|1934|105|USA|FRANK_CAPRA|COMEDIE,ROMANCE|HOLLYWOOD_CLASSIQUE|b|0.55|Une héritière en fuite partage un bus et une chambre avec un journaliste.
L_IMPOSSIBLE_MONSIEUR_BEBE_1938|Bringing Up Baby|L'Impossible Monsieur Bébé|1938|102|USA|HOWARD_HAWKS|COMEDIE,ROMANCE|HOLLYWOOD_CLASSIQUE|b|0.60|Un paléontologue, une héritière et un léopard détruisent toute gravité.
HIS_GIRL_FRIDAY_1940|His Girl Friday|His Girl Friday|1940|92|USA|HOWARD_HAWKS|COMEDIE|HOLLYWOOD_CLASSIQUE|b|0.62|Un rédacteur en chef veut récupérer son ex-femme reporter avant son remariage.
LA_CHEVAUCHEE_FANTASTIQUE_1939|Stagecoach|La Chevauchée fantastique|1939|96|USA|JOHN_FORD|WESTERN,AVENTURE|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|b|0.72|Une diligence traverse le territoire apache avec un échantillon de société.
LES_RAISINS_DE_LA_COLERE_1940|The Grapes of Wrath|Les Raisins de la colère|1940|129|USA|JOHN_FORD|DRAME|HOLLYWOOD_CLASSIQUE|b|0.78|Les Joad quittent l'Oklahoma poussiéreux pour le mirage californien.
LE_FAUCON_MALTAIS_1941|The Maltese Falcon|Le Faucon maltais|1941|100|USA|JOHN_HUSTON|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.74|Sam Spade hérite d'une affaire et d'une statuette que tout le monde veut.
ASSURANCE_SUR_LA_MORT_1944|Double Indemnity|Assurance sur la mort|1944|107|USA|BILLY_WILDER|FILM_NOIR,POLICIER,THRILLER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.82|Un assureur et une cliente inventent un meurtre trop bien pensé.
LE_GRAND_SOMMEIL_1946|The Big Sleep|Le Grand Sommeil|1946|114|USA|HOWARD_HAWKS|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.76|Marlowe entre chez les Sternwood et ne comprend plus qui paie qui.
LES_ENCHAINES_1946|Notorious|Les Enchaînés|1946|101|USA|ALFRED_HITCHCOCK|THRILLER,ROMANCE,FILM_NOIR|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.80|Une femme est envoyée séduire un nazi, sous le regard d'un agent trop amoureux.
SORTILEGES_1947|Out of the Past|Sortilèges|1947|97|USA|JACQUES_TOURNEUR|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.84|Un homme tente de refaire sa vie jusqu'à ce que le passé le rattrape.
LA_DAME_DE_SHANGHAI_1947|The Lady from Shanghai|La Dame de Shanghai|1947|87|USA|ORSON_WELLES|FILM_NOIR,THRILLER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.82|Un marin s'embarque avec une femme fatale et finit dans un labyrinthe de glaces.
LA_RIVIERE_ROUGE_1948|Red River|La Rivière rouge|1948|133|USA|HOWARD_HAWKS|WESTERN,DRAME|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|b|0.70|Un drive de bétail oppose un père tyrannique à son fils adoptif.
BOULEVARD_DU_CREPUSCULE_1950|Sunset Boulevard|Boulevard du crépuscule|1950|110|USA|BILLY_WILDER|FILM_NOIR,DRAME|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.86|Un scénariste raconte, déjà mort, comment une gloire du muet l'a capturé.
EVE_1950|All About Eve|Eve|1950|138|USA|JOSEPH_L_MANKIEWICZ|DRAME|HOLLYWOOD_CLASSIQUE|b|0.72|Une admiratrice s'insinue dans la vie d'une star de théâtre jusqu'à la remplacer.
UN_TRAMWAY_NOMME_DESIR_1951|A Streetcar Named Desire|Un tramway nommé Désir|1951|122|USA|ELIA_KAZAN|DRAME|HOLLYWOOD_CLASSIQUE|b|0.74|Blanche DuBois se réfugie chez sa sœur et heurte Stanley Kowalski.
CHANTONS_SOUS_LA_PLUIE_1952|Singin' in the Rain|Chantons sous la pluie|1952|103|USA|STANLEY_DONEN,GENE_KELLY|MUSICAL,COMEDIE,ROMANCE|HOLLYWOOD_CLASSIQUE|c|0.58|Hollywood passe au parlant et un duo danse pour masquer les voix truquées.
LE_TRAIN_SIFFLERA_TROIS_FOIS_1952|High Noon|Le train sifflera trois fois|1952|85|USA|FRED_ZINNEMANN|WESTERN,THRILLER|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|b|0.68|Un shérif attend midi sans personne pour l'aider.
FENETRE_SUR_COUR_1954|Rear Window|Fenêtre sur cour|1954|112|USA|ALFRED_HITCHCOCK|THRILLER,POLICIER|HOLLYWOOD_CLASSIQUE|c|0.76|Un photographe plâtré croit voir un meurtre dans l'immeuble d'en face.
LA_PRISONNIERE_DU_DESERT_1956|The Searchers|La Prisonnière du désert|1956|119|USA|JOHN_FORD|WESTERN,DRAME|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|c|0.86|Ethan Edwards cherche sa nièce enlevée et ne sait plus s'il vient pour la sauver.
LA_NUIT_DU_CHASSEUR_1955|The Night of the Hunter|La Nuit du chasseur|1955|92|USA|CHARLES_LAUGHTON|THRILLER,HORREUR,DRAME,FILM_NOIR|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.90|Un prédicateur tatoué chasse deux enfants et l'argent cousu dans une poupée.
LA_FUREUR_DE_VIVRE_1955|Rebel Without a Cause|La Fureur de vivre|1955|111|USA|NICHOLAS_RAY|DRAME|HOLLYWOOD_CLASSIQUE|c|0.64|Jim Stark cherche une famille de substitution dans la banlieue californienne.
SUEURS_FROIDES_1958|Vertigo|Sueurs froides|1958|128|USA|ALFRED_HITCHCOCK|THRILLER,ROMANCE|HOLLYWOOD_CLASSIQUE,CINEMA_D_AUTEUR|c|0.90|Un policier acrophobe est chargé de suivre une femme qui n'existe peut-être pas.
LA_SOIF_DU_MAL_1958|Touch of Evil|La Soif du mal|1958|110|USA|ORSON_WELLES|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.88|À la frontière, une bombe dans une voiture ouvre une enquête pourrie.
CERTAINS_L_AIMENT_CHAUD_1959|Some Like It Hot|Certains l'aiment chaud|1959|121|USA|BILLY_WILDER|COMEDIE,MUSICAL|HOLLYWOOD_CLASSIQUE|b|0.58|Deux musiciens se déguisent en femmes pour fuir la pègre.
PSYCHOSE_1960|Psycho|Psychose|1960|109|USA|ALFRED_HITCHCOCK|HORREUR,THRILLER|HOLLYWOOD_CLASSIQUE|b|0.78|Marion Crane s'arrête au motel Bates et l'histoire change de protagoniste.
LA_GARCONNIERE_1960|The Apartment|La Garçonnière|1960|125|USA|BILLY_WILDER|COMEDIE,DRAME,ROMANCE|HOLLYWOOD_CLASSIQUE|b|0.70|Un employé prête son appartement aux chefs et y trouve une femme brisée.
DOUZE_HOMMES_EN_COLERE_1957|12 Angry Men|Douze hommes en colère|1957|96|USA|SIDNEY_LUMET|DRAME,POLICIER|CINEMA_D_AUTEUR|b|0.72|Un juré refuse de voter coupable et force onze hommes à reparler.
EN_QUATRIEME_VITESSE_1956|The Killing|L'Ultime Razzia|1956|84|USA|STANLEY_KUBRICK|FILM_NOIR,POLICIER|FILM_NOIR_STYLE,CINEMA_D_AUTEUR|b|0.80|Un casse à l'hippodrome est raconté comme une mécanique qui se dérègle.
SUR_LES_QUAIS_1954|On the Waterfront|Sur les quais|1954|108|USA|ELIA_KAZAN|DRAME,POLICIER|HOLLYWOOD_CLASSIQUE|b|0.68|Un docker doit décider s'il parle contre le syndicat qui l'a fait boxeur.
GILDA_1946|Gilda|Gilda|1946|110|USA|CHARLES_VIDOR|FILM_NOIR,DRAME,ROMANCE|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.70|À Buenos Aires, une femme chante et un homme refuse d'admettre qu'il l'aime.
QUAND_LA_VILLE_DORT_1950|The Asphalt Jungle|Quand la ville dort|1950|112|USA|JOHN_HUSTON|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.76|Un casse scientifique se défait dès que les hommes retrouvent leurs faiblesses.
REGLEMENT_DE_COMPTES_1955|Kiss Me Deadly|En quatrième vitesse|1955|106|USA|ROBERT_ALDRICH|FILM_NOIR,THRILLER|FILM_NOIR_STYLE|b|0.80|Mike Hammer ouvre une boîte qui n'aurait dû rester fermée.
LE_PARRAIN_1972|The Godfather|Le Parrain|1972|175|USA|FRANCIS_FORD_COPPOLA|DRAME,POLICIER|NEW_HOLLYWOOD,CINEMA_D_AUTEUR|c|0.78|Michael Corleone voulait rester en dehors et devient le don.
LE_PARRAIN_2_1974|The Godfather Part II|Le Parrain 2|1974|202|USA|FRANCIS_FORD_COPPOLA|DRAME,POLICIER|NEW_HOLLYWOOD,CINEMA_D_AUTEUR|c|0.84|Le pouvoir de Michael et la jeunesse de Vito se répondent.
TAXI_DRIVER_1976|Taxi Driver|Taxi Driver|1976|114|USA|MARTIN_SCORSESE|DRAME,THRILLER|NEW_HOLLYWOOD,NEO_NOIR,CINEMA_D_AUTEUR|c|0.82|Travis Bickle ramène la nuit new-yorkaise jusqu'à la violence.
CHINATOWN_1974|Chinatown|Chinatown|1974|130|USA|ROMAN_POLANSKI|FILM_NOIR,POLICIER,THRILLER|NEW_HOLLYWOOD,NEO_NOIR|c|0.86|Un détective privé croit comprendre l'eau, l'inceste et Los Angeles.
LES_DENTS_DE_LA_MER_1975|Jaws|Les Dents de la mer|1975|124|USA|STEVEN_SPIELBERG|THRILLER,AVENTURE,HORREUR|NEW_HOLLYWOOD|c|0.52|Un requin ferme la plage et trois hommes partent le chasser.
LA_GUERRE_DES_ETOILES_1977|Star Wars|La Guerre des étoiles|1977|121|USA|GEORGE_LUCAS|SCIENCE_FICTION,AVENTURE|NEW_HOLLYWOOD|c|0.45|Un fermier de Tatooine rejoint une rébellion contre l'Empire.
APOCALYPSE_NOW_1979|Apocalypse Now|Apocalypse Now|1979|153|USA|FRANCIS_FORD_COPPOLA|GUERRE,DRAME|NEW_HOLLYWOOD,CINEMA_D_AUTEUR|c|0.88|Un officier remonte un fleuve pour tuer un colonel devenu dieu.
LES_AFFRANCHIS_1990|Goodfellas|Les Affranchis|1990|146|USA|MARTIN_SCORSESE|DRAME,POLICIER|NEO_NOIR,CINEMA_D_AUTEUR|c|0.70|Henry Hill raconte la mafia comme une fête qui tourne au piège.
PULP_FICTION_1994|Pulp Fiction|Pulp Fiction|1994|154|USA|QUENTIN_TARANTINO|POLICIER,COMEDIE,THRILLER|NEO_NOIR|c|0.64|Plusieurs récits de malfrats se croisent autour d'une mallette et d'un diner.
MESHES_OF_THE_AFTERNOON_1943|Meshes of the Afternoon|Meshes of the Afternoon|1943|14|USA|MAYA_DEREN,ALEXANDER_HAMMID|DRAME|CINEMA_EXPERIMENTAL|se|0.92|Une femme poursuit une figure voilée dans une maison qui se répète.
ERASERHEAD_1977|Eraserhead|Eraserhead|1977|89|USA|DAVID_LYNCH|HORREUR,DRAME|CINEMA_EXPERIMENTAL,CINEMA_D_AUTEUR|b|0.90|Un père tient un bébé monstrueux dans un univers industriel de rumeurs.
# --- Extra noir / Nouvelle Vague / marathon ---
LAURA_1944|Laura|Laura|1944|88|USA|OTTO_PREMINGER|FILM_NOIR,POLICIER,ROMANCE|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.74|Un détective tombe amoureux du portrait d'une morte qui n'est pas tout à fait morte.
LES_RUES_DE_LA_VILLE_1953|Pickup on South Street|Le Port de la drogue|1953|80|USA|SAMUEL_FULLER|FILM_NOIR,POLICIER|FILM_NOIR_STYLE|b|0.72|Un pickpocket vole un microfilm et se retrouve entre FBI et espions.
LA_RUE_ROUGE_1945|Scarlet Street|La Rue rouge|1945|102|USA|FRITZ_LANG|FILM_NOIR,DRAME|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.80|Un caissier timide peint, aime et se laisse ruiner par un couple d'escrocs.
REGLEMENT_DE_COMPTES_1953|The Big Heat|Règlement de comptes|1953|90|USA|FRITZ_LANG|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.76|Un flic voit sa femme tuée par une bombe et descend dans la corruption municipale.
DETOUR_1945|Detour|Detour|1945|68|USA|EDGAR_G_ULMER|FILM_NOIR,DRAME|FILM_NOIR_STYLE|b|0.78|Un pianiste fait du stop et le destin se referme en deux voitures.
DU_RIFIFI_CHEZ_LES_HOMMES_1955|Du rififi chez les hommes|Du rififi chez les hommes|1955|118|FRANCE|JULES_DASSIN|FILM_NOIR,POLICIER|FILM_NOIR_STYLE|b|0.82|Un casse silencieux à Paris, puis la chute des hommes qui l'ont réussi.
VIVRE_SA_VIE_1962|Vivre sa vie|Vivre sa vie|1962|85|FRANCE|JEAN_LUC_GODARD|DRAME|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|b|0.84|Nana quitte un homme, vend des disques, puis son corps, en douze tableaux.
BANDE_A_PART_1964|Bande à part|Bande à part|1964|95|FRANCE|JEAN_LUC_GODARD|POLICIER,COMEDIE,DRAME|NOUVELLE_VAGUE_FRANCAISE|b|0.76|Deux copains et Odile préparent un vol et dansent dans un café.
LE_BEAU_SERGE_1958|Le Beau Serge|Le Beau Serge|1958|98|FRANCE|CLAUDE_CHABROL|DRAME|NOUVELLE_VAGUE_FRANCAISE|b|0.74|Un étudiant revient au village et retrouve un ami alcoolique.
LES_COUSINS_1959|Les Cousins|Les Cousins|1959|112|FRANCE|CLAUDE_CHABROL|DRAME|NOUVELLE_VAGUE_FRANCAISE|b|0.76|Un provincial s'installe chez son cousin parisien et se perd dans un jeu mondain.
MA_NUIT_CHEZ_MAUD_1969|Ma nuit chez Maud|Ma nuit chez Maud|1969|111|FRANCE|ERIC_ROHMER|DRAME,ROMANCE|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|b|0.82|Un catholique discute hasard, grâce et désir pendant une nuit d'hiver.
SHOAH_1985|Shoah|Shoah|1985|566|FRANCE|CLAUDE_LANZMANN|DOCUMENTAIRE,HISTORIQUE|DOCUMENTAIRE_POETIQUE|c|0.95|Des témoins, des lieux et la parole reconstruisent l'extermination sans images d'archives.
OUT_1_1971|Out 1|Out 1 : Noli me tangere|1971|729|FRANCE|JACQUES_RIVETTE|DRAME|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|c|0.92|Deux théâtres, une conspiration imaginaire et Paris comme labyrinthe de treize heures.
KOYAANISQATSI_1982|Koyaanisqatsi|Koyaanisqatsi|1982|86|USA|GODFREY_REGGIO|DOCUMENTAIRE|CINEMA_EXPERIMENTAL,DOCUMENTAIRE_POETIQUE|c|0.80|La Terre et les villes s'enchaînent sans commentaire, portées par la musique de Glass.
# --- UK ---
LES_39_MARCHES_1935|The 39 Steps|Les 39 Marches|1935|86|UK|ALFRED_HITCHCOCK|THRILLER,AVENTURE|HOLLYWOOD_CLASSIQUE|b|0.70|Un homme innocent fuit à travers l'Écosse, menotté à une inconnue.
UNE_FEMME_DISPARAIT_1938|The Lady Vanishes|Une femme disparaît|1938|96|UK|ALFRED_HITCHCOCK|THRILLER,COMEDIE|HOLLYWOOD_CLASSIQUE|b|0.68|Dans un train, une vieille dame s'évapore et personne ne veut y croire.
BREVE_RENCONTRE_1945|Brief Encounter|Brève rencontre|1945|86|UK|DAVID_LEAN|DRAME,ROMANCE|CINEMA_D_AUTEUR|b|0.76|Deux inconnus se parlent dans une gare et n'iront presque nulle part.
LES_CHAUSSURES_ROUGES_1948|The Red Shoes|Les Chaussons rouges|1948|134|UK|MICHAEL_POWELL,EMERIC_PRESSBURGER|DRAME,MUSICAL|CINEMA_D_AUTEUR|c|0.84|Une danseuse doit choisir entre l'amour et une paire de chaussons qui dansent trop.
LE_TROISIEME_HOMME_1949|The Third Man|Le Troisième Homme|1949|104|UK|CAROL_REED|FILM_NOIR,POLICIER|FILM_NOIR_STYLE|b|0.86|À Vienne occupée, Holly Martins cherche Harry Lime dans les égouts et les ombres.
NOBLESSE_OBLIGE_1949|Kind Hearts and Coronets|Noblesse oblige|1949|106|UK|ROBERT_HAMER|COMEDIE,POLICIER| |b|0.66|Un héritier éloigné élimine huit membres d'une famille, tous joués par le même acteur.
LAWRENCE_D_ARABIE_1962|Lawrence of Arabia|Lawrence d'Arabie|1962|227|UK|DAVID_LEAN|HISTORIQUE,AVENTURE,GUERRE|CINEMA_D_AUTEUR|c|0.80|T. E. Lawrence traverse le désert et se perd entre révolte arabe et Empire.
KES_1969|Kes|Kes|1969|111|UK|KEN_LOACH|DRAME|BRITISH_NEW_WAVE|c|0.72|Un garçon de Barnsley dresse un crécerelle pour échapper à l'école et à la mine.
NE_VOUS_RETOURNEZ_PAS_1973|Don't Look Now|Ne vous retournez pas|1973|110|UK|NICOLAS_ROEG|HORREUR,DRAME,THRILLER|CINEMA_D_AUTEUR|c|0.80|À Venise, un couple endeuillé croit voir un enfant en manteau rouge.
2001_L_ODYSSEE_DE_L_ESPACE_1968|2001: A Space Odyssey|2001, l'Odyssée de l'espace|1968|139|UK|STANLEY_KUBRICK|SCIENCE_FICTION|CINEMA_D_AUTEUR|c|0.92|De l'os au vaisseau, une intelligence noire observe l'espèce humaine.
# --- Germany ---
M_LE_MAUDIT_1931|M|M le maudit|1931|111|GERMANY|FRITZ_LANG|POLICIER,THRILLER|EXPRESSIONNISME_ALLEMAND,FILM_NOIR_STYLE|b|0.90|Un tueur d'enfants est chassé par la police et par le milieu.
TOUS_LES_AUTRES_S_APPELLENT_ALI_1974|Angst essen Seele auf|Tous les autres s'appellent Ali|1974|93|GERMANY|RAINER_WERNER_FASSBINDER|DRAME,ROMANCE|NOUVEAU_CINEMA_ALLEMAND,MELODRAME|c|0.82|Une femme de ménage et un ouvrier marocain s'aiment sous le regard d'un immeuble.
LE_MARIAGE_DE_MARIA_BRAUN_1979|Die Ehe der Maria Braun|Le Mariage de Maria Braun|1979|120|GERMANY|RAINER_WERNER_FASSBINDER|DRAME,HISTORIQUE|NOUVEAU_CINEMA_ALLEMAND,MELODRAME|c|0.80|Maria reconstruit l'Allemagne d'après-guerre en vendant tout, y compris elle.
AGUIRRE_LA_COLERE_DE_DIEU_1972|Aguirre, der Zorn Gottes|Aguirre, la colère de Dieu|1972|95|GERMANY|WERNER_HERZOG|AVENTURE,DRAME,HISTORIQUE|NOUVEAU_CINEMA_ALLEMAND,CINEMA_D_AUTEUR|c|0.88|Un conquistador descend un fleuve et se prend pour la colère de Dieu.
FITZCARRALDO_1982|Fitzcarraldo|Fitzcarraldo|1982|158|GERMANY|WERNER_HERZOG|AVENTURE,DRAME|NOUVEAU_CINEMA_ALLEMAND|c|0.84|Un rêveur veut hisser un bateau par-dessus une montagne pour un opéra.
LES_AILES_DU_DESIR_1987|Der Himmel über Berlin|Les Ailes du désir|1987|128|GERMANY|WIM_WENDERS|DRAME,ROMANCE|NOUVEAU_CINEMA_ALLEMAND,CINEMA_D_AUTEUR|c|0.82|Un ange veut devenir mortel pour aimer une trapéziste à Berlin.
L_AMI_AMERICAIN_1977|Der amerikanische Freund|L'Ami américain|1977|125|GERMANY|WIM_WENDERS|POLICIER,THRILLER|NOUVEAU_CINEMA_ALLEMAND,NEO_NOIR|c|0.78|Un encadreur malade accepte un meurtre proposé par un faux Ami.
LE_TAMBOUR_1979|Die Blechtrommel|Le Tambour|1979|142|GERMANY|VOLKER_SCHLONDORFF|DRAME,HISTORIQUE|NOUVEAU_CINEMA_ALLEMAND|c|0.74|Oskar refuse de grandir et tambourine contre le nazisme naissant.
LE_BATEAU_1981|Das Boot|Le Bateau|1981|149|GERMANY|WOLFGANG_PETERSEN|GUERRE,DRAME,THRILLER| |c|0.60|Un U-Boot et son équipage tiennent dans un tube d'angoisse.
BERLIN_ALEXANDERPLATZ_1980|Berlin Alexanderplatz|Berlin Alexanderplatz|1980|894|GERMANY|RAINER_WERNER_FASSBINDER|DRAME|NOUVEAU_CINEMA_ALLEMAND,CINEMA_D_AUTEUR|c|0.88|Franz Biberkopf sort de prison et Berlin des années 1920 le reprend.
# --- Russia / USSR ---
ALEXANDRE_NEVSKI_1938|Александр Невский|Alexandre Nevski|1938|112|RUSSIA|SERGEI_EISENSTEIN|HISTORIQUE,GUERRE|CINEMA_SOVIETIQUE,MONTAGE_SOVIETIQUE|b|0.80|Le prince Nevski affronte les chevaliers teutoniques sur la glace.
IVAN_LE_TERRIBLE_1944|Иван Грозный|Ivan le Terrible|1944|99|RUSSIA|SERGEI_EISENSTEIN|HISTORIQUE,DRAME|CINEMA_SOVIETIQUE|b|0.84|Le tsar unifie la Russie et se retrouve seul parmi les complots.
QUAND_PASSENT_LES_CIGOGNES_1957|Летят журавли|Quand passent les cigognes|1957|97|RUSSIA|MIKHAIL_KALATOZOV|DRAME,GUERRE,ROMANCE|CINEMA_SOVIETIQUE|b|0.78|Veronika attend Boris parti au front dans un Moscou dévasté.
L_ENFANCE_D_IVAN_1962|Иваново детство|L'Enfance d'Ivan|1962|95|RUSSIA|ANDREI_TARKOVSKY|GUERRE,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|b|0.86|Un enfant éclaireur traverse la guerre comme un rêve déjà mort.
ANDREI_RUBLEV_1966|Андрей Рублёв|Andreï Roublev|1966|205|RUSSIA|ANDREI_TARKOVSKY|HISTORIQUE,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|b|0.94|Un peintre d'icônes traverse la violence du XVe siècle avant de retrouver la couleur.
SOLARIS_1972|Солярис|Solaris|1972|167|RUSSIA|ANDREI_TARKOVSKY|SCIENCE_FICTION,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|c|0.90|Une station spatiale ramène les morts que la planète a lus dans les consciences.
STALKER_1979|Сталкер|Stalker|1979|163|RUSSIA|ANDREI_TARKOVSKY|SCIENCE_FICTION,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|c|0.93|Un guide emmène deux hommes vers une Zone qui exauce les vœux.
REQUIEM_POUR_UN_MASSACRE_1985|Иди и смотри|Requiem pour un massacre|1985|142|RUSSIA|ELEM_KLIMOV|GUERRE,DRAME|CINEMA_SOVIETIQUE|c|0.88|Un adolescent biélorusse voit 1943 lui voler le visage.
GUERRE_ET_PAIX_1966|Война и мир|Guerre et Paix|1966|431|RUSSIA|SERGEI_BONDARCHUK|HISTORIQUE,GUERRE,DRAME,ROMANCE|CINEMA_SOVIETIQUE|c|0.78|Tolstoï filmé à l'échelle d'une armée, d'un bal et d'une âme.
LA_COULEUR_DE_LA_GRENADE_1969|Նռան գույնը|La Couleur de la grenade|1969|79|RUSSIA|SERGEI_PARAJANOV|DRAME,HISTORIQUE|CINEMA_SOVIETIQUE,CINEMA_EXPERIMENTAL,CINEMA_D_AUTEUR|c|0.95|La vie du poète Sayat-Nova en tableaux d'étoffes, de sang et de rituel.
# --- Sweden ---
LE_SEPTIEME_SCEAU_1957|Det sjunde inseglet|Le Septième Sceau|1957|96|SWEDEN|INGMAR_BERGMAN|DRAME,HISTORIQUE|CINEMA_D_AUTEUR|b|0.88|Un chevalier joue aux échecs avec la Mort sur fond de peste.
LES_FRAISES_SAUVAGES_1957|Smultronstället|Les Fraises sauvages|1957|91|SWEDEN|INGMAR_BERGMAN|DRAME|CINEMA_D_AUTEUR|b|0.86|Un vieux professeur revoit sa vie sur la route d'une cérémonie.
SOURIRES_D_UNE_NUIT_D_ETE_1955|Sommarnattens leende|Sourires d'une nuit d'été|1955|108|SWEDEN|INGMAR_BERGMAN|COMEDIE,ROMANCE|CINEMA_D_AUTEUR|b|0.70|Des couples se défont et se reforment pendant une nuit de campagne.
PERSONA_1966|Persona|Persona|1966|83|SWEDEN|INGMAR_BERGMAN|DRAME|CINEMA_D_AUTEUR,CINEMA_EXPERIMENTAL|be|0.94|Une actrice muette et son infirmière échangent peu à peu leurs visages.
CRIS_ET_CHUCHOTEMENTS_1972|Viskningar och rop|Cris et Chuchotements|1972|91|SWEDEN|INGMAR_BERGMAN|DRAME|CINEMA_D_AUTEUR|c|0.88|Trois sœurs et une servante veillent une agonie dans une maison rouge.
FANNY_ET_ALEXANDRE_1982|Fanny och Alexander|Fanny et Alexandre|1982|188|SWEDEN|INGMAR_BERGMAN|DRAME|CINEMA_D_AUTEUR|c|0.86|Deux enfants quittent le théâtre familial pour la maison d'un évêque.
# --- Iran ---
OU_EST_LA_MAISON_DE_MON_AMI_1987|خانه دوست کجاست؟|Où est la maison de mon ami ?|1987|83|IRAN|ABBAS_KIAROSTAMI|DRAME|NOUVELLE_VAGUE_IRANIENNE,CINEMA_D_AUTEUR|c|0.80|Un écolier doit rendre un cahier avant que son camarade soit renvoyé.
CLOSE_UP_1990|کلوزآپ ، نمای نزدیک|Close-up|1990|98|IRAN|ABBAS_KIAROSTAMI|DRAME,DOCUMENTAIRE|NOUVELLE_VAGUE_IRANIENNE,CINEMA_D_AUTEUR|c|0.90|Un homme se fait passer pour Makhmalbaf et le procès devient un film.
LE_GOUT_DE_LA_CERISE_1997|طعم گيلاس|Le Goût de la cerise|1997|95|IRAN|ABBAS_KIAROSTAMI|DRAME|NOUVELLE_VAGUE_IRANIENNE,CINEMA_D_AUTEUR|c|0.88|Un homme cherche quelqu'un pour recouvrir sa tombe après son suicide.
LA_MAISON_EST_NOIRE_1963|خانه سیاه است|La Maison est noire|1963|22|IRAN|FOROUGH_FARROKHZAD|DOCUMENTAIRE|NOUVELLE_VAGUE_IRANIENNE,DOCUMENTAIRE_POETIQUE,CINEMA_EXPERIMENTAL|b|0.90|Une léproserie filmée comme un poème, sans pitié cosmétique.
UNE_SEPARATION_2011|جدایی نادر از سیمین|Une séparation|2011|123|IRAN|ASGHAR_FARHADI|DRAME|NOUVELLE_VAGUE_IRANIENNE|c|0.74|Un divorce ouvre une affaire judiciaire où personne ne peut tout dire.
LE_VENT_NOUS_EMPORTERA_1999|باد ما را خواهد برد|Le Vent nous emportera|1999|118|IRAN|ABBAS_KIAROSTAMI|DRAME|NOUVELLE_VAGUE_IRANIENNE|c|0.84|Des citadins attendent la mort d'une villageoise en prétendant poser des câbles.
# --- Korea ---
THE_HOUSEMAID_1960|하녀|The Housemaid|1960|111|SOUTH_KOREA|KIM_KI_YOUNG|THRILLER,DRAME,HORREUR|KOREAN_NEW_WAVE|b|0.80|Une domestique bouleverse une famille de la classe moyenne jusqu'au crime.
OLDBOY_2003|올드보이|Oldboy|2003|120|SOUTH_KOREA|PARK_CHAN_WOOK|THRILLER,POLICIER|KOREAN_NEW_WAVE,NEO_NOIR|c|0.72|Un homme enfermé quinze ans doit découvrir pourquoi, en cinq jours.
MEMORIES_OF_MURDER_2003|살인의 추억|Memories of Murder|2003|132|SOUTH_KOREA|BONG_JOON_HO|POLICIER,DRAME,THRILLER|KOREAN_NEW_WAVE|c|0.78|Deux flics de province chassent un tueur que la pluie et l'incompétence dérobent.
PARASITE_2019|기생충|Parasite|2019|132|SOUTH_KOREA|BONG_JOON_HO|DRAME,THRILLER,COMEDIE|KOREAN_NEW_WAVE|c|0.70|Une famille s'infiltre dans une maison riche par le sous-sol.
POETRY_2010|시|Poetry|2010|139|SOUTH_KOREA|LEE_CHANG_DONG|DRAME|KOREAN_NEW_WAVE,CINEMA_D_AUTEUR|c|0.80|Une grand-mère apprend à écrire des vers pendant qu'un crime familial demande de l'argent.
BURNING_2018|버닝|Burning|2018|148|SOUTH_KOREA|LEE_CHANG_DONG|DRAME,THRILLER|KOREAN_NEW_WAVE|c|0.82|Un jeune livreur, une voisine et un riche amateur de serres cataboliques.
# --- India ---
LA_COMPLAINTE_DU_SENTIER_1955|পথের পাঁচালী|La Complainte du sentier|1955|126|INDIA|SATYAJIT_RAY|DRAME|INDIAN_PARALLEL,CINEMA_D_AUTEUR|b|0.88|Apu et Durga grandissent dans un village bengali trop pauvre pour garder ses morts.
L_INVAINCU_1956|অপরাজিত|L'Invaincu|1956|110|INDIA|SATYAJIT_RAY|DRAME|INDIAN_PARALLEL|b|0.84|Apu quitte le village, perd sa mère et continue vers Calcutta.
LE_MONDE_D_APU_1959|অপুর সংসার|Le Monde d'Apu|1959|105|INDIA|SATYAJIT_RAY|DRAME,ROMANCE|INDIAN_PARALLEL|b|0.86|Apu se marie par accident, devient père et doit revenir vers la vie.
LA_SALLE_DE_MUSIQUE_1958|জলসাঘর|Le Salon de musique|1958|100|INDIA|SATYAJIT_RAY|DRAME|INDIAN_PARALLEL|b|0.82|Un zamindar ruiné offre un dernier concert dans sa salle vide.
LA_DEESSE_1960|দেবী|La Déesse|1960|93|INDIA|SATYAJIT_RAY|DRAME|INDIAN_PARALLEL|b|0.80|Un beau-père prend sa belle-fille pour une incarnation de Kali.
CHARULATA_1964|চারুলতা|Charulata|1964|117|INDIA|SATYAJIT_RAY|DRAME,ROMANCE|INDIAN_PARALLEL,CINEMA_D_AUTEUR|b|0.88|Une femme cultivée s'éprend du cousin de son mari occupé par sa gazette.
L_ETOILE_CACHEE_1960|মেঘে ঢাকা তারা|L'Étoile cachée|1960|126|INDIA|RITWIK_GHATAK|DRAME|INDIAN_PARALLEL,MELODRAME|b|0.86|Une réfugiée du Partition travaille jusqu'à s'effondrer pour les siens.
# --- Greater China ---
PRINTEMPS_DANS_UNE_PETITE_VILLE_1948|小城之春|Printemps dans une petite ville|1948|98|CHINA|FEI_MU|DRAME,ROMANCE|CINEMA_D_AUTEUR|b|0.88|Dans une ville en ruine, un ami d'enfance réveille un mariage étouffé.
EPOUSES_ET_CONCUBINES_1991|大红灯笼高高挂|Épouses et concubines|1991|125|CHINA|ZHANG_YIMOU|DRAME|MELODRAME,CINEMA_D_AUTEUR|c|0.76|Une étudiante entre dans un palais où les lanternes décident qui est aimée.
IN_THE_MOOD_FOR_LOVE_2000|花樣年華|In the Mood for Love|2000|98|HONG_KONG|WONG_KAR_WAI|DRAME,ROMANCE|HONG_KONG_NEW_WAVE,CINEMA_D_AUTEUR|c|0.84|Deux voisins découvrent l'adultère de leurs conjoints et inventent une retenue.
CHUNGKING_EXPRESS_1994|重慶森林|Chungking Express|1994|102|HONG_KONG|WONG_KAR_WAI|DRAME,ROMANCE,POLICIER|HONG_KONG_NEW_WAVE|c|0.72|Deux policiers ratent l'amour dans un Hong Kong de boîtes de conserve et de perruques.
YI_YI_2000|一一|Yi Yi|2000|173|TAIWAN|EDWARD_YANG|DRAME|TAIWAN_NEW_CINEMA,CINEMA_D_AUTEUR|c|0.86|Une famille de Taipei traverse un mariage, une mort et les photos d'un enfant.
GONDE_JOUR_D_ETE_1991|牯嶺街少年殺人事件|Guling jie shaonian sharen shijian|1991|237|TAIWAN|EDWARD_YANG|DRAME,POLICIER|TAIWAN_NEW_CINEMA|c|0.88|À Taipei au début des années 1960, un adolescent glisse vers un crime.
LA_CITE_DES_DOULEURS_1989|悲情城市|La Cité des douleurs|1989|157|TAIWAN|HOU_HSIAO_HSIEN|DRAME,HISTORIQUE|TAIWAN_NEW_CINEMA,CINEMA_D_AUTEUR|c|0.90|Une famille vit l'arrivée du Kuomintang et le massacre de 1947.
A_TOUCH_OF_ZEN_1971|俠女|A Touch of Zen|1971|180|TAIWAN|KING_HU|AVENTURE,DRAME|JIDAIGEKI|c|0.80|Une fugitive, un lettré et des moines transforment le wuxia en apparition.
A_L_OUEST_DES_RAILS_2003|铁西区|À l'ouest des rails|2003|551|CHINA|WANG_BING|DOCUMENTAIRE|DOCUMENTAIRE_POETIQUE,CINEMA_DIRECT|c|0.86|La zone industrielle de Shenyang s'éteint, filmée pendant des années.
# --- Spain ---
VIRIDIANA_1961|Viridiana|Viridiana|1961|90|SPAIN|LUIS_BUNUEL|DRAME|SURREALISME,CINEMA_D_AUTEUR|b|0.88|Une novice visite son oncle et voit la charité se transformer en farce cruelle.
L_ESPRIT_DE_LA_RUCHE_1973|El espíritu de la colmena|L'Esprit de la ruche|1973|97|SPAIN|VICTOR_ERICE|DRAME|CINEMA_D_AUTEUR|c|0.86|Une petite fille croit au monstre de Frankenstein dans l'Espagne de 1940.
PARLE_AVEC_ELLE_2002|Hable con ella|Parle avec elle|2002|112|SPAIN|PEDRO_ALMODOVAR|DRAME,ROMANCE|MELODRAME,CINEMA_D_AUTEUR|c|0.74|Deux hommes veillent deux femmes dans le coma et parlent à leur place.
TOUT_SUR_MA_MERE_1999|Todo sobre mi madre|Tout sur ma mère|1999|101|SPAIN|PEDRO_ALMODOVAR|DRAME|MELODRAME,CINEMA_D_AUTEUR|c|0.72|Après la mort de son fils, Manuela retraverse Barcelone, le théâtre et les identités.
# --- Poland ---
CENDRES_ET_DIAMANT_1958|Popiół i diament|Cendres et diamant|1958|103|POLAND|ANDRZEJ_WAJDA|DRAME,GUERRE|ECOLE_POLONAISE|b|0.84|Le dernier jour de la guerre, un résistant doit tuer un communiste.
UN_COURT_METRAGE_SUR_LE_MEURTRE_1988|Krótki film o zabijaniu|Un court métrage sur le meurtre|1988|84|POLAND|KRZYSZTOF_KIESLOWSKI|DRAME,POLICIER|CINEMA_D_AUTEUR|c|0.88|Un meurtre stupide et une pendaison légale se répondent sans consolation.
TROIS_COULEURS_BLEU_1993|Trois couleurs : Bleu|Trois couleurs : Bleu|1993|98|POLAND,FRANCE|KRZYSZTOF_KIESLOWSKI|DRAME|CINEMA_D_AUTEUR|c|0.80|Une femme survit à un accident et tente de se vider de toute attache.
LE_MANUSCRIT_TROUVE_A_SARAGOSSE_1965|Rękopis znaleziony w Saragossie|Le Manuscrit trouvé à Saragosse|1965|182|POLAND|WOJCIECH_HAS|AVENTURE,DRAME|ECOLE_POLONAISE|b|0.84|Un officier entre dans un labyrinthe d'histoires emboîtées en Espagne.
# --- Denmark / Czech / Hungary ---
JOUR_DE_COLERE_1943|Vredens dag|Jour de colère|1943|97|DENMARK|CARL_THEODOR_DREYER|DRAME,HISTORIQUE|CINEMA_D_AUTEUR|b|0.86|Dans un village luthérien, l'accusation de sorcellerie dévore une famille.
ORDET_1955|Ordet|Ordet|1955|126|DENMARK|CARL_THEODOR_DREYER|DRAME|CINEMA_D_AUTEUR|b|0.94|La foi, la folie et un miracle disputent une ferme du Jutland.
FESTEN_1998|Festen|Festen|1998|105|DENMARK|THOMAS_VINTERBERG|DRAME|DOGME_95|c|0.74|Un fils lève son verre d'anniversaire pour dire l'inceste à toute la famille.
TRAINS_ETROITEMENT_SURVEILLES_1966|Ostře sledované vlaky|Trains étroitement surveillés|1966|93|CZECH|JIRI_MENZEL|COMEDIE,DRAME,GUERRE|NOUVELLE_VAGUE_TCHEQUE|b|0.72|Un aiguilleur novice cherche l'amour pendant l'Occupation.
LES_PETITES_MARGUERITES_1966|Sedmikrásky|Les Petites Marguerites|1966|76|CZECH|VERA_CHYTILOVA|COMEDIE|NOUVELLE_VAGUE_TCHEQUE,CINEMA_EXPERIMENTAL|c|0.86|Deux jeunes femmes jouent à tout détruire, y compris le banquet.
DIMENSIONS_OF_DIALOGUE_1982|Možnosti dialogu|Dimensions of Dialogue|1982|12|CZECH|JAN_SVANKMAJER|ANIMATION|CINEMA_EXPERIMENTAL,SURREALISME,ANIMATION_DAUTEUR|ce|0.90|Des têtes d'objets se dévorent jusqu'à n'être plus que bouillie.
SATANTANGO_1994|Sátántangó|Satantango|1994|450|HUNGARY|BELA_TARR|DRAME|CINEMA_D_AUTEUR|b|0.92|Un village collectiviste attend un messie et danse au bord de la boue.
LES_HARMONIES_WERCKMEISTER_2000|Werckmeister harmóniák|Les Harmonies Werckmeister|2000|145|HUNGARY|BELA_TARR|DRAME|CINEMA_D_AUTEUR|b|0.88|Une baleine empaillée arrive en ville et l'ordre se fissure.
LE_FILS_DE_SAUL_2015|Saul fia|Le Fils de Saul|2015|107|HUNGARY|LASZLO_NEMES|DRAME,GUERRE,HISTORIQUE| |c|0.80|Un Sonderkommando cherche à enterrer un garçon au milieu d'Auschwitz.
# --- Latin America ---
DIEU_NOIR_ET_DIABLE_BLOND_1964|Deus e o Diabo na Terra do Sol|Dieu noir et diable blond|1964|120|BRAZIL|GLAUBER_ROCHA|DRAME,WESTERN|CINEMA_NOVO,THIRD_CINEMA|b|0.86|Un couple de sertão passe du cangaço au fanatisme messianique.
CITE_DE_DIEU_2002|Cidade de Deus|La Cité de Dieu|2002|130|BRAZIL|FERNANDO_MEIRELLES,KATIA_LUND|DRAME,POLICIER| |c|0.62|La violence d'une favela racontée par un photographe qui voulait seulement regarder.
LIMITE_1931|Limite|Limite|1931|114|BRAZIL|MARIO_PEIXOTO|DRAME|CINEMA_MUET_MOUVEMENT,CINEMA_EXPERIMENTAL|s|0.88|Trois naufragés dérivent, entrecoupés de souvenirs presque abstraits.
LOS_OLVIDADOS_1950|Los olvidados|Los Olvidados|1950|80|MEXICO|LUIS_BUNUEL|DRAME|SURREALISME,CINEMA_D_AUTEUR|b|0.86|Des enfants des rues de Mexico s'entre-déchirent sans morale consolante.
ROMA_2018|Roma|Roma|2018|135|MEXICO|ALFONSO_CUARON|DRAME|CINEMA_D_AUTEUR|b|0.76|Une employée de maison traverse 1970 pendant que la bourgeoisie se défait.
AMORES_PERROS_2000|Amores perros|Amours chiennes|2000|154|MEXICO|ALEJANDRO_GONZALEZ_INARRITU|DRAME,THRILLER|NEO_NOIR|c|0.68|Un accident relie trois récits de chiens, d'amour et de déclassement.
LE_LABYRINTHE_DE_PAN_2006|El laberinto del fauno|Le Labyrinthe de Pan|2006|118|MEXICO,SPAIN|GUILLERMO_DEL_TORO|DRAME,HORREUR,AVENTURE| |c|0.64|Une fillette fuit le franquisme dans un labyrinthe de fées cruelles.
L_HISTOIRE_OFFICIELLE_1985|La historia oficial|L'Histoire officielle|1985|112|ARGENTINA|LUIS_PUENZO|DRAME,HISTORIQUE| |c|0.70|Une professeure découvre que sa fille adoptive vient des disparus.
LA_FEMME_SANS_TETE_2008|La mujer sin cabeza|La Femme sans tête|2008|87|ARGENTINA|LUCRECIA_MARTEL|DRAME,THRILLER|CINEMA_D_AUTEUR|c|0.80|Après un choc sur la route, une femme de la bourgeoisie ne sait plus ce qu'elle a heurté.
DANS_SES_YEUX_2009|El secreto de sus ojos|Dans ses yeux|2009|129|ARGENTINA|JUAN_JOSE_CAMPANELLA|POLICIER,DRAME,ROMANCE| |c|0.60|Un greffier rouvre un meurtre et un amour restés vingt-cinq ans en suspens.
# --- Africa ---
LA_NOIRE_DE_1966|La Noire de...|La Noire de...|1966|65|SENEGAL|OUSMANE_SEMBENE|DRAME|CINEMA_AFRICAIN,THIRD_CINEMA,CINEMA_D_AUTEUR|b|0.84|Une jeune Sénégalaise suit ses patrons en France et devient une domestique sans nom.
LE_MANDAT_1968|Mandabi|Le Mandat|1968|90|SENEGAL|OUSMANE_SEMBENE|DRAME,COMEDIE|CINEMA_AFRICAIN,THIRD_CINEMA|c|0.80|Un mandat de France se perd dans la bureaucratie de Dakar.
TOUKI_BOUKI_1973|Touki Bouki|Touki Bouki|1973|95|SENEGAL|DJIBRIL_DIOP_MAMBETY|DRAME,ROMANCE|CINEMA_AFRICAIN,CINEMA_D_AUTEUR|c|0.86|Mory et Anta veulent prendre le bateau pour Paris, entre vaches, océan et collages.
YEELEN_1987|Yeelen|Yeelen|1987|105|MALI|SOULEYMANE_CISSE|DRAME,AVENTURE|CINEMA_AFRICAIN|c|0.82|Un fils fuit son père sorcier à travers un Mali de lumière et d'épreuves.
GARE_CENTRALE_1958|باب الحديد|Gare centrale|1958|77|EGYPT|YOUSSEF_CHAHINE|DRAME,ROMANCE|CINEMA_AFRICAIN|b|0.74|Un porteur boiteux de la gare du Caire aime une vendeuse de limonade.
LA_MUMIE_1969|المومياء|La Nuit des compter les années|1969|102|EGYPT|SHADI_ABDEL_SALAM|DRAME,HISTORIQUE|CINEMA_AFRICAIN,CINEMA_D_AUTEUR|c|0.88|Une tribu pille les tombes jusqu'à ce qu'un fils refuse l'héritage.
TIMBUKTU_2014|Timbuktu|Timbuktu|2014|97|MALI,FRANCE|ABDERRAHMANE_SISSAKO|DRAME|CINEMA_AFRICAIN|c|0.76|L'occupation djihadiste d'une ville sahélienne, filmée au ras des vies ordinaires.
# --- Oceania / Canada / Belgium / Greece / Turkey ---
PICNIC_A_HANGING_ROCK_1975|Picnic at Hanging Rock|Pique-nique à Hanging Rock|1975|115|AUSTRALIA|PETER_WEIR|DRAME,THRILLER| |c|0.74|Des collégiennes disparaissent dans un paysage qui refuse l'explication.
LA_LECON_DE_PIANO_1993|The Piano|La Leçon de piano|1993|121|NEW_ZEALAND|JANE_CAMPION|DRAME,ROMANCE|CINEMA_D_AUTEUR|c|0.76|Une muette et son piano arrivent en Nouvelle-Zélande comme un pacte.
VIDEODROME_1983|Videodrome|Vidéodrome|1983|87|CANADA|DAVID_CRONENBERG|HORREUR,SCIENCE_FICTION,THRILLER|CINEMA_D_AUTEUR|c|0.80|Un câblodistributeur découvre une émission qui mute la chair.
WAVELENGTH_1967|Wavelength|Wavelength|1967|45|CANADA|MICHAEL_SNOW|DRAME|CINEMA_EXPERIMENTAL|ce|0.95|Un zoom de quarante-cinq minutes traverse un loft jusqu'à une photo de mer.
INCENDIES_2010|Incendies|Incendies|2010|131|CANADA|DENIS_VILLENEUVE|DRAME| |c|0.70|Deux jumeaux suivent le testament de leur mère jusqu'à une guerre du Levant.
JEANNE_DIELMAN_1975|Jeanne Dielman, 23, quai du Commerce, 1080 Bruxelles|Jeanne Dielman|1975|201|BELGIUM|CHANTAL_AKERMAN|DRAME|CINEMA_D_AUTEUR,CINEMA_EXPERIMENTAL|c|0.94|Trois jours d'une veuve dont les gestes ménagers finissent par se fêler.
ROSETTA_1999|Rosetta|Rosetta|1999|93|BELGIUM|JEAN_PIERRE_DARDENNE,LUC_DARDENNE|DRAME|CINEMA_D_AUTEUR|c|0.78|Une adolescente se bat pour un emploi et une place hors du camping.
DEUX_JOURS_UNE_NUIT_2014|Deux jours, une nuit|Deux jours, une nuit|2014|95|BELGIUM|JEAN_PIERRE_DARDENNE,LUC_DARDENNE|DRAME|CINEMA_D_AUTEUR|c|0.72|Sandra a un week-end pour convaincre ses collègues de renoncer à un bonus.
PAYSAGE_DANS_LE_BROUILLARD_1988|Τοπίο στην ομίχλη|Paysage dans le brouillard|1988|127|GREECE|THEO_ANGELOPOULOS|DRAME|CINEMA_D_AUTEUR,ROAD_MOVIE|c|0.86|Deux enfants traversent la Grèce pour un père allemand qui n'existe peut-être pas.
CANINE_2009|Κυνόδοντας|Canine|2009|97|GREECE|YORGOS_LANTHIMOS|DRAME,THRILLER|CINEMA_D_AUTEUR|c|0.80|Des parents enferment leurs enfants dans un vocabulaire et un jardin.
YOL_1982|Yol|Yol|1982|114|TURKEY|SERIF_GOREN|DRAME|CINEMA_D_AUTEUR|c|0.82|Des détenus en permission traversent une Turquie de neige, d'honneur et de contrôle.
IL_ETAIT_UNE_FOIS_EN_ANATOLIE_2011|Bir Zamanlar Anadolu'da|Il était une fois en Anatolie|2011|157|TURKEY|NURI_BILGE_CEYLAN|POLICIER,DRAME|CINEMA_D_AUTEUR|c|0.84|Une nuit entière pour trouver un cadavre que personne ne situe vraiment.
# --- Initiation classics ---
TITANIC_1997|Titanic|Titanic|1997|194|USA|JAMES_CAMERON|DRAME,ROMANCE| |c|0.32|Jack et Rose se rencontrent à bord du paquebot qui va sombrer.
AVATAR_2009|Avatar|Avatar|2009|162|USA|JAMES_CAMERON|SCIENCE_FICTION,AVENTURE| |c|0.30|Un marine paraplégique s'incarne chez les Na'vi et choisit leur forêt.
SEVEN_1995|Se7en|Seven|1995|127|USA|DAVID_FINCHER|THRILLER,POLICIER|NEO_NOIR|c|0.52|Deux flics traquent un tueur qui met en scène les sept péchés capitaux.
LE_ROI_LION_1994|The Lion King|Le Roi Lion|1994|88|USA|ROGER_ALLERS|ANIMATION,AVENTURE,DRAME| |c|0.28|Simba fuit puis revient pour reprendre la savane à son oncle.
FORREST_GUMP_1994|Forrest Gump|Forrest Gump|1994|142|USA|ROBERT_ZEMECKIS|DRAME,COMEDIE| |c|0.30|Un homme simple traverse l'Amérique, de la guerre du Vietnam à un banc.
# --- Wave 2 : pionniers, pays peu couverts, classiques cinéphiles ---
LA_SORTIE_DES_USINES_LUMIERE_1895|La Sortie de l'usine Lumière à Lyon|La Sortie de l'usine Lumière à Lyon|1895|1|FRANCE|LOUIS_LUMIERE|DOCUMENTAIRE|CINEMA_MUET_MOUVEMENT,DOCUMENTAIRE_POETIQUE|se|0.55|Les ouvriers d'une usine lyonnaise sortent, et le cinéma commence.
L_ARRIVEE_D_UN_TRAIN_1896|L'Arrivée d'un train en gare de La Ciotat|L'Arrivée d'un train en gare de La Ciotat|1896|1|FRANCE|LOUIS_LUMIERE|DOCUMENTAIRE|CINEMA_MUET_MOUVEMENT|se|0.58|Un train entre en gare et la profondeur de champ devient un événement.
LA_FEE_AUX_CHOUX_1896|La Fée aux choux|La Fée aux choux|1896|1|FRANCE|ALICE_GUY|COMEDIE,AVENTURE|CINEMA_MUET_MOUVEMENT|se|0.70|Une fée cueille des bébés dans un chou, parmi les premiers récits filmés.
LES_CONSEQUENCES_DU_FEMINISME_1906|Les Résultats du féminisme|Les Conséquences du féminisme|1906|7|FRANCE|ALICE_GUY|COMEDIE|CINEMA_MUET_MOUVEMENT|s|0.72|Les rôles hommes-femmes s'inversent dans une farce politique d'avant 1910.
LE_VOL_DU_GRAND_RAPIDE_1903|The Great Train Robbery|Le Vol du grand rapide|1903|12|USA|EDWIN_S_PORTER|WESTERN,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.68|Un hold-up ferroviaire, une poursuite, et un revolver tiré vers la caméra.
LE_LYS_BRISE_1919|Broken Blossoms|Le Lys brisé|1919|90|USA|DW_GRIFFITH|DRAME,ROMANCE|CINEMA_MUET_MOUVEMENT,HOLLYWOOD_CLASSIQUE|s|0.80|Un Chinois de Limehouse recueille une enfant battue dans un Londres de brume.
A_TRAVERS_L_ORAGE_1920|Way Down East|À travers l'orage|1920|145|USA|DW_GRIFFITH|DRAME,ROMANCE|CINEMA_MUET_MOUVEMENT,HOLLYWOOD_CLASSIQUE|s|0.78|Une femme trompée fuit jusqu'à une débâcle de glace.
JUDEX_1916|Judex|Judex|1916|300|FRANCE|LOUIS_FEUILLADE|POLICIER,AVENTURE|CINEMA_MUET_MOUVEMENT|s|0.74|Un justicier masqué défait un banquier sans quitter le serial.
LA_SOURIANTE_MADAME_BEUDET_1923|La Souriante Madame Beudet|La Souriante Madame Beudet|1923|38|FRANCE|GERMAINE_DULAC|DRAME|IMPRESSIONNISME_FRANCAIS,CINEMA_MUET_MOUVEMENT|s|0.84|Une épouse provincialise imagine tuer son mari, en superpositions.
HAXAN_1922|Häxan|La Sorcellerie à travers les âges|1922|87|DENMARK|BENJAMIN_CHRISTENSEN|DOCUMENTAIRE,HORREUR,HISTORIQUE|CINEMA_MUET_MOUVEMENT,CINEMA_EXPERIMENTAL|se|0.86|Un essai sur le sabbat, entre reconstitution médiévale et cabinet de curiosités.
LA_CHARRETTE_FANTOME_1921|Körkarlen|La Charrette fantôme|1921|107|SWEDEN|VICTOR_SJOSTROM|DRAME,HORREUR|CINEMA_MUET_MOUVEMENT|s|0.90|Le dernier mort de l'année doit conduire la charrette des âmes.
LA_SAGA_DE_GOSTA_BERLING_1924|Gösta Berlings saga|La Légende de Gösta Berling|1924|183|SWEDEN|MAURITZ_STILLER|DRAME,ROMANCE|CINEMA_MUET_MOUVEMENT|s|0.78|Un pasteur déchu et une comtesse traversent la neige du Värmland.
BODY_AND_SOUL_1925|Body and Soul|Body and Soul|1925|93|USA|OSCAR_MICHEAUX|DRAME|CINEMA_MUET_MOUVEMENT|s|0.80|Un faux révérend tyrannise une communauté noire, jusqu'au réveil.
LA_MERE_1926|Мать|La Mère|1926|90|RUSSIA|VSEVOLOD_PUDOVKIN|DRAME,HISTORIQUE|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.86|Une mère rejoint la grève de son fils, montée comme une marée.
ARSENAL_1929|Арсенал|Arsenal|1929|90|UKRAINE|ALEXANDER_DOVZHENKO|GUERRE,DRAME|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.88|Kiev 1918 : un ouvrier et une révolte filmés comme un poème de choc.
LA_TERRE_1930|Земля|La Terre|1930|76|UKRAINE|ALEXANDER_DOVZHENKO|DRAME|MONTAGE_SOVIETIQUE,CINEMA_SOVIETIQUE,CINEMA_MUET_MOUVEMENT|s|0.90|Un village collectivise, un fils meurt, et les pommes continuent de mûrir.
ASPHALT_1929|Asphalt|Asphalte|1929|90|GERMANY|JOE_MAY|POLICIER,DRAME|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.76|Un flic de Berlin cède à une voleuse et la ville devient piège.
LES_TROIS_LUMIERES_1921|Der müde Tod|Les Trois Lumières|1921|98|GERMANY|FRITZ_LANG|DRAME,HORREUR|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.86|Une jeune femme négocie trois vies avec la Mort.
LE_CABINET_DES_FIGURES_DE_CIRE_1924|Das Wachsfigurenkabinett|Le Cabinet des figures de cire|1924|83|GERMANY|PAUL_LENI|HORREUR|EXPRESSIONNISME_ALLEMAND,CINEMA_MUET_MOUVEMENT|s|0.80|Haroun al-Rachid, Ivan le Terrible et Jack l'Éventreur sortent de la cire.
VAMPYR_1932|Vampyr|Vampyr|1932|73|DENMARK,FRANCE|CARL_THEODOR_DREYER|HORREUR|CINEMA_D_AUTEUR|b|0.92|Un voyageur entre dans un village où les morts ne tiennent pas en place.
OSSESSIONE_1943|Ossessione|Les Amants diaboliques|1943|140|ITALY|LUCHINO_VISCONTI|DRAME,POLICIER|NEOREALISME_ITALIEN|b|0.84|Un vagabond et la patronne d'une trattoria s'aiment jusqu'au crime.
LA_TERRE_TREMBLE_1948|La terra trema|La Terre tremble|1948|160|ITALY|LUCHINO_VISCONTI|DRAME|NEOREALISME_ITALIEN|b|0.88|Des pêcheurs siciliens tentent de s'affranchir des grossistes.
ALLEMAGNE_ANNEE_ZERO_1948|Germania anno zero|Allemagne année zéro|1948|78|ITALY,GERMANY|ROBERTO_ROSSELLINI|DRAME,GUERRE|NEOREALISME_ITALIEN|b|0.86|Un enfant traverse Berlin en ruine jusqu'à un geste sans retour.
STROMBOLI_1950|Stromboli|Stromboli|1950|107|ITALY|ROBERTO_ROSSELLINI|DRAME|NEOREALISME_ITALIEN,CINEMA_D_AUTEUR|b|0.80|Une déplacée épouse un pêcheur et se heurte au volcan, au village et à elle-même.
BELLISSIMA_1951|Bellissima|Bellissima|1951|114|ITALY|LUCHINO_VISCONTI|DRAME,COMEDIE|NEOREALISME_ITALIEN|b|0.74|Une mère veut faire de sa fille une star Cinecittà.
LE_PETIT_SOLDAT_1963|Le Petit Soldat|Le Petit Soldat|1963|88|FRANCE|JEAN_LUC_GODARD|DRAME,THRILLER|NOUVELLE_VAGUE_FRANCAISE|b|0.82|Un déserteur photographie, trahit, et découvre la torture des deux bords.
UNE_FEMME_EST_UNE_FEMME_1961|Une femme est une femme|Une femme est une femme|1961|85|FRANCE|JEAN_LUC_GODARD|COMEDIE,MUSICAL,ROMANCE|NOUVELLE_VAGUE_FRANCAISE|c|0.76|Angela veut un enfant et le film se moque d'être une comédie musicale.
LES_BONNES_FEMMES_1960|Les Bonnes Femmes|Les Bonnes Femmes|1960|100|FRANCE|CLAUDE_CHABROL|DRAME|NOUVELLE_VAGUE_FRANCAISE|b|0.80|Quatre vendeuses rêvent d'autre chose ; l'une trouve un motard trop parfait.
LOLA_1961|Lola|Lola|1961|90|FRANCE|JACQUES_DEMY|DRAME,ROMANCE,MUSICAL|NOUVELLE_VAGUE_FRANCAISE|b|0.78|Une danseuse de cabaret attend un marin dans un Nantes de blanc et de hasard.
PARIS_NOUS_APPARTIENT_1961|Paris nous appartient|Paris nous appartient|1961|140|FRANCE|JACQUES_RIVETTE|DRAME,THRILLER|NOUVELLE_VAGUE_FRANCAISE|b|0.84|Une étudiante croise une troupe et un complot qui n'en finit pas d'être imaginé.
LE_GENOU_DE_CLAIRE_1970|Le Genou de Claire|Le Genou de Claire|1970|105|FRANCE|ERIC_ROHMER|DRAME,ROMANCE|NOUVELLE_VAGUE_FRANCAISE,CINEMA_D_AUTEUR|c|0.80|Un diplomate en vacances veut seulement poser la main sur un genou.
CREPUSCULE_A_TOKYO_1957|東京暮色|Crépuscule à Tokyo|1957|141|JAPAN|YASUJIRO_OZU|DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_D_AUTEUR|b|0.86|Deux sœurs, une fille enceinte et un père qui ne sait plus quoi dire.
LES_FEUX_DANS_LA_PLAINE_1959|野火|Les Feux dans la plaine|1959|105|JAPAN|KON_ICHIKAWA|GUERRE,DRAME|AGE_OR_CINEMA_JAPONAIS|b|0.90|Un soldat tuberculeux erre dans une campagne où l'on mange déjà les morts.
LA_VENGEANCE_D_UN_ACTEUR_1963|雪之丞変化|La Vengeance d'un acteur|1963|113|JAPAN|KON_ICHIKAWA|DRAME,HISTORIQUE|AGE_OR_CINEMA_JAPONAIS,JIDAIGEKI|c|0.84|Un onnagata prépare sa vengeance comme un rôle, jusqu'au fard qui craque.
BARBE_ROUGE_1965|赤ひげ|Barbe rouge|1965|185|JAPAN|AKIRA_KUROSAWA|DRAME|AGE_OR_CINEMA_JAPONAIS,CINEMA_D_AUTEUR|b|0.86|Un jeune médecin rejoint une clinique pauvre et apprend la clinique du monde.
DERSU_OUZALA_1975|Дерсу Узала|Dersou Ouzala|1975|144|RUSSIA,JAPAN|AKIRA_KUROSAWA|AVENTURE,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|c|0.84|Un guide goldi sauve un arpenteur dans la taïga, puis se perd dans la ville.
LES_MEILLEURES_ANNEES_DE_NOTRE_VIE_1946|The Best Years of Our Lives|Les Plus Belles Années de notre vie|1946|170|USA|WILLIAM_WYLER|DRAME,GUERRE|HOLLYWOOD_CLASSIQUE|b|0.78|Trois soldats rentrent et ne retrouvent ni travail, ni mariage, ni main.
SHANGHAI_EXPRESS_1932|Shanghai Express|Shanghai Express|1932|82|USA|JOSEF_VON_STERNBERG|AVENTURE,DRAME,ROMANCE|HOLLYWOOD_CLASSIQUE|b|0.80|Marlene Dietrich traverse la Chine en train, entre guerre et regard.
HAUTE_PEGRE_1932|Trouble in Paradise|Haute Pègre|1932|83|USA|ERNST_LUBITSCH|COMEDIE,ROMANCE|HOLLYWOOD_CLASSIQUE|b|0.78|Deux voleurs s'aiment et cambriolent une veuve trop élégante.
LA_POURSUITE_INFERNALE_1946|My Darling Clementine|La Poursuite infernale|1946|97|USA|JOHN_FORD|WESTERN|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|b|0.82|Wyatt Earp civilise Tombstone jusqu'à O.K. Corral.
RIO_BRAVO_1959|Rio Bravo|Rio Bravo|1959|141|USA|HOWARD_HAWKS|WESTERN|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|c|0.74|Un shérif, un ivrogne, un vieux et un jeune tiennent une prison.
L_HOMME_QUI_TUA_LIBERTY_VALANCE_1962|The Man Who Shot Liberty Valance|L'Homme qui tua Liberty Valance|1962|123|USA|JOHN_FORD|WESTERN,DRAME|HOLLYWOOD_CLASSIQUE,WESTERN_CLASSIQUE|b|0.86|La légende imprime mieux que le fait, et Ford le dit à visage découvert.
LA_HORDE_SAUVAGE_1969|The Wild Bunch|La Horde sauvage|1969|145|USA|SAM_PECKINPAH|WESTERN|NEW_HOLLYWOOD,WESTERN_CLASSIQUE|c|0.84|Des hors-la-loi vieillis se jettent dans un massacre au ralenti.
LES_TUEURS_1946|The Killers|Les Tueurs|1946|103|USA|ROBERT_SIODMAK|FILM_NOIR,POLICIER|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.82|Un homme attend ses assassins ; un enquêteur remonte le reste.
LE_VIOLENT_1950|In a Lonely Place|Le Violent|1950|94|USA|NICHOLAS_RAY|FILM_NOIR,DRAME|HOLLYWOOD_CLASSIQUE,FILM_NOIR_STYLE|b|0.86|Un scénariste soupçonné de meurtre se révèle plus dangereux amoureux.
LA_CITE_SANS_VOILES_1950|Night and the City|Les Forbans de la nuit|1950|96|UK|JULES_DASSIN|FILM_NOIR,POLICIER|FILM_NOIR_STYLE|b|0.84|Un rabatteur de Londres court après un coup trop gros dans le catch.
ALICE_DANS_LES_VILLES_1974|Alice in den Städten|Alice dans les villes|1974|110|GERMANY|WIM_WENDERS|DRAME|NOUVEAU_CINEMA_ALLEMAND,ROAD_MOVIE,CINEMA_D_AUTEUR|b|0.82|Un journaliste se retrouve avec une enfant à travers l'Allemagne et les Polaroids.
AU_FIL_DU_TEMPS_1976|Im Lauf der Zeit|Au fil du temps|1976|175|GERMANY|WIM_WENDERS|DRAME|NOUVEAU_CINEMA_ALLEMAND,ROAD_MOVIE|b|0.86|Deux hommes réparent des projecteurs le long de la frontière intérieure.
L_HONNEUR_PERDU_DE_KATHARINA_BLUM_1975|Die verlorene Ehre der Katharina Blum|L'Honneur perdu de Katharina Blum|1975|106|GERMANY|VOLKER_SCHLONDORFF|DRAME,THRILLER|NOUVEAU_CINEMA_ALLEMAND|c|0.80|Une femme héberge un homme une nuit ; la presse et la police la défont.
LA_VACHE_1969|گاو|La Vache|1969|100|IRAN|DARIUS_MEHRJUI|DRAME|NOUVELLE_VAGUE_IRANIENNE|b|0.86|Un villageois perd sa vache et commence à devenir l'animal.
LE_CERCLE_2000|دایره|Le Cercle|2000|90|IRAN|JAFAR_PANAHI|DRAME|NOUVELLE_VAGUE_IRANIENNE|c|0.84|Des femmes sortent de prison et se heurtent à un Téhéran circulaire.
LE_COUREUR_1985|دونده|Le Coureur|1985|94|IRAN|AMIR_NADERI|DRAME|NOUVELLE_VAGUE_IRANIENNE|c|0.82|Un enfant du Golfe court, recycle et apprend à lire contre le vent.
LE_MIROIR_1975|Зеркало|Le Miroir|1975|107|RUSSIA|ANDREI_TARKOVSKY|DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR,CINEMA_EXPERIMENTAL|c|0.95|Enfance, mère, guerre et poèmes se reflètent sans chronologie.
L_ASCENSION_1977|Восхождение|L'Ascension|1977|111|RUSSIA|LARISA_SHEPITKO|GUERRE,DRAME|CINEMA_SOVIETIQUE,CINEMA_D_AUTEUR|b|0.92|Deux partisans biélorusses sont pris : l'un trahit, l'autre gravit.
JE_SUIS_CUBA_1964|Soy Cuba|Je suis Cuba|1964|141|CUBA,RUSSIA|MIKHAIL_KALATOZOV|DRAME,HISTORIQUE|CINEMA_SOVIETIQUE,THIRD_CINEMA|b|0.90|Quatre sketches de l'île, caméra qui plonge des toits dans les piscines.
LES_CHEVAUX_DE_FEU_1965|Тіні забутих предків|Les Chevaux de feu|1965|97|UKRAINE|SERGEI_PARAJANOV|DRAME,ROMANCE|CINEMA_SOVIETIQUE,CINEMA_EXPERIMENTAL|c|0.92|Un amour houtzoule, des rites, des couleurs qui précèdent Paradjanov.
XALA_1975|Xala|Xala|1975|123|SENEGAL|OUSMANE_SEMBENE|COMEDIE,DRAME|CINEMA_AFRICAIN,THIRD_CINEMA|c|0.84|Un notable est frappé d'impuissance le soir de son troisième mariage.
CEDDO_1977|Ceddo|Ceddo|1977|117|SENEGAL|OUSMANE_SEMBENE|DRAME,HISTORIQUE|CINEMA_AFRICAIN,THIRD_CINEMA|c|0.86|Un village résiste à l'islam de cour, au christianisme et à la traite.
HYENES_1992|Hyènes|Hyènes|1992|110|SENEGAL|DJIBRIL_DIOP_MAMBETY|DRAME,COMEDIE|CINEMA_AFRICAIN,CINEMA_D_AUTEUR|c|0.84|Une femme riche revient faire payer à son village le prix d'un vieux déshonneur.
CHRONIQUE_DES_ANNEES_DE_BRAISE_1975|وقائع سنين الجمر|Chronique des années de braise|1975|177|ALGERIA|MOHAMMED_LAKHDAR_HAMINA|DRAME,HISTORIQUE,GUERRE|CINEMA_AFRICAIN,THIRD_CINEMA|c|0.86|Un village algérien traverse colonisation, famine et insurrection.
SAMBIZANGA_1972|Sambizanga|Sambizanga|1972|102|ANGOLA|SARAH_MALDOROR|DRAME,GUERRE|CINEMA_AFRICAIN,THIRD_CINEMA|c|0.84|Une femme cherche son mari arrêté par la PIDE, à la veille de 1961.
ALEXANDRIE_POURQUOI_1979|إسكندرية ليه|Alexandrie pourquoi ?|1979|133|EGYPT|YOUSSEF_CHAHINE|DRAME|CINEMA_AFRICAIN,CINEMA_D_AUTEUR|c|0.80|Un adolescent d'Alexandrie rêve Hollywood pendant la guerre.
YAABA_1989|Yaaba|Yaaba|1989|90|BURKINA_FASO|IDRISSA_OUEDRAOGO|DRAME|CINEMA_AFRICAIN|c|0.78|Un enfant se lie à une vieille femme que le village dit sorcière.
WEND_KUUNI_1982|Wend Kuuni|Wend Kuuni|1982|75|BURKINA_FASO|GASTON_KABORE|DRAME|CINEMA_AFRICAIN|c|0.80|Un enfant muet retrouve la parole en racontant d'où il vient.
MEMOIRES_DU_SOUS_DEVELOPPEMENT_1968|Memorias del subdesarrollo|Mémoires du sous-développement|1968|97|CUBA|TOMAS_GUTIERREZ_ALEA|DRAME|THIRD_CINEMA,CINEMA_D_AUTEUR|b|0.88|Un bourgeois reste à La Havane après 1959 et se filme en spectateur.
LUCIA_1968|Lucía|Lucía|1968|160|CUBA|HUMBERTO_SOLAS|DRAME,HISTORIQUE|THIRD_CINEMA|b|0.84|Trois Lucía, 1895, 1932, 1960 : l'île change, le prénom reste.
L_HEURE_DES_FOURNEAUX_1968|La hora de los hornos|L'Heure des fourneaux|1968|260|ARGENTINA|FERNANDO_SOLANAS,OCTAVIO_GETINO|DOCUMENTAIRE|THIRD_CINEMA,CINEMA_DIRECT|b|0.90|Un essai militant sur le néocolonialisme, à projeter et à interrompre.
PIXOTE_1980|Pixote: A Lei do Mais Fraco|Pixote|1980|128|BRAZIL|HECTOR_BABENCO|DRAME| |c|0.82|Un enfant des rues de São Paulo passe de la reforme au crime.
CENTRAL_DO_BRASIL_1998|Central do Brasil|Central do Brasil|1998|113|BRAZIL|WALTER_SALLES|DRAME|ROAD_MOVIE|c|0.70|Une lettreuse emmène un orphelin chercher un père dans le Nordeste.
NOSTALGIE_DE_LA_LUMIERE_2010|Nostalgia de la luz|Nostalgie de la lumière|2010|90|CHILE|PATRICIO_GUZMAN|DOCUMENTAIRE|DOCUMENTAIRE_POETIQUE,THIRD_CINEMA|c|0.88|Dans l'Atacama, astronomes et familles de disparus cherchent des traces.
LE_BOUTON_DE_NACRE_2015|El botón de nácar|Le Bouton de nacre|2015|82|CHILE|PATRICIO_GUZMAN|DOCUMENTAIRE|DOCUMENTAIRE_POETIQUE,THIRD_CINEMA|c|0.86|L'eau chilienne relie les Indiens de Patagonie et les corps jetés à la mer.
LE_CHACAL_DE_NAHUELTORO_1969|El Chacal de Nahueltoro|Le Chacal de Nahueltoro|1969|95|CHILE|MIGUEL_LITTIN|DRAME|THIRD_CINEMA|b|0.84|Un analphabète massacre une famille, apprend à lire, et l'État l'exécute.
L_ANGE_EXTERMINATEUR_1962|El ángel exterminador|L'Ange exterminateur|1962|95|MEXICO|LUIS_BUNUEL|DRAME,COMEDIE|SURREALISME,CINEMA_D_AUTEUR|b|0.92|Après un dîner, les invités ne peuvent plus franchir le seuil.
ANIKI_BOBO_1942|Aniki-Bóbó|Aniki-Bóbó|1942|71|PORTUGAL|MANOEL_DE_OLIVEIRA|DRAME|CINEMA_D_AUTEUR|b|0.80|Des enfants de Porto jouent, volent et se punissent entre eux.
JEUNESSE_EN_MARCHE_2006|Juventude em Marcha|En avant, jeunesse !|2006|156|PORTUGAL|PEDRO_COSTA|DRAME|CINEMA_D_AUTEUR|c|0.88|Ventura, ouvrier cap-verdien, erre dans un Lisbonne de relogement.
LA_FILLE_DE_L_USINE_ALLUMETTES_1990|Tulitikkutehtaan tyttö|La Fille aux allumettes|1990|69|FINLAND|AKI_KAURISMAKI|DRAME,COMEDIE|CINEMA_D_AUTEUR|c|0.84|Une ouvrière se fait abandonner et prépare une vengeance minuscule.
L_HOMME_SANS_PASSE_2002|Mies vailla menneisyyttä|L'Homme sans passé|2002|97|FINLAND|AKI_KAURISMAKI|COMEDIE,DRAME|CINEMA_D_AUTEUR|c|0.78|Un amnésique recommence sa vie au bord des rails, avec une fanfare.
ONCLE_BOONMEE_2010|ลุงบุญมีระลึกชาติ|Oncle Boonmee, celui qui se souvient de ses vies antérieures|2010|114|THAILAND|APICHATPONG_WEERASETHAKUL|DRAME|CINEMA_D_AUTEUR|c|0.90|Un homme malade reçoit les morts et les singes-fantômes de la forêt.
MALADIE_TROPICALE_2004|สัตว์ประหลาด|Maladie tropicale|2004|118|THAILAND|APICHATPONG_WEERASETHAKUL|DRAME,ROMANCE|CINEMA_D_AUTEUR|c|0.88|Un soldat et un garçon de la ville s'aiment, puis le récit change de peau.
MANILLE_DANS_LES_GRIFFES_DE_LA_LUMIERE_1975|Maynila, sa mga Kuko ng Liwanag|Manille dans les griffes de la lumière|1975|125|PHILIPPINES|LINO_BROCKA|DRAME|CINEMA_D_AUTEUR|c|0.86|Un provincial cherche sa fiancée dans une Manille de chantiers et de proxénètes.
UN_CAUCHEMAR_PARFUME_1977|Mababangong Bangungot|Un cauchemar parfumé|1977|93|PHILIPPINES|KIDLAT_TAHIMIK|COMEDIE,DOCUMENTAIRE|THIRD_CINEMA,CINEMA_EXPERIMENTAL|c|0.84|Un chauffeur de jeepney part en Europe et ramène le tiers-monde en super 8.
LA_PIANISTE_2001|La Pianiste|La Pianiste|2001|131|AUSTRIA,FRANCE|MICHAEL_HANEKE|DRAME|CINEMA_D_AUTEUR|c|0.86|Une professeure de piano impose à un élève le contrat de ses blessures.
FUNNY_GAMES_1997|Funny Games|Funny Games|1997|109|AUSTRIA|MICHAEL_HANEKE|THRILLER,DRAME|CINEMA_D_AUTEUR|c|0.90|Deux jeunes gens prennent une famille en otage et regardent la caméra.
UN_ANGE_A_MA_TABLE_1990|An Angel at My Table|Un ange à ma table|1990|158|NEW_ZEALAND|JANE_CAMPION|DRAME|CINEMA_D_AUTEUR|c|0.80|Janet Frame traverse asiles et îles jusqu'à l'écriture.
LA_DERNIERE_VAGUE_1977|The Last Wave|La Dernière Vague|1977|106|AUSTRALIA|PETER_WEIR|THRILLER,DRAME| |c|0.78|Un avocat de Sydney rêve d'eau apocalyptique en défendant des Aborigènes.
DEAD_RINGERS_1988|Dead Ringers|Faux-semblants|1988|116|CANADA|DAVID_CRONENBERG|THRILLER,DRAME,HORREUR|CINEMA_D_AUTEUR|c|0.84|Deux jumeaux gynécologues se partagent les femmes jusqu'à se confondre.
DE_BEAUX_LENDEMAINS_1997|The Sweet Hereafter|De beaux lendemains|1997|112|CANADA|ATOM_EGOYAN|DRAME|CINEMA_D_AUTEUR|c|0.82|Après un accident de bus, un avocat réveille une ville sous la neige.
L_ENFANT_2005|L'Enfant|L'Enfant|2005|95|BELGIUM|JEAN_PIERRE_DARDENNE,LUC_DARDENNE|DRAME|CINEMA_D_AUTEUR|c|0.80|Bruno vend le bébé de Sonia, puis tente de racheter ce qui n'a pas de prix.
JOURS_SAUVAGES_1990|阿飛正傳|Nos années sauvages|1990|94|HONG_KONG|WONG_KAR_WAI|DRAME,ROMANCE|HONG_KONG_NEW_WAVE,CINEMA_D_AUTEUR|c|0.84|Un fils de putain refuse de rester, de Manila à une mère qui n'écrit pas.
HAPPY_TOGETHER_1997|春光乍洩|Happy Together|1997|96|HONG_KONG|WONG_KAR_WAI|DRAME,ROMANCE|HONG_KONG_NEW_WAVE|c|0.82|Deux amants hongkongais se perdent à Buenos Aires.
POUSSIERES_DANS_LE_VENT_1986|戀戀風塵|Poussières dans le vent|1986|110|TAIWAN|HOU_HSIAO_HSIEN|DRAME,ROMANCE|TAIWAN_NEW_CINEMA,CINEMA_D_AUTEUR|c|0.86|Un couple de mine quitte le village ; Taipei les sépare sans drame apparent.
EL_VERDUGO_1963|El verdugo|Le Bourreau|1963|92|SPAIN|LUIS_GARCIA_BERLANGA|COMEDIE,DRAME| |b|0.84|Un croque-mort devient bourreau pour un appartement, sous Franco.
CRIA_CUERVOS_1976|Cría cuervos|Cría cuervos|1976|110|SPAIN|CARLOS_SAURA|DRAME|CINEMA_D_AUTEUR|c|0.86|Une enfant croit pouvoir tuer, dans une maison de l'Espagne finissante.
KANAL_1957|Kanał|Ils aimaient la vie|1957|91|POLAND|ANDRZEJ_WAJDA|GUERRE,DRAME|ECOLE_POLONAISE|b|0.86|L'insurrection de Varsovie se termine dans les égouts.
MARKETA_LAZAROVA_1967|Marketa Lazarová|Marketa Lazarová|1967|162|CZECH|FRANTISEK_VLACIL|DRAME,HISTORIQUE|NOUVELLE_VAGUE_TCHEQUE|b|0.90|Deux clans médiévaux, une jeune femme et un cinéma d'avant le roman.
MEPHISTO_1981|Mephisto|Mephisto|1981|144|HUNGARY,GERMANY|ISTVAN_SZABO|DRAME,HISTORIQUE| |c|0.80|Un acteur vend son talent au Reich pour rester au centre de la scène.
GERTRUD_1964|Gertrud|Gertrud|1964|116|DENMARK|CARL_THEODOR_DREYER|DRAME,ROMANCE|CINEMA_D_AUTEUR|b|0.92|Une femme quitte mari et amants au nom d'un amour qui n'existe peut-être pas.
LE_VOYAGE_DES_COMEDIENS_1975|Ο Θίασος|Le Voyage des comédiens|1975|230|GREECE|THEO_ANGELOPOULOS|DRAME,HISTORIQUE|CINEMA_D_AUTEUR|c|0.90|Une troupe joue Golfo à travers guerres, occupation et guerre civile.
L_ESPOIR_1970|Umut|L'Espoir|1970|103|TURKEY|YILMAZ_GUNEY|DRAME|CINEMA_D_AUTEUR|b|0.84|Un cocher ruiné cherche un trésor et trouve la misère organisée.
SOMMEIL_D_HIVER_2014|Kış Uykusu|Winter Sleep|2014|196|TURKEY|NURI_BILGE_CEYLAN|DRAME|CINEMA_D_AUTEUR|c|0.86|Un hôtelier de Cappadoce parle trop, et la neige isole chaque orgueil.
"""


def director_entry(code: str) -> dict:
    if code not in DIRECTORS:
        raise SystemExit(f"Unknown director '{code}'")
    first_name, last_name, characteristic_codes = DIRECTORS[code]
    display = f"{first_name} {last_name}".strip() if first_name else last_name
    entry: dict = {
        "code": code,
        "lastName": last_name,
        "displayName": display,
        "characteristicCodes": characteristic_codes,
    }
    if first_name:
        entry["firstName"] = first_name
    return entry


def pick_movies(movies: list[dict], codes: list[str]) -> list[dict]:
    available = {movie["code"]: movie for movie in movies}
    missing = [code for code in codes if code not in available]
    if missing:
        raise SystemExit(f"Collection references unknown movies: {missing}")
    return [{"code": code, "displayOrder": index} for index, code in enumerate(codes, start=1)]


def build_collections(movies: list[dict]) -> list[dict]:
    collections = [
        {
            "code": "COLLECTION_INITIATION",
            "displayOrder": 0,
            "name": "Initiation",
            "description": "Dix films que tout le monde a déjà croisés, pour ouvrir le rideau.",
            "longDescription": (
                "Le Roi Lion, Forrest Gump, Titanic, Le Voyage de Chihiro, Pulp Fiction, Seven, Avatar, "
                "Le Parrain, Star Wars et Les Dents de la mer : des titres vus, revus, cités, zappés un "
                "dimanche soir. Cette collection n'est pas un examen de cinéphile. C'est le premier rang "
                "de la salle. Suis-la, marque au moins un film comme vu, et le reste d'Urbinema s'ouvre : "
                "courants, pays, auteurs, collections plus exigeantes. Tu connais déjà ces images. "
                "Ici, tu commences simplement à les ranger."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LE_ROI_LION_1994", "FORREST_GUMP_1994", "TITANIC_1997",
                "LE_VOYAGE_DE_CHIHIRO_2001", "PULP_FICTION_1994", "SEVEN_1995",
                "AVATAR_2009", "LE_PARRAIN_1972", "LA_GUERRE_DES_ETOILES_1977",
                "LES_DENTS_DE_LA_MER_1975",
            ]),
            "countryCodes": ["USA", "JAPAN"],
        },
        {
            "code": "COLLECTION_001",
            "displayOrder": 3,
            "name": "Néoréalisme italien",
            "description": "Les gestes fondateurs d'un cinéma tourné vers la rue et l'après-guerre.",
            "longDescription": (
                "Le néoréalisme naît dans l'Italie défaite de 1945, quand les studios manquent de moyens "
                "et que la rue offre déjà tous les décors. Roberto Rossellini filme Rome occupée puis "
                "libérée, Vittorio De Sica suit un chômeur et un enfant à la recherche d'une bicyclette, "
                "Luchino Visconti descend en Sicile. On y voit des non-professionnels, la lumière du jour, "
                "des fins sans consolation. Le mouvement dure peu, de Roma città aperta à Umberto D., "
                "mais il déplace le cinéma mondial : la pauvreté cesse d'être un motif pittoresque. "
                "Fellini, encore proche de ces années, en héritera la tendresse des routes avant d'inventer "
                "autre chose. Le néoréalisme n'est pas un style unique, c'est une urgence historique."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "ROMA_CITTA_APERTA_1945", "OSSESSIONE_1943", "PAISA_1946",
                "ALLEMAGNE_ANNEE_ZERO_1948", "LE_VOLEUR_DE_BICYCLETTE_1948",
                "LA_TERRE_TREMBLE_1948", "STROMBOLI_1950", "UMBERTO_D_1952", "LA_STRADA_1954",
            ]),
            "characteristicCodes": ["NEOREALISME_ITALIEN"],
            "countryCodes": ["ITALY"],
        },
        {
            "code": "COLLECTION_002",
            "displayOrder": 1,
            "name": "Nouvelle Vague française",
            "description": "Une liberté de tournage et de récit qui transforme le cinéma français.",
            "longDescription": (
                "À la fin des années 1950, des critiques des Cahiers du cinéma passent derrière la caméra. "
                "François Truffaut, Jean-Luc Godard, Claude Chabrol, Éric Rohmer et Jacques Rivette refusent "
                "le « cinéma de qualité » au profit de tournages légers, de rues réelles et de montages "
                "saccadés. La Rive gauche, avec Alain Resnais, Agnès Varda et Chris Marker, y ajoute la "
                "mémoire, le documentaire et la modernité littéraire. De 1958 à 1965, Paris devient un "
                "studio à ciel ouvert. La Nouvelle Vague n'est pas un manifeste unique : c'est une "
                "génération qui rend visible le cinéaste comme auteur. Son héritage court encore, de "
                "la caméra portée aux récits troués."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LE_BEAU_SERGE_1958", "LES_QUATRE_CENTS_COUPS_1959", "LES_COUSINS_1959",
                "HIROSHIMA_MON_AMOUR_1959", "LES_BONNES_FEMMES_1960", "A_BOUT_DE_SOUFFLE_1960",
                "LOLA_1961", "UNE_FEMME_EST_UNE_FEMME_1961", "PARIS_NOUS_APPARTIENT_1961",
                "CLEO_DE_5_A_7_1962", "JULES_ET_JIM_1962", "VIVRE_SA_VIE_1962", "LE_MEPRIS_1963",
                "BANDE_A_PART_1964", "PIERROT_LE_FOU_1965", "MA_NUIT_CHEZ_MAUD_1969",
                "LE_GENOU_DE_CLAIRE_1970",
            ]),
            "characteristicCodes": ["NOUVELLE_VAGUE_FRANCAISE"],
            "countryCodes": ["FRANCE"],
            "eraCodes": ["CINEMA_MODERNE"],
        },
        {
            "code": "COLLECTION_003",
            "displayOrder": 4,
            "name": "Japon classique",
            "description": "Quelques portes d'entrée vers l'âge d'or du cinéma japonais.",
            "longDescription": (
                "Des années 1930 aux années 1960, les grands studios japonais produisent un cinéma "
                "d'une densité rare. Yasujirō Ozu observe familles et silences depuis un tatami. "
                "Kenji Mizoguchi suit le destin des femmes à travers époques et prostituées de luxe. "
                "Akira Kurosawa ouvre le jidai-geki au monde, de Rashōmon aux Sept Samouraïs. "
                "Masaki Kobayashi et Mikio Naruse y ajoutent la colère morale et le mélodrame urbain. "
                "Cet âge d'or n'est pas une école unique : c'est une industrie capable de porter "
                "des auteurs jusqu'au bout de leur forme. On y apprend à lire un plan comme un rite."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "PRINTEMPS_TARDIF_1949", "RASHOMON_1950", "LA_VIE_D_OHARU_1952",
                "VOYAGE_A_TOKYO_1953", "LES_CONTES_DE_LA_LUNE_VAGUE_1953",
                "SEPT_SAMOURAIS_1954", "L_INTENDANT_SANSHO_1954", "CREPUSCULE_A_TOKYO_1957",
                "LES_FEUX_DANS_LA_PLAINE_1959", "HARA_KIRI_1962",
            ]),
            "characteristicCodes": ["AGE_OR_CINEMA_JAPONAIS"],
            "countryCodes": ["JAPAN"],
        },
        {
            "code": "COLLECTION_004",
            "displayOrder": 9,
            "name": "Akira Kurosawa",
            "description": "Du tribunal de Rashōmon aux couleurs de Ran, une œuvre-monde.",
            "longDescription": (
                "Akira Kurosawa traverse presque tout le cinéma japonais d'après-guerre. Rashōmon "
                "impose en 1950 la relativité des récits. Les Sept Samouraïs inventent une épopée "
                "populaire que Hollywood n'a cessé de relire. Vivre, Yojimbo, Entre le ciel et l'enfer "
                "montrent un moraliste du plan large et de la pluie. Plus tard, Kagemusha et Ran "
                "déploient la couleur comme une tragédie shakespearienne. Kurosawa n'est pas seulement "
                "le Japon « exportable » : c'est un artisan du mouvement, du groupe et du doute. "
                "Cette collection suit l'arc d'un auteur qui n'a jamais cessé de filmer la justice."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "RASHOMON_1950", "VIVRE_1952", "SEPT_SAMOURAIS_1954",
                "LE_CHATEAU_DE_L_ARAIGNEE_1957", "YOJIMBO_1961",
                "ENTRE_LE_CIEL_ET_L_ENFER_1963", "BARBE_ROUGE_1965",
                "DERSU_OUZALA_1975", "KAGEMUSHA_1980", "RAN_1985",
            ]),
            "countryCodes": ["JAPAN"],
        },
        {
            "code": "COLLECTION_005",
            "displayOrder": 2,
            "name": "Hollywood classique",
            "description": "Le système des studios, ses genres et sa continuité invisible.",
            "longDescription": (
                "De 1930 à 1960, Hollywood fabrique un langage que le monde entier apprend. "
                "John Ford sculpte le western, Howard Hawks passe du polar à la comédie, "
                "Billy Wilder aiguise le dialogue, Hitchcock transforme le suspense en forme. "
                "Le code Hays bride, les stars portent, la continuité invisible coud les plans. "
                "Citizen Kane ouvre une brèche d'auteur à l'intérieur même du système. "
                "Cette période n'est pas un âge d'or innocent : elle est une industrie, une censure "
                "et une invention permanente. En la parcourant, on voit naître le film noir, "
                "le musical et le western comme mythologies modernes."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "SHANGHAI_EXPRESS_1932", "HAUTE_PEGRE_1932", "NEW_YORK_MIAMI_1934",
                "LA_CHEVAUCHEE_FANTASTIQUE_1939", "CITIZEN_KANE_1941", "CASABLANCA_1942",
                "ASSURANCE_SUR_LA_MORT_1944", "LES_MEILLEURES_ANNEES_DE_NOTRE_VIE_1946",
                "CHANTONS_SOUS_LA_PLUIE_1952", "FENETRE_SUR_COUR_1954",
                "LA_PRISONNIERE_DU_DESERT_1956", "SUEURS_FROIDES_1958", "PSYCHOSE_1960",
            ]),
            "characteristicCodes": ["HOLLYWOOD_CLASSIQUE"],
            "countryCodes": ["USA"],
            "eraCodes": ["CINEMA_CLASSIQUE"],
        },
        {
            "code": "COLLECTION_006",
            "displayOrder": 7,
            "name": "Expressionnisme allemand",
            "description": "Ombres, décors distendus et psyché visuelle de Weimar.",
            "longDescription": (
                "Après 1919, le cinéma de Weimar invente une ville intérieure. Le Cabinet du docteur "
                "Caligari peint ses rues de travers, Nosferatu fait du vampire une silhouette, "
                "Metropolis dresse une architecture de classes. Fritz Lang et F. W. Murnau "
                "n'illustrent pas seulement l'angoisse : ils la construisent en lumière. "
                "L'expressionnisme déborde le fantastique, jusqu'à M le maudit. Quand ses artisans "
                "partent à Hollywood, ils emportent les ombres qui nourriront le film noir. "
                "Cette collection relie le studio allemand à une idée durable : le décor pense."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LES_TROIS_LUMIERES_1921", "CABINET_DU_DOCTEUR_CALIGARI_1920", "LE_GOLEM_1920",
                "NOSFERATU_1922", "DOCTEUR_MABUSE_LE_JOUEUR_1922", "LE_CABINET_DES_FIGURES_DE_CIRE_1924",
                "LE_DERNIER_DES_HOMMES_1924", "FAUST_1926", "METROPOLIS_1927",
                "ASPHALT_1929", "M_LE_MAUDIT_1931", "VAMPYR_1932",
            ]),
            "characteristicCodes": ["EXPRESSIONNISME_ALLEMAND"],
            "countryCodes": ["GERMANY"],
        },
        {
            "code": "COLLECTION_007",
            "displayOrder": 14,
            "name": "Montage soviétique",
            "description": "Le choc des plans comme pensée politique.",
            "longDescription": (
                "Dans les années 1920, l'URSS fait du montage une théorie autant qu'une technique. "
                "Sergueï Eisenstein choque les plans pour produire une idée, Dziga Vertov filme "
                "la caméra comme un œil nouveau, Dovjenko cherche une poésie agraire. "
                "Le Cuirassé Potemkine, Octobre et L'Homme à la caméra ne racontent pas seulement "
                "la révolution : ils essaient de la rendre visible. Plus tard, Alexandre Nevski "
                "et Ivan le Terrible montrent comment cette énergie se plie au pouvoir. "
                "Le montage soviétique reste une leçon : un film pense par collisions."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LA_GREVE_1925", "LE_CUIRASSE_POTEMKINE_1925", "LA_MERE_1926",
                "OCTOBRE_1928", "ARSENAL_1929", "L_HOMME_A_LA_CAMERA_1929", "LA_TERRE_1930",
                "ALEXANDRE_NEVSKI_1938", "IVAN_LE_TERRIBLE_1944", "JE_SUIS_CUBA_1964",
                "LES_CHEVAUX_DE_FEU_1965", "LE_MIROIR_1975",
            ]),
            "characteristicCodes": ["MONTAGE_SOVIETIQUE", "CINEMA_SOVIETIQUE"],
            "countryCodes": ["RUSSIA", "UKRAINE", "CUBA"],
        },
        {
            "code": "COLLECTION_008",
            "displayOrder": 5,
            "name": "Film noir",
            "description": "Fatalité urbaine, éclairages contrastés et moralité trouble.",
            "longDescription": (
                "Le film noir n'est pas un genre déclaré par Hollywood, c'est un climat reconnu après coup. "
                "Assurance sur la mort, Le Faucon maltais, Boulevard du crépuscule : des hommes parlent "
                "trop bien et meurent trop vite. La guerre, l'expressionnisme émigré et le roman hard-boiled "
                "s'y rencontrent. Jules Dassin emporte la formule à Paris avec Rififi, Carol Reed la "
                "plante à Vienne dans Le Troisième Homme. Plus tard, Chinatown relit le mythe à Los Angeles. "
                "Cette collection suit une lumière : celle qui coupe un visage en deux."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LE_FAUCON_MALTAIS_1941", "ASSURANCE_SUR_LA_MORT_1944", "LAURA_1944",
                "LES_TUEURS_1946", "GILDA_1946", "LE_TROISIEME_HOMME_1949", "LE_VIOLENT_1950",
                "BOULEVARD_DU_CREPUSCULE_1950", "LA_CITE_SANS_VOILES_1950",
                "DU_RIFIFI_CHEZ_LES_HOMMES_1955", "LA_SOIF_DU_MAL_1958", "CHINATOWN_1974",
            ]),
            "characteristicCodes": ["FILM_NOIR_STYLE"],
        },
        {
            "code": "COLLECTION_009",
            "displayOrder": 6,
            "name": "Westerns",
            "description": "La frontière américaine, puis sa réinvention italienne.",
            "longDescription": (
                "Le western est le mythe fondateur d'Hollywood : la diligence, le shérif, le désert. "
                "John Ford en fait une élégie, de La Chevauchée fantastique à La Prisonnière du désert. "
                "Hawks, Zinnemann et d'autres y testent le courage et la communauté. Dans les années 1960, "
                "Sergio Leone et Sergio Corbucci déplacent le genre en Espagne et en Italie : close-up, "
                "violence, ironie. Le western spaghetti n'imite pas Ford, il le démonte. "
                "Passer de Stagecoach à Django, c'est voir un mythe changer de continent et de morale."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LE_VOL_DU_GRAND_RAPIDE_1903", "LA_CHEVAUCHEE_FANTASTIQUE_1939",
                "LA_POURSUITE_INFERNALE_1946", "LA_RIVIERE_ROUGE_1948",
                "LE_TRAIN_SIFFLERA_TROIS_FOIS_1952", "LA_PRISONNIERE_DU_DESERT_1956",
                "RIO_BRAVO_1959", "L_HOMME_QUI_TUA_LIBERTY_VALANCE_1962",
                "POUR_UNE_POIGNEE_DE_DOLLARS_1964", "LE_BON_LA_BRUTE_ET_LE_TRUAND_1966",
                "DJANGO_1966", "IL_ETAIT_UNE_FOIS_DANS_L_OUEST_1968", "LE_GRAND_SILENCE_1968",
                "LA_HORDE_SAUVAGE_1969",
            ]),
            "characteristicCodes": ["WESTERN_CLASSIQUE", "SPAGHETTI_WESTERN"],
        },
        {
            "code": "COLLECTION_010",
            "displayOrder": 10,
            "name": "Nouveau cinéma allemand",
            "description": "Le renouveau ouest-allemand, d'Oberhausen à Fassbinder.",
            "longDescription": (
                "Après le manifeste d'Oberhausen en 1962, une génération refuse le cinéma de papa. "
                "Rainer Werner Fassbinder filme la RFA comme un mélodrame politique, Werner Herzog "
                "envoie ses héros dans la jungle et sur une montagne, Wim Wenders fait de la route "
                "et des anges un langage. Volker Schlöndorff adapte Grass. De 1966 à 1982, "
                "l'Allemagne de l'Ouest se raconte enfin sa violence, ses immigrés, son miracle "
                "économique. Ce n'est pas une école unique, c'est une colère formelle. "
                "On y apprend qu'un pays peut se filmer à rebours de ses publicités."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "AGUIRRE_LA_COLERE_DE_DIEU_1972", "ALICE_DANS_LES_VILLES_1974",
                "TOUS_LES_AUTRES_S_APPELLENT_ALI_1974", "L_HONNEUR_PERDU_DE_KATHARINA_BLUM_1975",
                "AU_FIL_DU_TEMPS_1976", "L_AMI_AMERICAIN_1977", "LE_MARIAGE_DE_MARIA_BRAUN_1979",
                "LE_TAMBOUR_1979", "FITZCARRALDO_1982", "LES_AILES_DU_DESIR_1987",
            ]),
            "characteristicCodes": ["NOUVEAU_CINEMA_ALLEMAND"],
            "countryCodes": ["GERMANY"],
        },
        {
            "code": "COLLECTION_011",
            "displayOrder": 11,
            "name": "Nouvelle vague iranienne",
            "description": "L'enfance, le hors-champ et la vie quotidienne comme politique.",
            "longDescription": (
                "Le cinéma iranien moderne s'invente entre poésie et contrainte. Forough Farrokhzad "
                "filme une léproserie comme un vers. Abbas Kiarostami fait de l'enfance, du village "
                "et du hors-champ un art de la question. Close-up brouille documentaire et fiction, "
                "Le Goût de la cerise marche le long d'une colline. Plus tard, Asghar Farhadi "
                "replie cette éthique du regard dans le huis clos bourgeois. La censure n'est pas "
                "un décor : elle oblige à filmer autrement. Cette vague n'imite pas la France des "
                "années 1960, elle invente une modestie radicale."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LA_MAISON_EST_NOIRE_1963", "LA_VACHE_1969", "LE_COUREUR_1985",
                "OU_EST_LA_MAISON_DE_MON_AMI_1987", "CLOSE_UP_1990",
                "LE_GOUT_DE_LA_CERISE_1997", "LE_VENT_NOUS_EMPORTERA_1999",
                "LE_CERCLE_2000", "UNE_SEPARATION_2011",
            ]),
            "characteristicCodes": ["NOUVELLE_VAGUE_IRANIENNE"],
            "countryCodes": ["IRAN"],
        },
        {
            "code": "COLLECTION_012",
            "displayOrder": 8,
            "name": "Cinéma muet",
            "description": "L'âge des images avant la parole synchronisée.",
            "longDescription": (
                "Avant 1930, le cinéma invente presque tous ses langages. Méliès truque la Lune, "
                "Griffith monumentalisé le récit, Keaton et Chaplin font du corps une grammaire. "
                "L'Allemagne expressionniste, la France impressionniste et l'URSS du montage "
                "prouvent que le silence n'est pas un manque. La Passion de Jeanne d'Arc colle "
                "aux visages, L'Aurore invente une caméra lyrique, Napoléon déborde l'écran. "
                "Le parlant n'efface pas cet âge : il le recouvre. Revenir au muet, c'est "
                "réapprendre à voir avant d'écouter."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "LA_SORTIE_DES_USINES_LUMIERE_1895", "L_ARRIVEE_D_UN_TRAIN_1896",
                "LA_FEE_AUX_CHOUX_1896", "VOYAGE_DANS_LA_LUNE_1902", "LE_VOL_DU_GRAND_RAPIDE_1903",
                "LE_LYS_BRISE_1919", "LA_CHARRETTE_FANTOME_1921", "CABINET_DU_DOCTEUR_CALIGARI_1920",
                "HAXAN_1922", "LE_CUIRASSE_POTEMKINE_1925", "LA_RUEE_VERS_LOR_1925",
                "METROPOLIS_1927", "L_AURORE_1927", "NAPOLEON_1927",
                "LA_PASSION_DE_JEANNE_DARC_1928", "L_HOMME_A_LA_CAMERA_1929",
                "UN_CHIEN_ANDALOU_1929",
            ]),
            "characteristicCodes": ["CINEMA_MUET_MOUVEMENT"],
            "eraCodes": ["CINEMA_MUET"],
        },
        {
            "code": "COLLECTION_013",
            "displayOrder": 12,
            "name": "Cinémas d'Afrique",
            "description": "Des fables politiques, de Sembène à Cissé et Sissako.",
            "longDescription": (
                "Ousmane Sembène, souvent appelé le père des cinémas africains, filme Dakar, "
                "le mandat et la domesticité coloniale. Djibril Diop Mambéty collant Touki Bouki "
                "invente une modernité wolof, entre vaches et paquebot. Au Mali, Souleymane Cissé "
                "ouvre Yeelen comme un récit initiatique. Youssef Chahine et Shadi Abdel Salam "
                "inscrivent l'Égypte dans une histoire plus ancienne que Nasser. Plus tard, "
                "Abderrahmane Sissako observe Timbuktu sous occupation. Cette collection n'unifie "
                "pas un continent : elle refuse qu'on le réduise à un hors-champ."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "GARE_CENTRALE_1958", "LA_NOIRE_DE_1966", "LE_MANDAT_1968", "LA_MUMIE_1969",
                "SAMBIZANGA_1972", "TOUKI_BOUKI_1973", "XALA_1975",
                "CHRONIQUE_DES_ANNEES_DE_BRAISE_1975", "CEDDO_1977", "WEND_KUUNI_1982",
                "YEELEN_1987", "YAABA_1989", "HYENES_1992", "TIMBUKTU_2014",
            ]),
            "characteristicCodes": ["CINEMA_AFRICAIN"],
            "continentCodes": ["AFRICA"],
        },
        {
            "code": "COLLECTION_014",
            "displayOrder": 13,
            "name": "Amérique latine",
            "description": "Du Cinema Novo aux récits contemporains du Mexique et de l'Argentine.",
            "longDescription": (
                "Glauber Rocha proclame une esthétique de la faim et arme le sertão. "
                "Luis Buñuel, exilé au Mexique, filme Los Olvidados sans misérabilisme. "
                "Plus tard, la Cité de Dieu, Roma, Amours chiennes et le Labyrinthe de Pan "
                "montrent un cinéma latin américain devenu visible dans les festivals du Nord, "
                "sans cesser de parler de classes, de bonnes, de favelas et de dictatures. "
                "En Argentine, l'Histoire officielle et Lucrecia Martel travaillent la mémoire "
                "et le non-dit bourgeois. Cette carte n'est pas exhaustive : elle ouvre des routes."
            ),
            "isPublished": True,
            "movies": pick_movies(movies, [
                "L_ANGE_EXTERMINATEUR_1962", "LOS_OLVIDADOS_1950",
                "DIEU_NOIR_ET_DIABLE_BLOND_1964", "MEMOIRES_DU_SOUS_DEVELOPPEMENT_1968",
                "L_HEURE_DES_FOURNEAUX_1968", "LUCIA_1968", "LE_CHACAL_DE_NAHUELTORO_1969",
                "PIXOTE_1980", "L_HISTOIRE_OFFICIELLE_1985", "CENTRAL_DO_BRASIL_1998",
                "AMORES_PERROS_2000", "CITE_DE_DIEU_2002", "LE_LABYRINTHE_DE_PAN_2006",
                "LA_FEMME_SANS_TETE_2008", "NOSTALGIE_DE_LA_LUMIERE_2010",
                "LE_BOUTON_DE_NACRE_2015", "ROMA_2018",
            ]),
            "continentCodes": ["SOUTH_AMERICA", "NORTH_AMERICA"],
        },
    ]
    tracks = {
        "COLLECTION_INITIATION": "GATEWAY",
        "COLLECTION_005": "GATEWAY",
        "COLLECTION_002": "CLUB",
        "COLLECTION_003": "CLUB",
        "COLLECTION_006": "CLUB",
        "COLLECTION_008": "CLUB",
        "COLLECTION_009": "CLUB",
        "COLLECTION_001": "DARKROOM",
        "COLLECTION_004": "DARKROOM",
        "COLLECTION_010": "DARKROOM",
        "COLLECTION_012": "CINEMATHEQUE",
        "COLLECTION_011": "CINEMATHEQUE",
        "COLLECTION_013": "CINEMATHEQUE",
        "COLLECTION_014": "CINEMATHEQUE",
        "COLLECTION_007": "OFFSCREEN",
    }
    for collection in collections:
        code = collection["code"]
        if code not in tracks:
            raise SystemExit(f"Missing difficulty track for {code}")
        collection["track"] = tracks[code]
    return collections


def used_directors(movies: list[dict]) -> list[dict]:
    ordered: list[str] = []
    seen: set[str] = set()
    for movie in movies:
        for item in movie["directors"]:
            code = item["code"]
            if code not in seen:
                seen.add(code)
                ordered.append(code)
    return [director_entry(code) for code in ordered]


def validate_pack(pack: dict) -> list[str]:
    errors: list[str] = []
    movies = pack["movies"]
    if len(movies) != REQUIRED_MOVIE_COUNT:
        errors.append(f"expected {REQUIRED_MOVIE_COUNT} movies, got {len(movies)}")
    codes = [movie["code"] for movie in movies]
    if len(codes) != len(set(codes)):
        dup = sorted({code for code in codes if codes.count(code) > 1})
        errors.append(f"duplicate movie codes: {dup}")
    missing_required = sorted(REQUIRED_MOVIE_CODES - set(codes))
    if missing_required:
        errors.append(f"missing required movies: {missing_required}")

    type_codes = {item[0] for item in CHARACTERISTIC_TYPES}
    country_codes = {item[0] for item in COUNTRIES}
    continent_codes = {item[0] for item in CONTINENTS}
    director_codes = {item["code"] for item in pack["directors"]}
    characteristic_codes = {item[0] for item in CHARACTERISTICS}
    genre_codes = {item[0] for item in GENRES}
    era_codes = {item[0] for item in ERAS}
    movie_codes = set(codes)

    for movie in movies:
        path = movie["code"]
        if movie["durationMinutes"] <= 0:
            errors.append(f"{path}: duration must be positive")
        if movie["releaseYear"] < 1880 or movie["releaseYear"] > 2028:
            errors.append(f"{path}: year out of range")
        if movie["format"] not in {"SHORT", "MEDIUM", "FEATURE", "EXTENDED"}:
            errors.append(f"{path}: invalid format")
        if movie["durationMinutes"] >= 180 and movie["format"] != "EXTENDED":
            errors.append(f"{path}: EXTENDED required for duration >= 180")
        for score_name in ("historicalDistance", "artisticDemand", "historicalRichness", "culturalRichness"):
            score = movie[score_name]
            if not 0.0 <= score <= 1.0:
                errors.append(f"{path}: {score_name} out of [0,1]")
        primaries = [row for row in movie["countries"] if row["isPrimary"]]
        if len(primaries) != 1:
            errors.append(f"{path}: need exactly one primary country")
        if not movie["directors"]:
            errors.append(f"{path}: need at least one director")
        for row in movie["countries"]:
            if row["code"] not in country_codes:
                errors.append(f"{path}: unknown country {row['code']}")
        for row in movie["directors"]:
            if row["code"] not in director_codes:
                errors.append(f"{path}: unknown director {row['code']}")
        for genre in movie["genreCodes"]:
            if genre not in genre_codes:
                errors.append(f"{path}: unknown genre {genre}")
        for char in movie["characteristicCodes"]:
            if char not in characteristic_codes:
                errors.append(f"{path}: unknown characteristic {char}")
        if movie["format"] == "EXTENDED" and movie["durationMinutes"] < 180:
            errors.append(f"{path}: EXTENDED but duration < 180")

    for collection in pack["collections"]:
        for row in collection["movies"]:
            if row["code"] not in movie_codes:
                errors.append(f"{collection['code']}: unknown movie {row['code']}")
        for code in collection.get("characteristicCodes", []):
            if code not in characteristic_codes:
                errors.append(f"{collection['code']}: unknown characteristic {code}")
        for code in collection.get("countryCodes", []):
            if code not in country_codes:
                errors.append(f"{collection['code']}: unknown country {code}")
        for code in collection.get("continentCodes", []):
            if code not in continent_codes:
                errors.append(f"{collection['code']}: unknown continent {code}")
        for code in collection.get("eraCodes", []):
            if code not in era_codes:
                errors.append(f"{collection['code']}: unknown era {code}")
        if not collection.get("longDescription"):
            errors.append(f"{collection['code']}: missing longDescription")

    for char in pack["characteristics"]:
        if char["typeCode"] not in type_codes:
            errors.append(f"characteristic {char['code']}: unknown type {char['typeCode']}")
    for country in pack["countries"]:
        for continent in country["continentCodes"]:
            if continent not in continent_codes:
                errors.append(f"country {country['code']}: unknown continent {continent}")
    for director in pack["directors"]:
        for char in director.get("characteristicCodes", []):
            if char not in characteristic_codes:
                errors.append(f"director {director['code']}: unknown characteristic {char}")

    if len(pack["rankings"]) != 10:
        errors.append("need 10 rankings")
    if any(not ranking.get("longDescription") for ranking in pack["rankings"]):
        errors.append("rankings need longDescription")
    if len(pack["badges"]) != 30:
        errors.append("need 30 badges")
    return errors


def build_pack() -> dict:
    movies = parse_film_table(FILM_TABLE)
    return {
        "version": VERSION,
        "generatedAt": GENERATED_AT,
        "mediaAssets": [],
        "characteristicTypes": [
            {"typeCode": code, "name": name} for code, name in CHARACTERISTIC_TYPES
        ],
        "continents": [{"code": code, "name": name} for code, name in CONTINENTS],
        "countries": [
            {"code": code, "name": name, "isoCode": iso, "continentCodes": continents}
            for code, name, iso, continents in COUNTRIES
        ],
        "directors": used_directors(movies),
        "characteristics": [
            {"code": code, "name": name, "typeCode": type_code, "description": description}
            for code, name, type_code, description in CHARACTERISTICS
        ],
        "genres": [{"code": code, "name": name} for code, name in GENRES],
        "eras": [
            {"code": code, "name": name, "startYear": start, "endYear": end}
            for code, name, start, end in ERAS
        ],
        "movies": movies,
        "collections": build_collections(movies),
        "rankings": [
            {
                "code": code,
                "displayOrder": order,
                "name": name,
                "description": RANK_SHORT[code],
                "longDescription": description,
            }
            for code, order, name, description in RANKINGS
        ],
        "badges": [
            {
                "code": code,
                "name": name,
                "description": description,
                "difficulty": difficulty,
                "category": category,
            }
            for code, name, description, difficulty, category in BADGES
        ],
        "quests": [
            {
                "code": code,
                "name": name,
                "description": description,
                "difficulty": difficulty,
                "ruleCode": rule,
                "targetCount": target,
            }
            for code, name, description, difficulty, rule, target in QUESTS
        ],
    }


def summarize(pack: dict) -> None:
    movies = pack["movies"]
    silent = sum(1 for movie in movies if movie.get("isSilent"))
    experimental = sum(1 for movie in movies if movie.get("isExperimental"))
    before_1950 = sum(1 for movie in movies if movie["releaseYear"] < 1950)
    long_3h = sum(1 for movie in movies if movie["durationMinutes"] > 180)
    long_5h = sum(1 for movie in movies if movie["durationMinutes"] > 300)
    asian = {
        next(country["code"] for country in movie["countries"] if country["isPrimary"])
        for movie in movies
        if any(
            country_code in {row[0] for row in COUNTRIES if "ASIA" in row[3]}
            for country_code in [c["code"] for c in movie["countries"] if c["isPrimary"]]
        )
    }
    print(f"movies={len(movies)} countries={len(pack['countries'])} "
          f"directors={len(pack['directors'])} collections={len(pack['collections'])}")
    print(f"silent={silent} experimental={experimental} before1950={before_1950} "
          f">180min={long_3h} >300min={long_5h} asianPrimaryCountries={len(asian)}")


def main() -> int:
    pack = build_pack()
    errors = validate_pack(pack)
    if errors:
        print("Catalog validation failed:", file=sys.stderr)
        for error in errors[:50]:
            print(f" - {error}", file=sys.stderr)
        if len(errors) > 50:
            print(f" - ... and {len(errors) - 50} more", file=sys.stderr)
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(OUTPUT.read_text(encoding="utf-8"))
    summarize(pack)
    print(f"wrote {OUTPUT}")
    print("json_valid=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
