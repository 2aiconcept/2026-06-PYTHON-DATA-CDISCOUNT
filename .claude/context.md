# Contexte de la formation Python Data Cdiscount — fichier de reprise

> Ce fichier permet à **toute nouvelle conversation Claude Code** de reprendre la rédaction de la formation
> exactement là où on s'est arrêté, avec les mêmes conventions. Il est importé automatiquement par le
> `CLAUDE.md` à la racine du projet.
>
> **À la fin de chaque chapitre / sous-chapitre terminé, ajouter une ligne dans la section
> « Journal d'avancement » en bas de ce fichier.**

---

## 1. Le projet

Formation **Python Data de 4 jours pour Cdiscount**, en présentiel, pour **10 stagiaires** data analysts /
pricing managers : **débutants complets en Python**, mais à l'aise en **SQL** et **Excel** (passerelles
pédagogiques principales).

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
8. **Commentaires de code SANS accents** (encoding console Windows cp1252). La prose Markdown garde ses accents ;
   seuls les commentaires/`print` dans les cellules de code s'écrivent sans accent (« reflexe defensif », pas
   « réflexe défensif »). Important surtout pour les scripts exécutés hors notebook (J4 cas d'usage).
9. **Code des cas d'usage J4 : réutilisable TEL QUEL en prod.** Hormis les **connexions** (credentials Snowflake,
   chemins de répertoires partagés, URLs internes), aucune ligne ne doit être réécrite pour passer du TP à la prod.
   Code idiomatique et robuste : `try/except` sur toute source externe, fallbacks explicites, fonctions réutilisables.

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
- **Quiz 2** : ❌ PAS dans le notebook — Sébastien le fait directement dans le **guide HTML** via l'app Claude (décision prise en fin de chapitre 4).

---

## 8. Plan du chapitre 4 (notebook `04_jour3.ipynb`)

| Sous-section | Contenu | État |
|---|---|---|
| **4.1 Pandas approfondi** | 4.1.1 merge (4 types, jouet) · 4.1.2 merge réel (référentiel → marge) · 4.1.3 concat (+ piège `.append()`) · 4.1.4 dates avancées (`to_datetime`, `.dt`, `Timedelta`) | ✅ TERMINÉ |
| **4.2 Snowflake** | 4.2.1 connexion (getpass, cas A/B) · 4.2.2 `read_sql_query` + merge catalogue · 4.2.3 règle d'or « filtrer côté serveur » (chronométré) · 4.2.4 bonnes pratiques (`with`, secrets, `LIMIT`, `close`) | ✅ TERMINÉ |
| **4.3 Lire Excel et JSON** | 4.3.1 `pd.read_excel` (multi-feuilles, `sheet_name`) · 4.3.2 `pd.read_json` (liste plate, fichier local + callout `requests`). | ✅ TERMINÉ |
| **4.4 Nettoyage rapide** | 4.4.1 `drop_duplicates` · 4.4.2 `isna`/`fillna`/`dropna` · 4.4.3 `astype` (table « sale » fil rouge). Bonus : `round` banquier vs `Decimal` ROUND_HALF_UP. | ✅ TERMINÉ |
| **4.5 TP S1 Reporting multi-sources** | Rapport par catégorie : Snowflake (CA agrégé serveur) + Excel (objectifs/responsables) + JSON (avis) → `merge`×3 + colonnes calculées. Énoncé **guidé pas à pas** + correction 1 cellule. | ✅ TERMINÉ |
| **4.6 Récap chapitre 4** | ❌ PAS dans le notebook — Sébastien le fait directement dans le **guide HTML** via l'app Claude. | ⏭️ HORS NOTEBOOK |

---

## 9. Cas d'usage J4 (nouveau bloc — notebook à créer)

> Le contenu « chapitres » (J1→J3 = chapitres 1 à 4) est **terminé dans le guide HTML**. Le J4 est un bloc à part :
> deux **cas d'usage métier** + un **Quiz 3 final**. Nouveau prompt cadre fourni par Sébastien (mémorisé ici).

**Structure du J4 (timing pour MOI, jamais écrit dans les énoncés) :**
- **Matin** : Cas 1 — **Google Trends** (remonté par Loïc Sutel, pricing).
- **Après-midi** : Cas 2 — **Task Scheduler Windows** (remonté par Aurore via Raphaël). Boucle narrative :
  « on a écrit le script le matin → on l'automatise pour qu'il tourne seul tous les jours à 8h ».
- **Clôture** : **Quiz 3** final de synthèse (5 QCM : pandas, Snowflake, APIs, nettoyage, automatisation), 10-15 min.

**⚠️ On ne produit QUE ces 2 cas (Google Trends + Task Scheduler).** Les 4 cas bonus sont gérés par Sébastien
en autonomie post-formation — **NE PAS les produire** : L1 Météo France (`requests`), S3 Prophet + LLM, A3 Microsoft
(`pywin32` Excel/Outlook), A1 sFTP (`paramiko`).

**Règles de production spécifiques J4** (en plus des conventions §2-§3) :
- **Code réutilisable tel quel en prod** (sauf connexions) — voir convention §2.9.
- **Robustesse** : `try/except` sur toute source externe, fallbacks explicites, commentaires FR sans accents.
- **Format par cas** : 1 cellule Markdown (énoncé **guidé pas-à-pas**, style TP 4.5) + 1 cellule Code (solution
  d'un seul tenant, **vérifiée en bash avant livraison**) + **sortie verrouillée** (je donne la vraie sortie à coller
  dans le guide) + **décodage à l'oral** (4-6 points, dans la conversation, hors notebook).
- **Avant chaque cas : demander à Sébastien ce qu'il veut produire en premier.** Ne pas tout lancer d'un coup.

