"""
=============================================================================
Script de seeding - Table MESURES_TRENDS
=============================================================================
Genere 6 mois d'historique simule credible pour la table Snowflake
MESURES_TRENDS, afin que le TP Google Trends ait des donnees riches
des le premier appel.

Volumetrie generee :
- 30 mots-cles (10 categories x 3 sous-categories)
- ~48 mesures par mot-cle (2 par semaine pendant 6 mois)
- Total : ~1440 lignes inserees

A executer UNE SEULE FOIS en amont de la formation, par le formateur,
avec son compte ACCOUNTADMIN (CHRISTOPHEGUEROULT01).

Pre-requis :
- Table MESURES_TRENDS deja creee (voir create_tables.sql)
- snowflake-connector-python installe (deja dans le venv myenv)
- Fichier categories_cdiscount.json present dans le meme dossier
=============================================================================
"""

import json
import random
import math
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
SNOWFLAKE_TABLE = "MESURES_TRENDS"

NOMBRE_MOIS_HISTORIQUE = 6
FICHIER_CATEGORIES = "categories_cdiscount.json"

random.seed(42)


# =============================================================================
# PROFILS SAISONNIERS DES MOTS-CLES
# =============================================================================
# Chaque mot-cle a un profil saisonnier qui determine sa courbe annuelle.
# Valeur d'interet finale = valeur_base * facteur_saison * (1 + bruit)
#
# Profils disponibles :
#   "ete"      : pic en mai-aout
#   "hiver"    : pic en novembre-fevrier
#   "rentree"  : pic en aout-septembre
#   "noel"     : pic en novembre-decembre
#   "stable"   : peu de variation
#   "printemps": pic en mars-mai
#   "tech"     : pic en septembre (sorties iPhone/Samsung)

PROFILS_MOTS_CLES = {
    # Electromenager - stable
    "frigo": ("stable", 45),
    "machine à laver": ("stable", 38),
    "lave-vaisselle": ("stable", 32),
    # Salon - printemps et noel
    "canapé d'angle": ("printemps", 55),
    "fauteuil relax": ("hiver", 28),
    "table basse": ("stable", 22),
    # Multimedia - pic Noel
    "télévision OLED": ("noel", 65),
    "barre de son": ("noel", 35),
    "vidéoprojecteur": ("noel", 25),
    # Informatique - rentree
    "PC portable": ("rentree", 70),
    "écran 27 pouces": ("stable", 30),
    "imprimante laser": ("rentree", 18),
    # Telephonie - tech (septembre)
    "iPhone 17": ("tech", 95),
    "smartphone Samsung": ("tech", 58),
    "coque de protection": ("tech", 25),
    # Jardin - ete et printemps
    "barbecue gaz": ("ete", 75),
    "tondeuse électrique": ("printemps", 60),
    "salon de jardin": ("ete", 50),
    # Bricolage - printemps
    "perceuse visseuse": ("printemps", 40),
    "escabeau": ("stable", 15),
    "aspirateur atelier": ("stable", 20),
    # Cuisine - leger pic noel
    "robot multifonction": ("noel", 48),
    "four micro-ondes": ("stable", 35),
    "cafetière à grain": ("noel", 42),
    # Mode - rentree, ete, noel
    "sac à dos": ("rentree", 50),
    "montre connectée": ("noel", 45),
    "sneakers": ("ete", 65),
    # Sport et loisirs - printemps et ete
    "vélo électrique": ("printemps", 80),
    "trottinette électrique": ("printemps", 55),
    "tente camping": ("ete", 35)
}


# =============================================================================
# FONCTIONS DE GENERATION
# =============================================================================

def calculer_facteur_saisonnier(profil, mois):
    """
    Retourne un multiplicateur entre 0.5 et 1.8 selon le profil
    saisonnier du mot-cle et le mois de l'annee (1-12).
    """
    if profil == "ete":
        return 0.6 + 0.9 * (1 + math.sin((mois - 4) * math.pi / 6)) / 2
    elif profil == "hiver":
        return 0.6 + 0.9 * (1 + math.cos((mois - 1) * math.pi / 6)) / 2
    elif profil == "rentree":
        if mois in [8, 9]:
            return 1.55
        if mois in [7, 10]:
            return 1.20
        return 0.85
    elif profil == "noel":
        if mois in [11, 12]:
            return 1.60
        if mois == 10:
            return 1.15
        if mois in [1, 2]:
            return 0.65
        return 0.85
    elif profil == "printemps":
        if mois in [3, 4, 5]:
            return 1.40
        if mois in [2, 6]:
            return 1.10
        return 0.85
    elif profil == "tech":
        if mois == 9:
            return 1.80
        if mois in [10, 11]:
            return 1.30
        return 0.85
    else:  # "stable"
        return 0.95 + 0.10 * math.sin(mois * math.pi / 6)


