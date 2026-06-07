"""
test_env.py — Validation de l'environnement Python pour la formation
Cdiscount Python Data — 4 jours.

Usage (dans le venv activé) :
    python test_env.py

Sortie attendue : "✅ TOUT OK — environnement validé pour la formation"
Si une étape échoue, le script affiche l'erreur précise et stoppe.

Couvre :
- Version Python
- Import + version de toutes les libs cœur
- Création d'un DataFrame pandas (équivalent cellule 1.6 du guide)
- Génération d'un graphique matplotlib en backend non-interactif
  (équivalent cellule 1.7)
- Test minimal de Prophet (compile cmdstan si nécessaire au 1er run)
- Test de l'import snowflake-connector (sans tenter de connexion)
- Test de l'import ipykernel (intégration Jupyter)
"""

import sys
import traceback
from pathlib import Path

REQUIRED_PYTHON = (3, 12, 7)   # version cible validée projet
RESULTS = []
SCRIPT_DIR = Path(__file__).resolve().parent


def ok(label):
    RESULTS.append(("✅", label))
    print(f"  ✅ {label}")


def ko(label, err):
    RESULTS.append(("❌", f"{label} — {err}"))
    print(f"  ❌ {label}")
    print(f"     → {err}")


# ========== 1. Version Python ==========
print("\n[1/8] Version Python")
v = sys.version_info
print(f"  Python détecté : {v.major}.{v.minor}.{v.micro}")
if (v.major, v.minor) == REQUIRED_PYTHON[:2]:
    ok(f"Python {v.major}.{v.minor}.x conforme à la cible")
else:
    ko(
        f"Python attendu {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x",
        f"trouvé {v.major}.{v.minor}.{v.micro}",
    )

# ========== 2. Imports des libs cœur ==========
print("\n[2/8] Imports des librairies du programme")
libs = [
    ("pandas", "pd"),
    ("numpy", "np"),
    ("openpyxl", None),
    ("snowflake.connector", None),
    ("requests", None),
    ("bs4", None),                  # beautifulsoup4
    ("matplotlib", None),
    ("seaborn", "sns"),
    ("sklearn", None),              # scikit-learn
    ("prophet", None),
    ("ipykernel", None),
]
imported = {}
for module_name, alias in libs:
    try:
        mod = __import__(module_name)
        version = getattr(mod, "__version__", "?")
        imported[module_name] = mod
        ok(f"{module_name} {version}")
    except Exception as e:
        ko(f"import {module_name}", repr(e))

# ========== 3. DataFrame pandas (équiv. cellule 1.6) ==========
print("\n[3/8] Test pandas — création DataFrame")
try:
    import pandas as pd
    data = {
        "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
        "Ventes": [120, 145, 98, 167, 189, 210],
        "Retours": [12, 18, 8, 22, 15, 19],
    }
    df = pd.DataFrame(data)
    assert df.shape == (6, 3), f"shape inattendue : {df.shape}"
    assert df["Ventes"].sum() == 929, "somme Ventes incorrecte"
    html_repr = df._repr_html_()    # ce que Jupyter affiche en cellule 1.6
    assert html_repr and "<table" in html_repr, "repr HTML manquant"
    ok(f"DataFrame {df.shape} créé, repr HTML OK, sum(Ventes)=929")
except Exception as e:
    ko("DataFrame pandas", repr(e))

# ========== 4. Graphique matplotlib (équiv. cellule 1.7) ==========
print("\n[4/8] Test matplotlib — génération graphique")
try:
    import matplotlib
    matplotlib.use("Agg")          # backend non-interactif (pas de fenêtre)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Mois"], df["Ventes"], marker="o", linewidth=2, label="Ventes")
    ax.plot(df["Mois"], df["Retours"], marker="s", linewidth=2, label="Retours")
    ax.set_title("Test — Ventes vs Retours")
    ax.legend()
    ax.grid(True, alpha=0.3)
    out_png = SCRIPT_DIR / "_test_plot.png"
    plt.savefig(out_png)
    plt.close(fig)
    assert out_png.exists() and out_png.stat().st_size > 1000, "PNG vide"
    ok(f"graphique généré ({out_png.stat().st_size // 1024} Ko) → {out_png.name}")
    out_png.unlink()               # cleanup
except Exception as e:
    ko("matplotlib", repr(e))

# ========== 5. Test Prophet — fit + predict ==========
print("\n[5/8] Test Prophet — fit + predict")
print("  (peut prendre 30-60 s au premier run si cmdstan doit compiler)")
try:
    from prophet import Prophet
    import pandas as pd

    df_p = pd.DataFrame({
        "ds": pd.date_range("2024-01-01", periods=30, freq="D"),
        "y": range(30),
    })
    m = Prophet()
    m.fit(df_p)
    future = m.make_future_dataframe(periods=7)
    forecast = m.predict(future)
    assert len(forecast) == 37, f"longueur forecast inattendue : {len(forecast)}"
    ok(f"Prophet fit + predict OK ({len(forecast)} lignes prédites)")
except Exception as e:
    ko("Prophet", repr(e))
    print()
    print("  💡 Diagnostic Prophet :")
    print("     - cmdstan installé ?  python -c \"import cmdstanpy; print(cmdstanpy.cmdstan_path())\"")
    print("     - RTools40 dans PATH ?  echo %PATH% | findstr RTools40")
    print("     - voir procédure complète dans le guide formation (Annexe A.5)")

# ========== 6. ipykernel — intégration Jupyter ==========
print("\n[6/8] Test ipykernel — kernel Jupyter")
try:
    import ipykernel
    from jupyter_client import KernelManager
    ok(f"ipykernel {ipykernel.__version__} + jupyter_client présents")
except Exception as e:
    ko("ipykernel / jupyter_client", repr(e))

# ========== 7. snowflake-connector (import seul, pas de connexion) ==========
print("\n[7/8] Test snowflake-connector (import uniquement)")
try:
    import snowflake.connector
    ok(f"snowflake-connector-python {snowflake.connector.__version__}")
    print("     (test de connexion réelle à faire séparément avec credentials)")
except Exception as e:
    ko("snowflake-connector", repr(e))

# ========== 8. Verdict final ==========
print("\n[8/8] Verdict final")
print("─" * 60)
fails = [r for r in RESULTS if r[0] == "❌"]
if not fails:
    print("✅ TOUT OK — environnement validé pour la formation")
    sys.exit(0)
else:
    print(f"❌ {len(fails)} erreur(s) détectée(s) :")
    for _, msg in fails:
        print(f"   - {msg}")
    print()
    print("→ Merci de transmettre cette sortie complète au formateur")
    print("  (sebastien@2aiconcept.com) avant J1.")
    sys.exit(1)