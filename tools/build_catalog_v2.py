#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prépare catalog_v2 (méta + CSV 1000 films) puis fusionne le JSON TMDB."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_V1 = ROOT / "app/src/main/assets/catalog/catalog_v1.json"
CATALOG_V2 = ROOT / "app/src/main/assets/catalog/catalog_v2.json"
CATALOG_LIVE = ROOT / "app/src/main/assets/catalog/catalog.json"
LIST_1000 = ROOT / "specs/Listes_Fonctionnelles/Liste_1000_Films_Hors_Catalogue.txt"
INPUT_1000 = ROOT / "batchPosters/input/input_1000.txt"
TMDB_MOVIES = ROOT / "batchPosters/output/catalog/movies.json"
POSTERS_OUT = ROOT / "batchPosters/output/posters"
POSTERS_APP = ROOT / "app/src/main/assets/media/posters"

sys.path.insert(0, str(ROOT / "batchPosters"))
from catalog_enrich import ascii_slug, movie_code, scores_for  # noqa: E402


def fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^\w]+", " ", stripped.casefold(), flags=re.UNICODE).strip()


NEW_CHARACTERISTICS = [
    ("NOUVELLE_VAGUE_JAPONAISE", "Nouvelle Vague japonaise (Nūberu Bāgu)", "WAVE",
     "Le nūberu bāgu des années 1960 : Ōshima, Imamura, Shinoda, Yoshida, Suzuki."),
    ("CINEMA_CLASSIQUE_ITALIEN", "Cinéma classique italien", "PERIOD",
     "L'âge des auteurs italiens après le néoréalisme : Fellini, Antonioni, Visconti."),
    ("CINEMA_POLITIQUE_ITALIEN", "Cinéma politique italien", "CURRENT",
     "Le cinéma engagé italien, de Pasolini et Rosi à Bertolucci et Pontecorvo."),
    ("CINEMA_INDEPENDANT_AMERICAIN", "Cinéma indépendant américain", "CURRENT",
     "Hors studios : Cassavetes, Jarmusch, l'indie US et ses héritiers."),
    ("CINEMA_VERITE", "Cinéma-vérité", "SCHOOL",
     "Caméra participante, parole directe : Rouch, Morin, et la tradition vérité."),
    ("CINQUIEME_GENERATION_CHINOISE", "Cinquième génération chinoise", "WAVE",
     "Les cinéastes sortis de Pékin après 1982 : Chen Kaige, Zhang Yimou, Tian Zhuangzhuang."),
    ("SIXIEME_GENERATION_CHINOISE", "Sixième génération chinoise", "WAVE",
     "Le cinéma urbain chinois des années 1990-2000 : Jia Zhangke, Wang Bing, Jiang Wen."),
    ("ECOLE_BRITANNIQUE_DOCUMENTAIRE", "École britannique documentaire", "SCHOOL",
     "Le documentaire social britannique, de Grierson et Jennings au Free Cinema."),
    ("FREE_CINEMA", "Free Cinema britannique", "WAVE",
     "Courts documentaires et fictions sociales britanniques de la fin des années 1950."),
    ("NOUVELLE_VAGUE_BRITANNIQUE", "Nouvelle Vague britannique / Kitchen Sink", "WAVE",
     "Le réalisme social britannique : Saturday Night, This Sporting Life, Loach, Leigh."),
    ("NOUVELLE_GENERATION_IRANIENNE", "Nouvelle génération iranienne", "WAVE",
     "Après Kiarostami : Panahi, Farhadi, et le cinéma iranien des années 2000."),
    ("CINEMA_QUEBECOIS_MODERNE", "Cinéma québécois moderne", "CURRENT",
     "Le cinéma québécois d'auteur, de Jutra et Arcand à Egoyan et Villeneuve."),
    ("AUSTRALIAN_NEW_WAVE", "Australian New Wave", "WAVE",
     "La vague australienne des années 1970 : Weir, Armstrong, Beresford, Schepisi."),
    ("LA_REBELLION", "Cinéma afro-américain indépendant / L.A. Rebellion", "SCHOOL",
     "L.A. Rebellion et le cinéma noir indépendant : Burnett, Dash, Gerima, Spike Lee."),
    ("NEW_QUEER_CINEMA", "New Queer Cinema", "WAVE",
     "Le New Queer Cinema des années 1990 : Haynes, Van Sant, Jarman, Livingston."),
    ("NOUVEAU_CINEMA_ROUMAIN", "Nouveau cinéma roumain", "WAVE",
     "La Romanian New Wave : Puiu, Mungiu, Porumboiu, le plan-séquence du réel."),
    ("NOUVELLE_VAGUE_HONGROISE", "Nouvelle Vague hongroise", "WAVE",
     "Jancsó, Szabó, et le cinéma hongrois moderne des années 1960."),
    ("BLACK_WAVE_YOUGOSLAVE", "Black Wave yougoslave", "WAVE",
     "Le Black Wave yougoslave : Makavejev, Petrović, Pavlović, Žilnik."),
    ("CINEMA_POLITIQUE_LATINO", "Cinéma politique latino-américain", "CURRENT",
     "Le cinéma politique latino-américain, de Cuba à l'Argentine et au Chili."),
    ("NOUVELLE_VAGUE_PHILIPPINE", "Nouvelle Vague philippine", "WAVE",
     "Brocka, Bernal, Diaz : le cinéma philippin d'auteur et de dénonciation."),
    ("CINEMA_DU_LOOK", "Cinéma du look français", "STYLE",
     "Beineix, Besson, Carax : image saturée, clips et romantisme des années 1980."),
    ("NEW_FRENCH_EXTREMITY", "New French Extremity", "CURRENT",
     "L'extrême contemporain français : Noé, Denis, Haneke, horreur et transgression."),
    ("SLOW_CINEMA", "Slow Cinema", "STYLE",
     "Plans longs, temps dilaté : Tarr, Costa, Tsai, Díaz, Weerasethakul."),
    ("NUEVO_CINE_ARGENTINO", "Nuevo Cine Argentino", "WAVE",
     "Le nouveau cinéma argentin des années 1990-2000 : Martel, Bielinsky, Llinás."),
    ("NUEVO_CINE_MEXICANO", "Nuevo Cine Mexicano", "WAVE",
     "Le renouveau mexicain : Cuarón, Iñárritu, del Toro, Reygadas."),
    ("CINEMA_ESPAGNOL_MODERNE", "Nouvelle vague / cinéma moderne espagnol", "WAVE",
     "Erice, Saura, Berlanga, Almodóvar : l'Espagne après le franquisme et avant."),
    ("NOUVELLE_VAGUE_SCANDINAVE", "Nouvelle vague scandinave", "WAVE",
     "Bergman et ses héritiers, Kaurismäki, Moodysson, Andersson, Trier (hors Dogme)."),
    ("CINEMA_TURC_MODERNE", "Cinéma turc moderne", "CURRENT",
     "Güney, Ceylan, et le cinéma turc d'auteur contemporain."),
    ("CINEMA_MAGHREBIN", "Cinéma maghrébin postcolonial", "CURRENT",
     "Algérie, Tunisie, Maroc : Lakhdar-Hamina, Allouache, Tlatli, Boughedir."),
    ("CINEMA_AFRICAIN_POSTCOLONIAL", "Cinéma africain postcolonial", "CURRENT",
     "Les cinémas d'Afrique après les indépendances, au-delà du Sénégal et du Mali."),
    ("NOUVELLE_VAGUE_CHILIENNE", "Nouvelle vague chilienne", "WAVE",
     "Littín, Guzmán, Larraín : exil, mémoire et cinéma chilien."),
    ("RETOMADA_BRESILIENNE", "Retomada brésilienne", "WAVE",
     "La retomada des années 1990-2010 : Salles, Padilha, Mendonça Filho."),
    ("CINEMA_THAILANDAIS", "Cinéma thaïlandais contemporain", "CURRENT",
     "Weerasethakul et le cinéma thaïlandais d'auteur contemporain."),
    ("CINEMA_INDONESIEN", "Cinéma indonésien contemporain", "CURRENT",
     "Nugroho, Surya, Anwar, et le cinéma indonésien contemporain."),
    ("CINEMA_MALAYALAM", "Cinéma malayalam contemporain", "CURRENT",
     "Le cinéma du Kerala, de Gopalakrishnan au New Malayalam."),
    ("NOUVELLE_VAGUE_SINGAPOURIENNE", "Nouvelle vague singapourienne", "WAVE",
     "Khoo, Chen, Tan : le cinéma singapourien d'auteur."),
    ("CINEMA_VIETNAMIEN", "Cinéma vietnamien moderne", "CURRENT",
     "Tran Anh Hung et le cinéma vietnamien moderne."),
    ("CINEMA_CAMBODGIEN", "Cinéma cambodgien moderne", "CURRENT",
     "Rithy Panh et la mémoire du Cambodge contemporain."),
    ("NOUVELLE_VAGUE_GEORGIENNE", "Nouvelle vague géorgienne", "WAVE",
     "Iosseliani, Abuladze, et le cinéma géorgien d'auteur."),
    ("CINEMA_BALTE", "Cinéma balte contemporain", "CURRENT",
     "Estonie, Lettonie, Lituanie : le cinéma balte contemporain."),
    ("CINEMA_POST_SOVIETIQUE", "Cinéma post-soviétique", "PERIOD",
     "Après 1991 : Sokurov, Zvyagintsev, German, Balabanov."),
    ("NOUVELLE_VAGUE_ISRAELIENNE", "Nouvelle vague israélienne", "WAVE",
     "Le cinéma israélien contemporain : Folman, Maoz, Kolirin."),
    ("CINEMA_PALESTINIEN", "Cinéma palestinien", "CURRENT",
     "Suleiman, Abu-Assad, Khleifi : le cinéma palestinien."),
    ("NOUVELLE_VAGUE_LIBANAISE", "Nouvelle vague libanaise", "WAVE",
     "Labaki, Doueiri, et le cinéma libanais contemporain."),
    ("NOLLYWOOD", "Cinéma nigérian / Nollywood", "CURRENT",
     "Nollywood et le New Nigerian Cinema : Afolayan, Adetiba, Nnaji."),
    ("CINEMA_SUD_AFRICAIN", "Cinéma sud-africain contemporain", "CURRENT",
     "Le cinéma sud-africain après l'apartheid : Tsotsi, District 9, The Wound."),
    ("CINEMA_SENEGALAIS", "Cinéma sénégalais", "CURRENT",
     "Sembène, Mambéty, Diop, Gomis : le cinéma sénégalais."),
    ("CINEMA_MALIEN", "Cinéma malien", "CURRENT",
     "Cissé, Sissako, Sissoko : le cinéma malien."),
    ("CINEMA_ETHIOPIEN", "Cinéma éthiopien contemporain", "CURRENT",
     "Haile Gerima et le cinéma éthiopien contemporain."),
    ("CINEMA_NEO_ZELANDAIS", "Cinéma néo-zélandais", "CURRENT",
     "Campion, Jackson, Waititi : le cinéma néo-zélandais."),
    ("CINEMA_AUTOCHTONE", "Cinéma amérindien / Indigenous Cinema", "CURRENT",
     "Kunuk, Eyre, Barnaby, Zhao : le cinéma autochtone."),
    ("CINEMA_FEMINISTE", "Cinéma féministe", "CURRENT",
     "Un cinéma qui place l'expérience des femmes au centre du regard."),
    ("CINEMA_QUEER_CONTEMPORAIN", "Cinéma queer contemporain", "CURRENT",
     "Le cinéma queer après le New Queer Cinema : Moonlight, Carol, 120 BPM."),
    ("CINEMA_MILITANT", "Cinéma militant", "CURRENT",
     "Films de lutte, de grève et de manifeste politique."),
    ("CINEMA_POSTCOLONIAL", "Cinéma postcolonial", "CURRENT",
     "Un cinéma qui pense l'après-empire, la langue et la mémoire coloniale."),
    ("CINEMA_DIASPORIQUE", "Cinéma diasporique", "CURRENT",
     "Exil, migration, double culture : La Haine, Head-On, Minari, Atlantique."),
    ("CINEMA_TRANSGRESSION", "Cinéma de transgression", "STYLE",
     "Waters, Korine, Ferrara : trash, scandale et transgression assumée."),
    ("CINEMA_PUNK", "Cinéma punk", "STYLE",
     "L'esprit punk à l'écran : Jubilee, Repo Man, Decline of Western Civilization."),
    ("NO_WAVE", "No Wave Cinema", "WAVE",
     "Le No Wave new-yorkais : Jarmusch, Ferrara, Borden, Gordon."),
    ("BLAXPLOITATION", "Blaxploitation", "STYLE",
     "Shaft, Super Fly, Coffy : le cycle blaxploitation des années 1970."),
    ("POLIZIOTTESCO", "Poliziottesco", "STYLE",
     "Le polar italien violent des années 1970 : Di Leo, Lenzi, Castellari."),
    ("MUMBLECORE", "Mumblecore", "WAVE",
     "Bujalski, Swanberg, Duplass : dialogues, DIY et indé US des années 2000."),
    ("CINEMA_EXPLOITATION", "Cinéma d'exploitation", "STYLE",
     "Sexploitation, horreur cheap, drive-in : Meyer, Corman, Craven."),
    ("GRINDHOUSE", "Grindhouse", "STYLE",
     "Le circuit grindhouse et ses hommages : Hills Have Eyes, Death Proof."),
    ("CINEMA_GORE", "Cinéma gore", "STYLE",
     "Splatter et gore : Fulci, Romero, Jackson, Gordon."),
    ("PSYCHOTRONIC", "Psychotronic Cinema", "STYLE",
     "Cultes bizarres, Troma, Liquid Sky, Donnie Darko."),
    ("CINEMA_ABSTRAIT", "Cinéma abstrait", "STYLE",
     "Cinéma visuel non figuratif : Whitney, Belson, Kubelka, Conrad."),
    ("CINEMA_DADAISTE", "Cinéma dadaïste", "MOVEMENT",
     "Dada à l'écran : Entr'acte, Anémic Cinéma, Man Ray, Richter."),
    ("CINEMA_PUR", "Cinéma pur", "MOVEMENT",
     "Le cinéma pur et les city symphonies : Cavalcanti, Ivens, Manhatta."),
    ("STRUCTURAL_FILM", "Structural Film", "SCHOOL",
     "Le structural film : Snow, Frampton, Gehr, Brakhage."),
    ("EXPANDED_CINEMA", "Expanded Cinema", "STYLE",
     "L'expanded cinema : Warhol, McCall, installations et durée extrême."),
    ("FOUND_FOOTAGE", "Found Footage Cinema", "STYLE",
     "Found footage expérimental et pop : Conner, Morrison, Blair Witch."),
    ("ESSAY_FILM", "Essay Film / cinéma-essai", "STYLE",
     "Le film-essai : Marker, Welles, Akerman, Andersen, Farrokhzad."),
    ("AGE_OR_HOLLYWOOD", "Âge d'or d'Hollywood", "PERIOD",
     "Le studio system et le star system, ~1927–1960, apogée des majors."),
    ("NOUVEL_AGE_OR_HOLLYWOOD", "Nouvel âge d'or hollywoodien", "PERIOD",
     "Renaissance prestige US ~1990–2015 : Tarantino, PTA, Coen, Fincher, Nolan."),
]

