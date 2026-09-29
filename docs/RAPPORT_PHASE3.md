# Rapport d'Exécution Phase 3 — Matrice d'Ablation Factorielle E4B (2x2)

> **Document produit dans le cadre du plan d'amélioration (`docs/PLAN_AMELIORATION.md`, Phase 3)**  
> **Date** : 29 septembre 2026  
> **Auteur** : Antigravity & Rémi Soubeyrand  
> **Statut** : Validé — Protocole et harnais factoriel 2x2 prêts pour exécution

---

## 1. Objectifs & Cadre Scientifique

La comparaison historique entre `Condition A-4B` et `Condition E` souffrait d'un biais d'architecture majeur mis en lumière par l'audit Phase 1 :
* `Condition A-4B` utilisait en réalité `gemma-4-26b-a4b-it` (modèle sparse MoE de 26 milliards de paramètres avec ~4B actifs et 30 couches).
* `Condition E` utilisait `gemma-4-e4b-it` (modèle dense pur de 4 milliards de paramètres et 42 couches) combiné à notre adaptateur LoRA.

Pour **isoler mathématiquement l'effet du LoRA**, la Phase 3 établit un plan factoriel complet $2 \times 2$ sur le **même modèle dense** `google/gemma-4-e4b-it` :

$$\text{Taux de Résolution } Y = \beta_0 + \beta_{\text{LoRA}} \cdot X_{\text{LoRA}} + \beta_{\text{Replay}} \cdot X_{\text{Replay}} + \gamma \cdot (X_{\text{LoRA}} \times X_{\text{Replay}})$$

---

## 2. Définition de la Matrice 2x2

| Identifiant | Modèle de Base | Adaptateur LoRA ($X_1$) | Rejeu Dynamique ($X_2$) | Rétro-action (Retries) | Question Scientifique Isolée |
|:---|:---:|:---:|:---:|:---:|---|
| **E4B-base** | `gemma-4-e4b-it` | ❌ Non ($0$) | ❌ Non ($0$) | $0$ | Quel est le niveau plancher intrinsèque du 4B dense ? |
| **E4B-replay** | `gemma-4-e4b-it` | ❌ Non ($0$) | ✅ Oui ($1$) | $2$ | Quel est l'apport du rejeu seul sans fine-tuning ? |
| **E4B-lora** | `gemma-4-e4b-it` | ✅ Oui ($1$) | ❌ Non ($0$) | $0$ | Quel est l'apport de l'adaptateur LoRA seul ? |
| **E4B-lora-replay** | `gemma-4-e4b-it` | ✅ Oui ($1$) | ✅ Oui ($1$) | $2$ | Y a-t-il une synergie multiplicative ($\gamma > 0$) ? |

### Constantes Contrôlées et Verrouillées
Toutes les conditions partagent strictement :
1. **Règles métier** : injection de `rules_prestashop.py` et du glossaire métier (`glossary_hits`).
2. **Budgets de tokens** : 4 096 tokens en entrée, 2 048 tokens en génération.
3. **Moteur de recherche** : fenêtres de code indexées par `windows_ranked()`.
4. **Oracles de validation** : oracles E2E Playwright cachés et smoke tests de non-régression sur base MariaDB remise à zéro.

---

## 3. Harnais d'Exécution Implémenté

Le script d'orchestration officiel a été implémenté dans [`bench/matrix_e4b.py`](../bench/matrix_e4b.py) :
* Support des exécutions séquentielles ou ciblées via `--configs E4B-base E4B-replay E4B-lora E4B-lora-replay`.
* Mode de simulation et validation statistique (`--dry-run`).
* Décomposition automatique des effets principaux ($\beta_{\text{LoRA}}$, $\beta_{\text{Replay}}$) et du terme d'interaction ($\gamma$).

---

## 4. Livrables Associés

1. **Script du Harnais Expérimental** : [`bench/matrix_e4b.py`](../bench/matrix_e4b.py).
2. **Le présent Rapport Méthodologique** : [`docs/RAPPORT_PHASE3.md`](RAPPORT_PHASE3.md).

---

## 5. Transition vers la Phase 4 (Amélioration de la Localisation)

Le banc d'ablation étant opérationnel, nous enchaînons directement sur la **Phase 4** pour intégrer la localisation par symboles et les fenêtres classées par pertinence (`windows_ranked`) au cœur de `agent/flow.py` et mesurer le gain sur le ciblage des fichiers.
