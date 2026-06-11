"""
=============================================================================
Script de seeding - Table VENTES
=============================================================================
Genere 6 mois d'historique de ventes journalieres pour Cdiscount, avec des
correlations CACHEES mais REELLES avec :
- Les valeurs Google Trends (lecture depuis MESURES_TRENDS)
- La meteo (lecture depuis METEO_HISTORIQUE)
- Des effets saisonniers et jour de la semaine

Volumetrie generee :
- 30 sous-categories x 4 produits x ~180 jours
- Total : ~21 600 lignes inserees

A executer UNE SEULE FOIS en amont de la formation.

Pre-requis :
- Tables MESURES_TRENDS et METEO_HISTORIQUE deja remplies
- snowflake-connector-python[pandas] installe (avec pyarrow)
=============================================================================
"""

import random
from datetime import date, timedelta
from getpass import getpass

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas


# =============================================================================
# CONFIGURATION
# =============================================================================

SNOWFLAKE_ACCOUNT = "LAWHABL-JB80530"
SNOWFLAKE_USER = "CHRISTOPHEGUEROULT01"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "FORMATION_DB"
SNOWFLAKE_SCHEMA = "PUBLIC"
SNOWFLAKE_TABLE = "VENTES"

NOMBRE_MOIS_HISTORIQUE = 6

random.seed(456)


# =============================================================================
# CATALOGUE PRODUITS PAR SOUS-CATEGORIE
# =============================================================================
# Pour chaque sous-categorie : liste de 4 produits avec
#   (nom_produit, prix_unitaire_euros, quantite_base_par_jour)
# La quantite base est la quantite moyenne journaliere France entiere
# avant application des effets meteo/trends/saisonniers.