COURANT_TO_CODE = {
    "Hollywood classique": "HOLLYWOOD_CLASSIQUE",
    "Montage soviétique": "MONTAGE_SOVIETIQUE",
    "Néoréalisme italien": "NEOREALISME_ITALIEN",
    "Nouvelle Vague française": "NOUVELLE_VAGUE_FRANCAISE",
    "Expressionnisme allemand": "EXPRESSIONNISME_ALLEMAND",
    "Nouvel Hollywood": "NEW_HOLLYWOOD",
    "Surréalisme cinématographique": "SURREALISME",
    "Film noir": "FILM_NOIR_STYLE",
    "Impressionnisme français": "IMPRESSIONNISME_FRANCAIS",
    "Nouvelle Vague japonaise (Nūberu Bāgu)": "NOUVELLE_VAGUE_JAPONAISE",
    "Nouveau cinéma allemand": "NOUVEAU_CINEMA_ALLEMAND",
    "Âge d'or du cinéma japonais": "AGE_OR_CINEMA_JAPONAIS",
    "Nouvelle Vague taïwanaise": "TAIWAN_NEW_CINEMA",
    "Cinéma Novo brésilien": "CINEMA_NOVO",
    "Cinéma soviétique / russe moderne": "CINEMA_SOVIETIQUE",
    "Cinéma classique italien": "CINEMA_CLASSIQUE_ITALIEN",
    "Nouvelle Vague hongkongaise": "HONG_KONG_NEW_WAVE",
    "Cinéma politique italien": "CINEMA_POLITIQUE_ITALIEN",
    "Cinéma parallèle indien (Parallel Cinema)": "INDIAN_PARALLEL",
    "Cinéma indépendant américain": "CINEMA_INDEPENDANT_AMERICAIN",
    "École polonaise du cinéma": "ECOLE_POLONAISE",
    "Cinéma-vérité": "CINEMA_VERITE",
    "Nouvelle Vague tchécoslovaque": "NOUVELLE_VAGUE_TCHEQUE",
    "Cinéma direct": "CINEMA_DIRECT",
    "Spaghetti Western": "SPAGHETTI_WESTERN",
    "Nouvelle Vague sud-coréenne": "KOREAN_NEW_WAVE",
    "Cinquième génération chinoise": "CINQUIEME_GENERATION_CHINOISE",
    "Réalisme poétique français": "REALISME_POETIQUE",
    "Cinéma expérimental américain / New American Cinema": "CINEMA_EXPERIMENTAL",
    "Troisième Cinéma": "THIRD_CINEMA",
    "Nouvelle vague iranienne": "NOUVELLE_VAGUE_IRANIENNE",
    "Sixième génération chinoise": "SIXIEME_GENERATION_CHINOISE",
    "École britannique documentaire / documentaire social britannique": "ECOLE_BRITANNIQUE_DOCUMENTAIRE",
    "Free Cinema britannique": "FREE_CINEMA",
    "Nouvelle Vague britannique / Kitchen Sink": "NOUVELLE_VAGUE_BRITANNIQUE",
    "Commedia all'italiana": "COMMEDIA_ALL_ITALIANA",
    "Nouvelle génération iranienne": "NOUVELLE_GENERATION_IRANIENNE",
    "Cinéma québécois moderne": "CINEMA_QUEBECOIS_MODERNE",
    "Australian New Wave": "AUSTRALIAN_NEW_WAVE",
    "Cinéma afro-américain indépendant / L.A. Rebellion": "LA_REBELLION",
    "Dogme 95": "DOGME_95",
    "New Queer Cinema": "NEW_QUEER_CINEMA",
    "Nouveau cinéma roumain / Romanian New Wave": "NOUVEAU_CINEMA_ROUMAIN",
    "Nouvelle Vague hongroise": "NOUVELLE_VAGUE_HONGROISE",
    "Black Wave yougoslave": "BLACK_WAVE_YOUGOSLAVE",
    "Cinéma politique latino-américain": "CINEMA_POLITIQUE_LATINO",
    "Nouvelle Vague philippine": "NOUVELLE_VAGUE_PHILIPPINE",
    "Cinéma du look français": "CINEMA_DU_LOOK",
    "New French Extremity": "NEW_FRENCH_EXTREMITY",
    "Slow Cinema": "SLOW_CINEMA",
    "Nuevo Cine Argentino": "NUEVO_CINE_ARGENTINO",
    "Nuevo Cine Mexicano": "NUEVO_CINE_MEXICANO",
    "Nouvelle vague / cinéma moderne espagnol": "CINEMA_ESPAGNOL_MODERNE",
    "Nouvelle vague scandinave": "NOUVELLE_VAGUE_SCANDINAVE",
    "Cinéma turc moderne": "CINEMA_TURC_MODERNE",
    "Cinéma maghrébin postcolonial": "CINEMA_MAGHREBIN",
    "Cinéma africain postcolonial": "CINEMA_AFRICAIN_POSTCOLONIAL",
    "Nouvelle vague chilienne": "NOUVELLE_VAGUE_CHILIENNE",
    "Retomada brésilienne": "RETOMADA_BRESILIENNE",
    "Cinéma thaïlandais contemporain": "CINEMA_THAILANDAIS",
    "Cinéma indonésien contemporain": "CINEMA_INDONESIEN",
    "Cinéma malayalam contemporain": "CINEMA_MALAYALAM",
    "Nouvelle vague singapourienne": "NOUVELLE_VAGUE_SINGAPOURIENNE",
    "Cinéma vietnamien moderne": "CINEMA_VIETNAMIEN",
    "Cinéma cambodgien moderne": "CINEMA_CAMBODGIEN",
    "Nouvelle vague géorgienne": "NOUVELLE_VAGUE_GEORGIENNE",
    "Cinéma balte contemporain": "CINEMA_BALTE",
    "Cinéma post-soviétique": "CINEMA_POST_SOVIETIQUE",
    "Nouvelle vague israélienne": "NOUVELLE_VAGUE_ISRAELIENNE",
    "Cinéma palestinien": "CINEMA_PALESTINIEN",
    "Nouvelle vague libanaise": "NOUVELLE_VAGUE_LIBANAISE",
    "Cinéma nigérian / Nollywood": "NOLLYWOOD",
    "Cinéma sud-africain contemporain": "CINEMA_SUD_AFRICAIN",
    "Cinéma sénégalais": "CINEMA_SENEGALAIS",
    "Cinéma malien": "CINEMA_MALIEN",
    "Cinéma éthiopien contemporain": "CINEMA_ETHIOPIEN",
    "Cinéma néo-zélandais": "CINEMA_NEO_ZELANDAIS",
    "Cinéma amérindien / Indigenous Cinema": "CINEMA_AUTOCHTONE",
    "Cinéma féministe": "CINEMA_FEMINISTE",
    "Cinéma queer contemporain": "CINEMA_QUEER_CONTEMPORAIN",
    "Cinéma militant": "CINEMA_MILITANT",
    "Cinéma postcolonial": "CINEMA_POSTCOLONIAL",
    "Cinéma diasporique": "CINEMA_DIASPORIQUE",
    "Cinéma de transgression": "CINEMA_TRANSGRESSION",
    "Cinéma punk": "CINEMA_PUNK",
    "No Wave Cinema": "NO_WAVE",
    "Blaxploitation": "BLAXPLOITATION",
    "Poliziottesco": "POLIZIOTTESCO",
    "Mumblecore": "MUMBLECORE",
    "Cinéma d'exploitation": "CINEMA_EXPLOITATION",
    "Grindhouse": "GRINDHOUSE",
    "Cinéma gore": "CINEMA_GORE",
    "Psychotronic Cinema": "PSYCHOTRONIC",
    "Cinéma abstrait": "CINEMA_ABSTRAIT",
    "Cinéma dadaïste": "CINEMA_DADAISTE",
    "Cinéma pur": "CINEMA_PUR",
    "Structural Film": "STRUCTURAL_FILM",
    "Expanded Cinema": "EXPANDED_CINEMA",
    "Found Footage Cinema": "FOUND_FOOTAGE",
    "Essay Film / cinéma-essai": "ESSAY_FILM",
    "Âge d'or d'Hollywood": "AGE_OR_HOLLYWOOD",
    "Nouvel âge d'or hollywoodien": "NOUVEL_AGE_OR_HOLLYWOOD",
}

