# Gemma 4 × PrestaShop : Réparation Autonome de Code Legacy par Rejeu Dynamique et QLoRA Frugal

Projet pour le hackathon officiel **Kaggle Gemma 4**.

**Question de recherche fondamentale** : Un modèle compact et ouvert de 4 milliards de paramètres (**Gemma 4 4B**) peut-il réparer du code d'entreprise complexe et hautement couplé (**PrestaShop 8/9**, PHP 8.1, Symfony 6, MySQL) lorsqu'il est guidé par un vérificateur d'exécution déterministe (rejeu de tests E2E Playwright sur conteneurs Docker réinitialisés) ?

---

## 1. En Bref & Chiffres Clés

* **Double Périmètre Évalué** :
  - **42 Bugs Réels du Cœur PrestaShop** : 33 incidents fermés post-cutoff (9.1.x) strictement étanches + 9 incidents cœur réévalués.
  - **42 Modules Tiers de l'Écosystème** : Analyse d'extensibilité sur 8 domaines e-commerce avec cas d'étude pilote validé sur `ps_facetedsearch` (PR #1340).
* **Conditions Expérimentales Étudiées** :
  - `Condition A` (Baseline 31B) : Ticket seul brut → **41.2% (17.3/42)**.
  - `Condition R` (RAG Few-Shot 31B) : Ticket + 2 exemples similaires → **41.2% (+0.0 pt)**.
  - `Condition B` (Replay Test 31B) : Ticket + feedback dynamique Playwright → **52.4% (+11.2 pts, 22.0/42)**.
  - `Condition O` (Borne Haute 31B) : Ticket + verdict direct de l'oracle → **57.1% (+15.9 pts, 24.0/42)**.
  - `Condition A-4B` (Ablation Base 4B) : Gemma 4 4B Zero-Shot sans LoRA → **4.8% (2.0/42)** (42.8% de rejets syntaxiques).
  - `Condition E` (LoRA Frugal 4B) : Gemma 4 4B spécialisé via `ChunkedLossTrainer` → **19.0% (+14.2 pts, 8.0/42)**.
* **Preuve Causale de l'Adaptation LoRA** : Le LoRA apporte un gain net isolé de **+14.2 à +16.6 points**, réduisant le taux d'erreur de syntaxe de 42.8% à 14.3%.
* **Frugalité Énergétique Métrologique** : **1.9 Wh par bug** mesuré à 100 ms sur Nvidia Tesla T4 via `nvidia-smi` (33x à 55x inférieur aux clusters H100).
* **Budget Réel** : **0,00 €** d'API propriétaire récurrente (`runs/_budget.json`).

---

## 2. Volume de Données Injectées (Data Footprint)

1. **Données d'Entraînement (Fine-Tuning QLoRA)** :
   - **585 trajectoires de résolution vérifiées** (`trajectories/train.jsonl` : 569 PR historiques reconstruites + 25 auto-chemins `self.jsonl`).
   - **~2,21 millions de tokens** au total (moyenne de 3 889 tokens par exemple).
   - **3 époques complètes** (~6,6 millions de tokens vus).
   - Micro-chunks différentiables de **256 tokens** via `ChunkedLossTrainer` (chute de 94% du pic VRAM, < 300 Mo).
   - Adaptateur final autonome de **134 Mo** (`adapter_model.safetensors`).
2. **Données Injectées à l'Inférence (Contexte au tour par tour)** :
   - Fenêtre ciblée de **1 500 à 3 500 tokens** (très inférieure aux 8 192 tokens de Gemma 4).
   - `windows()` : extraction de ±20 lignes autour des mots-clés, plafonné à 120 lignes / fichier (évite d'injecter des classes de 5 000 lignes).
   - Feedback d'erreur d'assertion Playwright : ~200 à 500 tokens.

---

## 3. Documents Maîtres & Spécifications

* **[RAPPORT_GLOBAL.md](docs/RAPPORT_GLOBAL.md)** : Rapport scientifique et technique exhaustif all-in-one (52+ KB, 11 sections, incluant le Writeup officiel Kaggle en anglais).
* **[PLAN_DE_TESTS.md](docs/PLAN_DE_TESTS.md)** : Cahier de recette intégral des 42 bugs du Cœur et des 42 modules tiers, pyramide en 5 niveaux, grille d'audit Kaggle.
* **[MODULES_TIERS.md](docs/MODULES_TIERS.md)** : Répertoire d'architecture et benchmark d'extensibilité des 42 modules communautaires.
* **Plateforme Web Démonstrateur** : `https://kaggle.d1dev.fr/rapport` (Basic Auth : `d1dev` / `d1dev`, bouton 1-clic pour copie intégrale).

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
training/chunked_loss.py Trainer Hugging Face micro-chunks 256 tokens (baisse 94% VRAM)
trajectories/          Chemins d'apprentissage vérifiés (train.jsonl, self.jsonl)
docs/RAPPORT_GLOBAL.md Document maître de synthèse (52+ KB, Writeup officiel en anglais)
docs/PLAN_DE_TESTS.md  Cahier de recette officiel (42 bugs Cœur + 42 Modules tiers)
docs/MODULES_TIERS.md  Répertoire d'extensibilité sur 42 modules de l'écosystème
notebook/resultats.ipynb Notebook Kaggle officiel avec frontière de Pareto et test McNemar
```