CATALOGUE_PRODUITS = {
    # Electromenager
    "frigo": [
        ("Frigo Samsung RB29 250L", 449.0, 18),
        ("Frigo Bosch KGN36 380L", 699.0, 12),
        ("Frigo Whirlpool W7 combine", 549.0, 22),
        ("Frigo Beko CSA encastrable", 399.0, 25)
    ],
    "machine à laver": [
        ("Lave-linge Samsung WW80 8kg", 399.0, 30),
        ("Lave-linge Bosch WAN 7kg", 489.0, 22),
        ("Lave-linge Whirlpool FWG81", 349.0, 35),
        ("Lave-linge Beko WTV 6kg", 289.0, 40)
    ],
    "lave-vaisselle": [
        ("Lave-vaisselle Bosch SMS 12 couverts", 549.0, 15),
        ("Lave-vaisselle Samsung DW60 14 couverts", 649.0, 12),
        ("Lave-vaisselle Whirlpool WFE 13c", 449.0, 20),
        ("Lave-vaisselle Beko BDFN 13c", 339.0, 25)
    ],

    # Salon
    "canapé d'angle": [
        ("Canape angle gauche tissu gris", 599.0, 8),
        ("Canape angle convertible 5 places", 799.0, 6),
        ("Canape angle reversible cuir", 1199.0, 4),
        ("Canape angle compact 4 places", 449.0, 12)
    ],
    "fauteuil relax": [
        ("Fauteuil relax electrique cuir", 599.0, 10),
        ("Fauteuil relax massant tissu", 449.0, 15),
        ("Fauteuil relax manuel", 249.0, 25),
        ("Fauteuil relax XXL", 699.0, 8)
    ],
    "table basse": [
        ("Table basse bois massif", 199.0, 30),
        ("Table basse verre design", 159.0, 35),
        ("Table basse releveuse", 249.0, 20),
        ("Table basse industrielle metal", 179.0, 28)
    ],

    # Multimedia
    "télévision OLED": [
        ("TV OLED LG 55 pouces C3", 1299.0, 12),
        ("TV OLED Samsung 65 pouces S95C", 2299.0, 6),
        ("TV OLED Sony 55 pouces A80L", 1599.0, 8),
        ("TV OLED Philips 48 pouces OLED808", 899.0, 15)
    ],
    "barre de son": [
        ("Barre de son Sonos Beam Gen 2", 499.0, 25),
        ("Barre de son Samsung Q800C", 699.0, 18),
        ("Barre de son Bose Soundbar 600", 549.0, 22),
        ("Barre de son LG SC9S 4.1.5", 999.0, 10)
    ],
    "vidéoprojecteur": [
        ("Videoprojecteur Epson EH-TW7100", 1199.0, 8),
        ("Videoprojecteur BenQ TK700STi", 1499.0, 6),
        ("Videoprojecteur Xgimi Horizon Pro", 1599.0, 5),
        ("Videoprojecteur ViewSonic X1", 999.0, 12)
    ],

    # Informatique
    "PC portable": [
        ("PC portable HP Pavilion 15 i5", 749.0, 35),
        ("PC portable Lenovo IdeaPad 5 Ryzen 7", 899.0, 28),
        ("PC portable Asus VivoBook 17 i7", 999.0, 22),
        ("PC portable Acer Aspire 5 i3", 549.0, 45)
    ],
    "écran 27 pouces": [
        ("Ecran Dell P2725H 27 pouces IPS", 299.0, 30),
        ("Ecran LG 27UP650 27 pouces 4K", 399.0, 22),
        ("Ecran Samsung Odyssey G5 27 gaming", 349.0, 35),
        ("Ecran Iiyama ProLite XU2792 IPS", 229.0, 40)
    ],
    "imprimante laser": [
        ("Imprimante laser HP LaserJet M209", 199.0, 25),
        ("Imprimante laser Brother HL-L2375DW", 229.0, 22),
        ("Imprimante laser couleur HP M283fdw", 449.0, 12),
        ("Imprimante laser Samsung Xpress", 159.0, 30)
    ],

    # Telephonie
    "iPhone 17": [
        ("iPhone 17 128 Go Noir", 1099.0, 50),
        ("iPhone 17 Pro 256 Go Titane", 1499.0, 35),
        ("iPhone 17 Plus 256 Go Bleu", 1299.0, 30),
        ("iPhone 17 Pro Max 512 Go", 1799.0, 20)
    ],
    "smartphone Samsung": [
        ("Samsung Galaxy S25 Ultra 256 Go", 1299.0, 40),
        ("Samsung Galaxy S25+ 256 Go", 1099.0, 45),
        ("Samsung Galaxy A55 128 Go", 449.0, 80),
        ("Samsung Galaxy Z Flip 6 256 Go", 1199.0, 25)
    ],
    "coque de protection": [
        ("Coque iPhone 17 silicone Apple", 49.0, 150),
        ("Coque Samsung Galaxy S25 Spigen", 24.0, 200),
        ("Coque iPhone 17 antichoc transparente", 19.0, 250),
        ("Coque universelle cuir vegan", 29.0, 180)
    ],

    # Jardin
    "barbecue gaz": [
        ("Barbecue gaz Weber Spirit II E-310", 749.0, 8),
        ("Barbecue gaz Campingaz Class 3", 449.0, 15),
        ("Barbecue gaz Char-Broil Performance 4", 599.0, 10),
        ("Barbecue gaz Naterial Aramis 3 brul", 299.0, 22)
    ],
    "tondeuse électrique": [
        ("Tondeuse Bosch ARM 32", 149.0, 25),
        ("Tondeuse Einhell GE-CM 36 Li", 299.0, 18),
        ("Tondeuse Black+Decker BEMW461BH", 119.0, 35),
        ("Tondeuse Greenworks 40V", 249.0, 22)
    ],
    "salon de jardin": [
        ("Salon de jardin resine tressee 4p", 599.0, 12),
        ("Salon de jardin teck 6 places", 1199.0, 6),
        ("Salon de jardin aluminium modulable", 799.0, 9),
        ("Salon de jardin bistrot 2 places", 199.0, 25)
    ],

    # Bricolage
    "perceuse visseuse": [
        ("Perceuse-visseuse Bosch GSR 18V-21", 149.0, 30),
        ("Perceuse-visseuse Makita DDF483", 199.0, 25),
        ("Perceuse-visseuse Dewalt DCD777", 169.0, 28),
        ("Perceuse-visseuse Einhell TE-CD 18", 89.0, 40)
    ],
    "escabeau": [
        ("Escabeau aluminium 5 marches Hailo", 79.0, 35),
        ("Escabeau telescopique 11 marches", 129.0, 22),
        ("Escabeau pliant 4 marches acier", 49.0, 45),
        ("Escabeau plateforme 6 marches", 99.0, 28)
    ],
    "aspirateur atelier": [
        ("Aspirateur atelier Karcher WD3", 99.0, 30),
        ("Aspirateur atelier Bosch UniversalVac", 119.0, 25),
        ("Aspirateur atelier Einhell TE-VC 1925", 79.0, 35),
        ("Aspirateur cendres Ribimex 1200W", 59.0, 40)
    ],

    # Cuisine
    "robot multifonction": [
        ("Robot Thermomix TM6", 1499.0, 8),
        ("Robot Magimix Cook Expert", 1199.0, 10),
        ("Robot Moulinex Companion XL", 599.0, 22),
        ("Robot Kenwood KCook Multi", 449.0, 18)
    ],
    "four micro-ondes": [
        ("Micro-ondes Samsung MS23 23L", 99.0, 50),
        ("Micro-ondes combine Whirlpool MWP", 199.0, 25),
        ("Micro-ondes Panasonic NN-CD58", 249.0, 18),
        ("Micro-ondes Bosch HMT75M624", 159.0, 30)
    ],
    "cafetière à grain": [
        ("Cafetiere a grain DeLonghi Magnifica", 449.0, 22),
        ("Cafetiere a grain Philips 3200 LatteGo", 549.0, 18),
        ("Cafetiere a grain Krups Evidence", 599.0, 15),
        ("Cafetiere a grain Melitta CI Touch", 749.0, 10)
    ],

    # Mode et accessoires
    "sac à dos": [
        ("Sac a dos Eastpak Padded Pak'r", 49.0, 80),
        ("Sac a dos Herschel Little America", 99.0, 50),
        ("Sac a dos The North Face Borealis", 89.0, 60),
        ("Sac a dos Kipling Seoul", 119.0, 40)
    ],
    "montre connectée": [
        ("Montre Apple Watch Series 10 GPS", 449.0, 60),
        ("Montre Samsung Galaxy Watch 7", 329.0, 50),
        ("Montre Garmin Venu 3", 499.0, 30),
        ("Montre Xiaomi Redmi Watch 4", 79.0, 100)
    ],
    "sneakers": [
        ("Sneakers Nike Air Max 90", 129.0, 90),
        ("Sneakers Adidas Stan Smith", 99.0, 110),
        ("Sneakers New Balance 574", 89.0, 100),
        ("Sneakers Veja V-10", 149.0, 60)
    ],

    # Sport et loisirs
    "vélo électrique": [
        ("Velo electrique VTC Decathlon Elops", 1299.0, 15),
        ("Velo electrique route Moustache", 2499.0, 6),
        ("Velo electrique pliant Brompton", 3199.0, 4),
        ("Velo electrique ville Nakamura", 999.0, 22)
    ],
    "trottinette électrique": [
        ("Trottinette Xiaomi Mi Electric Pro 2", 449.0, 30),
        ("Trottinette Segway Ninebot Max G2", 799.0, 18),
        ("Trottinette Dualtron Mini 2024", 1299.0, 10),
        ("Trottinette Wegoboard Suprem", 349.0, 35)
    ],
    "tente camping": [
        ("Tente Quechua MH100 4 places", 79.0, 35),
        ("Tente Coleman Coastline 4 places", 199.0, 20),
        ("Tente MSR Hubba Hubba NX 2p", 549.0, 8),
        ("Tente Decathlon 2 Seconds Easy", 129.0, 28)
    ]
}


