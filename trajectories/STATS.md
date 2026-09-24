# Chemins d'entraînement

Coupure : **2025-06-01**. TRAIN = 820 bugs, TEST = 187 bugs (catalogue `bench/catalog.jsonl`).

| Source | Chemins |
|---|---|
| reconstruit | 424 |
| auto | 0 (runs de l'agent à venir) |

Rejets : {'ok': 424, 'fichier_absent_recherche': 205, 'exclu_etancheite': 58, 'trop_long': 25, 'hors_format': 100, 'search_non_unique': 8}

Longueur estimée (tokens ≈ caractères / 3) : médiane 4039, max 7971, plafond 8000.
Chaque chemin est **vérifié** : ses blocs SEARCH/REPLACE reproduisent exactement le fichier du commit correctif.
Format identique à `agent/flow.py` (déroulé fixe, condition C). Entraînement : loss sur les tours `assistant` uniquement.
