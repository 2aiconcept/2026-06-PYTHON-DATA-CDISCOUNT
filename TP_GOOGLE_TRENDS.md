# TP Google Trends — Radar concurrentiel multi-sources Cdiscount

> **Fichier de cadrage à lire AVANT toute génération de code.**
> Ce TP est l'aboutissement applicatif de la formation Python Data Cdiscount.
> Il croise 3 sources de données (Google Trends, ventes, météo) pour produire
> un rapport Excel multi-onglets exploitable par le service pricing.

---

## 1. Le contexte métier

**Loïc Sutel** est responsable pricing chez Cdiscount. Il gère le pricing de centaines de catégories de produits regroupées dans une **taxonomie hiérarchique** : environ 10 catégories principales (Électroménager, Salon, Multimédia, etc.) × environ 100 sous-catégories chacune (frigo, machine à laver, lave-vaisselle, four...).

Aujourd'hui, Loïc aimerait surveiller les **tendances de recherche Google** sur ses produits pour anticiper son pricing, et croiser ces tendances avec ses **données de ventes internes** ainsi qu'avec la **météo** pour identifier des leviers d'action concrets. Mais c'est **infaisable manuellement** : il faudrait croiser des milliers de mots-clés avec ses tables de ventes et des données météo.

**Sa demande** : un script Python qui produit automatiquement un **rapport Excel multi-onglets** croisant ces 3 sources et lui permet de prendre des décisions pricing immédiates.

C'est le cas d'usage type d'un **radar concurrentiel automatisé** qui justifie à lui seul l'investissement dans une formation Python pour data analysts.

---

## 2. L'utilisateur final du code

Le code généré sera lu, exécuté, modifié et réutilisé par des **data analysts Cdiscount, débutants complets en Python**. Ils ont suivi une formation Python Data de 4 jours. Ils sont à l'aise en SQL et Excel mais découvrent Python. Ils utilisent un notebook Jupyter dans VS Code.

**Conséquences pour le code :**

