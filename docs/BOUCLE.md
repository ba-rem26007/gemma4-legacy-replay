# Boucle d'auto-apprentissage — rendement (Gemma 4 31B seul)

Régénéré par `python3 bench/loop_stats.py`.

## Étape 1 — oracles écrits par Gemma (validés : échoue avant correctif, passe après)

| Mode | Validés | Échecs | Erreurs | Taux |
|---|---|---|---|---|
| ui | 0 | 6 | 0 | 0% |
| explore | 0 | 4 | 0 | 0% |
| php | 17 | 23 | 0 | 42% |

Oracles validés : #35587, #36082, #36123, #36662, #36807, #36875, #36905, #37191, #37589, #37747, #37877, #37955, #37970, #37996, #38168, #38341, #38417

## Étape 2 — agent Gemma avec l'oracle comme retour (condition O, TRAIN)

| Bug | Run | Résolu (oracle) |
|---|---|---|
| #35587 | 20260927-011259-O | oui |
| #36082 | 20260927-003701-O | oui |
| #36123 | 20260926-222343-O | oui |
| #36662 | 20260926-234331-O | oui |
| #36807 | 20260926-220642-O | non |
| #36875 | 20260926-224923-O | oui |
| #36905 | 20260926-223141-O | oui |
| #37191 | 20260926-221333-O | non |
| #37589 | 20260926-212516-O | oui |
| #37747 | 20260926-205706-O | non |
| #37877 | 20260926-200233-O | non |
| #37955 | 20260926-195641-O | oui |
| #37970 | 20260926-201731-O | oui |
| #37996 | 20260926-203717-O | non |
| #38168 | 20260926-193740-O | oui |
| #38341 | 20260926-193601-O | non |
| #38417 | 20260926-184142-O | oui |

## Étape 3 — chemins acceptés (`trajectories/self_paths.py`)

`9 chemins → trajectories/self.jsonl  {'hors_fichiers_officiels': 1, 'non_resolu': 6, 'hors_fonctions_officielles': 1, 'ok': 9}`

Garde-fous : verdict réévalué, éditions limitées aux fichiers du correctif officiel (anti-contournement),
blocs SEARCH/REPLACE reproduisant exactement le patch, < 8 000 tokens, aucun bug TEST.
