# Démo 1 : chaîne de bout en bout (2026-09-24)

**Ce qui tourne** : bug réel PrestaShop → agent en déroulé fixe (localiser → lire → éditer → tester) → patch → PrestaShop en Docker au commit d'avant le correctif → test de rejeu Playwright → verdict.

## 1. Chaîne validée sans modèle (politique « reconstruit »)
Les réponses de l'agent sont celles du **chemin reconstruit** à partir du correctif officiel : c'est exactement le format d'entraînement.
Ce run prouve que le format, les outils, l'application du patch et l'évaluation fonctionnent de bout en bout.

```
python3 agent/run.py --bugs 35322 35902 --condition B --policy reconstruit
```

| Bug | Mots-clés (étape 1) | Fichier lu (étape 2) | Patch appliqué | Replay | Régression | Durée éval. |
|---|---|---|---|---|---|---|
| [#35322](https://github.com/PrestaShop/PrestaShop/pull/35322) frais de port HT/TTC (FO) | OrderDetailLazyArray, getShipping | src/Adapter/Presenter/Order/OrderDetailLazyArray.php | ✓ | ✓ corrigé | aucune | 9 s |
| [#35902](https://github.com/PrestaShop/PrestaShop/pull/35902) quantité minimale (FO) | ProductController, displayAjaxRefresh… | controllers/front/ProductController.php | ✓ | ✓ corrigé | aucune | ~15 s |

Trace complète de chaque tour (entrée, réponse, outil, résultat, temps) : `runs/20260924-233019-B/<pr>/trace.jsonl`, patch `patch.diff`, verdict `result.json`.

## 2. Données d'entraînement prêtes
- `trajectories/train.jsonl` : **424 chemins reconstruits vérifiés** (vivier TRAIN, avant la coupure provisoire au 2025-06-01). Chaque chemin reproduit exactement le fichier corrigé. Aucun modèle n'a servi à les produire.
- 58 bugs TRAIN exclus par le contrôle d'étanchéité (même fonction qu'un bug TEST) : `data/ETANCHEITE.md`.
- Fine-tuning QLoRA prêt pour ton GPU : `training/README.md`.

## 3. Avec Gemma 4 (dès que la clé est dans .env)
```
python3 agent/run.py --list-models                          # identifiant exact du modèle Gemma 4
python3 agent/run.py --bugs 35322 35902 --condition A --model <id>
python3 agent/run.py --bugs 35322 35902 --condition B --model <id>
```
A = ticket seul · B = + test de rejeu + retour d'exécution (2 essais de correction).

## Limites de cette démo
- Les 2 bugs sont en vivier **TRAIN** (2024) : il s'agit d'une démo de la chaîne, pas d'une évaluation. L'évaluation se fera sur le vivier TEST (9.x, après la coupure).
- Le test de rejeu a été écrit à la main ; la chaîne automatique de génération (phase 4) viendra ensuite.
- #35384 n'est pas reconstructible en l'état (bloc SEARCH ambigu) : il faut élargir le contexte.
