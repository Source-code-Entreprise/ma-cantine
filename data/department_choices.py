from django.db import models

class Department(models.TextChoices):
        ain = "01", "01 - Ain"
        aisne = "02", "02 - Aisne"
        allier = "03", "03 - Allier"
        alpes_de_haute_provence = "04", "04 - Alpes-de-Haute-Provence"
        hautes_alpes = "05", "05 - Hautes-Alpes"
        alpes_maritimes = "06", "06 - Alpes-Maritimes"
        ardeche = "07", "07 - Ardèche"
        ardennes = "08", "08 - Ardennes"
        ariege = "09", "09 - Ariège"
        aube = "10", "10 - Aube"
        aude = "11", "11 - Aude"
        aveyron = "12", "12 - Aveyron"
        bouches_du_rhone = "13", "13 - Bouches-du-Rhône"
        calvados = "14", "14 - Calvados"
        cantal = "15", "15 - Cantal"
        charente = "16", "16 - Charente"
        charente_maritime = "17", "17 - Charente-Maritime"
        cher = "18", "18 - Cher"
        correze = "19", "19 - Corrèze"
        cote_d_or = "21", "21 - Côte-d'or"
        cotes_d_armor = "22", "22 - Côtes-d'armor"
        creuse = "23", "23 - Creuse"
        dordogne = "24", "24 - Dordogne"
        doubs = "25", "25 - Doubs"
        drome = "26", "26 - Drôme"
        eure = "27", "27 - Eure"
        eure_et_loir = "28", "28 - Eure-et-Loir"
        finistere = "29", "29 - Finistère"
        corse_du_sud = "2a", "2a - Corse-du-Sud"
        haute_corse = "2b", "2b - Haute-Corse"
        gard = "30", "30 - Gard"
        haute_garonne = "31", "31 - Haute-Garonne"
        gers = "32", "32 - Gers"
        gironde = "33", "33 - Gironde"
        herault = "34", "34 - Hérault"
        ille_et_vilaine = "35", "35 - Ille-et-Vilaine"
        indre = "36", "36 - Indre"
        indre_et_loire = "37", "37 - Indre-et-Loire"
        isere = "38", "38 - Isère"
        jura = "39", "39 - Jura"
        landes = "40", "40 - Landes"
        loir_et_cher = "41", "41 - Loir-et-Cher"
        loire = "42", "42 - Loire"
        haute_loire = "43", "43 - Haute-Loire"
        loire_atlantique = "44", "44 - Loire-Atlantique"
        loiret = "45", "45 - Loiret"
        lot = "46", "46 - Lot"
        lot_et_garonne = "47", "47 - Lot-et-Garonne"
        lozere = "48", "48 - Lozère"
        maine_et_loire = "49", "49 - Maine-et-Loire"
        manche = "50", "50 - Manche"
        marne = "51", "51 - Marne"
        haute_marne = "52", "52 - Haute-Marne"
        mayenne = "53", "53 - Mayenne"
        meurthe_et_moselle = "54", "54 - Meurthe-et-Moselle"
        meuse = "55", "55 - Meuse"
        morbihan = "56", "56 - Morbihan"
        moselle = "57", "57 - Moselle"
        nievre = "58", "58 - Nièvre"
        nord = "59", "59 - Nord"
        oise = "60", "60 - Oise"
        orne = "61", "61 - Orne"
        pas_de_calais = "62", "62 - Pas-de-Calais"
        puy_de_dome = "63", "63 - Puy-de-Dôme"
        pyrenees_atlantiques = "64", "64 - Pyrénées-Atlantiques"
        hautes_pyrenees = "65", "65 - Hautes-Pyrénées"
        pyrenees_orientales = "66", "66 - Pyrénées-Orientales"
        bas_rhin = "67", "67 - Bas-Rhin"
        haut_rhin = "68", "68 - Haut-Rhin"
        rhone = "69", "69 - Rhône"
        haute_saone = "70", "70 - Haute-Saône"
        saone_et_loire = "71", "71 - Saône-et-Loire"
        sarthe = "72", "72 - Sarthe"
        savoie = "73", "73 - Savoie"
        haute_savoie = "74", "74 - Haute-Savoie"
        paris = "75", "75 - Paris"
        seine_maritime = "76", "76 - Seine-Maritime"
        seine_et_marne = "77", "77 - Seine-et-Marne"
        yvelines = "78", "78 - Yvelines"
        deux_sevres = "79", "79 - Deux-Sèvres"
        somme = "80", "80 - Somme"
        tarn = "81", "81 - Tarn"
        tarn_et_garonne = "82", "82 - Tarn-et-Garonne"
        var = "83", "83 - Var"
        vaucluse = "84", "84 - Vaucluse"
        vendee = "85", "85 - Vendée"
        vienne = "86", "86 - Vienne"
        haute_vienne = "87", "87 - Haute-Vienne"
        vosges = "88", "88 - Vosges"
        yonne = "89", "89 - Yonne"
        territoire_de_belfort = "90", "90 - Territoire de Belfort"
        essonne = "91", "91 - Essonne"
        hauts_de_seine = "92", "92 - Hauts-de-Seine"
        seine_saint_denis = "93", "93 - Seine-Saint-Denis"
        val_de_marne = "94", "94 - Val-de-Marne"
        val_d_oise = "95", "95 - Val-d'oise"
        guadeloupe = "971", "971 - Guadeloupe"
        martinique = "972", "972 - Martinique"
        guyane = "973", "973 - Guyane"
        la_reunion = "974", "974 - La Réunion"
        mayotte = "976", "976 - Mayotte"
        polynesie_française = "987", "987 - Polynésie Française"
        nouvelle_caledonie = "988", "988 - Nouvelle Calédonie"