NEW_GENRES = [
    ("ACTION", "Action"),
    ("ARTS_MARTIAUX", "Arts martiaux"),
    ("BIOGRAPHIQUE", "Biographique"),
    ("CATASTROPHE", "Catastrophe"),
    ("COMEDIE_DRAMATIQUE", "Comédie dramatique"),
    ("CRIME", "Crime"),
    ("ENQUETE", "Enquête"),
    ("EPOUVANTE", "Épouvante"),
    ("EROTIQUE", "Érotique"),
    ("ESPIONNAGE", "Espionnage"),
    ("FAMILLE", "Famille"),
    ("FANTASTIQUE", "Fantastique"),
    ("GANGSTER", "Gangster"),
    ("MYSTERE", "Mystère"),
    ("PEPLUM", "Péplum"),
    ("POLITIQUE", "Politique"),
    ("SPORT", "Sport"),
    ("SUPER_HEROS", "Super-héros"),
]

NEW_COUNTRIES = [
    ("NIGERIA", "Nigeria", "NG", ["AFRICA"]),
    ("PALESTINE", "Palestine", "PS", ["ASIA"]),
    ("LEBANON", "Liban", "LB", ["ASIA"]),
    ("SINGAPORE", "Singapour", "SG", ["ASIA"]),
    ("INDONESIA", "Indonésie", "ID", ["ASIA"]),
    ("BOLIVIA", "Bolivie", "BO", ["SOUTH_AMERICA"]),
    ("ETHIOPIA", "Éthiopie", "ET", ["AFRICA"]),
    ("MAURITANIA", "Mauritanie", "MR", ["AFRICA"]),
    ("CAMEROON", "Cameroun", "CM", ["AFRICA"]),
    ("ZIMBABWE", "Zimbabwe", "ZW", ["AFRICA"]),
    ("CHAD", "Tchad", "TD", ["AFRICA"]),
    ("ESTONIA", "Estonie", "EE", ["EUROPE"]),
    ("LITHUANIA", "Lituanie", "LT", ["EUROPE"]),
    ("LATVIA", "Lettonie", "LV", ["EUROPE"]),
    ("NORWAY", "Norvège", "NO", ["EUROPE"]),
    ("TUNISIA", "Tunisie", "TN", ["AFRICA"]),
    ("ISRAEL", "Israël", "IL", ["ASIA"]),
    ("GEORGIA", "Géorgie", "GE", ["ASIA", "EUROPE"]),
    ("ROMANIA", "Roumanie", "RO", ["EUROPE"]),
    ("NETHERLANDS", "Pays-Bas", "NL", ["EUROPE"]),
    ("VIETNAM", "Viêt Nam", "VN", ["ASIA"]),
    ("CAMBODIA", "Cambodge", "KH", ["ASIA"]),
    ("SOUTH_AFRICA", "Afrique du Sud", "ZA", ["AFRICA"]),
    ("YUGOSLAVIA", "Yougoslavie", "YU", ["EUROPE"]),
    ("SERBIA", "Serbie", "RS", ["EUROPE"]),
    ("CROATIA", "Croatie", "HR", ["EUROPE"]),
    ("BOSNIA", "Bosnie-Herzégovine", "BA", ["EUROPE"]),
    ("IRELAND", "Irlande", "IE", ["EUROPE"]),
    ("SWITZERLAND", "Suisse", "CH", ["EUROPE"]),
    ("ICELAND", "Islande", "IS", ["EUROPE"]),
    ("MOROCCO", "Maroc", "MA", ["AFRICA"]),
    ("COLOMBIA", "Colombie", "CO", ["SOUTH_AMERICA"]),
    ("PERU", "Pérou", "PE", ["SOUTH_AMERICA"]),
    ("VENEZUELA", "Venezuela", "VE", ["SOUTH_AMERICA"]),
    ("URUGUAY", "Uruguay", "UY", ["SOUTH_AMERICA"]),
    ("MALAYSIA", "Malaisie", "MY", ["ASIA"]),
    ("ARMENIA", "Arménie", "AM", ["ASIA"]),
    ("SLOVAKIA", "Slovaquie", "SK", ["EUROPE"]),
    ("SLOVENIA", "Slovénie", "SI", ["EUROPE"]),
    ("KAZAKHSTAN", "Kazakhstan", "KZ", ["ASIA"]),
    ("SAUDI_ARABIA", "Arabie saoudite", "SA", ["ASIA"]),
    ("JORDAN", "Jordanie", "JO", ["ASIA"]),
    ("GHANA", "Ghana", "GH", ["AFRICA"]),
    ("IVORY_COAST", "Côte d'Ivoire", "CI", ["AFRICA"]),
    ("GUINEA", "Guinée", "GN", ["AFRICA"]),
    ("MOZAMBIQUE", "Mozambique", "MZ", ["AFRICA"]),
    ("CONGO", "Congo", "CG", ["AFRICA"]),
    ("DR_CONGO", "République démocratique du Congo", "CD", ["AFRICA"]),
]

