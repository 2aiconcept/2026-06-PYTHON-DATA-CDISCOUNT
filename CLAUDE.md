# CLAUDE.md — Formation Python Data Cdiscount

Ce projet est une **formation Python Data pour Cdiscount**, rédigée cellule par cellule dans des notebooks Jupyter.

**AVANT TOUTE CHOSE** : lis le fichier de contexte ci-dessous. Il contient les conventions inviolables, le format
de livraison des cellules, les paramètres Snowflake, le plan des chapitres et le point d'arrêt exact pour reprendre
la formation là où elle en est.

@.claude/context.md

---

## Rappel express (le détail est dans le contexte importé ci-dessus)

- **Format de livraison** : 1 cellule Markdown (théorie + énoncé) + 1 cellule Code, **les deux copiables-collables** ;
  le déchiffrage du code et les points à souligner à l'oral vont **dans la conversation**, pas dans le notebook.
- **Conventions** : analogies SQL/Excel uniquement (jamais JS) ; vouvoiement en prose, tutoiement en commentaires ;
  aucune mention de timing de formation ; code qui tourne tel quel ; sortie attendue annoncée et vérifiée.
- **Vérification des sorties** : exécuter avec `C:\formation_python\myenv\Scripts\python.exe` (pandas 3.0.2).
- **Workflow** : on livre une sous-section, Sébastien valide (« on enchaîne »), on passe à la suivante.
- **À la fin de chaque sous-chapitre terminé** : mettre à jour le « Journal d'avancement » et le point d'arrêt
  dans `.claude/context.md`.
