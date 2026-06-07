"""
Génération du fichier ventes_retours.csv pour le Mini-projet 3.8 de la formation Python Data Cdiscount.

Reproductible : random.seed(42) garantit que chaque exécution produit le même CSV.
"""
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

# Chemin absolu basé sur l'emplacement du script
# → le CSV est toujours créé à côté du script, peu importe d'où on le lance
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================================
# CATALOGUE PRODUITS
# =====================================================
# Les 6 produits du fil rouge + 6 nouveaux dans le même esprit (périphériques)
PRODUITS = [
    # (nom, prix_unitaire, categorie)
    ("Casque",          49.90, "Standard"),
    ("Souris",          19.90, "Entrée de gamme"),
    ("Clavier",         79.00, "Standard"),
    ("Écran",          199.00, "Premium"),
    ("Webcam",          34.90, "Standard"),
    ("Tapis",            9.90, "Entrée de gamme"),
    ("Hub USB",         14.90, "Entrée de gamme"),
    ("Enceinte",        89.90, "Standard"),
    ("Imprimante",     249.00, "Premium"),
    ("Disque externe",  69.00, "Standard"),
    ("Micro USB",       39.90, "Standard"),
    ("Support écran",   24.90, "Entrée de gamme"),
]

# Pondération des produits pour avoir une hiérarchie réaliste
# (les périphériques de base se vendent plus que les Premium)
POIDS_PRODUITS = [
    14,   # Casque
    20,   # Souris (best-seller)
    12,   # Clavier
    5,    # Écran (Premium, moins fréquent)
    10,   # Webcam
    18,   # Tapis (entrée de gamme, gros volume)
    12,   # Hub USB
    7,    # Enceinte
    3,    # Imprimante (Premium, le moins fréquent)
    6,    # Disque externe
    9,    # Micro USB
    14,   # Support écran
]

# =====================================================
# RÉGIONS CLIENTES
# =====================================================
REGIONS = [
    "Île-de-France",
    "Auvergne-Rhône-Alpes",
    "Provence-Alpes-Côte d'Azur",
    "Occitanie",
    "Nouvelle-Aquitaine",
    "Hauts-de-France",
    "Grand Est",
    "Bretagne",
]

# Pondération réaliste (IDF concentre une grande partie des achats e-commerce)
POIDS_REGIONS = [30, 15, 12, 10, 10, 10, 8, 5]

# =====================================================
# PARAMÈTRES DE GÉNÉRATION
# =====================================================
NB_LIGNES = 150
DATE_DEBUT = date(2026, 1, 1)
DATE_FIN = date(2026, 3, 31)
TAUX_RETOUR_BASE = 0.15  # 15% de retours en moyenne

# Taux de retour différencié par catégorie (Premium retourné plus souvent : plus cher, plus exigeant)
TAUX_RETOUR_PAR_CATEGORIE = {
    "Premium":         0.25,  # 25% de retour
    "Standard":        0.13,  # 13% de retour
    "Entrée de gamme": 0.08,  # 8% de retour
}

# Distribution des quantités (la plupart des commandes sont à 1 ou 2 produits)
QUANTITES = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5]


def generer_date_aleatoire():
    """Date aléatoire entre DATE_DEBUT et DATE_FIN."""
    nb_jours = (DATE_FIN - DATE_DEBUT).days
    delta = random.randint(0, nb_jours)
    return DATE_DEBUT + timedelta(days=delta)


def main():
    lignes = []
    for id_commande in range(1, NB_LIGNES + 1):
        # Tirage du produit selon les poids
        produit_data = random.choices(PRODUITS, weights=POIDS_PRODUITS, k=1)[0]
        nom, prix, categorie = produit_data

        # Statut (Vente ou Retour) selon catégorie
        taux_retour = TAUX_RETOUR_PAR_CATEGORIE[categorie]
        statut = "Retour" if random.random() < taux_retour else "Vente"

        # Quantité
        quantite = random.choice(QUANTITES)

        # Région
        region = random.choices(REGIONS, weights=POIDS_REGIONS, k=1)[0]

        # Date
        date_commande = generer_date_aleatoire()

        lignes.append([
            id_commande,
            date_commande.isoformat(),  # YYYY-MM-DD
            nom,
            categorie,
            f"{prix:.2f}",
            quantite,
            statut,
            region,
        ])

    # Tri par date pour avoir un CSV chronologique (plus naturel)
    lignes.sort(key=lambda row: row[1])

    # Renumérotation des id_commande après tri
    for i, ligne in enumerate(lignes, start=1):
        ligne[0] = i

    # Écriture du CSV
    chemin = os.path.join(SCRIPT_DIR, "ventes_retours.csv")
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_commande", "date", "produit", "categorie",
            "prix_unitaire", "quantite", "statut", "client_region",
        ])
        writer.writerows(lignes)

    print(f"✅ {chemin} généré avec {NB_LIGNES} lignes")

    # Stats descriptives pour vérification rapide
    nb_ventes = sum(1 for l in lignes if l[6] == "Vente")
    nb_retours = NB_LIGNES - nb_ventes
    print(f"   Ventes  : {nb_ventes} ({nb_ventes/NB_LIGNES:.1%})")
    print(f"   Retours : {nb_retours} ({nb_retours/NB_LIGNES:.1%})")

    # Comptage par catégorie
    from collections import Counter
    cat_count = Counter(l[3] for l in lignes)
    print(f"\n   Répartition par catégorie :")
    for cat, n in cat_count.most_common():
        print(f"     {cat:<20} {n:>3} commandes")

    # Comptage par mois
    mois_count = Counter(l[1][:7] for l in lignes)
    print(f"\n   Répartition par mois :")
    for mois in sorted(mois_count):
        print(f"     {mois}  {mois_count[mois]:>3} commandes")


if __name__ == "__main__":
    main()
