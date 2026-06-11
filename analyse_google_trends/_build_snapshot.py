# -*- coding: utf-8 -*-
# Constructeur du snapshot de secours pytrends (30 mots-cles).
# Robuste au 429 : retry EXPLICITE (sleep croissant), sans retries/backoff pytrends
# (incompatibles avec urllib3 2.x -> TypeError method_whitelist).
import sys, io, warnings, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import date
import pandas as pd
from pytrends.request import TrendReq

warnings.filterwarnings("ignore", category=FutureWarning)

GEO = "FR"
TIMEFRAME = "today 3-m"
PAUSE_BASE = 12          # espacement de base entre mots-cles
MAX_TENTATIVES = 5       # nb d'essais par mot-cle avant abandon
DATE_JOUR = date.today()

taxo = json.load(open("categories_cdiscount.json", encoding="utf-8"))
a_faire = []
for cat in taxo["categories"]:
    for sc in cat["sous_categories"]:
        a_faire.append({"CATEGORIE": cat["nom"], "SOUS_CATEGORIE": sc})

# Client simple (retries=0 par defaut -> evite le bug urllib3)
pytrends = TrendReq(hl="fr-FR", tz=60, timeout=(10, 30))

resultats = {}

def chercher(sc):
    # retry explicite : on reessaie en attendant de plus en plus longtemps sur 429
    for tentative in range(MAX_TENTATIVES):
        try:
            pytrends.build_payload([sc], geo=GEO, timeframe=TIMEFRAME)
            dfi = pytrends.interest_over_time()
            return int(dfi[sc].iloc[-1])
        except Exception as e:
            attente = PAUSE_BASE * (tentative + 1)   # 12, 24, 36, 48, 60s
            print(f"   ... {sc}: {type(e).__name__}, nouvelle tentative dans {attente}s", flush=True)
            time.sleep(attente)
    return None

def une_passe(items, label):
    restants = []
    for item in items:
        sc = item["SOUS_CATEGORIE"]
        valeur = chercher(sc)
        if valeur is not None:
            resultats[sc] = valeur
            print(f"[{label}] OK   {sc:24s} = {valeur}", flush=True)
        else:
            restants.append(item)
            print(f"[{label}] FAIL {sc:24s} (abandon apres {MAX_TENTATIVES} essais)", flush=True)
        time.sleep(PAUSE_BASE)
    return restants

restants = une_passe(a_faire, "P1")
if restants:
    print(f"--- {len(restants)} echecs, cooldown 120s avant passe 2 ---", flush=True)
    time.sleep(120)
    restants = une_passe(restants, "P2")

lignes = []
for item in a_faire:
    sc = item["SOUS_CATEGORIE"]
    if sc in resultats:
        lignes.append({
            "DATE_MESURE": DATE_JOUR,
            "CATEGORIE": item["CATEGORIE"],
            "SOUS_CATEGORIE": sc,
            "MOT_CLE": sc,
            "VALEUR_INTERET": resultats[sc],
        })

df = pd.DataFrame(lignes)
df.to_csv("snapshot_trends_secours.csv", index=False, encoding="utf-8")
print("=== TERMINE ===", flush=True)
print(f"{len(df)}/30 mots-cles recuperes -> snapshot_trends_secours.csv", flush=True)
if restants:
    print("Manquants:", [i["SOUS_CATEGORIE"] for i in restants], flush=True)