# =============================================================================
# PROFILS DE SENSIBILITE PAR SOUS-CATEGORIE
# =============================================================================
# Pour chaque sous-categorie : (alpha_temp, alpha_pluie, lag_trends_jours)
# alpha_temp : sensibilite a la temperature (-1.0 a +1.0)
#   +1 = ventes augmentent fortement avec la chaleur
#    0 = aucun effet
#   -1 = ventes augmentent fortement avec le froid
# alpha_pluie : sensibilite aux precipitations (-1.0 a +1.0)
#   +1 = ventes augmentent quand il pleut (on reste dedans)
#   -1 = ventes diminuent quand il pleut (activites exterieures)
# lag_trends_jours : decalage Trends -> Ventes
#    0 = achat immediat (achat impulsif apres panne)
#    7 = decision en une semaine
#   14-30 = produit reflechi (recherche longue)

SENSIBILITES = {
    # Electromenager : peu sensible meteo, achats impulsifs (lag faible)
    "frigo": (0.0, 0.0, 3),
    "machine à laver": (0.0, 0.0, 3),
    "lave-vaisselle": (0.0, 0.0, 5),

    # Salon : sensible pluie (on reste dedans), lag moyen
    "canapé d'angle": (-0.1, 0.4, 14),
    "fauteuil relax": (-0.2, 0.3, 10),
    "table basse": (0.0, 0.2, 7),

    # Multimedia : sensible pluie ++, lag long (achat reflechi)
    "télévision OLED": (-0.2, 0.6, 14),
    "barre de son": (-0.1, 0.4, 10),
    "vidéoprojecteur": (-0.1, 0.5, 14),

    # Informatique : sensible pluie (work from home), lag moyen
    "PC portable": (-0.1, 0.5, 10),
    "écran 27 pouces": (0.0, 0.4, 7),
    "imprimante laser": (0.0, 0.3, 7),

    # Telephonie : pas meteo-sensible, lag tres long (recherche prolongee)
    "iPhone 17": (0.0, 0.0, 30),
    "smartphone Samsung": (0.0, 0.0, 21),
    "coque de protection": (0.0, 0.0, 3),

    # Jardin : tres meteo-sensible chaleur, anti-pluie
    "barbecue gaz": (0.8, -0.7, 7),
    "tondeuse électrique": (0.6, -0.5, 5),
    "salon de jardin": (0.7, -0.6, 14),

    # Bricolage : leger effet chaleur (motivation outdoor)
    "perceuse visseuse": (0.2, 0.1, 5),
    "escabeau": (0.1, 0.0, 3),
    "aspirateur atelier": (0.1, 0.1, 5),

    # Cuisine : peu sensible meteo
    "robot multifonction": (0.0, 0.1, 10),
    "four micro-ondes": (0.0, 0.0, 5),
    "cafetière à grain": (-0.1, 0.1, 14),

    # Mode : sensible saison
    "sac à dos": (0.1, 0.0, 7),
    "montre connectée": (0.0, 0.0, 14),
    "sneakers": (0.5, -0.3, 7),

    # Sport et loisirs : tres meteo-sensible
    "vélo électrique": (0.6, -0.5, 21),
    "trottinette électrique": (0.6, -0.6, 14),
    "tente camping": (0.7, -0.4, 21)
}