COUNTRY_FR_TO_CODE = {
    "États-Unis": "USA", "France": "FRANCE", "Royaume-Uni": "UK", "Italie": "ITALY",
    "URSS": "RUSSIA", "Japon": "JAPAN", "Suède": "SWEDEN", "Chine": "CHINA",
    "Taïwan": "TAIWAN", "Espagne": "SPAIN", "Mexique": "MEXICO", "Allemagne": "GERMANY",
    "Hong Kong": "HONG_KONG", "Canada": "CANADA", "Russie": "RUSSIA", "Inde": "INDIA",
    "Sénégal": "SENEGAL", "Allemagne de l'Ouest": "GERMANY", "Brésil": "BRAZIL",
    "Nigeria": "NIGERIA", "Corée du Sud": "SOUTH_KOREA", "Australie": "AUSTRALIA",
    "Iran": "IRAN", "Danemark": "DENMARK", "Argentine": "ARGENTINA",
    "Nouvelle-Zélande": "NEW_ZEALAND", "Géorgie": "GEORGIA", "Thaïlande": "THAILAND",
    "Portugal": "PORTUGAL", "Israël": "ISRAEL", "Chili": "CHILE",
    "Afrique du Sud": "SOUTH_AFRICA", "Belgique": "BELGIUM", "Yougoslavie": "YUGOSLAVIA",
    "Cuba": "CUBA", "Palestine": "PALESTINE", "Singapour": "SINGAPORE",
    "Roumanie": "ROMANIA", "Turquie": "TURKEY", "Algérie": "ALGERIA",
    "Burkina Faso": "BURKINA_FASO", "Liban": "LEBANON", "Indonésie": "INDONESIA",
    "Hongrie": "HUNGARY", "Éthiopie": "ETHIOPIA", "Philippines": "PHILIPPINES",
    "Mali": "MALI", "Viêt Nam": "VIETNAM", "Cambodge": "CAMBODIA",
    "Tchécoslovaquie": "CZECH", "Pays-Bas": "NETHERLANDS", "Bolivie": "BOLIVIA",
    "Estonie": "ESTONIA", "Autriche": "AUSTRIA", "Tunisie": "TUNISIA", "Tchad": "CHAD",
    "Pologne": "POLAND", "Égypte": "EGYPT", "Cameroun": "CAMEROON",
    "Zimbabwe": "ZIMBABWE", "Grèce": "GREECE", "Mauritanie": "MAURITANIA",
    "Finlande": "FINLAND", "Lituanie": "LITHUANIA", "Lettonie": "LATVIA",
    "Norvège": "NORWAY", "Irlande": "IRELAND", "Suisse": "SWITZERLAND",
    "Islande": "ICELAND", "Maroc": "MOROCCO", "Serbie": "SERBIA",
    "Croatie": "CROATIA", "Bosnie-Herzégovine": "BOSNIA", "Arménie": "ARMENIA",
}

