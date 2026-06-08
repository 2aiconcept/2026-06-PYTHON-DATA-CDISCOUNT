# Contexte de la formation Python Data Cdiscount — fichier de reprise

> Ce fichier permet à **toute nouvelle conversation Claude Code** de reprendre la rédaction de la formation
> exactement là où on s'est arrêté, avec les mêmes conventions. Il est importé automatiquement par le
> `CLAUDE.md` à la racine du projet.
>
> **À la fin de chaque chapitre / sous-chapitre terminé, ajouter une ligne dans la section
> « Journal d'avancement » en bas de ce fichier.**

---

## 1. Le projet

Formation **Python Data de 4 jours pour Cdiscount**, en présentiel, pour **4 stagiaires** data analysts /
responsables pricing : **débutants complets en Python**, mais avec un **solide socle SQL** (passerelle
pédagogique principale).

- **Formateur** : Sébastien Gueroult, 2AI Concept (dev front/back JS confirmé, débutant Python). Email : contact@2aiconcept.com
- **Client** : Loïc Sutel (pricing) et Raphaël Combasson (data analyst). Stagiaires identifiés : Soumaya, Aurore.
- **Livrable** : un guide HTML stagiaire (`guide_formation_python_data_v4.html`) + des notebooks Jupyter.

Le contenu des chapitres se rédige **cellule par cellule** dans des notebooks, validé au fur et à mesure
par Sébastien (il copie-colle les cellules dans le notebook puis dit « on enchaîne »).

---

## 2. Conventions pédagogiques INVIOLABLES