# =============================================================================
# FONCTIONS DE GENERATION DES VENTES
# =============================================================================

def calculer_facteur_weekend(jour_semaine):
    """
    Effet jour de la semaine sur les ventes.
    0 = lundi, 6 = dimanche.
    Weekend : leger pic (les gens commandent plus le samedi/dimanche).
    """
    if jour_semaine in [5, 6]:  # samedi, dimanche
        return 1.15
    elif jour_semaine == 4:  # vendredi
        return 1.05
    elif jour_semaine == 0:  # lundi
        return 0.95
    else:
        return 1.0


def calculer_facteur_meteo(temperature, precipitations, alpha_temp, alpha_pluie):
    """
    Calcule le multiplicateur meteo applique aux ventes.
    Temperature de reference : 13C (moyenne France sur 6 mois).
    Precipitations de reference : 0 mm (jour sec).
    """
    # Effet temperature : ecart par rapport a la reference, divise par 25 pour
    # avoir un effet borné (a 25C d'ecart, on est a 100% de l'effet alpha)
    effet_temp = alpha_temp * (temperature - 13.0) / 25.0

    # Effet pluie : 0 mm = pas d'effet, 20 mm = effet maximal
    effet_pluie = alpha_pluie * min(precipitations, 20.0) / 20.0

    # Multiplicateur final : centré sur 1.0, plage typique 0.7 - 1.3
    multiplicateur = 1.0 + effet_temp + effet_pluie

    # Borner pour eviter les extremes
    return max(0.4, min(1.8, multiplicateur))


