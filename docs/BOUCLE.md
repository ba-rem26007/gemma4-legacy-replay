# Boucle d'auto-apprentissage — rendement (Gemma 4 31B seul)

Régénéré par `python3 bench/loop_stats.py`.

## Étape 1 — oracles écrits par Gemma (validés : échoue avant correctif, passe après)

| Mode | Validés | Échecs | Erreurs | Taux |
|---|---|---|---|---|
| ui | 0 | 5 | 0 | 0% |
| explore | 0 | 4 | 0 | 0% |
| php | 2 | 3 | 0 | 40% |

Oracles validés : #38341, #38417

## Étape 2 — agent Gemma avec l'oracle comme retour (condition O, TRAIN)

| Bug | Run | Résolu (oracle) |
|---|---|---|
| #38341 | 20260926-190632-O | non |
| #38417 | 20260926-184142-O | oui |

## Étape 3 — chemins acceptés (`trajectories/self_paths.py`)

`0 chemins → /home/elrems/kaggle/runs/_self_stats.jsonl  {'hors_fichiers_officiels': 1, 'non_resolu': 1}`

Garde-fous : verdict réévalué, éditions limitées aux fichiers du correctif officiel (anti-contournement),
blocs SEARCH/REPLACE reproduisant exactement le patch, < 8 000 tokens, aucun bug TEST.