1. **Aucune analogie JavaScript.** Uniquement des analogies **SQL** et **Excel** (les stagiaires n'ont aucune base JS).
2. **Vouvoiement** dans la prose Markdown ; **tutoiement** dans les commentaires de code et les énoncés de TP.
3. **Aucune notion de timing de formation.** Bannir : « jour 1/2/3/4 », « J1 », « ce matin », « cet après-midi »,
   « demain », « hier », « début/fin de journée ». Utiliser des formulations neutres : « plus tôt dans la formation »,
   « à cette étape », « à venir », « dans les chapitres précédents/suivants ». Raison : protéger les stagiaires du
   stress si le formateur prend de l'avance ou du retard.
4. **Code 100 % copiable-collable** : uniquement du Python valide, qui tourne tel quel. Pas de prose, pas de `...`,
   pas de placeholder. Une variable construite ailleurs se signale **en commentaire dans le code**.
5. **Annoncer la sortie attendue** sous chaque cellule de code, **vérifiée numériquement** au préalable.
6. **Pas de Q&A violet pré-anticipées** dans le guide ; préférer des callouts « pour aller plus loin ».
7. **Toujours garder `.copy()`** après un filtre (`df[...].copy()`), même si pandas 3 (Copy-on-Write) le rend
   optionnel. Réflexe défensif + portabilité pandas 2. (Validé par Sébastien.)

---

## 3. Format de livraison des cellules (IMPÉRATIF)

Pour **chaque sous-section** de chapitre, livrer EXACTEMENT :

1. **UNE SEULE cellule Markdown** à copier-coller = théorie + énoncé + explications théoriques réunis.
   Jamais deux blocs Markdown séparés.
2. **UNE SEULE cellule Code** à copier-coller.
3. **Le déchiffrage du code (« ce qu'il faut retenir ») ET les points à souligner à l'oral** : écrits
   **normalement dans la conversation**, JAMAIS dans une cellule du notebook.

**Règle de présentation** : quand la cellule Markdown contient elle-même des blocs de code (```），l'entourer
d'une clôture à **4 backticks** (````) pour qu'elle reste UN seul bloc copiable (sinon les ``` internes la
coupent visuellement en deux).

Workflow : on livre une sous-section, Sébastien valide en disant « on enchaîne », puis on passe à la suivante.

---

## 4. Stack technique

- **Python 3.13.13** dans le venv **`myenv`** : `C:\formation_python\myenv\` →
  exécutable de vérification : `C:\formation_python\myenv\Scripts\python.exe` (**pandas 3.0.2**).
  ⚠️ Utiliser CE python pour vérifier les sorties. `env_formation` est en pandas 2.2.3 — NE PAS l'utiliser pour valider.
- **pandas 3.0.2** — breaking changes vs pandas 2 : `.append()` supprimé → `pd.concat()` ; PyArrow strings par
  défaut (dtype `str`) ; Copy-on-Write activé ; `to_datetime` renvoie `datetime64[us]` (et non `[ns]`).
- **snowflake-connector-python 4.4.0**, **openpyxl 3.1.5**, **matplotlib 3.10.9**, **requests 2.32.3**,
  **beautifulsoup4 4.12.3**, **Prophet 1.3.0** (chapitre ultérieur), + paramiko, pywin32, trendspyg.

---

## 5. Fichiers du projet `C:\formation_python\`

- `hello_data.ipynb` — validation environnement
- `03_jour1.ipynb` — chapitre 3 complet (jusqu'au mini-projet 3.8 inclus)
- `04_jour3.ipynb` — chapitre 4 **en cours de rédaction** (Pandas approfondi + Snowflake + multi-sources)
- `ventes_retours.csv` — 150 commandes Q1 2026 (UTF-8, `,`, point décimal, dates ISO). 12 produits, 3 catégories,
  8 régions. ~85 % Ventes / 15 % Retours.
- `ventes_retours_export_excel.csv` — mêmes données en format Excel français (cp1252, `;`, virgule décimale,
  dates JJ/MM/AAAA). **Généré par Claude** lors du chapitre 3.8.9.
- `generer_ventes_retours.py` — script de reproduction des CSV (seed=42).
- `test_env.py`, `test_snowflake.py` — tests de validation.

### Données de référence `ventes_retours.csv`
Colonnes : `id_commande, date, produit, categorie, prix_unitaire, quantite, statut, client_region`.
Résultats clés vérifiés (chapitre 3.8) : CA total ventes = **13 927,70 €** (128 ventes / 22 retours).

---

## 6. Snowflake — paramètres VALIDÉS et opérationnels

- **Account** : voir `.claude/secrets.local.md` (non versionné)
- **Démo formateur** : compte `ACCOUNTADMIN` — identifiants dans `.claude/secrets.local.md`
- **Stagiaires** : `STAGIAIRE_1` à `STAGIAIRE_10`, rôle `FORMATION_STAGIAIRE` — mot de passe commun dans `.claude/secrets.local.md`
- **Authenticator** : `password` (compte trial, pas de SSO) → saisie via `getpass.getpass()` au runtime
- **Warehouse** : `COMPUTE_WH` (X-Small, auto-suspend) — **Database** : `FORMATION_DB` — **Schema** : `PUBLIC`
- **Connexion entreprise future (Cdiscount)** : prévue en `authenticator="externalbrowser"` (SSO), laissée en
  commentaire « Cas B » dans la cellule de connexion 4.2.1.

### Tables (toutes lisibles par les stagiaires)
- **`CATALOGUE_PRODUITS`** (12 lignes) : `PRODUIT, CATEGORIE, PRIX_REVIENT, FOURNISSEUR, MARGE_CIBLE_PCT, DATE_REFERENCEMENT`
- **`FOURNISSEURS`** (3 lignes) : `CODE_FOURNISSEUR, NOM_COMMERCIAL, PAYS_ORIGINE, SCORE_QUALITE, DELAI_LIVRAISON_J`
- **`TAUX_TVA`** (3 lignes) : `CATEGORIE, TAUX_TVA`
- **`HISTORIQUE_VENTES`** (20 000 lignes) : `DATE_VENTE, PRODUIT, QUANTITE, CLIENT_REGION, PRIX_UNITAIRE`

### Pièges Snowflake rencontrés (et résolus)
- **MUST_CHANGE_PASSWORD** : un user fraîchement créé refuse la connexion connecteur tant que le mot de passe n'a
  pas été « dé-flaggé ». Fix admin : `ALTER USER STAGIAIRE_X SET PASSWORD='<voir secrets.local.md>' MUST_CHANGE_PASSWORD=FALSE;`
- **`getpass` dans VS Code** : la boîte de saisie apparaît **en haut au centre** de la fenêtre VS Code (pas sous la
  cellule). Ne pas cliquer ailleurs sinon la saisie est annulée et la cellule semble « bloquée ».
- **`UserWarning` pandas/SQLAlchemy** : `read_sql_query` avec le connecteur Snowflake (DBAPI2) affiche un warning
  bénin. On le filtre une fois en haut de la cellule connexion :
  `warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")`. (Ajouté par Sébastien.)
- **Colonnes en MAJUSCULES** : Snowflake renvoie les noms de colonnes en majuscules → normaliser avec
  `df.columns = df.columns.str.lower()` avant tout merge avec des données locales.

---

## 7. Décisions pédagogiques transverses (chapitre 4)

- **Jeu de données** : réutiliser au maximum le contexte `ventes_retours` que les stagiaires connaissent.
  Pour les jointures, mini-tables « jouet » (3-4 lignes) pour VOIR l'effet, puis cas réel.
- **Référentiel produits** créé en 4.1.2 = même structure que `CATALOGUE_PRODUITS` Snowflake (continuité narrative :
  « le référentiel tapé à la main, le voici pour de vrai dans le cloud » en 4.2.2).
- **Fil rouge du pattern** : `merge → filtre → colonne calculée → agrégation`. Le merge se branche EN AMONT de la
  chaîne `filtre → colonne calculée → agrégation` apprise au chapitre 3.
- **Ponts narratifs** : SQLite 3.6 → Snowflake 4.2 (même `read_sql_query`) ; CSV 3.7-3.8 → multi-sources 4.5.
- **Quiz 2** : à construire APRÈS le contenu du chapitre 4, pas avant.

---

## 8. Plan du chapitre 4 (notebook `04_jour3.ipynb`)

| Sous-section | Contenu | État |
|---|---|---|
| **4.1 Pandas approfondi** | 4.1.1 merge (4 types, jouet) · 4.1.2 merge réel (référentiel → marge) · 4.1.3 concat (+ piège `.append()`) · 4.1.4 dates avancées (`to_datetime`, `.dt`, `Timedelta`) | ✅ TERMINÉ |
| **4.2 Snowflake** | 4.2.1 connexion (getpass, cas A/B) · 4.2.2 `read_sql_query` + merge catalogue · 4.2.3 règle d'or « filtrer côté serveur » (chronométré) · 4.2.4 bonnes pratiques (`with`, secrets, `LIMIT`, `close`) | ✅ TERMINÉ |
| **4.3 Lire Excel et JSON** | `pd.read_excel` (multi-feuilles, `sheet_name`) · `pd.read_json` (réponse API aplatie). Volontairement basique. | ⏳ À FAIRE |
| **4.4 Nettoyage rapide** | `drop_duplicates`, `isna`/`fillna`/`dropna`, `astype`. Message : « 80 % du travail data = nettoyer ». | ⏳ À FAIRE |
| **4.5 TP S1 Reporting multi-sources** | Combiner table Snowflake + Excel local + JSON API en un rapport pandas. Mêmes 4 réflexes. Énoncé + correction + décodage. | ⏳ À FAIRE |
| **4.6 Récap chapitre 4** | Callout récap + tableau des outils + 4 réflexes data. | ⏳ À FAIRE |

---

## 9. Journal d'avancement (mettre à jour à chaque chapitre terminé)

- **Chapitre 3 (`03_jour1.ipynb`)** — TERMINÉ. Inclut le mini-projet 3.8 (5 questions métier, tableau de bord,
  export Excel simple + formaté openpyxl, mini-défi Excel français 3.8.9).
- **4.1 Pandas approfondi** — TERMINÉ (4.1.1 → 4.1.4). Variantes bonus produites : jours/mois/dates en français
  (mapping `.dt.dayofweek` + `strftime("%d/%m/%Y")`).
- **4.2 Snowflake** — TERMINÉ (4.2.1 → 4.2.4). Connexion opérationnelle, warning filtré, démo « filtrer côté serveur »
  validée (réel : 20 000 lignes / 2,89 s → 2 422 lignes / 0,15 s pour l'Île-de-France). Variante `with` autonome fournie.

### ⏸️ ON S'EST ARRÊTÉ ICI
Fin de **4.2 (Snowflake)**. **Prochaine étape : sous-section 4.3 (Lire Excel et JSON)**, à démarrer au format
habituel (1 cellule Markdown + 1 cellule Code + déchiffrage/points dans la conversation). Pour 4.3, on pourra
réutiliser `ventes_retours_export_excel.csv` / un nouvel Excel multi-feuilles à générer, et un petit JSON d'API
à fabriquer si besoin (à proposer à Sébastien avant de produire les cellules).