def calculer_facteur_trends(valeur_trends, valeur_trends_moyenne):
    """
    Calcule le multiplicateur Trends applique aux ventes.
    Si Trends est elevee par rapport a la moyenne historique : ventes augmentent.
    """
    if valeur_trends_moyenne == 0:
        return 1.0

    # Ratio par rapport a la moyenne, centre sur 1.0
    ratio = valeur_trends / valeur_trends_moyenne

    # Borner et appliquer une attenuation (l'effet Trends n'est pas total)
    # Un Trends 2x plus eleve que la moyenne donne ventes 1.4x plus elevees
    facteur = 1.0 + 0.4 * (ratio - 1.0)
    return max(0.5, min(1.8, facteur))


def construire_lookup_trends(df_trends):
    """
    Construit un dictionnaire pour acceder rapidement aux mesures Trends.
    Cle : (sous_categorie, date)
    Valeur : valeur_interet
    Egalement : calcule la moyenne par sous-categorie.
    """
    lookup = {}
    moyennes = {}

    for sous_cat in df_trends['SOUS_CATEGORIE'].unique():
        sous_df = df_trends[df_trends['SOUS_CATEGORIE'] == sous_cat]
        moyennes[sous_cat] = sous_df['VALEUR_INTERET'].mean()

        for _, row in sous_df.iterrows():
            lookup[(sous_cat, row['DATE_MESURE'])] = row['VALEUR_INTERET']

    return lookup, moyennes


def trouver_trends_avec_lag(lookup_trends, moyennes, sous_categorie, date_vente, lag_jours):
    """
    Pour une date de vente donnee, recupere la valeur Trends de
    'date_vente - lag_jours', avec fallback sur la mesure la plus proche
    si pas de mesure exacte (Trends est bi-hebdomadaire).
    """
    date_recherche = date_vente - timedelta(days=lag_jours)

    # Chercher la mesure la plus proche dans les 14 jours precedents
    for offset in range(14):
        cle = (sous_categorie, date_recherche - timedelta(days=offset))
        if cle in lookup_trends:
            return lookup_trends[cle]

    # Si rien trouve : retourner la moyenne
    return moyennes.get(sous_categorie, 30)


