"""
test_env.py — Validation de l'environnement de formation Python Data
À exécuter dans le venv activé :

    (env_formation) PS> python test_env.py

Le script valide en 4 étapes :
1. Import des 10 librairies cœur
2. Manipulation pandas basique
3. Entraînement Prophet end-to-end (test critique)
4. Import des 3 librairies des cas d'usage (sFTP, Microsoft, Google Trends)

En cas d'échec, le script s'arrête immédiatement avec un code retour != 0.
"""

import sys

print(f"Python    : {sys.version}")
print(f"Executable: {sys.executable}")
print("-" * 60)

# === Test 1 : import des 10 librairies cœur ===
print("\n[Test 1/4] Import des 10 librairies coeur...")
try:
    import pandas as pd
    import openpyxl
    import snowflake.connector
    import requests
    from bs4 import BeautifulSoup
    import matplotlib.pyplot as plt
    import seaborn as sns
    import sklearn
    from prophet import Prophet
    import ipykernel
    print("  OK - Toutes les librairies importees")
    print(f"     pandas       : {pd.__version__}")
    print(f"     matplotlib   : {plt.matplotlib.__version__}")
    print(f"     scikit-learn : {sklearn.__version__}")
except ImportError as e:
    print(f"  ECHEC import : {e}")
    sys.exit(1)

# === Test 2 : mini-calcul pandas ===
print("\n[Test 2/4] Creation et manipulation d'un DataFrame...")
try:
    df = pd.DataFrame({
        'Mois': ['Jan', 'Fev', 'Mar', 'Avr'],
        'Ventes': [120, 145, 98, 167]
    })
    total = df['Ventes'].sum()
    assert total == 530, f"Somme attendue 530, obtenue {total}"
    print(f"  OK - DataFrame cree, somme calculee : {total}")
except Exception as e:
    print(f"  ECHEC pandas : {e}")
    sys.exit(1)

# === Test 3 : entraînement Prophet (TEST CRITIQUE) ===
print("\n[Test 3/4] Entrainement d'un modele Prophet...")
print("  (peut prendre 1-3 min au premier lancement - compilation Stan)")
try:
    df_prophet = pd.DataFrame({
        'ds': pd.date_range('2024-01-01', periods=30),
        'y': range(30)
    })
    m = Prophet()
    m.fit(df_prophet)
    forecast = m.predict(m.make_future_dataframe(periods=7))
    assert len(forecast) == 37, "Forecast attendu : 37 lignes"
    print("  OK - Prophet : modele entraine, prevision sur 7 jours generee")
except Exception as e:
    print(f"  ECHEC Prophet : {e}")
    print("  -> Verifier l'installation cmdstan (section 3.5 du document DSI)")
    sys.exit(1)

# === Test 4 : librairies des cas d'usage (sFTP, Microsoft, Google Trends) ===
print("\n[Test 4/4] Import des 3 librairies des cas d'usage...")
print("  (paramiko = sFTP J3, pywin32 = Microsoft J4, trendspyg = Google Trends J3)")
try:
    import paramiko
    import win32com.client          # fourni par pywin32 (Windows uniquement)
    import trendspyg
    print("  OK - Librairies cas d'usage importees")
    print(f"     paramiko  : {getattr(paramiko, '__version__', '?')}")
    print(f"     pywin32   : OK (win32com.client disponible)")
    print(f"     trendspyg : {getattr(trendspyg, '__version__', '?')}")
except ImportError as e:
    print(f"  ECHEC import cas d'usage : {e}")
    print("  -> Verifier l'installation : pip install paramiko pywin32 trendspyg")
    print("  -> Pour pywin32, post-install requis :")
    print("     python <venv>\\Scripts\\pywin32_postinstall.py -install")
    sys.exit(1)

print("\n" + "=" * 60)
print("  ENVIRONNEMENT 100% VALIDE - POSTE PRET POUR LA FORMATION")
print("=" * 60)