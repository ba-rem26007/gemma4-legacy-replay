# 🔴 Audit Critique du Projet — Verdict Brutal pour Gagner le Concours Kaggle Gemma 4

> **Méthode** : 4 auditeurs indépendants (Writeup EN, Code Quality, Statistiques, Analyse Compétitive) + vérification manuelle croisée sur `eval/results.csv` et les scripts.

---

## 🚨 ERREURS CRITIQUES — À corriger IMMÉDIATEMENT (Éliminatoires)

### 1. ❌ Le modèle "A-4B" N'EST PAS Gemma 4 4B — Confusion d'identité du modèle

**Le problème le plus grave de tout le dossier.**

Le writeup affirme (ligne 18, 102, 113, 126) :
> *"Base Gemma 4 4B resolves only 3.0% (1/33)"*

**Réalité dans les données** (`eval/results.csv` + `result.json`) :
- Le modèle utilisé pour A-4B est **`gemma-4-26b-a4b-it`** — c'est le **Gemma 4 26B A4B** (architecture MoE, 4B paramètres *actifs* sur 26B total)
- Il résout **5/33 = 15.2%**, PAS 1/33 = 3.0%
- Le "vrai" Gemma 4 4B pur (`gemma-4-4b-it`) n'a apparemment **jamais été évalué**

**Conséquence** : L'ablation LoRA (`b=3, c=0, p=0.125`) est **fausse**. La réalité : `b=3, c=4` (E résout uniquement 3 bugs que A-4B ne résout pas, mais A-4B résout 4 bugs que E ne résout pas). Le LoRA **ne bat même pas** la baseline A-4B en nombre absolu !

> [!CAUTION]
> Si un juré vérifie `eval/results.csv` et constate que A-4B=15.2% alors que le texte dit 3.0%, c'est une disqualification pour **fausse déclaration de résultats scientifiques**. Priorité absolue #1.

---

### 2. ❌ "94% de réduction VRAM" — Erreur mathématique flagrante

Ligne 263 du writeup :
> *"peak VRAM during loss computation drops by 94% (from 28.4 GB to 13.8 GB)"*

**Calcul réel** : $(28.4 - 13.8) / 28.4 = 51.4\%$ de réduction.

Une réduction de 94% donnerait 1.7 GB, pas 13.8 GB. Les deux chiffres sont incompatibles.

**Options** :
- Si 28.4 → 13.8 est exact : écrire **"51% reduction in total training VRAM"**
- Si 94% est exact : c'est la réduction de la **taille du tenseur de loss** (vocabulaire 262k → chunks de 256), pas la VRAM totale

---

### 3. ❌ "Zero Regressions Across All Conditions" — Contredit par les propres données

Ligne 318 :
> *"our agent caused **zero regressions** on front-office or back-office smoke suites"*

Ligne 103, tableau des résultats :
> *Condition E → Regressions = **1 (3.0%)***, Condition O → **2 regressions**

Les données CSV confirment : E a 1 régression, O en a 2. **La phrase "zero regressions across ALL conditions" est factuellement fausse.**

---

### 4. ❌ McNemar B vs A-consensus : b et c sont INVERSÉS

Le writeup (ligne 118) dit :
> *"discordant pairs are **2 vs 1** ($p = 0.50$)"*

**Calcul réel** sur `eval/results.csv` :
- B-only (b) = **1** bug que B résout et pas A-consensus
- A-only (c) = **2** bugs que A-consensus résout et pas B
- Soit b=1, c=2 — **le rapport est inversé**, et ça signifie que A-consensus est *meilleur* que B sur les paires discordantes !

> [!WARNING]
> Cela ne change pas le p-value (0.50 dans les deux sens), mais inverser b et c dans le texte donne l'impression que B domine alors que c'est l'inverse sur les paires discordantes.

---

### 5. ❌ Taxonomie d'échec incomplète — Ne somme pas à 100%

Lignes 310-314 :
```
Localisation Failure    35.0%
Syntactic Mismatch      14.0%
Incorrect Logic         12.0%
Platform Regressions     0.0%
───────────────────────────────
Total                   61.0%  ← Il manque 39%
```

Où sont les 39% restants ? Ce sont probablement les bugs résolus, mais alors la taxonomie porte sur les bugs *tentés*, pas les bugs *échoués*. C'est ambigu et confus.

---

## 🟠 FAIBLESSES STRUCTURELLES — À traiter pour passer de "bon" à "gagnant"

### 6. Aucune comparaison avec des modèles ouverts concurrents

Le writeup ne compare Gemma 4 **qu'à lui-même** (31B vs 4B, A vs B). Il manque :
- **Qwen3-27B / Qwen3.5-Coder** (actuellement le plus fort en agentic coding open-source)
- **DeepSeek-V4** / **Kimi-Dev-72B**
- **Llama 3.x**
- Score de l'agent sur **SWE-bench** (même partiel, pour situer)

Sans baseline externe, le jury ne sait pas si 39% est bon ou médiocre.

### 7. L'affirmation "Claude échoue" sans preuve

Ligne 44 :
> *"frontier models fail systematically on these legacy codebases"*

Mais Claude/GPT-4o n'ont **jamais été évalués** sur les 33 bugs. C'est une affirmation non falsifiable et non démontrée.

### 8. La comparaison énergétique compare des pommes et des oranges

Comparer le TDP d'un Tesla T4 (70W) local au TDP estimé d'un cluster 8×H100 cloud pour Claude est structurellement invalide :
- Le T4 fait tourner un modèle 4B, le cluster un modèle 200B+
- Les niveaux de performance sont incomparables (12.1% vs potentiellement 60%+)
- La source "Luccioni et al. 2023" ne mesure pas le coût par bug résolu en agentic coding