LINE_RE = re.compile(
    r"^\d{4}\. (.+) \((\d{4})\) — (.+) — (.+) — (.+) — (.+)$"
)


def display_director(raw: str) -> str:
    first = raw.split("&")[0].split("/")[0].strip()
    if "," in first:
        last, firstn = [part.strip() for part in first.split(",", 1)]
        return f"{firstn} {last}".strip()
    return first


def parse_1000() -> list[dict]:
    rows = []
    started = False
    for line in LIST_1000.read_text(encoding="utf-8").splitlines():
        if line.startswith("0001."):
            started = True
        if not started:
            continue
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        title, year, country, courant, director, source = m.groups()
        rows.append({
            "title": title.strip(),
            "year": int(year),
            "country": country.strip(),
            "courant": courant.strip(),
            "director": director.strip(),
            "source": source.strip(),
        })
    return rows


def existing_movie_codes(pack: dict) -> set[str]:
    return {m["code"] for m in pack.get("movies", [])}


def assign_code(title: str, year: int, used: set[str], director: str) -> str:
    base = movie_code(title, year)
    if base not in used:
        used.add(base)
        return base
    extra = ascii_slug(display_director(director).split()[-1] if display_director(director) else "X")
    candidate = f"{base}_{extra}" if extra else f"{base}_B"
    n = 2
    while candidate in used:
        candidate = f"{base}_{n}"
        n += 1
    used.add(candidate)
    return candidate


