# Récapitulatif Stratégique Complet & Plan d'Action Opérationnel
## Compétition Kaggle : "Google – The Gemma 4 Developer Agent"
### Double Voie : Main Track (Leaderboard 129 Tâches) & Paper Track (Deadline 12/11)

---

## 1. Les Règles Officielles Confirmées & Contraintes Techniques

| Paramètre | Spécification Officielle | Impact Concret sur le Projet |
| :--- | :--- | :--- |
| **Modèle Imposé** | `gemma-4-31b-it-qat-w4a16-ct` (obligatoire pour l'agent principal et tout sous-agent) | Les pistes MoE 26B-A4B et Vision tombent du Main Track. Le 31B QAT est l'unique cible d'inférence. |
| **Fenêtre de Contexte** | **32 768 tokens** (`max_model_len=32768`) | Abandon définitif du contexte long 256K. Priorité absolue au fenêtrage chirurgical (`windows_ranked`). |
| **Tool Calling & Thinking** | Natif dans le harness (`tool_call_parser='gemma4'`, `thinking_budget: 4096`) | Standardisé par Google. Inutile de coder un parser custom. |
| **Outil d'Édition** | `edit_file(old_string, new_string)` | **Transposition directe à 100% de notre moteur SEARCH/REPLACE.** |
| **Environnement d'Éval** | 129 tâches Python (FastAPI, etc.), max 12h offline, instance 4× Nvidia L4 (96 Go VRAM) | Temps alloué : ~5,5 minutes par tâche en moyenne. |
| **Format de Soumission** | `submission.zip` avec `agent.yaml` (Google ADK), skills, prompts, adapters | Respect strict des conventions Vertex AI / Google GenAI Agent Development Kit. |
| **Réglementation LoRA** | PEFT `.safetensors` autorisés (`max_lora_rank=128`, `max_loras=8`) | Un adaptateur par agent possible. Attention : l'entraînement sur 4× L4 consomme le double de quota. |
| **Paper Track** | Deadline **12 novembre 2026** (12/11) | Vise à documenter scientifiquement son approche pour la compétition. |

---

## 2. Le Repositionnement Gagnant de Nos Travaux

Aucun de nos développements passés n'est perdu ; ils sont réaffectés là où ils ont le plus fort impact :

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ARCHITECTURE DU PROJET                                 │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│         MAIN TRACK (LEADERBOARD)          │          PAPER TRACK (12 NOVEMBRE)         │
│         Compétition d'Ingénierie          │             Rigueur Académique             │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • Modèle : Gemma 4 31B QAT                │ • Cœur : Rejeu Dynamique (A vs B)          │
│ • Cible : 129 tâches Python (FastAPI)     │ • Benchmark : PrestaShop 9.1 (Legacy BDD)  │
│ • Skill ADK : Boucle de rejeu pytest      │ • Graphe : Analyse de faillite embeddings  │
│ • Format : edit_file(SEARCH/REPLACE)      │ • Frugalité : Gemma 4 E4B + Chunked Loss   │
│ • Objectif : Maximiser le PASS@1          │ • Éthique : Découverte du Reward Hacking   │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 3. L'Observation Majeure sur le Graphe & les Embeddings (Thème Officiel Graph Reasoning)

Les logs de notre propre notebook d'exploration révèlent une **défaillance structurelle** du système de graphe fourni par le harness officiel :

1. **Faillite de la Recherche Sémantique** :
   - L'appel `search_similar_code("Server Sent Events")` renvoie **0 résultat**, obligeant l'agent à se rabattre sur un simple `grep`.
2. **Effondrement de la Discrimination des Embeddings** :
   - Les scores de similarité cosinus sont artificiellement écrasés entre **0,999 et 1,000**, même entre un composant d'infrastructure critique (`APIRouter.__init__`) et un tutoriel utilisateur.
3. **Pénalité Critique sur le Score** :
   - La Tâche 1 du benchmark échoue par **timeout** (10 appels d'outils stériles en 1 minute sans émettre la moindre modification de code).
4. **Opportunité pour le Paper Track** :
   - Démontrer métrologiquement que la recherche par graphe / embeddings denses souffre d'un manque de sélectivité sur les symboles de code par rapport à un *grep lexical structuré avec fenêtrage pertinent par densité de symboles* (`windows_ranked`). C'est exactement le type d'audit technique que le jury Google valorise.

---

## 4. Priorités Opérationnelles & Calendrier d'Exécution

```
  SEMAINE 1 : MAIN TRACK (LEADERBOARD)
  ├── 1. Soumettre le baseline agent.yaml (sample) pour caler le score de référence
  ├── 2. Implémenter la Skill ADK de Rejeu Dynamique (run_command -> pytest -> retry)
  └── 3. Mesurer le différentiel A vs B sur les 129 tâches Python
  
  SEMAINE 2 : EXPÉRIMENTATIONS & LORA
  ├── 4. Extraire les métriques d'échec du Graphe vs Grep (similarité 0.999, timeouts)
  └── 5. Si le quota de calcul 4× L4 le permet : Fine-tuning QLoRA du 31B QAT
  
  SEMAINE 3 & 4 : PAPER TRACK (DEADLINE 12/11)
  └── 6. Rédaction finale du papier intégrant les 4 thèmes officiels :
         - Rejeu dynamique (résultat central)
         - Analyse critique du Graphe (Graph Reasoning)
         - Banc d'épreuve PrestaShop (Tasks & Benchmarks)
         - Frugalité E4B & Reward Hacking (Tuning & Optimization)
```

---

## 5. Spécification de la Skill ADK de Rejeu Dynamique

Pour transposer notre boucle PrestaShop dans le harness officiel Google ADK :

```yaml
# agent.yaml (Structure Conceptuelle ADK)
name: gemma4_replay_agent
model: gemma-4-31b-it-qat-w4a16-ct
parameters:
  max_model_len: 32768
  thinking_budget: 4096
tools:
  - edit_file
  - run_command
  - grep_search
  - list_dir
skills:
  - name: test_driven_replay
    description: "Exécute pytest après chaque édition de fichier et fournit la trace d'erreur pour correction."
    trigger: "after_edit"
    max_retries: 2
```

**Déroulé de la boucle :**
1. **Édition** : L'agent appelle `edit_file(old_string, new_string)`.
2. **Rejeu** : La skill exécute automatiquement `run_command("pytest <test_path>")`.
3. **Correction conditionnelle** :
   - Si les tests passent (`exit code 0`) : Fin de tâche, soumission du patch.
   - Si les tests échouent : La trace condensée de l'échec est renvoyée comme retour d'observation, et l'agent bénéficie d'une reprise pour corriger son diff.

---

## 6. Structure du Papier Officiel (Paper Track - 12/11)

Le papier couvrira les 4 thèmes officiels du concours :

1. **Tasks & Benchmarks (Ressource)** :
   - Présentation de notre banc d'épreuve PrestaShop 9.1 (33 bugs réels post-coupure, oracles Playwright, réinitialisation de base MariaDB, 462+ exécutions Docker tracées).
2. **Code Comprehension & Replay (Résultat Principal)** :
   - Gain mesuré de la boucle de rejeu dynamique (A vs B) sur les 129 tâches Python et sur PrestaShop.
3. **Graph Reasoning (Audit Technique)** :
   - Analyse empirique des limites des embeddings du harness officiel (perte de sélectivité cosinus, temps perdu) et supériorité du fenêtrage lexical guidé.
4. **Tuning, Optimization & Safety (Frugalité & Garde-fous)** :
   - Adaptation `ChunkedLossTrainer` (-51% VRAM sur modèles 4B).
   - Étude de sobriété énergétique métrologique (1,81 Wh par bug, 4,29 Go VRAM).
   - Découverte formelle du **Reward Hacking** (31,7% des trajectoires auto-générées contournant le correctif sans ancrage humain).
