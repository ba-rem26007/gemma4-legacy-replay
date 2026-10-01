# Stratégie Unifiée Kaggle Gemma 4 : Main Track (129 Tâches) & Paper Track (12/11)

> **Document de Cadrage Officiel** — Basé sur les spécifications directes du harness de compétition Google/Kaggle, les contraintes matérielles (4× L4, 96 Go VRAM) et les 4 thèmes officiels du Paper Track.

---

## 1. Ce que les Spécifications Officielles Changent & Clarifient

| Paramètre | Spécification Officielle Confirmée | Impact & Décision Projet |
| :--- | :--- | :--- |
| **Modèle Obligatoire** | `gemma-4-31b-it-qat-w4a16-ct` (agent principal & sous-agents) | Les expérimentations 26B-A4B et vision tombent du Main Track. Le 31B QAT est l'unique cible d'inférence. |
| **Contexte Modèle** | 32K tokens (`max_model_len=32768`) | Abandon définitif des pistes de « contexte long 256K ». Priorité au fenêtrage chirurgical et à la compacité. |
| **Outils & Parsing** | `tool_call_parser='gemma4'`, `thinking_budget: 4096` | Natif dans le harness. Le thinking et les tool calls sont gérés en amont. |
| **Outil d'Édition** | `edit_file(old_string, new_string)` | **Transposition exacte à 100% de notre moteur SEARCH/REPLACE.** |
| **Format Soumission** | `submission.zip` avec `agent.yaml` (ADK), skills, prompts | Packaging au standard Google GenAI Agent Development Kit (ADK). |
| **Évaluation Leaderboard**| 129 tâches Python (FastAPI, etc.), max 12h offline sur 4× L4 | ~5,5 min par tâche. Exécution via `run_command` (pytest). |
| **Rôle du Paper Track** | Deadline 12/11. Documenter scientifiquement l'approche | Notre travail sur PrestaShop et le 4B E4B devient le cœur du papier académique. |

---

## 2. Le Coup de Maître : Alignement sur les 4 Thèmes Officiels du Paper Track

Notre projet ne perd rien de son travail antérieur ; au contraire, il coche **simultanément les 4 thèmes officiels** définis par Google :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LES 4 THÈMES DU PAPER TRACK                           │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. Tasks & Benchmarks         │ Le banc PrestaShop 9.1 (33 bugs réels       │
│                               │ post-cutoff, oracles Playwright, MariaDB)   │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Code Comprehension         │ L'analyse A vs B (apport du rejeu d'éxéc.)  │
│    & Replay Dynamics          │ sur les 129 tâches Python et PrestaShop     │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 3. Graph Reasoning            │ L'audit critique du graphe/embeddings du    │
│    (La Découverte en Or)      │ harness (similarité à 0.999, faillite RAG)  │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ 4. Tuning, Optimization       │ Chunked Cross-Entropy Loss (-51% VRAM),     │
│    & Self-Learning Bounds     │ et découverte du Reward Hacking (32% cheat) │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 3. L'Observation Majeure sur le Graphe & les Embeddings (Thème 3)

L'audit des logs du notebook officiel met en lumière une faille majeure de l'approche par graphe/embeddings standard fournie par l'organisation :
1. **Échec de Recherche Sémantique** : L'appel `search_similar_code("Server Sent Events")` renvoie **0 résultat**, forçant l'agent à se rabattre sur un `grep` classique.
2. **Effondrement de la Discrimination** : Les scores de similarité cosinus sont compressés entre **0,999 et 1,000** (y compris entre des tutoriels et le cœur d'un routeur FastAPI), rendant le reranking sémantique inopérant.
3. **Conséquence** : Des tâches échouent par **timeout** (10 appels d'outils stériles en 1 minute sans émettre de patch).
4. **Notre Valeur Ajoutée pour le Papier** : Présenter une comparaison quantitative rigoureuse entre *Recherche par Graphe/Embeddings* vs *Grep Lexical Structuré + Fenêtrage Pertinent* (`windows_ranked`). C'est exactement le type d'analyse que recherche le jury Google !

---

## 4. Plan d'Action Opérationnel (Ordre de Priorité)

### Phase 1 : Baseline Leaderboard (Main Track)
1. **Soumission de l'Agent Sample** : Soumettre le `submission.zip` de base fourni par Kaggle pour caler la pipeline et valider le score de référence sur les 129 tâches.
2. **Implémentation du Rejeu en Skill ADK** :
   - Configurer `agent.yaml` avec une skill qui appelle `run_command("pytest ...")` après chaque `edit_file`.
   - Transposer notre boucle séquentielle : si le test échoue, injecter la trace condensée et autoriser 2 reprises de correction.
3. **Mesure de l'Écart A vs B sur les 129 Tâches** :
   - Baseline A : `edit_file` à partir de la consigne seule.
   - Condition B : `edit_file` + exécution pytest + retry.

### Phase 2 : Papier Académique (Paper Track - Deadline 12/11)
1. **Structure du Papier** :
   - **Introduction** : La fracture entre le code unitaire isolé (SWE-bench) et le monde réel (PHP legacy, e-commerce, applications d'entreprise).
   - **Section Graphe vs Grep** : L'analyse métrologique des embeddings du harness (0.999 de similarité, timeouts).
   - **Section Rejeu Dynamique** : Résultats croisés sur les 129 tâches Python et sur les 33 bugs PrestaShop.
   - **Section Tasks & Benchmarks** : Documentation complète du benchmark PrestaShop (Playwright, Docker, snapshots SQL).
   - **Section Frugalité & Auto-apprentissage** :
     - Étude de cas Gemma 4 E4B (4,29 Go VRAM, 1,81 Wh par bug).
     - La méthode `ChunkedLossTrainer` (adaptation sobre de la cross-entropy par blocs).
     - La découverte du *Reward Hacking* (13/41 correctifs contournant les tests sans ancrage de commit).

---

## 5. Synthèse des Livrables

- `submission.zip` : L'agent officiel pour le Leaderboard Kaggle (Gemma 4 31B QAT + ADK + Skill de rejeu).
- `KAGGLE_FINAL_WRITEUP.md` : Le papier académique révisé, enrichi de l'analyse du graphe et des 129 tâches.
- `https://kaggle.d1dev.fr/rapport` : La vitrine et le démonstrateur public pérenne du benchmark.
