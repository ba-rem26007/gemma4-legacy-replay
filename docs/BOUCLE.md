# Boucle d'auto-apprentissage — rendement (Gemma 4 31B seul)

Régénéré par `python3 bench/loop_stats.py`.

## Étape 1 — oracles écrits par Gemma (validés : échoue avant correctif, passe après)

| Mode | Validés | Échecs | Erreurs | Taux |
|---|---|---|---|---|
| ui | 0 | 5 | 0 | 0% |
| explore | 0 | 4 | 0 | 0% |
| php | 6 | 6 | 0 | 50% |

Oracles validés : #37877, #37955, #37970, #38168, #38341, #38417

## Étape 2 — agent Gemma avec l'oracle comme retour (condition O, TRAIN)

| Bug | Run | Résolu (oracle) |
|---|---|---|
| #37877 | 20260926-200233-O | non |
| #37955 | 20260926-195641-O | oui |
| #37970 | 20260926-201731-O | oui |
| #38168 | 20260926-193740-O | oui |
| #38341 | 20260926-193601-O | non |
| #38417 | 20260926-184142-O | oui |

## Étape 3 — chemins acceptés (`trajectories/self_paths.py`)

`2 chemins → /home/elrems/kaggle/runs/_self_stats.jsonl  {'hors_fichiers_officiels': 1, 'non_resolu': 2, 'hors_fonctions_officielles': 1, 'ok': 2}`

Garde-fous : verdict réévalué, éditions limitées aux fichiers du correctif officiel (anti-contournement),
blocs SEARCH/REPLACE reproduisant exactement le patch, < 8 000 tokens, aucun bug TEST.