def generer_ventes_journalieres(df_trends, df_meteo, dates_ventes):
    """
    Genere toutes les lignes de ventes.
    Retourne une liste de dictionnaires prets pour write_pandas.
    """
    lignes = []

    # Pre-calcul des lookups pour acces rapide
    print(f"      Construction des lookups Trends et Meteo...")
    lookup_trends, moyennes_trends = construire_lookup_trends(df_trends)

    lookup_meteo = {}
    for _, row in df_meteo.iterrows():
        lookup_meteo[row['DATE_METEO']] = (
            float(row['TEMPERATURE_MOYENNE']),
            float(row['PRECIPITATIONS_MM'])
        )

    print(f"      OK : {len(lookup_trends)} mesures Trends, {len(lookup_meteo)} jours meteo")

    # Boucle principale
    print(f"      Generation des ventes pour {len(dates_ventes)} jours...")

    for date_vente in dates_ventes:
        # Recuperer meteo du jour (fallback sur valeurs moyennes si manquant)
        temp, pluie = lookup_meteo.get(date_vente, (13.0, 2.0))

        jour_semaine = date_vente.weekday()
        facteur_weekend = calculer_facteur_weekend(jour_semaine)

        # Pour chaque sous-categorie et chaque produit
        for sous_categorie, produits in CATALOGUE_PRODUITS.items():
            # Recuperer la categorie parente
            categorie_parent = trouver_categorie_parent(sous_categorie)

            # Recuperer profils
            alpha_temp, alpha_pluie, lag_trends = SENSIBILITES.get(
                sous_categorie, (0.0, 0.0, 7)
            )

            # Recuperer Trends avec lag
            valeur_trends = trouver_trends_avec_lag(
                lookup_trends, moyennes_trends,
                sous_categorie, date_vente, lag_trends
            )
            moyenne_trends = moyennes_trends.get(sous_categorie, 30)

            # Calculer multiplicateurs
            facteur_meteo = calculer_facteur_meteo(
                temp, pluie, alpha_temp, alpha_pluie
            )
            facteur_trends = calculer_facteur_trends(valeur_trends, moyenne_trends)

            # Generer une ligne par produit
            for nom_produit, prix_unitaire, quantite_base in produits:
                # Calcul de la quantite vendue ce jour
                bruit = random.uniform(0.85, 1.15)
                quantite = quantite_base * facteur_weekend * facteur_meteo * facteur_trends * bruit
                quantite = max(0, round(quantite))

                if quantite == 0:
                    continue  # ne pas inserer de ligne avec 0 ventes

                chiffre_affaires = round(quantite * prix_unitaire, 2)

                lignes.append({
                    "DATE_VENTE": date_vente,
                    "CATEGORIE": categorie_parent,
                    "SOUS_CATEGORIE": sous_categorie,
                    "PRODUIT": nom_produit,
                    "QUANTITE": quantite,
                    "PRIX_UNITAIRE": prix_unitaire,
                    "CHIFFRE_AFFAIRES": chiffre_affaires
                })

    return lignes


def trouver_categorie_parent(sous_categorie):
    """
    Retourne la categorie parente d'une sous-categorie.
    Defini en dur pour eviter de relire le JSON.
    """
    mapping = {
        "frigo": "Électroménager", "machine à laver": "Électroménager", "lave-vaisselle": "Électroménager",
        "canapé d'angle": "Salon", "fauteuil relax": "Salon", "table basse": "Salon",
        "télévision OLED": "Multimédia", "barre de son": "Multimédia", "vidéoprojecteur": "Multimédia",
        "PC portable": "Informatique", "écran 27 pouces": "Informatique", "imprimante laser": "Informatique",
        "iPhone 17": "Téléphonie", "smartphone Samsung": "Téléphonie", "coque de protection": "Téléphonie",
        "barbecue gaz": "Jardin", "tondeuse électrique": "Jardin", "salon de jardin": "Jardin",
        "perceuse visseuse": "Bricolage", "escabeau": "Bricolage", "aspirateur atelier": "Bricolage",
        "robot multifonction": "Cuisine", "four micro-ondes": "Cuisine", "cafetière à grain": "Cuisine",
        "sac à dos": "Mode et accessoires", "montre connectée": "Mode et accessoires", "sneakers": "Mode et accessoires",
        "vélo électrique": "Sport et loisirs", "trottinette électrique": "Sport et loisirs", "tente camping": "Sport et loisirs"
    }
    return mapping.get(sous_categorie, "Inconnu")


# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

