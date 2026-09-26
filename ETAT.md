# ÉTAT — reprise : « Lis ETAT.md et reprends »

Mis à jour : 2026-09-25. Référence : `KIT.md` · Décisions : `DECISIONS.md` · Procédures : `docs/PROCEDURES.md` · Site : https://kaggle.d1dev.fr

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
- **Éval TEST définitive** (4 essais, réévalués) : **A 39 %** (12,8/33) · **R 38 %** (12,5/33), écart −0,8 pt (IC95 −10,6/+8,3), 0 régression. Voir `docs/RESULTATS.md`.
- **Condition B (tests écrits depuis le ticket)** : 10/33 reproduits, 1 fidèle ; sur ces 10 bugs B 3,5/10 vs A 4,5/10 → pas d'aide. Il faut la vraie chaîne de rejeu (capture sur la boutique).
- (historique) **Éval TEST en cours** (Gemma 4 31B, 1 run/bug) : A 3/22 · **R 4/16** (fine-tuning simulé). Régressions en cours de run non fiables (anti-régression déplacée avant l'oracle ; `bench/reeval.py` à lancer en fin de run).
- Oracles automatiques par différentiel : **0/12** (résultat négatif, à publier).
- Coût : **0 €** (Gemma gratuit sur l'API ; quota 16 000 tokens/min).

## TODO (ordre)
- [x] **Taxonomie des échecs** (`docs/ECHECS.md`) : 35 % mauvais fichier, 14 % aucune édition, 12 % correctif faux, 0 régression → la localisation est le premier levier (condition C).
- [~] **B\* / condition O** (borne haute : oracle comme retour, 2 corrections) sur 33 bugs — en cours (`runs/test_O1.log`).
- [~] **Condition C** (glossaire automatique provisoire `glossaire/glossaire_auto.csv`, 51 entrées + 4 graines, 16/33 tickets TEST concernés) — en file après O (`runs/test_C1.log`). Relecture de Rémi attendue pour la version définitive.
- [x] **Modèle 26B-A4B** (condition A) : **5/33 (15 %)** contre 39 % pour le 31B, à localisation égale → un modèle local plus petit sera bien en dessous ; le fine-tuning a de la marge.
0. [ ] **PRIORITÉ (jalon 20 oct.) : condition B sur TEST** = tests de rejeu générés par la chaîne (phase 4) → démontrer Q1. Sans ça, pas de thèse.
1. [ ] Fin des runs A/R → `bench/reeval.py` → tableau final (docs/DEMO.md ou docs/RESULTATS.md).
2. [ ] Tests TRAIN à grande échelle : Gemma écrit le test depuis ticket + correctif, validé pre/post automatiquement (proposé, en attente de GO).
3. [ ] Condition C (glossaire relu par Rémi) ; 3 runs par condition.
4. [ ] `RELATED.md` + date de coupure réelle (model card Gemma 4) → relancer split / reconstruct / glossaire.
5. [ ] Régler le texte officiel du concours dans `REGLES.md`.
6. [ ] Fine-tuning QLoRA sur le PC (ou Kaggle), puis condition D.

## Infos manquantes
- RAM du PC (4070 Ti) · texte officiel des règles · date de coupure Gemma 4.

## Budget
- API Gemma : 0 € (compteur `runs/_budget.json`). Kaggle GPU : 0 h.