def append_unique(items: list[dict], key: str, news: list[dict]) -> int:
    have = {item[key] for item in items}
    added = 0
    for item in news:
        if item[key] in have:
            continue
        items.append(item)
        have.add(item[key])
        added += 1
    return added


def prepare() -> None:
    pack = json.loads(CATALOG_V1.read_text(encoding="utf-8"))
    chars = pack.setdefault("characteristics", [])
    added_c = append_unique(chars, "code", [
        {"code": code, "name": name, "typeCode": type_code, "description": desc}
        for code, name, type_code, desc in NEW_CHARACTERISTICS
    ])
    genres = pack.setdefault("genres", [])
    added_g = append_unique(genres, "code", [
        {"code": code, "name": name} for code, name in NEW_GENRES
    ])
    countries = pack.setdefault("countries", [])
    added_k = append_unique(countries, "code", [
        {"code": code, "name": name, "isoCode": iso, "continentCodes": continents}
        for code, name, iso, continents in NEW_COUNTRIES
    ])

    films = parse_1000()
    used = existing_movie_codes(pack)
    lines = [
        "frenchTitle;releaseYear;director;code;originalTitle",
    ]
    meta = []
    skipped = 0
    unknown_courants = set()
    for film in films:
        code = assign_code(film["title"], film["year"], used, film["director"])
        char_code = COURANT_TO_CODE.get(film["courant"])
        if not char_code:
            unknown_courants.add(film["courant"])
        country_code = COUNTRY_FR_TO_CODE.get(film["country"], "USA")
        director_display = display_director(film["director"])
        meta.append({
            **film,
            "code": code,
            "charCode": char_code,
            "countryCode": country_code,
            "directorDisplay": director_display,
        })
        lines.append(
            ";".join([
                json.dumps(film["title"], ensure_ascii=False),
                str(film["year"]),
                json.dumps(director_display, ensure_ascii=False),
                code,
                json.dumps(film["title"], ensure_ascii=False),
            ])
        )
    INPUT_1000.parent.mkdir(parents=True, exist_ok=True)
    INPUT_1000.write_text("\n".join(lines) + "\n", encoding="utf-8")
    meta_path = ROOT / "batchPosters/input/input_1000_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    pack["version"] = 13
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    CATALOG_V2.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"characteristics +{added_c} (total {len(chars)})")
    print(f"genres +{added_g} (total {len(genres)})")
    print(f"countries +{added_k} (total {len(countries)})")
    print(f"input films {len(meta)} skipped {skipped} -> {INPUT_1000}")
    if unknown_courants:
        print("UNKNOWN COURANTS", sorted(unknown_courants))