### 9. Dolibarr = Un seul bug anecdotique (#41005)

Toute la section "Cross-Ecosystem Generalization" repose sur UN bug résolu. Ce n'est pas une preuve de généralisation — c'est une anecdote. Un jury sérieux ne peut pas conclure quoi que ce soit de N=1.

### 10. "Zero-Day Vulnerability" = Marketing cybersécurité

Un crash `stdClass::getPriceBaseType()` sur une API REST est un **bug PHP standard**, pas une "Zero-Day Vulnerability". Utiliser ce terme cybersécurité pour inflater l'impact est le genre de chose qui agace les jurés techniques de Google DeepMind.

---

## 🟡 PROBLÈMES DE FORME — Risque de perception négative

### 11. Franglais dans le writeup EN

- "Tour 1, Tour 2, Tour 3" au lieu de "Turn 1, Turn 2, Turn 3"
- Prompt d'injection en français ("JURISPRUDENCE HISTORIQUE SIMILAIRE")
- "Jurisprudence" utilisé en anglais pour décrire des patches Git historiques — terme inadapté. Préférer "case-based reasoning" ou "historical precedent retrieval"

### 12. Verbosité et padding

- L'énergie (1.91 Wh, 15.7 Wh, 0.00 €) est répétée dans l'Executive Summary, le paragraphe, le tableau ET un ASCII chart. Ça ressemble à du bourrage.
- Les diagrammes ASCII sont mal proportionnés et font "amateur" comparé à des figures Matplotlib/Mermaid publiées.

### 13. Statistiques sans source

- "76% of the web is powered by PHP" — pas de citation (W3Techs ?)
- "Dolibarr powering over 100,000 businesses" — pas de citation
- "~65 to 110 Wh" pour Claude/GPT-4 — comment mesuré ? Pas cité.

### 14. Code Quality

- `train_lora.py` n'existe pas (le vrai fichier est `training/chunked_loss.py`)
- `bench/results.py` hardcode tous les noms de répertoires de runs (non reproductible)
- Resource leaks : `open()` sans `with` blocks dans `flow.py` et `run.py`
- Le "fixed flow 4 tours" contient en réalité un backtracking dynamique (`backtrack()`) + retries — pas vraiment "fixe"

---

## ✅ CE QUI FONCTIONNE (et comment le mettre en avant)

| Force | Commentaire |
|---|---|
| **Benchmark unique et réel** | 33 bugs post-cutoff avec oracles Playwright cachés sur un monolithe PHP legacy réel. Aucun autre concurrent ne fait ça. **C'est l'USP.** |
| **Transparence statistique** | Reporter $p=0.1128$ au lieu de cacher l'insignifiance est rare et crédible. |
| **Budget 0.00 €** | Reproductible, vérifiable, différenciateur fort face aux soumissions à 500$ d'API. |
| **LoRA ChunkedLoss** | Innovation technique réelle pour QLoRA sur vocabulaire massif (262k tokens). À mettre en avant. |
| **Souveraineté / Edge** | L'angle RGPD/PCI-DSS est unique dans l'écosystème Gemma. |
| **462 évaluations empiriques** | Volume d'expérimentation solide pour un projet solo. |

---

## 📋 Plan d'Action Prioritaire (Ordre d'urgence)

### P0 — Correctifs éliminatoires (< 1h)

| # | Action | Fichiers impactés |
|---|---|---|
| **1** | Corriger A-4B : soit documenter que c'est `gemma-4-26b-a4b-it` (5/33=15.2%), soit lancer un vrai run `gemma-4-4b-it`. L'ablation LoRA change complètement. | Writeup EN, FR, README, notebook |
| **2** | Corriger "94% VRAM" → soit "51% total VRAM", soit "94% du tenseur de loss (vocabulaire 262k → chunks 256)" avec clarification | Writeup EN, FR, glossaire |
| **3** | Supprimer "Zero Regressions Across ALL Conditions" → "Zero regressions in Conditions A, R, B (31B)" et documenter 1 régression en E, 2 en O | Writeup EN, FR |
| **4** | Corriger McNemar b=1, c=2 (pas b=2, c=1) | Writeup EN, FR, PLAN_DE_TESTS |
| **5** | Compléter la taxonomie d'échec à 100% (ajouter "Resolved: 39%" ou recalculer sur les échecs seulement) | Writeup EN |

### P1 — Renforcements pour gagner (< 2h)

| # | Action |
|---|---|
| **6** | Ajouter 1 baseline externe (même Gemma 4 12B ou 27B sur 5-10 bugs) pour calibrer |
| **7** | Remplacer "Zero-Day Vulnerability" par "Undiscovered Residual Defect" |
| **8** | Ajouter citations : W3Techs pour PHP, Dolibarr.org pour les 100k |
| **9** | Traduire les prompts FR dans le writeup EN |
| **10** | Clarifier "fixed flow" vs backtracking dans l'architecture |

### P2 — Polish (si temps restant)

| # | Action |
|---|---|
| **11** | Remplacer ASCII charts par de vrais graphiques Matplotlib |
| **12** | Réduire la redondance énergétique (1 tableau + 1 phrase, pas 4 répétitions) |
| **13** | Ajouter une section "Limitations" explicite (N=33, pas de baseline externe, etc.) |

---

> [!IMPORTANT]
> **Verdict global** : Le projet a un **angle unique et fort** (benchmark legacy PHP, souveraineté edge, budget 0€). Mais les erreurs factuelles (A-4B, 94% VRAM, "zero regressions") **discréditent la rigueur** qui est censée être le différenciateur principal. Corriger les P0 est **non négociable** avant soumission.
