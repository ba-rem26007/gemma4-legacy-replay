# Démo 1 : chaîne de bout en bout (2026-09-24)

**Ce qui tourne** : bug réel PrestaShop → agent en déroulé fixe (localiser → lire → éditer → tester) → patch → PrestaShop en Docker au commit d'avant le correctif → test de rejeu Playwright → verdict.

## 1. Chaîne validée sans modèle (politique « reconstruit »)
Les réponses de l'agent sont celles du **chemin reconstruit** à partir du correctif officiel : c'est exactement le format d'entraînement.
Ce run prouve que le format, les outils, l'application du patch et l'évaluation fonctionnent de bout en bout.

```
python3 agent/run.py --bugs 35322 35384 35902 --condition B --policy reconstruit
```

| Bug | Mots-clés (étape 1) | Fichier lu (étape 2) | Patch appliqué | Replay | Régression | Durée éval. |
|---|---|---|---|---|---|---|
| [#35322](https://github.com/PrestaShop/PrestaShop/pull/35322) frais de port HT/TTC (FO) | OrderDetailLazyArray, getShipping | src/Adapter/Presenter/Order/OrderDetailLazyArray.php | ✓ | ✓ corrigé | aucune | 9 s |
| [#35384](https://github.com/PrestaShop/PrestaShop/pull/35384) stock, recherche à 2 mots-clés (BO) | StockController, listProductsAction | src/PrestaShopBundle/Controller/Api/StockController.php | ✓ | ✓ corrigé | aucune | ~15 s |
| [#35902](https://github.com/PrestaShop/PrestaShop/pull/35902) quantité minimale (FO) | ProductController, displayAjaxRefresh… | controllers/front/ProductController.php | ✓ | ✓ corrigé | aucune | ~15 s |

Résultat : **3/3 corrigés, localisation 3/3, 0 régression** (run `runs/20260925-000132-B`, évaluations sérialisées par verrou). Trace complète de chaque tour (entrée, réponse, outil, résultat, temps) : `runs/20260925-000132-B/<pr>/trace.jsonl`, patch `patch.diff`, verdict `result.json`.

## 2. Données d'entraînement prêtes
- `trajectories/train.jsonl` : **569 chemins reconstruits vérifiés** (vivier TRAIN, avant la coupure provisoire au 2025-06-01). Chaque chemin reproduit exactement le fichier corrigé. Aucun modèle n'a servi à les produire.
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

## 4. Premier run réel : Gemma 4 31B (API Google AI Studio), 2026-09-25
Un seul run par bug et par condition, température 0,2, graine non fixable par l'API. **Non significatif statistiquement** : le kit prévoit 3 runs.

| Bug | A (ticket seul) | B (+ replay + 2 corrections) |
|---|---|---|
| #35322 frais de port HT/TTC | ✓ corrigé | ✗ bonne ligne trouvée, mais logique inversée, puis page cassée pendant les corrections |
| #35384 stock, recherche à 2 mots-clés | ✗ trouve `Api/StockController` mais tourne en rond en relectures | ✗ idem (8 tours, aucune édition) |
| #35902 quantité minimale | — (quota API 429) | ✗ bon fichier, correction de `getProductMinimalQuantity` jamais suffisante (attendu 1, reçu 3) |
| **Total** | **1/2** | **0/3** (localisation 2/3) |

Runs : `runs/20260925-053823-A`, `runs/20260925-055234-B` (traces complètes tour par tour).

### Ce que ce premier run apprend
- **La chaîne tient** : patchs de Gemma appliqués, rejoués et jugés automatiquement, sans intervention.
- **Le vérificateur attrape les correctifs faux ou trop larges.** Dans un run précédent, Gemma forçait la quantité minimale à 1 partout et le replay l'a détecté (attendu 3 avant l'ajout au panier).
- **La localisation reste le verrou** (#35384) : c'est l'hypothèse Q2, à tester avec la condition C (glossaire).
- **La variance est forte** (#35322 corrigé en A, raté en B) : les 3 runs par condition et un bench de 30 à 40 bugs sont indispensables.
- **Le quota gratuit de l'API** ne suffit pas pour le bench complet : les runs officiels passeront en local (Ollama sur le PC), ce qui permet aussi de fixer la graine.

### Défauts du harness corrigés pendant la démo
Budget de tokens mangé par la réflexion `<thought>` de Gemma (4k → 16k), recherche de contenu cassée (parsing `git grep -o`), déroulé sans retour arrière (2 permis désormais), `chown -R` lent dans `checkout.sh`, évaluations concurrentes (verrou), 429 (attente de `retryDelay`).