def load_meta() -> list[dict]:
    return json.loads((ROOT / "batchPosters/input/input_1000_meta.json").read_text(encoding="utf-8"))


def split_person(display: str) -> tuple[str | None, str]:
    parts = [p for p in display.replace(".", " ").split() if p]
    if not parts:
        return None, display
    if len(parts) == 1:
        return None, parts[0]
    return " ".join(parts[:-1]), parts[-1]


def merge() -> None:
    pack = json.loads(CATALOG_V2.read_text(encoding="utf-8"))
    meta = load_meta()
    tmdb = {}
    new_directors = []
    new_countries = []
    if TMDB_MOVIES.is_file():
        payload = json.loads(TMDB_MOVIES.read_text(encoding="utf-8"))
        for movie in payload.get("movies") or []:
            tmdb[movie["code"]] = movie
        new_directors = payload.get("newDirectors") or []
        new_countries = payload.get("newCountries") or []

    known_directors = {d["code"]: d for d in pack["directors"]}
    for item in new_directors:
        if item["code"] not in known_directors:
            pack["directors"].append(item)
            known_directors[item["code"]] = item

    known_countries = {c["code"]: c for c in pack["countries"]}
    continent_by_iso = {item[2]: (item[0], item[3]) for item in NEW_COUNTRIES}
    for item in new_countries:
        code = item.get("code")
        if not code or code in known_countries:
            continue
        iso = item.get("isoCode") or ""
        if iso in continent_by_iso:
            mapped, continents = continent_by_iso[iso]
            if mapped in known_countries:
                continue
            item["continentCodes"] = continents
        if not item.get("continentCodes"):
            item["continentCodes"] = ["EUROPE"]
        pack["countries"].append(item)
        known_countries[code] = item

    known_chars = {c["code"] for c in pack["characteristics"]}
    known_genres = {g["code"] for g in pack["genres"]}
    existing_codes = {m["code"] for m in pack["movies"]}
    added = 0
    stubs = 0
    posters_ok = 0
    missing_posters = []

    for film in meta:
        code = film["code"]
        if code in existing_codes:
            continue
        movie = tmdb.get(code)
        if not movie:
            stubs += 1
            first, last = split_person(film["directorDisplay"])
            dcode = ascii_slug(film["directorDisplay"]) or "DIRECTOR"
            if dcode not in known_directors:
                pack["directors"].append({
                    "code": dcode,
                    "firstName": first,
                    "lastName": last,
                    "displayName": film["directorDisplay"],
                    "characteristicCodes": [],
                })
                known_directors[dcode] = pack["directors"][-1]
            hd, ad, hr, cr = scores_for(code, film["year"], film["year"] <= 1929, False, 0.70)
            movie = {
                "code": code,
                "originalTitle": film["title"],
                "frenchTitle": film["title"],
                "releaseYear": film["year"],
                "durationMinutes": 90,
                "format": "FEATURE",
                "synopsis": "",
                "historicalDistance": hd,
                "artisticDemand": ad,
                "historicalRichness": hr,
                "culturalRichness": cr,
                "countries": [{"code": film["countryCode"], "isPrimary": True}],
                "directors": [{"code": dcode, "billingOrder": 0}],
                "genreCodes": ["DRAME"],
                "characteristicCodes": [],
            }
            if film["year"] <= 1929:
                movie["isSilent"] = True
            if film["year"] <= 1954:
                movie["isBlackAndWhite"] = True

        chars = [c for c in (movie.get("characteristicCodes") or []) if c in known_chars]
        editorial = film.get("charCode")
        if editorial and editorial in known_chars and editorial not in chars:
            chars.insert(0, editorial)
        movie["characteristicCodes"] = chars
        movie["genreCodes"] = [g for g in (movie.get("genreCodes") or []) if g in known_genres] or ["DRAME"]
        countries = movie.get("countries") or []
        countries = [c for c in countries if c.get("code") in known_countries]
        if not countries:
            countries = [{"code": film["countryCode"], "isPrimary": True}]
        if sum(1 for c in countries if c.get("isPrimary")) != 1:
            countries[0]["isPrimary"] = True
            for extra in countries[1:]:
                extra["isPrimary"] = False
        movie["countries"] = countries
        directors = movie.get("directors") or []
        directors = [d for d in directors if d.get("code") in known_directors]
        if not directors:
            dcode = ascii_slug(film["directorDisplay"]) or "DIRECTOR"
            if dcode not in known_directors:
                first, last = split_person(film["directorDisplay"])
                pack["directors"].append({
                    "code": dcode,
                    "firstName": first,
                    "lastName": last,
                    "displayName": film["directorDisplay"],
                    "characteristicCodes": [],
                })
                known_directors[dcode] = pack["directors"][-1]
            directors = [{"code": dcode, "billingOrder": 0}]
        seen_d = set()
        clean_d = []
        for index, credit in enumerate(directors):
            if credit["code"] in seen_d:
                continue
            seen_d.add(credit["code"])
            credit["billingOrder"] = index
            clean_d.append(credit)
        movie["directors"] = clean_d
        if int(movie.get("durationMinutes") or 0) <= 0:
            movie["durationMinutes"] = 90
        if not movie.get("originalTitle"):
            movie["originalTitle"] = film["title"]
        if not movie.get("frenchTitle"):
            movie["frenchTitle"] = film["title"]
        pack["movies"].append(movie)
        existing_codes.add(code)
        added += 1
        poster = None
        for ext in ("webp", "png", "jpg", "jpeg"):
            candidate = POSTERS_OUT / f"{code}.{ext}"
            if candidate.is_file() and candidate.stat().st_size > 1000:
                poster = candidate
                break
        if poster:
            posters_ok += 1
        else:
            missing_posters.append(code)

    pack["version"] = 13
    pack["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    CATALOG_V2.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"merged movies +{added} stubs={stubs} total={len(pack['movies'])}")
    print(f"directors={len(pack['directors'])} countries={len(pack['countries'])} chars={len(pack['characteristics'])}")
    print(f"posters found {posters_ok}/{added} missing {len(missing_posters)}")
    (ROOT / "batchPosters/output/reports/missing_posters.txt").write_text(
        "\n".join(missing_posters) + ("\n" if missing_posters else ""),
        encoding="utf-8",
    )


def copy_posters() -> int:
    POSTERS_APP.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in POSTERS_OUT.iterdir():
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        dest = POSTERS_APP / src.name
        dest.write_bytes(src.read_bytes())
        copied += 1
    print(f"copied {copied} posters -> {POSTERS_APP}")
    return copied


def publish() -> None:
    CATALOG_LIVE.write_bytes(CATALOG_V2.read_bytes())
    print(f"published {CATALOG_V2.name} -> {CATALOG_LIVE.name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if cmd == "prepare":
        prepare()
    elif cmd == "merge":
        merge()
    elif cmd == "copy-posters":
        copy_posters()
    elif cmd == "publish":
        publish()
    else:
        raise SystemExit(f"unknown command {cmd}")