**Cas 1 — Google Trends (détail technique) :**
- Lib : **`trendspyg==0.4.3`** (alternative moderne à pytrends) ; dépend de **Chrome headless**.
- Pipeline cible : `download_google_trends_csv(geo='FR', hours=168, category='shopping')` → ~400 trends bruts
  → **set-difference** vs historique JSON (snapshots précédents) pour détecter les « nouveaux » (≈ `EXCEPT` SQL)
  → top 25 trié par trafic → sauvegarde du nouveau snapshot dans l'historique.
- Résilience : `try/except` + **snapshot CSV de secours** pré-téléchargé par Sébastien avant le J3.
- **Historique simulé** : 6-8 snapshots JSON crédibles, fabriqués **par Sébastien en amont**.
- Volumétrie script v1 CSV : ~70 lignes. **Variante bonus** (si temps) : ~15 lignes via le **flux RSS** Google Trends
  (découplage source/traitement).

**Cas 2 — Task Scheduler Windows (détail) :**
- Automatiser l'exécution quotidienne du script Google Trends **sans droits admin** (tâches utilisateur suffisent).
- Pointer le **`python.exe` du venv** + chemin absolu du script ; gérer le **working directory** (fichiers I/O au bon
  endroit) ; tester exécution manuelle puis planifiée ; variantes logs / fréquence / conditions de déclenchement.

**Stack / environnement J4 :** venv DSI `myenv` (Python 3.13.13) avec `trendspyg`, `paramiko`, `pywin32` + libs data.
Stagiaires sans droits admin Windows.

---

## 10. Journal d'avancement (mettre à jour à chaque chapitre terminé)

- **Chapitre 3 (`03_jour1.ipynb`)** — TERMINÉ. Inclut le mini-projet 3.8 (5 questions métier, tableau de bord,
  export Excel simple + formaté openpyxl, mini-défi Excel français 3.8.9).
- **4.1 Pandas approfondi** — TERMINÉ (4.1.1 → 4.1.4). Variantes bonus produites : jours/mois/dates en français
  (mapping `.dt.dayofweek` + `strftime("%d/%m/%Y")`).
- **4.2 Snowflake** — TERMINÉ (4.2.1 → 4.2.4). Connexion opérationnelle, warning filtré, démo « filtrer côté serveur »
  validée (réel : 20 000 lignes / 2,89 s → 2 422 lignes / 0,15 s pour l'Île-de-France). Variante `with` autonome fournie.
- **4.3 Lire Excel et JSON** — TERMINÉ. Nouveaux fichiers SOURCE générés par `generer_objectifs_et_avis.py` :
  `objectifs_commerciaux_2026.xlsx` (feuilles `Objectifs` + `Responsables`) et `avis_clients_api.json` (liste plate,
  12 produits, note/nb_avis). JSON volontairement local (callout `requests` « pour aller plus loin » non exécuté).
- **4.4 Nettoyage rapide** — TERMINÉ (4.4.1 → 4.4.3) sur une table « sale » créée en mémoire (`commandes_brutes` :
  1 doublon, 2 `NaN`, `prix_unitaire` en texte). Bonus livré : différence `round()` (arrondi banquier) vs fonction
  `arrondi_scolaire` (`Decimal` + `ROUND_HALF_UP`), + écart Excel/pandas sur les `.5`.
- **4.5 TP S1 Reporting multi-sources** — TERMINÉ. Rapport par catégorie validé sur données RÉELLES Snowflake.
  Objectifs Excel **recalibrés** sur l'échelle de `HISTORIQUE_VENTES` (CA réel : Entrée de gamme 2 151 599 €,
  Standard 1 570 515 €, Premium 2 580 704 € ; total 6 302 818 €). Objectifs retenus : 2 000 000 / 1 600 000 /
  2 700 000 → statut Atteint / Manqué / Manqué. Énoncé livré en **2 versions** (standard + très guidé pas à pas, le
  guidé étant la version retenue). Correction en 1 cellule (`with` + agrégation serveur + merge×3 + `np.where`).
  ⚠️ Le bloc « repli sans réseau » de la correction référence `ca_categorie_secours.csv` / `referentiel_secours.csv`
  qui **n'ont pas été générés** (lignes commentées) — à produire si on veut un vrai plan B hors-ligne.

### ⏸️ ON S'EST ARRÊTÉ ICI
**Chapitre 4 (notebook `04_jour3.ipynb`) TERMINÉ** (4.1 → 4.5). Le **récap 4.6** et le **Quiz 2** ne seront PAS
faits dans le notebook : Sébastien les rédige directement dans le **guide HTML** via l'app Claude.

**Restes / pistes éventuelles :**
- **Commit/push** en attente pour rendre les fichiers récupérables dans le ZIP GitHub : `objectifs_commerciaux_2026.xlsx`
  (exception ajoutée au `.gitignore` car `*.xlsx` était ignoré), `avis_clients_api.json`, `generer_objectifs_et_avis.py`,
  `.gitignore`, `04_jour3.ipynb`. Rappel sécurité : `account="LAWHABL-JB80530"` apparaît en clair dans le notebook
  (identifiant de compte, pas un mot de passe) — neutraliser si le repo devient public.
- Fichiers de secours CSV du TP 4.5 non générés (voir ci-dessus).
- **PROCHAINE ÉTAPE : bloc J4 — Cas d'usage (voir §9).** On commence par le **Cas 1 (Google Trends)**, mais
  **attendre que Sébastien dise quoi produire en premier** avant de lancer quoi que ce soit. Notebook J4 à créer
  (nom à convenir, ex. `05_jour4.ipynb`). Quiz 3 final à la fin.
