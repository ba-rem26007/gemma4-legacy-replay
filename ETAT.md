# ÉTAT — reprise : « Lis ETAT.md et reprends »

Mis à jour : 2026-09-26. Référence : `KIT.md` · Décisions : `DECISIONS.md` · Procédures : `docs/PROCEDURES.md` · Site : https://kaggle.d1dev.fr

## Jalons
| Date | Jalon | État |
|---|---|---|
| 1er oct | État de l'art, GO/NO-GO des viviers | viviers **GO** (TEST 33 ≥ 20 ; TRAIN > 1 000) ; `RELATED.md` à faire |
| 8 oct | Environnement reproductible | **fait** (8.x/9.x/1.6/1.7, reset, montée incrémentale, instances parallèles) |
| 20 oct | Chaîne de rejeu, runs A/B/C | runs A et R en cours sur TEST |
| 22 oct | GO/NO-GO fine-tuning | 569 chemins reconstruits prêts (≥ 150) |
| 29 oct | Adaptateur, runs D | — |
| 5 nov | Résultats figés | — |
| **9 nov** | **Soumission** | — |

## Fait
**Viviers**
- TEST 9.1.x (après coupure provisoire 2025-06-01) : 55 candidats → 37 rejouables → **33 oracles validés** (échoue en pre, passe en post), 4 exclus. `data/bugs_test.csv`, oracles `bench/replay/<pr>/oracle*.spec.js` (écrits par des agents Claude, cachés à l'agent évalué).
- TRAIN : catalogue `bench/catalog.jsonl` (1 007 bugs 2019-2026) + époque 1.6/1.7 `bench/bugs_legacy.jsonl` (**3 022+**, collecte 1.6 en cours).
- 569 chemins reconstruits vérifiés (`trajectories/train.jsonl`), étanchéité `data/ETANCHEITE.md`.

**Environnement** (`bench/checkout.sh`) : images officielles 8.x/9.x (`classic`)/1.6/1.7, montée incrémentale 9.1.x, reset de base par instantané, rattrapage de code, isolation entre bugs, instances parallèles `PSB=n`.

**Agent** (`agent/`) : déroulé fixe, API compatible OpenAI (curl), réflexion `<thought>` retirée, limiteur de débit partagé, budget ≤ 30 €, conditions A/B/C/D/**R**, traces complètes.

**Résultats**
- Démo pilotes (chemins reconstruits) : 3/3.
- Premier run réel Gemma 4 31B sur pilotes : A 1/2, B 0/3.
- **Éval TEST définitive** (4 essais, réévalués deux fois) : **A 39 %** (12,8/33) · **R 39 %** (12,8/33), écart 0,0 pt (IC95 −9,1/+9,1), 0 régression · **O 16/33 (48 %)** · C 13/33 · 26B 5/33. Voir `docs/RESULTATS.md`.
- **Condition B (tests écrits depuis le ticket)** : 10/33 reproduits, 1 fidèle ; sur ces 10 bugs B 3,5/10 vs A 4,5/10 → pas d'aide. Il faut la vraie chaîne de rejeu (capture sur la boutique).
- (historique) **Éval TEST en cours** (Gemma 4 31B, 1 run/bug) : A 3/22 · **R 4/16** (fine-tuning simulé). Régressions en cours de run non fiables (anti-régression déplacée avant l'oracle ; `bench/reeval.py` à lancer en fin de run).
- Oracles automatiques par différentiel : **0/12** (résultat négatif, à publier).
- Coût : **0 €** (Gemma gratuit sur l'API ; quota 16 000 tokens/min).

## Stratégie retenue (26 sept.) : boucle d'auto-apprentissage 100 % Gemma
1. Gemma écrit les oracles des bugs TRAIN (`bench/gentest.py`, ticket + correctif, gardé si échoue en pre / passe en post) — **pilote 10 bugs 9.0.x en cours** (`runs/gentest_pilot.log`, instance 4).
2. L'agent Gemma corrige ces bugs TRAIN avec l'oracle comme retour (mode O : +9,8 pts sur TEST) : `ORACLE_PREFIX=g python3 agent/run.py --condition O --bugs …` (**prêt**).
3. Chemins réussis vérifiés → `trajectories/self_paths.py` (**prêt**, testé sur runs TEST hors trajectories/ : 25 chemins / 29 résolus ; garde-fou d'étanchéité) → données de fine-tuning (source `gemma_self`, aucune sortie propriétaire), en plus des 569 chemins reconstruits.
4. QLoRA → condition D sur TEST (go/no-go 22 oct.).
Oracles Gemma = vérificateurs ; les trajectoires gardées sont celles de Gemma, validées par exécution.

## TODO (ordre)
- [x] **Taxonomie des échecs** (`docs/ECHECS.md`) : 35 % mauvais fichier, 14 % aucune édition, 12 % correctif faux, 0 régression → la localisation est le premier levier (condition C).
- [~] **B\* / condition O** (borne haute : oracle comme retour, 2 corrections) : run terminé : 1re tentative **13/33** (≈ A 12,8), **16/33 après retour de l'oracle** (+3 : #41299, #41394, #41923) → un vérificateur parfait apporte ≈ +9 pts. Section dans `docs/RESULTATS.md` ; **réévalué : 16/33 confirmés** (les 3 faux négatifs dus au bug d’évaluation sont levés).
- [~] **Bug d'évaluation corrigé** (`bench/checkout.sh`) : les fichiers modifiés par l'agent HORS du correctif officiel n'étaient pas restaurés → restaient patchés pour les bugs suivants sur la même image (48/172 patchs A/R concernés ; 3 faux négatifs visibles en O). **Réévaluation complète A/R/26B** sur instances neuves (`runs/reeval2.sh`, `runs/reeval2_*.log` → `result_reeval2.json`, prioritaire dans `bench/results.py`). **Terminée : 290 verdicts réévalués, 1 seul change** (#41652, un essai de R). **Chiffres définitifs : A 12,8/33 (39 %), R 12,8/33 (39 %), R − A = 0,0 pt [−9,1 ; +9,1]**, 0 régression ; taxonomie inchangée (35 % mauvais fichier).
- [x] **Notebook public** `notebook/resultats.ipynb` (recalcule tout depuis `eval/results.csv`, pandas) : écarts appariés contre A (IC 95 % bootstrap) — **O +9,8 pts [+0,8 ; +20,5]** (significatif), R −0,8 [−10,6 ; +9,1], C +0,8 [−12,9 ; +13,6], 26B −23,5 [−38,6 ; −9,1].
- [x] `eval/results.csv` (kit phase 8) : une ligne par condition × essai × bug, régénéré par `bench/results.py`.
- [x] Section « Autres conditions contre A » dans `bench/results.py` (résolus, bon fichier, gagnés/perdus).
- [x] **Condition C terminée : 13/33 (A 12,8), bon fichier 18/33 (A 19,8)** ; sur les 16 tickets avec entrée : résolus 4 vs 4, bon fichier 6 vs 7,75 → **le glossaire automatique n'aide pas** (résultat négatif). Détail : (glossaire automatique provisoire `glossaire/glossaire_auto.csv`, 51 entrées + 4 graines, 16/33 tickets TEST concernés) — en file après O (`runs/test_C1.log`). Relecture de Rémi attendue pour la version définitive.
- [x] **Micro-index classes / méthodes / hooks** (`agent/symbols.py`, idée de Rémi ; contrôle `bench/symcheck.py`, hors ligne, sans modèle) : pointe le fichier corrigé pour 12/33 tickets, mais A trouve déjà ce fichier 4 fois sur 4 pour 11 d'entre eux → **1 seul bug gagnable** (#41652). Les 12 bugs « durs » (A trouve le fichier ≤ 1 fois sur 4) ont des tickets en langage métier sans identifiant de code ; un index mots du ticket → noms de classes : 0/12. → Le levier restant = connaissance de l'architecture (glossaire relu par Rémi, fine-tuning D).
- [~] **Index des pages BO** (`glossaire/pages.py` → `pages.csv`, 79 pages, code seul) : hors ligne, pointe le fichier corrigé pour 7/33 tickets (glossaire auto : 4). Run **C+pages** en file après C (`runs/queue_Cp.sh` → `runs/test_Cp1.log`).
- [x] **Modèle 26B-A4B** (condition A) : **5/33 (15 %)** contre 39 % pour le 31B, à localisation égale → un modèle local plus petit sera bien en dessous ; le fine-tuning a de la marge.
0. [ ] **PRIORITÉ (jalon 20 oct.) : condition B sur TEST** = tests de rejeu générés par la chaîne (phase 4) → démontrer Q1. Sans ça, pas de thèse.
1. [ ] Fin des runs A/R → `bench/reeval.py` → tableau final (docs/DEMO.md ou docs/RESULTATS.md).
2. [ ] Tests TRAIN à grande échelle : Gemma écrit le test depuis ticket + correctif, validé pre/post automatiquement (proposé, en attente de GO).
3. [ ] Condition C (glossaire relu par Rémi) ; 3 runs par condition.
4. [~] `RELATED.md` : 6 références vérifiées (SWE-bench, Multi-SWE-bench sans PHP, SWE-agent, Agentless, SWE-Gym, SWE-smith) + nouveauté en 3 phrases ; reste golden master / record-replay / model card. Date de coupure réelle (model card Gemma 4) → relancer split / reconstruct / glossaire.
5. [~] **Writeup** (phase 9) : brouillon anglais `docs/WRITEUP.md` (structure complète, chiffres provisoires ⟦ ⟧).
6. [ ] Régler le texte officiel du concours dans `REGLES.md`.
6. [ ] Fine-tuning QLoRA sur le PC (ou Kaggle), puis condition D.

## Infos manquantes
- RAM du PC (4070 Ti) · texte officiel des règles · date de coupure Gemma 4.

## Budget
- API Gemma : 0 € (compteur `runs/_budget.json`). Kaggle GPU : 0 h.
