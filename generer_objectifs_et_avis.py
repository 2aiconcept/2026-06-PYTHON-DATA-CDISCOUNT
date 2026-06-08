# -*- coding: utf-8 -*-
"""
Genere les jeux de donnees de la sous-section 4.3 (Lire Excel et JSON) :
  - objectifs_commerciaux_2026.xlsx : classeur 2 feuilles (Objectifs, Responsables)
  - avis_clients_api.json           : reponse "API" d'avis clients (liste plate)

Noms de categories / produits ALIGNES sur ventes_retours.csv pour permettre
les merges du TP 4.5. Reproductible (aucun aleatoire : valeurs ecrites en dur).

Lancer avec le python du venv myenv (pandas 3.0.2, openpyxl) :
    C:\\formation_python\\myenv\\Scripts\\python.exe generer_objectifs_et_avis.py
"""
import json
import pandas as pd

# ---------------------------------------------------------------
# 1. Excel multi-feuilles : objectifs_commerciaux_2026.xlsx
# ---------------------------------------------------------------
objectifs = pd.DataFrame({
    "categorie": ["Entrée de gamme", "Standard", "Premium"],
    "objectif_ca_t1": [3000.0, 7500.0, 3500.0],
})

responsables = pd.DataFrame({
    "categorie": ["Entrée de gamme", "Standard", "Premium"],
    "responsable": ["Soumaya", "Aurore", "Raphaël"],
})

with pd.ExcelWriter("objectifs_commerciaux_2026.xlsx", engine="openpyxl") as writer:
    objectifs.to_excel(writer, sheet_name="Objectifs", index=False)
    responsables.to_excel(writer, sheet_name="Responsables", index=False)

print("OK -> objectifs_commerciaux_2026.xlsx (feuilles : Objectifs, Responsables)")

# ---------------------------------------------------------------
# 2. JSON "reponse API" : avis_clients_api.json (liste plate)
#    Un objet par produit -> pd.read_json donne directement un DataFrame.
# ---------------------------------------------------------------
avis = [
    {"produit": "Souris",         "note_moyenne": 4.3, "nb_avis": 512},
    {"produit": "Casque",         "note_moyenne": 4.6, "nb_avis": 874},
    {"produit": "Disque externe", "note_moyenne": 4.1, "nb_avis": 203},
    {"produit": "Webcam",         "note_moyenne": 3.8, "nb_avis": 147},
    {"produit": "Tapis",          "note_moyenne": 4.4, "nb_avis": 321},
    {"produit": "Hub USB",        "note_moyenne": 4.0, "nb_avis": 98},
    {"produit": "Clavier",        "note_moyenne": 4.5, "nb_avis": 656},
    {"produit": "Enceinte",       "note_moyenne": 4.2, "nb_avis": 489},
    {"produit": "Support écran",  "note_moyenne": 3.9, "nb_avis": 76},
    {"produit": "Micro USB",      "note_moyenne": 3.7, "nb_avis": 54},
    {"produit": "Imprimante",     "note_moyenne": 3.5, "nb_avis": 412},
    {"produit": "Écran",          "note_moyenne": 4.7, "nb_avis": 938},
]

with open("avis_clients_api.json", "w", encoding="utf-8") as f:
    json.dump(avis, f, ensure_ascii=False, indent=2)

print("OK -> avis_clients_api.json (%d produits)" % len(avis))
