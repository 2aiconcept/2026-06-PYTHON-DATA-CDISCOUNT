# TP Google Trends — Détection des nouveautés shopping France

> Fichier de cadrage à lire AVANT toute génération de code. Ce TP s'inscrit dans une formation Python Data Cdiscount.

---

## 1. Le contexte métier

**Loïc Sutel** est responsable pricing chez Cdiscount. Il gère les prix de centaines de produits et a besoin de détecter, le plus tôt possible, les produits qui montent en tendance pour ajuster sa stratégie pricing en anticipation (et pas en réaction).

Aujourd'hui il fait ce travail à la main : il scrolle Google Trends, regarde les actualités, croise avec ses dashboards internes. C'est lent et il manque les signaux faibles. Sa demande : un script Python qui sort chaque matin **les nouveaux mots-clés qui émergent dans Google Trends catégorie shopping France**, triés par volume de recherche, en évitant de remontrer ceux des jours précédents.

C'est le cas d'usage type d'un radar concurrentiel automatisé que personne n'a le temps de tenir manuellement.

---

## 2. L'utilisateur final du code

Le code généré sera lu, exécuté, modifié et réutilisé par des **data analysts Cdiscount, débutants complets en Python**. Ils ont suivi une formation Python Data de 4 jours. Ils sont à l'aise en SQL et Excel mais découvrent Python. Ils utilisent un notebook Jupyter dans VS Code.

**Conséquences pour le code :**

