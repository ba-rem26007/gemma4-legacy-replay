# Chemins d'entraînement

Coupure : **2025-06-01**. TRAIN = 820 bugs, TEST = 187 bugs (catalogue `bench/catalog.jsonl`).

| Source | Chemins |
|---|---|
| reconstruit | 573 |
| auto | 0 (runs de l'agent à venir) |

Rejets : {'ok': 573, 'exclu_etancheite': 58, 'fichier_absent_recherche': 56, 'trop_long': 30, 'hors_format': 93, 'non_reproductible': 4, 'search_non_unique': 6}

Longueur estimée (tokens ≈ caractères / 3) : médiane 3581, max 7945, plafond 8000.
Chaque chemin est **vérifié** : ses blocs SEARCH/REPLACE reproduisent exactement le fichier du commit correctif.
Format identique à `agent/flow.py` (déroulé fixe, condition C). Entraînement : loss sur les tours `assistant` uniquement.