- Code **basique uniquement**, niveau débutant
- Pas de constructions avancées (pas de list comprehensions imbriquées, pas de lambda complexes, pas de décorateurs, pas d'async/await)
- Privilégier la **lisibilité absolue** à la concision
- Une instruction = une ligne (pas d'enchaînement type `df.dropna().reset_index().sort_values(...)`)
- Les analogies **SQL/Excel** sont bienvenues dans les commentaires

---

## 3. Méthode pédagogique : pseudo-code puis code

Pour chaque section du notebook, on suit **strictement** ce protocole en 2 temps :

### Temps 1 — Génération du pseudo-code (par Claude.ai ou Claude Code)

Pour chaque cellule, **commencer par écrire le pseudo-code en français** dans un commentaire Python en début de cellule. Le pseudo-code décrit l'intention métier et la logique d'enchaînement, sans syntaxe Python.

### Temps 2 — Génération du code Python (par Claude Code)

**Sous le pseudo-code**, écrire le code Python qui réalise l'algorithme décrit. Le pseudo-code reste dans la cellule sous forme de commentaires — il sert de documentation embarquée.

### Exemple visuel d'une cellule

```python
# ============================================================
# SECTION 3.2 : Boucle d'interrogation Google Trends
# ============================================================
#
# PSEUDO-CODE :
# Pour chaque categorie de la taxonomie :
#     Pour chaque sous-categorie de la categorie :
#         Tenter d'appeler Google Trends sur ce mot-cle
#         Si succes : ajouter la mesure a la liste
#         Si echec : logger l'erreur et continuer avec le suivant
#         Attendre 1.5 seconde avant le prochain appel
# A la fin : verifier qu'on a recu au moins 25 mesures sur 30

# CODE :
mesures_du_jour = []
client_trends = TrendReq(hl="fr-FR", tz=60, timeout=(10, 30))

for categorie_obj in taxonomie["categories"]:
    nom_categorie = categorie_obj["nom"]
    for sous_categorie in categorie_obj["sous_categories"]:
        try:
            client_trends.build_payload([sous_categorie], geo='FR', timeframe='today 3-m')
            df_interet = client_trends.interest_over_time()
            valeur = int(df_interet[sous_categorie].iloc[-1])
            mesures_du_jour.append({...})
        except Exception as erreur:
            print(f"Echec pour '{sous_categorie}' : {erreur}")
        time.sleep(1.5)

print(f"Total : {len(mesures_du_jour)} mesures recuperees sur 30 attendues")
```

### Pourquoi cette méthode

- Le stagiaire **comprend l'intention** avant de voir la syntaxe
- Quand il relit son notebook plus tard, il a la **doc embarquée**
- Si une portion plante, il sait **pourquoi elle existe**
- C'est ce qu'on lui demandera de faire en autonomie **après la formation** : penser en français avant de coder

---

## 4. L'architecture du pipeline

```
+----------------+      +----------------+      +----------------+
| Google Trends  |      | Snowflake      |      | Snowflake      |
| (live)         |      | VENTES         |      | METEO_HISTORIQUE|
+--------+-------+      +--------+-------+      +--------+-------+
         |                       |                       |
         | (1) interrogation     | (2) lecture           | (3) lecture
         | + insertion           |                       |
         v                       v                       v
   +-----------+           +-----------+           +-----------+
   | Snowflake |           | DataFrame |           | DataFrame |
   | MESURES_  |           | ventes    |           | meteo     |
   | TRENDS    |           +-----+-----+           +-----+-----+
   +-----+-----+                 |                       |
         |                       |                       |
         +-----------+-----------+-----------+-----------+
                                 |
                                 v
                      +----------------------+
                      | (4) Calculs croises  |
                      | et correlations      |
                      +----------+-----------+
                                 |
                                 v
                      +----------------------+
                      | (5) Rapport Excel    |
                      | 8 onglets pour Loic  |
                      +----------------------+
```

---

## 5. Les 8 sections du notebook

Le notebook est structuré en **8 sections numérotées**. Chacune contient plusieurs cellules avec pseudo-code + code, dans une granularité qui permet à Claude Code de générer une cellule à la fois.

### Section 1 — Préparation et imports
- **1.1** Imports Python (json, time, datetime, pandas, snowflake, openpyxl)
- **1.2** Configuration Snowflake (constantes : account, warehouse, database, schema)
- **1.3** Configuration générale (chemins de fichiers, paramètres)

### Section 2 — Lecture de la taxonomie produits
- **2.1** Ouvrir et lire `categories_cdiscount.json`
- **2.2** Vérifier le contenu (afficher le nombre de catégories chargées)

### Section 3 — Interrogation Google Trends et stockage Snowflake
- **3.1** Préparation de la liste des mots-clés à interroger
- **3.2** Boucle d'interrogation Google Trends avec try/except (cœur du script)
- **3.3** Assemblage du DataFrame des mesures du jour
- **3.4** Connexion à Snowflake et saisie du mot de passe
- **3.5** Insertion bulk dans `MESURES_TRENDS` via `write_pandas`

### Section 4 — Lecture des ventes depuis Snowflake
- **4.1** Requête SELECT pour récupérer les 6 mois d'historique de ventes
- **4.2** Exploration rapide du DataFrame retourné

### Section 5 — Lecture de la météo depuis Snowflake
- **5.1** Requête SELECT pour récupérer les 6 mois d'historique météo
- **5.2** Exploration rapide du DataFrame retourné

### Section 6 — Calculs d'analyses et de corrélations
- **6.1** Requête SQL d'analyse comparative Trends (deltas vs moyenne 14 jours)
- **6.2** Calcul de la matrice "Signaux pricing" (écart Trends vs Ventes par sous-catégorie)
- **6.3** Calcul de la sensibilité météo (corrélation Pearson par sous-catégorie)
- **6.4** Détection des anomalies (seuils glissants sur les ventes)
- **6.5** Calcul des horizons prédictifs (corrélation avec lag)

### Section 7 — Génération du rapport Excel multi-onglets
- **7.1** Ouverture d'un `pd.ExcelWriter` sur `rapport_trends_YYYY-MM-DD.xlsx`
- **7.2** Génération de l'onglet 1 "Signaux pricing"
- **7.3** Génération de l'onglet 2 "Sensibilité météo"
- **7.4** Génération de l'onglet 3 "Anomalies à investiguer"
- **7.5** Génération de l'onglet 4 "Évolution Trends"
- **7.6** Génération de l'onglet 5 "Évolution des ventes"
- **7.7** Génération de l'onglet 6 "Horizons prédictifs"
- **7.8** Génération de l'onglet 7 "Météo brute"
- **7.9** Génération de l'onglet 8 "Données brutes"
- **7.10** Fermeture du writer et confirmation

### Section 8 — Clôture et démo automatisation
- **8.1** Fermeture de la connexion Snowflake
- **8.2** Affichage du récap final
- **8.3** (Démo formateur) Configuration Task Scheduler Windows pour automatisation

---

## 6. Les 8 onglets du rapport Excel — détail du contenu

### Onglet 1 — 🎯 Signaux pricing
**Le money slide pour Loïc.** Matrice 2×2 des sous-catégories selon l'évolution Trends et l'évolution des ventes sur les 30 derniers jours.

| | Ventes ↑ | Ventes → ou ↓ |
|---|---|---|
| **Trends ↑** | ✅ Cohérent | 🔴 **Demande non convertie** (action pricing à la baisse) |
| **Trends → ou ↓** | 🟡 Sur-performance (pricing potentiellement à la hausse) | 🟢 Cohérent |

Colonnes attendues : `SOUS_CATEGORIE`, `evolution_trends_pct`, `evolution_ventes_pct`, `quadrant`, `recommandation`.

Trier par priorité d'action (quadrant rouge en haut).

### Onglet 2 — 🌦️ Sensibilité météo
Pour chaque sous-catégorie, coefficient de corrélation Pearson entre :
- Ventes journalières et température
- Ventes journalières et précipitations

Colonnes : `SOUS_CATEGORIE`, `correlation_temperature`, `correlation_precipitations`, `interpretation`.

Identifier les catégories `|correlation| > 0.5` comme **météo-sensibles** et les afficher en tête.

### Onglet 3 — 🚨 Anomalies à investiguer
Liste des **jours x produits** où les ventes ont été anormalement élevées ou basses (>1.5x ou <0.5x la moyenne sur 7 jours glissants). Pour chaque anomalie, afficher le contexte :

Colonnes : `DATE_VENTE`, `PRODUIT`, `quantite`, `moyenne_7j`, `ratio`, `valeur_trends_ce_jour`, `temperature`, `precipitations`, `hypothese`.

### Onglet 4 — 📊 Évolution Trends
Pour chaque sous-catégorie, valeurs Google Trends agrégées sur plusieurs fenêtres temporelles :

Colonnes : `SOUS_CATEGORIE`, `moyenne_7j`, `moyenne_30j`, `moyenne_90j`, `moyenne_180j`, `evolution_30j_vs_90j`.

### Onglet 5 — 💰 Évolution des ventes
Pour chaque sous-catégorie, ventes agrégées par mois sur 6 mois.

Colonnes : `SOUS_CATEGORIE`, `ventes_mois_1`, `ventes_mois_2`, ..., `ventes_mois_6`, `evolution_pct`.

### Onglet 6 — 🔮 Horizons prédictifs
Analyse de lag Trends → Ventes. Pour chaque sous-catégorie, on teste plusieurs décalages (lag 0, 7, 14, 21, 30 jours) et on identifie celui qui maximise la corrélation.

Colonnes : `SOUS_CATEGORIE`, `lag_optimal_jours`, `correlation_max`, `interpretation`.

### Onglet 7 — 🌡️ Météo brute
Dump complet de la table `METEO_HISTORIQUE` pour exploration libre.

### Onglet 8 — 📁 Données brutes
Dump complet de la table `VENTES` pour exploration libre.

---

## 7. Stack technique imposée

- **Python 3.13.13** (venv `myenv` dans `C:\formation_python\`)
- **pandas** pour la manipulation des données
- **pytrends 4.9.2** pour interroger Google Trends — indice d'intérêt 0-100 par mot-clé
  (`build_payload` + `interest_over_time`). Tire **`lxml`** comme dépendance.
- **snowflake-connector-python[pandas]** pour Snowflake (avec pyarrow)
- **openpyxl** pour la génération Excel multi-onglets
- **json**, **time**, **warnings**, **datetime**, **getpass** (standard library)

Filet de résilience : un **snapshot CSV** (`snapshot_trends_secours.csv`) pré-téléchargé sert de
repli quand Google rate-limite (HTTP 429), afin que la cellule produise toujours les 30 mesures.

---

## 8. Configuration Snowflake

- **Compte** : `LAWHABL-JB80530`
- **Base** : `FORMATION_DB`
- **Schéma** : `PUBLIC`
- **Tables cibles** :
  - `MESURES_TRENDS` (1530+ lignes pré-alimentées, INSERT autorisé)
  - `VENTES` (~21 600 lignes pré-alimentées, SELECT seulement)
  - `METEO_HISTORIQUE` (181 lignes pré-alimentées, SELECT seulement)
- **Warehouse** : `COMPUTE_WH`
- **Rôle des stagiaires** : `FORMATION_STAGIAIRE`
- **Users stagiaires** : `STAGIAIRE_1` à `STAGIAIRE_10`, mot de passe `Formation2026!`

---

## 9. Schémas des 3 tables Snowflake

### `MESURES_TRENDS`
```
ID INTEGER AUTOINCREMENT PRIMARY KEY
DATE_MESURE DATE NOT NULL
CATEGORIE VARCHAR(100) NOT NULL
SOUS_CATEGORIE VARCHAR(100) NOT NULL
MOT_CLE VARCHAR(200) NOT NULL
VALEUR_INTERET INTEGER NOT NULL
CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
```

### `VENTES`
```
ID INTEGER AUTOINCREMENT PRIMARY KEY
DATE_VENTE DATE NOT NULL
CATEGORIE VARCHAR(100) NOT NULL
SOUS_CATEGORIE VARCHAR(100) NOT NULL
PRODUIT VARCHAR(200) NOT NULL
QUANTITE INTEGER NOT NULL
PRIX_UNITAIRE DECIMAL(10, 2) NOT NULL
CHIFFRE_AFFAIRES DECIMAL(12, 2) NOT NULL
CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
```

### `METEO_HISTORIQUE`
```
ID INTEGER AUTOINCREMENT PRIMARY KEY
DATE_METEO DATE NOT NULL UNIQUE
TEMPERATURE_MOYENNE DECIMAL(5, 2) NOT NULL
PRECIPITATIONS_MM DECIMAL(6, 2) NOT NULL
ENSOLEILLEMENT_HEURES DECIMAL(4, 2) NOT NULL
CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
```

**Important** : toutes les colonnes sont en **MAJUSCULES** (convention Snowflake). Pour insérer un DataFrame, utiliser `write_pandas(..., quote_identifiers=False)`.

---

## 10. Résilience attendue — gestion d'erreurs

L'appel à `pytrends` peut échouer pour plusieurs raisons : **rate limit Google (HTTP 429)** quand on enchaîne trop d'appels depuis la même IP, réseau coupé, format de réponse modifié.

Pattern à implémenter pour chaque mot-clé :

```python
try:
    # Tentative d'interrogation Google Trends pour ce mot-cle
    client_trends.build_payload([mot_cle], geo='FR', timeframe='today 3-m')
    df_interet = client_trends.interest_over_time()
    valeur = int(df_interet[mot_cle].iloc[-1])
except Exception as erreur:
    # En cas d'echec, on logge et on met le mot-cle de cote (repli snapshot ensuite)
    print(f"Echec pour '{mot_cle}' : {erreur}")
    valeur = None
```

Deuxième ligne de défense : les mots-clés en échec sont **complétés depuis le snapshot de secours**
(`snapshot_trends_secours.csv`), si bien que le script ne plante jamais et produit toujours 30 mesures.

**Aucune** opération de lecture externe (Google Trends) ou écriture (Snowflake INSERT, Excel) ne doit se faire sans try/except.

---

## 11. Conventions de code

- **Tous les commentaires en français SANS ACCENTS** (encoding cp1252 Windows)
- **Un commentaire au-dessus de chaque bloc logique** expliquant ce qu'il fait
- **Pas de commentaires triviaux** (`x = 5  # on assigne 5 a x`)
- **Privilégier les commentaires explicatifs** ("on calcule la moyenne mobile sur les 14 derniers jours, equivalent d'un AVG OVER en SQL")
- **Noms de variables explicites en français** : `mesures_du_jour`, `df_ventes`, `mot_de_passe`, `taxonomie`
- **Pas de chaînage de méthodes** : une instruction par ligne
- **Snowflake colonnes MAJUSCULES** : utiliser `quote_identifiers=False` dans `write_pandas`
- **Credentials JAMAIS en clair** : utiliser `getpass.getpass()` pour saisie au runtime

---

## 12. Pièges connus à éviter

- **Encoding cp1252** : commentaires Python sans accents impérativement
- **Colonnes MAJUSCULES Snowflake** : `write_pandas(..., quote_identifiers=False)`
- **Rate limit Google Trends** : 1-2 secondes de `time.sleep()` entre chaque appel
- **Credentials Snowflake en clair** : JAMAIS. Utiliser `getpass.getpass()`
- **DataFrame vide après filtrage** : vérifier `len(df) > 0` avant `write_pandas`
- **Comparaison de strings sensible à la casse** : normaliser via `.str.lower().str.strip()` si jointure avec données externes
- **`pd.read_sql_query` retourne dates en datetime** : penser à faire `.dt.date` si on veut juste la date

---

## 13. Mode d'emploi pour Claude Code en formation

### Étape 1 — Lecture initiale du TP
Le stagiaire demande à Claude Code :
> *« Lis le fichier `TP_GOOGLE_TRENDS.md` qui décrit le besoin métier. »*

### Étape 2 — Génération du pseudo-code section par section
Le stagiaire demande à Claude Code :
> *« Génère le pseudo-code en français de la Section 1 (Préparation et imports). Découpe-le en petites portions claires correspondant aux sous-sections 1.1, 1.2, 1.3. »*

Claude Code écrit le pseudo-code dans une cellule du notebook.

### Étape 3 — Génération du code Python sous chaque portion
Le stagiaire demande à Claude Code :
> *« Sous chaque portion de pseudo-code, écris le code Python correspondant. Garde le pseudo-code en commentaires au-dessus. »*

### Étape 4 — Test de la cellule
Le stagiaire exécute la cellule, vérifie l'output, et corrige avec Claude Code si nécessaire.

### Étape 5 — Passage à la section suivante
On répète pour les sections 2, 3, ..., 8.

### Règles d'or pour Claude Code

1. **Référer à ce fichier** pour vérifier le style attendu, les pièges, les contraintes
2. **Une portion à la fois** (5 à 15 lignes maximum)
3. **Commenter en français sans accents** chaque ligne ou groupe logique
4. **Toujours envelopper les sources externes** dans try/except
5. **Snowflake : agrégations et calculs côté serveur** dès que possible
6. **Ne pas inventer** de fonctionnalités non listées dans les 8 sections
7. **Pour `pytrends`** : ne PAS activer le retry interne (`retries=`/`backoff_factor=`) — incompatible
   avec urllib3 2.x (`TypeError: method_whitelist`). Gérer le 429 par try/except + repli snapshot.

Si une demande sort de ce périmètre ou semble ambiguë, demander confirmation au formateur avant de coder.

---

## 14. Démo finale — Automatisation avec Task Scheduler (Section 8)

Une fois le notebook complet et fonctionnel, le formateur fait une **démo de 15-20 minutes en clôture** pour montrer comment automatiser l'exécution.

### Scénario de la démo

Le formateur partage son écran et :

1. Ouvre le **Task Scheduler Windows** (`taskschd.msc`)
2. Crée une nouvelle tâche basique :
   - **Action** : "Démarrer un programme"
   - **Programme** : `C:\formation_python\myenv\Scripts\python.exe`
   - **Arguments** : `C:\analyse_google_trends\analyse_trends.py`
   - **Démarrer dans** : `C:\analyse_google_trends\`
3. Planifie la tâche :
   - Tous les **lundis et jeudis** à **8h00**
   - (Ou tous les jours, tous les 3 jours, etc. — montrer la flexibilité)
4. Lance la tâche manuellement pour vérifier qu'elle fonctionne
5. Explique : *« Désormais, Loïc reçoit son rapport Excel à 8h05 chaque lundi et jeudi, sans intervention humaine. C'est ça la vraie valeur ajoutée de Python pour vous. »*

### Note technique pour Task Scheduler

Pour que la tâche fonctionne sans intervention humaine, le mot de passe Snowflake doit être stocké de manière sécurisée (variable d'environnement Windows, fichier `.env`, ou key-pair authentication). Cette partie n'est **pas démontrée en formation** (sortirait du périmètre). À mentionner comme cas post-formation.

---

## 15. Lien avec les cas Raphaël (post-formation)

Ce TP est massivement réutilisable pour l'équipe de Raphaël Combasson. Les **patterns** que les stagiaires repartent avec :

| Pattern du TP | Cas d'usage métier Raphaël |
|---|---|
| Boucle sur API externe + gestion d'erreurs | API Google Analytics, API internes |
| `write_pandas()` insertion bulk Snowflake | Ingestion de données dans l'entrepôt |
| Requêtes SQL côté serveur avec CTE | Tous les reportings internes |
| Génération Excel multi-onglets | Tous les rapports pour managers métier |
| Calcul de corrélation Pearson | Croisement de N'importe quelle source |
| Détection d'anomalies (seuils glissants) | Détection de fraude, monitoring opérationnel |
| Analyse de lag | Identification d'indicateurs avancés |
| Task Scheduler | Automatisation de tout rapport récurrent |

C'est un **kit de productivité** pour data analyst.

---

## 16. Structure finale du projet sur disque

```
C:\analyse_google_trends\
├── TP_GOOGLE_TRENDS.md                ← ce fichier
├── categories_cdiscount.json          ← taxonomie produits
├── analyse_trends.ipynb               ← le notebook à construire en formation
└── rapport_trends_YYYY-MM-DD.xlsx     ← généré à chaque exécution
```

Les scripts de seeding (`create_tables.sql`, `seeding_trends.py`, `seeding_meteo.py`, `seeding_ventes.py`) sont à utiliser **une seule fois en amont** par le formateur et ne sont pas redistribués aux stagiaires.
