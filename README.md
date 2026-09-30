# Gemma 4 × PrestaShop : Réparation Autonome de Code Legacy par Rejeu Dynamique et QLoRA Frugal

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ba-rem26007/gemma4-legacy-replay/blob/main/notebook/colab_gemma4_evaluation.ipynb)
[![Live Protected Platform](https://img.shields.io/badge/Live_Showcase-kaggle.d1dev.fr-06b6d4)](https://kaggle.d1dev.fr)
[![Energy Metrology](https://img.shields.io/badge/Energy-1.9_Wh/bug-10b981)](https://kaggle.d1dev.fr/SOBRIETE.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Projet pour le hackathon officiel **Kaggle Gemma 4**.

**Question de recherche fondamentale** : Un modèle compact et ouvert de 4 milliards de paramètres (**Gemma 4 4B**) peut-il réparer du code d'entreprise complexe et hautement couplé (**PrestaShop 8/9**, PHP 8.1, Symfony 6, MySQL) lorsqu'il est guidé par un vérificateur d'exécution déterministe (rejeu de tests E2E Playwright sur conteneurs Docker réinitialisés) ?

---

## 1. En Bref & Chiffres Clés

* **Périmètre Évalué & Cartographie** :
  - **33 Bugs Réels Certifiés du Cœur PrestaShop** : Incidents fermés post-cutoff (9.1.x) strictement étanches, chacun validé par un oracle Playwright de bout en bout sur instance Docker `psbench2` réinitialisée.
  - **Cartographie d'Extensibilité Écosystème** : 42 dépôts majeurs de modules communautaires audités (hooks, CQRS, typage PHP 8.2+).
* **Conditions Expérimentales Étudiées (Vivier 33 Bugs)** :
  - `Condition A` (Baseline 31B) : Ticket seul brut → **39.0% (12.8 / 33)** (moyenne sur 4 runs indépendants).
  - `Condition R` (RAG Few-Shot 31B) : Ticket + 2 exemples similaires → **39.0% (+0.0 pt)**.
  - `Condition C` (Glossaire Auto 31B) : Ticket + glossaire métier contextuel → **39.4% (13.0 / 33)**.
  - `Condition B` (Replay Test 31B) : Ticket + feedback dynamique Playwright → **45.5% (+6.5 pts, 15 / 33)**, **0 régression**.
  - `Condition O` (Borne Haute 31B) : Ticket + verdict direct de l'oracle → **48.5% (+9.8 pts, 16 / 33)**, **2 régressions**.
  - `Condition A-4B` (MoE 26B) : Modèle `gemma-4-26b-a4b-it` (~4B active) → **15.2% (5 / 33)**.
  - `Condition E` (LoRA Frugal 4B) : Modèle dense `gemma-4-e4b-it` spécialisé via `ChunkedLossTrainer` → **12.1% (4 / 33)**, **1 régression**.
* **Note sur les architectures** : A-4B et E utilisent des modèles de base différents (MoE vs dense). Il ne s'agit pas d'une ablation LoRA pure.
* **Frugalité Énergétique Métrologique** : **1,9 Wh par bug tenté** (soit ≈ 15,7 Wh par bug résolu en Condition E) mesuré à 100 ms sur Nvidia Tesla T4 via `nvidia-smi` (33x à 55x inférieur par tentative aux clusters H100, 4x à 6x par bug résolu).
* **Budget Réel** : **0,00 €** d'API propriétaire récurrente (`runs/_budget.json`).

---

## 2. Volume de Données Injectées & Évolution du Corpus

1. **Données d'Entraînement & Plan d'Amélioration** ([`docs/PLAN_AMELIORATION.md`](docs/PLAN_AMELIORATION.md)) :
   - **Historique v15** : 585 trajectoires préparées, mais seules **89 avaient été retenues après tokenisation** suite à la limite de 2 048 tokens et à des fenêtres de code trop larges ([`docs/AUDIT_PHASE1.md`](docs/AUDIT_PHASE1.md)).
   - **Corpus Compact v2** : [`trajectories/train_compact.jsonl`](trajectories/train_compact.jsonl) génère **660 trajectoires certifiées** par patch Git en mémoire. Avec un fenêtrage affiné (`WINDOW=8`, `MAX_LINES=50`), **641 trajectoires tiennent sous 4 096 tokens (97,1% de rétention)**, multipliant par **$7{,}2\times$** le volume réellement entraînable ([`docs/RAPPORT_PHASE2.md`](docs/RAPPORT_PHASE2.md)).
   - **Reprise après Erreur** : [`trajectories/train_recovery.jsonl`](trajectories/train_recovery.jsonl) intègre **17 trajectoires multi-tours d'auto-apprentissage** (erreur d'oracle $\to$ correction $\to$ succès), 100% sans fuite du test set ([`docs/RAPPORT_PHASE5.md`](docs/RAPPORT_PHASE5.md)).
   - **Architecture Frugale** : Micro-chunks différentiables de **256 tokens** via `ChunkedLossTrainer` (VRAM totale réduite de 28.4 à 13.8 Go = −51%). Adaptateur final de **134 Mo** (`adapter_model.safetensors`, SHA256: `fac3f1af...`).
2. **Données Injectées à l'Inférence (Contexte au tour par tour)** :
   - **Localisation par pertinence (`windows_ranked`)** : Classement par densité de symboles (regex mot entier, stacktraces) au lieu de l'ordre linéaire du fichier, évitant de saturer le budget sur les licences en tête de fichier ([`docs/RAPPORT_PHASE4.md`](docs/RAPPORT_PHASE4.md)).
   - Fenêtre ciblée de **1 500 à 3 500 tokens** (très inférieure aux 8 192 tokens de Gemma 4).
   - Feedback d'erreur d'assertion Playwright : ~200 à 500 tokens.

---

## 3. Documents Maîtres & Spécifications

* **[RAPPORT_GLOBAL.md](docs/RAPPORT_GLOBAL.md)** : Rapport scientifique et technique exhaustif all-in-one (52+ KB, 11 sections, incluant le Writeup officiel Kaggle en anglais).
* **[PLAN_DE_TESTS.md](docs/PLAN_DE_TESTS.md)** : Cahier de recette intégral des 42 bugs du Cœur et des 42 modules tiers, pyramide en 5 niveaux, grille d'audit Kaggle.
* **[MODULES_TIERS.md](docs/MODULES_TIERS.md)** : Répertoire d'architecture et benchmark d'extensibilité des 42 modules communautaires.
* **[colab_gemma4_evaluation.ipynb](notebook/colab_gemma4_evaluation.ipynb)** : Notebook Google Colab interactif (GPU T4 gratuit, rejeu #40971, graphiques Pareto et tests statistiques).
* **Plateforme Web Démonstrateur** : `https://kaggle.d1dev.fr/rapport` (accès restreint pendant la mise au point).

---

## 4. Démarrage Rapide & Reproductibilité Clé en Main

### 1. Rejouer l'évaluation sur le bug emblématique #40971 (LogoUploader)
```bash
# 1. Préparer l'instance Docker déterministe (port 8082 psbench2)
PSB=2 bash bench/checkout.sh 40971 pre

# 2. Exécuter l'agent Gemma 4 (4B LoRA) en local / offline
python3 agent/run.py --bugs 40971 --condition E

# 3. Évaluer le patch généré avec l'oracle Playwright et les sondes HTTP FO/BO
python3 bench/eval.py 40971
```

### 2. Recalculer instantanément les métriques et tableaux officiels (sans modèle payant)
```bash
python3 bench/results.py
```

### 3. Clause « Zero Proprietary AI Policy » & Intégrité
* **100% Modèles Ouverts & Données Réelles** : Aucun modèle propriétaire fermé (OpenAI GPT-4, Anthropic Claude) n'a été utilisé pour distiller des tokens ou créer des données synthétiques. L'ensemble des 585 trajectoires d'apprentissage provient exclusivement de PRs humaines historiques mergées sur PrestaShop.
* **Fonctionnement Offline** : L'adaptateur de 134 Mo (`training/lora_final/extracted/adapter_model.safetensors`) s'exécute en local sans aucun accès internet sortant actif.
* **Coût Récurrent** : 0,00 € vérifié dans `runs/_budget.json`.

---

## 5. Structure du Dépôt

```
bench/select.py        Sélection des bugs (GitHub PrestaShop)
bench/checkout.sh      Conteneur Docker, état pre / post / patch (port 8082 psbench2)
bench/replay/          Tests Playwright de replay (un dossier par bug)
bench/analyze.py       Catalogue d'incidents (ticket, résolution, symboles) → catalog.jsonl
bench/qualify.py       Parcours / difficulté, split TEST/TRAIN → data/bugs_*.csv
bench/eval.py          Évalue un patch (anti-régression HTTP 200 + oracle binaire)
bench/test_pool.py     Vivier TEST 9.1.x post-cutoff → data/bugs_test.csv
agent/flow.py          Déroulé fixe (localiser → lire fenêtré → éditer → tester)
agent/run.py           Agent Gemma (API standard OpenAI-compatible), traces → runs/
training/chunked_loss.py Trainer Hugging Face micro-chunks 256 tokens (baisse 51% VRAM)
trajectories/          Chemins d'apprentissage vérifiés (train.jsonl, self.jsonl)
docs/RAPPORT_GLOBAL.md Document maître de synthèse (52+ KB, Writeup officiel en anglais)
docs/PLAN_DE_TESTS.md  Cahier de recette officiel (42 bugs Cœur + 42 Modules tiers)
docs/MODULES_TIERS.md  Répertoire d'extensibilité sur 42 modules de l'écosystème
notebook/resultats.ipynb Notebook Kaggle officiel avec frontière de Pareto et test McNemar
```