def main():
    print("=" * 70)
    print("SEEDING DE LA TABLE VENTES")
    print("=" * 70)

    # 1. Connexion Snowflake
    print(f"\n[1/5] Connexion a Snowflake...")
    mot_de_passe = getpass(f"      Mot de passe pour {SNOWFLAKE_USER} : ")

    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=SNOWFLAKE_USER,
            password=mot_de_passe,
            role=SNOWFLAKE_ROLE,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        print(f"      OK : connecte a {SNOWFLAKE_ACCOUNT}")
    except Exception as erreur:
        print(f"      ERREUR : connexion echouee : {erreur}")
        return

    # 2. Lecture des tables Trends et Meteo
    print(f"\n[2/5] Lecture des donnees Trends et Meteo depuis Snowflake...")
    try:
        df_trends = pd.read_sql_query(
            "SELECT DATE_MESURE, SOUS_CATEGORIE, VALEUR_INTERET FROM MESURES_TRENDS",
            conn
        )
        df_meteo = pd.read_sql_query(
            "SELECT DATE_METEO, TEMPERATURE_MOYENNE, PRECIPITATIONS_MM FROM METEO_HISTORIQUE",
            conn
        )
        print(f"      OK : {len(df_trends)} mesures Trends, {len(df_meteo)} jours meteo")
    except Exception as erreur:
        print(f"      ERREUR : lecture echouee : {erreur}")
        conn.close()
        return

    # Conversion des dates en objets date Python
    df_trends['DATE_MESURE'] = pd.to_datetime(df_trends['DATE_MESURE']).dt.date
    df_meteo['DATE_METEO'] = pd.to_datetime(df_meteo['DATE_METEO']).dt.date

    # 3. Generer les dates de ventes (180 jours consecutifs)
    print(f"\n[3/5] Generation des dates de ventes...")
    date_fin = df_meteo['DATE_METEO'].max()
    date_debut = df_meteo['DATE_METEO'].min()
    dates_ventes = []
    courant = date_debut
    while courant <= date_fin:
        dates_ventes.append(courant)
        courant += timedelta(days=1)
    print(f"      OK : {len(dates_ventes)} jours")
    print(f"      Du {dates_ventes[0]} au {dates_ventes[-1]}")

    # 4. Generation des ventes
    print(f"\n[4/5] Generation des ventes journalieres...")
    lignes = generer_ventes_journalieres(df_trends, df_meteo, dates_ventes)
    df_ventes = pd.DataFrame(lignes)
    print(f"      OK : {len(df_ventes)} lignes generees")
    print(f"      Apercu :")
    print(df_ventes.head(5).to_string(index=False))

    # Statistiques
    print(f"\n      Statistiques :")
    print(f"      - Total ventes : {df_ventes['QUANTITE'].sum():,} unites")
    print(f"      - CA total : {df_ventes['CHIFFRE_AFFAIRES'].sum():,.2f} euros")
    print(f"      - Nombre de produits distincts : {df_ventes['PRODUIT'].nunique()}")

    # 5. Insertion bulk
    print(f"\n[5/5] Insertion des donnees dans {SNOWFLAKE_TABLE}...")
    try:
        succes, nombre_chunks, nombre_lignes_inserees, _ = write_pandas(
            conn,
            df_ventes,
            table_name=SNOWFLAKE_TABLE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            quote_identifiers=False
        )

        if succes:
            print(f"      OK : {nombre_lignes_inserees} lignes inserees")
            print(f"      ({nombre_chunks} chunk(s) de transfert)")
        else:
            print(f"      ATTENTION : insertion partielle")

    except Exception as erreur:
        print(f"      ERREUR : insertion echouee : {erreur}")
        conn.close()
        return

    # Verification finale
    print(f"\nVerification du contenu de la table...")
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {SNOWFLAKE_TABLE}")
    total = cursor.fetchone()[0]
    cursor.execute(
        f"SELECT MIN(DATE_VENTE), MAX(DATE_VENTE), COUNT(DISTINCT PRODUIT), "
        f"SUM(QUANTITE), SUM(CHIFFRE_AFFAIRES) FROM {SNOWFLAKE_TABLE}"
    )
    date_min, date_max, nb_produits, total_qte, total_ca = cursor.fetchone()
    cursor.close()

    print(f"      Total de lignes : {total:,}")
    print(f"      Plage de dates : {date_min} au {date_max}")
    print(f"      Produits distincts : {nb_produits}")
    print(f"      Total unites vendues : {total_qte:,}")
    print(f"      Chiffre d'affaires total : {total_ca:,.2f} euros")

    conn.close()

    print("\n" + "=" * 70)
    print("SEEDING TERMINE AVEC SUCCES")
    print("=" * 70)
    print(f"\nLa table VENTES est maintenant pre-alimentee avec des donnees")
    print(f"correlées avec Google Trends et la meteo.")
    print(f"\nLes 3 tables sont maintenant pretes pour le TP.")


if __name__ == "__main__":
    main()