- Code **basique uniquement**, niveau débutant
- Pas de constructions avancées (pas de list comprehensions imbriquées, pas de lambda complexes, pas de décorateurs, pas d'async/await, pas de classes sauf si vraiment nécessaire)
- Privilégier la **lisibilité absolue** à la concision
- Une instruction = une ligne (pas d'enchaînement type `df.dropna().reset_index().sort_values(...)` sur une seule ligne)
- Les analogies **SQL/Excel** sont bienvenues dans les commentaires

---

## 3. Le pipeline cible — ce que le script doit faire

Le script déroule les étapes suivantes, dans cet ordre :

1. **Récupérer les trends actuels** : interroger Google Trends pour la zone géographique France, catégorie shopping, sur les 7 derniers jours (168 heures). On récupère environ 400 trends bruts.

2. **Charger l'historique** : lire un dossier `historique/` contenant 6 à 8 fichiers JSON, chacun représentant les trends d'un jour précédent (snapshots).

3. **Faire la différence** : retirer de la liste actuelle tout ce qui apparaissait déjà dans l'un quelconque des snapshots précédents. Équivalent SQL : `WHERE trend NOT IN (...)`. Équivalent Excel : un anti-RECHERCHEV pour ne garder que les valeurs absentes de la table de référence.

4. **Trier par trafic décroissant** : sur ce qui reste (les vraies nouveautés), trier par volume de recherche, du plus fort au plus faible.

5. **Garder le top 25** : limiter le résultat aux 25 trends les plus significatifs.

6. **Afficher le résultat** dans le notebook (DataFrame pandas).

7. **Sauvegarder le snapshot du jour** : ajouter au dossier `historique/` un nouveau fichier JSON avec la date du jour, contenant les trends récupérés à l'étape 1. Ainsi demain, ce qu'on a vu aujourd'hui devient à son tour de l'historique.

---

## 4. Stack technique imposée

- **Python 3.13.13** (venv `myenv` dans `C:\formation_python\`)
- **pandas** pour la manipulation des données
- **trendspyg 0.4.3** pour interroger Google Trends — fonction clé : `download_google_trends_csv(geo='FR', hours=168, category='shopping')`. Cette lib dépend de Chrome installé sur le poste (headless browser)
- **json** (standard library) pour lire/écrire les snapshots
- **os** + **pathlib** (standard library) pour gérer les chemins de fichiers
- **datetime** pour timestamper le snapshot du jour

Aucune autre dépendance externe.

---

## 5. Résilience attendue — gestion d'erreurs

L'appel à `trendspyg` peut échouer pour plusieurs raisons : rate limit Google, Chrome qui plante, réseau coupé, format de réponse modifié. **C'est inacceptable en production** : Loïc ne doit pas voir le script échouer un jour sans recours.

Pattern à implémenter :

```python
try:
    # Tentative de telechargement depuis Google Trends
    df_trends = download_google_trends_csv(geo='FR', hours=168, category='shopping')
except Exception as erreur:
    # Fallback : on charge le snapshot CSV de secours pre-telecharge
    print(f"Echec du telechargement live : {erreur}")
    print("Bascule sur le snapshot CSV de secours.")
    df_trends = pd.read_csv("snapshot_secours.csv")
```

Le fichier `snapshot_secours.csv` est pré-téléchargé en amont par le formateur et placé à la racine du projet.

**Aucune** opération de lecture externe (Google Trends, lecture JSON, écriture JSON) ne doit se faire sans try/except.

---

## 6. Style de commentaires

- **Tous les commentaires en français SANS ACCENTS** (la console Windows utilise l'encoding cp1252 qui peut faire planter les `é`, `è`, `à`, etc.)
- **Un commentaire au-dessus de chaque bloc logique** expliquant ce qu'il fait en français simple
- **Pas de commentaires triviaux** (pas de `x = 5  # on assigne 5 a x`)
- **Privilégier les commentaires explicatifs** ("on retire les trends deja vus les jours precedents — equivalent d'un EXCEPT en SQL")

---

## 7. Structure du projet sur disque

Voici l'arborescence du dossier de travail :

- `C:\formation_python\` (racine du projet)
  - `TP_GOOGLE_TRENDS.md` — ce fichier de cadrage
  - `tp_google-trends.ipynb` — le notebook à construire
  - `snapshot_secours.csv` — fourni par le formateur (fallback)
  - `historique/` — dossier des snapshots des jours précédents
    - `2026-06-03-trends.json`
    - `2026-06-04-trends.json`
    - `2026-06-05-trends.json`
    - `2026-06-06-trends.json`
    - `2026-06-07-trends.json`
    - `2026-06-08-trends.json`
    - `2026-06-09-trends.json`
    - (le snapshot du jour s'ajoutera ici à la fin de l'exécution)

---

## 8. Format des snapshots JSON

Chaque fichier `YYYY-MM-DD-trends.json` dans le dossier `historique/` a la structure suivante :

```json
{
  "date": "2026-06-03",
  "geo": "FR",
  "category": "shopping",
  "trends": [
    {"terme": "iPhone 17 Pro", "trafic": 125000},
    {"terme": "Robot piscine Dolphin", "trafic": 89000},
    {"terme": "Casque Sony WH-1000XM6", "trafic": 67000}
  ]
}
```

Pour l'étape "set-difference" : on extrait juste les termes (`item["terme"]`) de chaque snapshot historique, on les fusionne en un set Python `termes_deja_vus`, et on filtre le DataFrame actuel pour ne garder que les lignes dont `terme` n'est pas dans ce set.

---

## 9. Variables clés et sortie attendue

À la fin de l'exécution, le notebook doit contenir :

- Une variable `df_trends_aujourd_hui` : DataFrame pandas avec les ~400 trends récupérés (colonnes `terme`, `trafic`)
- Une variable `termes_deja_vus` : set Python contenant les termes vus dans les snapshots historiques
- Une variable `df_nouveautes` : DataFrame des trends nouveaux uniquement, triés par trafic décroissant
- Une variable `df_top_25` : DataFrame des 25 nouveautés les plus significatives — c'est le **résultat métier** affiché à Loïc

Et sur disque : un nouveau fichier `historique/YYYY-MM-DD-trends.json` créé avec la date du jour.

---

## 10. Pièges connus à éviter

- **Encoding cp1252** : les commentaires Python avec accents peuvent planter selon la console. Tout commentaire en français sans accents.
- **Comparaison de strings sensible à la casse** : `"iphone 17"` ≠ `"iPhone 17"`. Normaliser en `.lower().strip()` avant la set-difference si on veut éviter les faux positifs.
- **Lecture JSON corrompue** : un fichier mal formé fait planter `json.load`. Envelopper la lecture des snapshots dans une boucle avec try/except, et continuer même si un fichier est cassé.
- **Volume de retour de trendspyg** : la fonction renvoie un DataFrame qui peut avoir des colonnes différentes selon la version. Toujours vérifier `df_trends.columns` avant d'utiliser une colonne précise.
- **Fichier `snapshot_secours.csv` absent** : si même le fallback n'est pas disponible, afficher un message d'erreur clair et arrêter proprement, plutôt qu'une stack trace incompréhensible.

---

## 11. Volumétrie cible

Le notebook complet doit faire environ **70 lignes de code** réparties en 5 à 8 cellules. Chaque cellule = une étape logique du pipeline.

---

## 12. Pour aller plus loin (post-formation)

Une **variante avec flux RSS** est possible (~15 lignes) en remplaçant l'appel à `trendspyg` par une lecture du flux RSS de Google Trends. Démontre le découplage source/traitement : tout le reste du pipeline (différence, tri, sauvegarde) reste identique.

Une **variante avec IA** est possible (post-formation, démo formateur seul) : envoyer chaque nouveau trend à un LLM via `requests` pour le catégoriser automatiquement (catégorie produit Cdiscount, segment marché, urgence). **À ne pas implémenter dans ce TP.**

---

## 13. Mode d'emploi pour Claude Code

À chaque demande de génération de code dans le cadre de ce TP :

1. **Référer à ce fichier** pour vérifier le style attendu, les pièges connus, les contraintes
2. **Produire une portion à la fois** (5 à 15 lignes maximum)
3. **Commenter en français sans accents** chaque ligne ou groupe logique
4. **Toujours envelopper les sources externes** dans try/except
5. **Respecter exactement les noms de variables** définis en section 9
6. **Ne pas inventer de fonctionnalités** non listées dans le pipeline section 3

Si une demande sort de ce périmètre ou semble ambiguë, demander confirmation au formateur avant de coder.
