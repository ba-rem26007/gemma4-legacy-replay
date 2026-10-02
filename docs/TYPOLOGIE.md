# Typologie des données d'entraînement (TRAIN uniquement)

Généré par `python3 trajectories/typology.py` (déterministe, motifs sur le correctif officiel `bench/diffs/<pr>.diff`).
Étiquettes multiples possibles (couches, natures) : les parts ne somment pas à 100 %.
**Règle : la composition se décide d'après TRAIN seul — la typologie des bugs TEST n'est pas regardée.**

Exemples : **592** ({'reconstruit': 569, 'gemma_self': 23}) ; vivier TRAIN de comparaison : 820 bugs du catalogue antérieurs au 2025-06-01.

### Couches touchées

| Étiquette | Exemples | Part |
|---|---|---|
| legacy_classes | 178 | 30% |
| symfony_bundle | 138 | 23% |
| js | 88 | 15% |
| symfony_adapter | 71 | 12% |
| legacy_controllers | 71 | 12% |
| autre | 53 | 9% |
| symfony_core | 47 | 8% |
| templates | 40 | 7% |
| config | 14 | 2% |
| admin_legacy | 11 | 2% |
| sql_install | 9 | 2% |

### Natures du correctif

| Étiquette | Exemples | Part |
|---|---|---|
| condition | 270 | 46% |
| autre | 188 | 32% |
| garde_null_vide | 110 | 19% |
| conversion_echappement | 94 | 16% |
| signature | 76 | 13% |
| traduction | 51 | 9% |
| requete_sql | 46 | 8% |
| multiboutique | 44 | 7% |
| template | 40 | 7% |
| formulaire_validation | 35 | 6% |
| prix_taxe | 32 | 5% |
| cache | 9 | 2% |
| hook | 6 | 1% |

### Taille (lignes modifiées)

| Étiquette | Exemples | Part |
|---|---|---|
| ≤5 | 289 | 49% |
| 6-20 | 207 | 35% |
| 21-60 | 76 | 13% |
| >60 | 20 | 3% |

- Correctifs **multi-fichiers** : 152 (26%) ; **croisés legacy + Symfony** : 15 (3%).

## Le jeu d'entraînement est-il représentatif du vivier TRAIN ?

### Couches

| Étiquette | Jeu d'entraînement (592) | Vivier TRAIN (820) | Écart |
|---|---|---|---|
| legacy_classes | 30% | 27% | +3 pts |
| symfony_bundle | 23% | 24% | -1 pts |
| js | 15% | 17% | -2 pts |
| legacy_controllers | 12% | 12% | +0 pts |
| symfony_adapter | 12% | 10% | +2 pts |
| autre | 9% | 12% | -3 pts |
| symfony_core | 8% | 8% | +0 pts |
| templates | 7% | 8% | -1 pts |
| config | 2% | 2% | +0 pts |
| admin_legacy | 2% | 6% | -4 pts |
| sql_install | 2% | 1% | +0 pts |

### Natures

| Étiquette | Jeu d'entraînement (592) | Vivier TRAIN (820) | Écart |
|---|---|---|---|
| condition | 46% | 45% | +0 pts |
| autre | 32% | 34% | -2 pts |
| garde_null_vide | 19% | 20% | -1 pts |
| conversion_echappement | 16% | 16% | -0 pts |
| signature | 13% | 13% | -0 pts |
| traduction | 9% | 10% | -2 pts |
| requete_sql | 8% | 7% | +1 pts |
| multiboutique | 7% | 7% | +0 pts |
| template | 7% | 8% | -1 pts |
| formulaire_validation | 6% | 6% | -0 pts |
| prix_taxe | 5% | 6% | -1 pts |
| cache | 2% | 2% | -0 pts |
| hook | 1% | 1% | +0 pts |

### Portée

| Étiquette | Jeu d'entraînement (592) | Vivier TRAIN (820) | Écart |
|---|---|---|---|
| multi_fichiers | 26% | 35% | -9 pts |
| croise | 3% | 4% | -1 pts |

## Lecture

- Un écart fort (± 10 pts) signale une catégorie sur- ou sous-représentée par la construction des chemins
  (`trajectories/reconstruct.py` : ≤ 3 fichiers lus, blocs SEARCH/REPLACE reproductibles, < 8 000 tokens).
- L'ordre d'entraînement reste aléatoire (mélange à chaque époque) ; l'équilibrage se fait par la composition.
