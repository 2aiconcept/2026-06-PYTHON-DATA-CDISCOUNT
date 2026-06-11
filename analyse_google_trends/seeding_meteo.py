"""
=============================================================================
Script de seeding - Table METEO_HISTORIQUE
=============================================================================
Genere 6 mois de meteo France journaliere simulee credible pour la table
Snowflake METEO_HISTORIQUE.

Volumetrie generee :
- 1 ligne par jour sur 6 mois
- Total : ~180 lignes inserees

Variables generees pour chaque jour :
- TEMPERATURE_MOYENNE (degres Celsius) : variation saisonniere realiste
- PRECIPITATIONS_MM (millimetres) : pluviometrie credible
- ENSOLEILLEMENT_HEURES : duree d'ensoleillement journaliere

A executer UNE SEULE FOIS en amont de la formation, par le formateur,
avec son compte ACCOUNTADMIN (CHRISTOPHEGUEROULT01).

Pre-requis :
- Table METEO_HISTORIQUE deja creee (voir create_tables.sql)
- snowflake-connector-python[pandas] installe (avec pyarrow)
=============================================================================
"""

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
SNOWFLAKE_TABLE = "METEO_HISTORIQUE"

NOMBRE_MOIS_HISTORIQUE = 6

# Reproductibilite (graine differente de seeding_trends pour eviter
# les correlations artificielles trop parfaites)
random.seed(123)


# =============================================================================
# PROFILS METEO PAR MOIS POUR LA FRANCE METROPOLITAINE
# =============================================================================
# Pour chaque mois : (temp_moyenne, amplitude_temp, precipitations_mm, ensoleillement_h)
# Donnees inspirees des moyennes France realistes mais simplifiees.

PROFILS_METEO_PAR_MOIS = {
    1:  (4.5,  3, 65, 2.5),   # Janvier : froid, pluvieux, peu de soleil
    2:  (5.5,  3, 55, 3.5),   # Fevrier : froid sec
    3:  (8.5,  4, 60, 5.0),   # Mars : doux, pluvieux
    4:  (11.5, 5, 65, 6.5),   # Avril : doux, pluvieux
    5:  (15.0, 5, 70, 7.5),   # Mai : doux, parfois orageux
    6:  (18.5, 6, 55, 9.0),   # Juin : chaud, modere
    7:  (21.0, 6, 45, 10.0),  # Juillet : chaud, sec
    8:  (21.0, 6, 50, 9.5),   # Aout : chaud, sec
    9:  (17.5, 5, 60, 7.5),   # Septembre : doux, pluvieux
    10: (13.5, 4, 80, 5.5),   # Octobre : frais, tres pluvieux
    11: (8.0,  3, 75, 3.5),   # Novembre : froid, tres pluvieux
    12: (5.0,  3, 70, 2.5)    # Decembre : froid, pluvieux
}


# =============================================================================
# FONCTIONS DE GENERATION
# =============================================================================

def generer_temperature(mois, jour_du_mois):
    """
    Genere une temperature moyenne journaliere realiste pour la France
    en fonction du mois, avec une variation lente sur le mois et du bruit.
    """
    temp_base, amplitude, _, _ = PROFILS_METEO_PAR_MOIS[mois]

    # Variation lente intra-mois (legere sinusoide pour simuler des periodes
    # plus chaudes ou plus froides au sein d'un meme mois)
    variation_intra_mois = amplitude * math.sin((jour_du_mois - 1) * math.pi / 15)

    # Bruit aleatoire pour rendre le quotidien credible
    bruit = random.uniform(-2.5, 2.5)

    temperature = temp_base + variation_intra_mois + bruit
    return round(temperature, 1)


def generer_precipitations(mois):
    """
    Genere les precipitations journalieres en mm.
    La plupart des jours sont secs (0 mm), avec quelques jours de pluie
    et plus rarement de gros episodes pluvieux.
    """
    _, _, precip_mensuelle, _ = PROFILS_METEO_PAR_MOIS[mois]

    # Probabilite qu'il pleuve aujourd'hui (proportionnelle a la pluviometrie mensuelle)
    proba_pluie = precip_mensuelle / 100.0

    if random.random() > proba_pluie:
        # Jour sec
        return 0.0

    # Jour de pluie : la plupart du temps modere, parfois plus fort
    type_pluie = random.random()

    if type_pluie < 0.70:
        # Pluie legere (70% des jours de pluie)
        return round(random.uniform(0.5, 5.0), 1)
    elif type_pluie < 0.95:
        # Pluie moderee (25%)
        return round(random.uniform(5.0, 15.0), 1)
    else:
        # Episode pluvieux fort (5%)
        return round(random.uniform(15.0, 35.0), 1)