def generer_dates_mesure(date_fin, nombre_mois):
    """
    Genere la liste des dates de mesure (lundi et jeudi de chaque semaine)
    sur les N derniers mois jusqu'a date_fin.
    """
    date_debut = date_fin - timedelta(days=nombre_mois * 30)
    dates = []
    courant = date_debut
    while courant <= date_fin:
        # weekday() : 0 = lundi, 3 = jeudi
        if courant.weekday() in [0, 3]:
            dates.append(courant)
        courant += timedelta(days=1)
    return dates


def generer_mesures(taxonomie, dates_mesure):
    """
    Genere toutes les lignes de mesures fictives.
    Retourne une liste de dictionnaires pretes pour write_pandas.
    """
    lignes = []

    for categorie_obj in taxonomie["categories"]:
        nom_categorie = categorie_obj["nom"]

        for sous_categorie in categorie_obj["sous_categories"]:
            profil, valeur_base = PROFILS_MOTS_CLES.get(
                sous_categorie,
                ("stable", 30)
            )

            for date_mes in dates_mesure:
                facteur = calculer_facteur_saisonnier(profil, date_mes.month)
                bruit = random.uniform(-0.10, 0.10)
                valeur = valeur_base * facteur * (1 + bruit)
                valeur_finale = max(1, round(valeur))

                lignes.append({
                    "DATE_MESURE": date_mes,
                    "CATEGORIE": nom_categorie,
                    "SOUS_CATEGORIE": sous_categorie,
                    "MOT_CLE": sous_categorie,
                    "VALEUR_INTERET": valeur_finale
                })

    return lignes


# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

def main():
    print("=" * 70)
    print("SEEDING DE LA TABLE MESURES_TRENDS")
    print("=" * 70)

    # 1. Charger la taxonomie
    print(f"\n[1/5] Chargement de {FICHIER_CATEGORIES}...")
    try:
        with open(FICHIER_CATEGORIES, "r", encoding="utf-8") as fichier:
            taxonomie = json.load(fichier)
        print(f"      OK : {len(taxonomie['categories'])} categories chargees")
    except FileNotFoundError:
        print(f"      ERREUR : fichier introuvable {FICHIER_CATEGORIES}")
        return
    except json.JSONDecodeError as erreur:
        print(f"      ERREUR : JSON mal forme : {erreur}")
        return

    # 2. Generer les dates de mesure
    print(f"\n[2/5] Generation des dates de mesure...")
    dates_mesure = generer_dates_mesure(date.today(), NOMBRE_MOIS_HISTORIQUE)
    print(f"      OK : {len(dates_mesure)} dates generees")
    print(f"      Du {dates_mesure[0]} au {dates_mesure[-1]}")

    # 3. Generer toutes les lignes de mesures
    print(f"\n[3/5] Generation des lignes de mesures...")
    lignes = generer_mesures(taxonomie, dates_mesure)
    df_mesures = pd.DataFrame(lignes)
    print(f"      OK : {len(df_mesures)} lignes generees")
    print(f"      Apercu :")
    print(df_mesures.head(3).to_string(index=False))

    # 4. Connexion Snowflake
    print(f"\n[4/5] Connexion a Snowflake...")
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

    # 5. Insertion bulk
    print(f"\n[5/5] Insertion des donnees dans {SNOWFLAKE_TABLE}...")
    try:
        succes, nombre_chunks, nombre_lignes_inserees, _ = write_pandas(
            conn,
            df_mesures,
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
        f"SELECT MIN(DATE_MESURE), MAX(DATE_MESURE) FROM {SNOWFLAKE_TABLE}"
    )
    date_min, date_max = cursor.fetchone()
    cursor.close()

    print(f"      Total de lignes dans la table : {total}")
    print(f"      Plage de dates : {date_min} au {date_max}")

    conn.close()

    print("\n" + "=" * 70)
    print("SEEDING TERMINE AVEC SUCCES")
    print("=" * 70)
    print(f"\nLa table MESURES_TRENDS est maintenant pre-alimentee avec")
    print(f"{NOMBRE_MOIS_HISTORIQUE} mois d'historique simule.")


if __name__ == "__main__":
    main()