def generer_ensoleillement(mois, precipitations):
    """
    Genere les heures d'ensoleillement en fonction du mois et de la pluie.
    Plus il pleut, moins il y a de soleil.
    """
    _, _, _, ensoleil_base = PROFILS_METEO_PAR_MOIS[mois]

    # Reduction d'ensoleillement si pluie
    if precipitations == 0:
        reduction = 0
    elif precipitations < 5:
        reduction = 1.5
    elif precipitations < 15:
        reduction = 3.0
    else:
        reduction = 5.0

    # Bruit aleatoire
    bruit = random.uniform(-1.0, 1.0)

    ensoleillement = ensoleil_base - reduction + bruit
    # Bornes physiques : entre 0 et 14h
    ensoleillement = max(0.0, min(14.0, ensoleillement))

    return round(ensoleillement, 2)


def generer_dates_meteo(date_fin, nombre_mois):
    """
    Genere la liste de toutes les dates journalieres sur les N derniers mois.
    """
    date_debut = date_fin - timedelta(days=nombre_mois * 30)
    dates = []
    courant = date_debut
    while courant <= date_fin:
        dates.append(courant)
        courant += timedelta(days=1)
    return dates


def generer_meteo(dates_meteo):
    """
    Genere toutes les lignes meteo pour la liste de dates fournie.
    Retourne une liste de dictionnaires prets pour write_pandas.
    """
    lignes = []

    for date_mes in dates_meteo:
        mois = date_mes.month
        jour = date_mes.day

        temperature = generer_temperature(mois, jour)
        precipitations = generer_precipitations(mois)
        ensoleillement = generer_ensoleillement(mois, precipitations)

        lignes.append({
            "DATE_METEO": date_mes,
            "TEMPERATURE_MOYENNE": temperature,
            "PRECIPITATIONS_MM": precipitations,
            "ENSOLEILLEMENT_HEURES": ensoleillement
        })

    return lignes


# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

def main():
    print("=" * 70)
    print("SEEDING DE LA TABLE METEO_HISTORIQUE")
    print("=" * 70)

    # 1. Generer les dates
    print(f"\n[1/4] Generation des dates meteo...")
    dates_meteo = generer_dates_meteo(date.today(), NOMBRE_MOIS_HISTORIQUE)
    print(f"      OK : {len(dates_meteo)} jours generes")
    print(f"      Du {dates_meteo[0]} au {dates_meteo[-1]}")

    # 2. Generer toutes les lignes meteo
    print(f"\n[2/4] Generation des donnees meteo...")
    lignes = generer_meteo(dates_meteo)
    df_meteo = pd.DataFrame(lignes)
    print(f"      OK : {len(df_meteo)} lignes generees")
    print(f"      Apercu :")
    print(df_meteo.head(5).to_string(index=False))
    print(f"      ...")
    print(df_meteo.tail(3).to_string(index=False))

    # Statistiques pour controle visuel
    print(f"\n      Statistiques generales :")
    print(f"      - Temperature : min={df_meteo['TEMPERATURE_MOYENNE'].min():.1f} "
          f"max={df_meteo['TEMPERATURE_MOYENNE'].max():.1f} "
          f"moy={df_meteo['TEMPERATURE_MOYENNE'].mean():.1f}")
    print(f"      - Precipitations : total={df_meteo['PRECIPITATIONS_MM'].sum():.0f}mm "
          f"jours_pluie={(df_meteo['PRECIPITATIONS_MM'] > 0).sum()}")
    print(f"      - Ensoleillement : moy={df_meteo['ENSOLEILLEMENT_HEURES'].mean():.1f}h/jour")

    # 3. Connexion Snowflake
    print(f"\n[3/4] Connexion a Snowflake...")
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

    # 4. Insertion bulk
    print(f"\n[4/4] Insertion des donnees dans {SNOWFLAKE_TABLE}...")
    try:
        succes, nombre_chunks, nombre_lignes_inserees, _ = write_pandas(
            conn,
            df_meteo,
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
        f"SELECT MIN(DATE_METEO), MAX(DATE_METEO) FROM {SNOWFLAKE_TABLE}"
    )
    date_min, date_max = cursor.fetchone()
    cursor.execute(
        f"SELECT AVG(TEMPERATURE_MOYENNE), AVG(PRECIPITATIONS_MM), AVG(ENSOLEILLEMENT_HEURES) "
        f"FROM {SNOWFLAKE_TABLE}"
    )
    temp_avg, prec_avg, ens_avg = cursor.fetchone()
    cursor.close()

    print(f"      Total de lignes : {total}")
    print(f"      Plage de dates : {date_min} au {date_max}")
    print(f"      Moyennes : temp={temp_avg:.1f}C, precip={prec_avg:.1f}mm/jour, "
          f"ensoleil={ens_avg:.1f}h/jour")

    conn.close()

    print("\n" + "=" * 70)
    print("SEEDING TERMINE AVEC SUCCES")
    print("=" * 70)
    print(f"\nLa table METEO_HISTORIQUE est maintenant pre-alimentee avec")
    print(f"{NOMBRE_MOIS_HISTORIQUE} mois de meteo France simulee.")


if __name__ == "__main__":
    main()
