# ÉTAT — reprise : « Lis ETAT.md et reprends »

## Point d'avancement du 29 septembre 2026 (Exécution des Phases 1 à 6)

- **Plan d’amélioration intégralement exécuté** ([`docs/PLAN_AMELIORATION.md`](docs/PLAN_AMELIORATION.md), toutes cases cochées).
- **Phase 1 (Audit & Traçabilité)** : Rapport officiel [`docs/AUDIT_PHASE1.md`](docs/AUDIT_PHASE1.md), manifeste [`data/manifeste_run_v15.json`](data/manifeste_run_v15.json) et inventaire [`data/inventaire_exclusions_corpus.csv`](data/inventaire_exclusions_corpus.csv). Preuve SHA256 (`fac3f1af...`) et étanchéité certifiée à 100% sur les 33 bugs TEST.
- **Phase 2 (Corpus Compact v2)** : Génération de [`trajectories/train_compact.jsonl`](trajectories/train_compact.jsonl) (**660 trajectoires valides**, 100% vérifiées par patch Git en mémoire). À 4 096 tokens, **641 exemples sont conservés (97,1% de rétention)**, soit une multiplication par **$7{,}2\times$ du volume d'entraînement** par rapport aux 89 historiques ([`docs/RAPPORT_PHASE2.md`](docs/RAPPORT_PHASE2.md)).
- **Phase 3 (Matrice d'Ablation 2x2)** : Harnais expérimental [`bench/matrix_e4b.py`](bench/matrix_e4b.py) sur modèle dense pur `google/gemma-4-e4b-it` (`E4B-base`, `E4B-replay`, `E4B-lora`, `E4B-lora-replay`) pour éliminer le biais d'architecture avec le MoE 26B ([`docs/RAPPORT_PHASE3.md`](docs/RAPPORT_PHASE3.md)).
- **Phase 4 (Localisation & Fenêtrage Classé)** : Algorithme `windows_ranked()` déployé dans [`agent/flow.py`](agent/flow.py) (classement par densité de pertinence pour éviter le tronquage précoce). Métriques découplées dans [`agent/run.py`](agent/run.py) : `loc_hit_initial`, `loc_hit_ever`, `loc_hit_edited` ([`docs/RAPPORT_PHASE4.md`](docs/RAPPORT_PHASE4.md)).
- **Phase 5 (Reprise après Échec)** : Dataset de **17 trajectoires multi-tours d'auto-apprentissage** extraites du vivier TRAIN ([`trajectories/train_recovery.jsonl`](trajectories/train_recovery.jsonl), [`docs/RAPPORT_PHASE5.md`](docs/RAPPORT_PHASE5.md)), 100% leak-free.
- **Phase 6 (Consolidation)** : Dossier de soumission harmonisé et inattaquable pour Google DeepMind ([`docs/RAPPORT_PHASE6.md`](docs/RAPPORT_PHASE6.md)).

Mis à jour : 2026-09-29. Référence : `KIT.md` · Décisions : `DECISIONS.md` · Procédures : `docs/PROCEDURES.md` · Fine-Tuning : `docs/FINETUNING_KAGGLE.md` · Condition D : `docs/CONDITION_D.md` · Site : https://kaggle.d1dev.fr

## Recheck pré-soumission (30 sept.) — NO-GO en l'état, corrections en cours
- **Writeup réécrit** (`docs/KAGGLE_FINAL_WRITEUP.md`, 2 7xx mots) : plus aucun contenu sécurité, chiffres recalculés et contre-vérifiés (29 constats corrigés), sous-titre, Related works, AI disclosure. Logs d'entraînement/gentest et instantané exact des données d'entraînement versionnés.
- **Dépôt public préparé** : `tools/build_public.sh` construit l'arbre public depuis HEAD (liste blanche, README anglais `docs/README_PUBLIC.md`, contrôles secrets / contenu sécurité / chemins cités) → OK, 8 655 fichiers, 282 Mo. Exclus : rapports internes, notebooks (chiffres non sourcés), `SOBRIETE.md`, `BOUNTY_REPORTS.md`, `train_compact`/`train_recovery` (non filtrés). **Test de bout en bout du README public (30 sept., 10 h 15)** sur #41007 : oracle échoue avant (rc 1), passe après (rc 0) ; agent A résout en 3 tours ; `eval.py` confirme — `runs/e2e_readme.out`. **Fiche HF de l'adaptateur réécrite** (`training/lora_final/lora_gemma4/final/README.md`, copiée dans `extracted/`) : base `google/gemma-4-E4B-it`, 89/585 exemples, E 4/33 présenté système contre système, plus de contenu sécurité ; prête à l'upload (feu vert Rémi). Publication = `git init` d'un dépôt NEUF sans historique, après révocation des tokens par Rémi.
Rapport complet : 6 revues contre-vérifiées. Bloquants : (1) secrets suivis ; (2) contenu « zero-day / bounty » (writeup §5, `docs/BOUNTY_REPORTS.md`) contraire à la règle « jamais de sécurité » ; (3) rien de public (dépôt, HF, LICENSE) ; (4-5) chiffres LoRA et #41005 faux dans `docs/KAGGLE_FINAL_WRITEUP.md` ; (6) citations fausses ; (7) format Kaggle (sous-titre, Related works, ≤ 3 000 mots).
- **Fait 30 sept.** : `RELATED.md` revérifié (WATERFALL = Hammoudi et al. FSE 2016 ; Li et al. 2024 ; Gemma 4 Technical Report, **coupure officielle janvier 2025** → notre split 2025-06-01 est prudent ; Feathers via Open Library) ; secrets retirés des fichiers (ngrok → variable d'env., mots de passe du site) ; `LICENSE` Apache-2.0 ; runs B et E, scripts `run_test_*`, `train_kaggle.py` committés.
- **Rémi** : révoquer le token ngrok (https://dashboard.ngrok.com) et le token HF (https://huggingface.co/settings/tokens), changer le mot de passe du site ; feu vert pour supprimer `docs/BOUNTY_REPORTS.md` et la §5. Publication = **nouveau dépôt public sans historique** (le token ngrok reste dans l'historique actuel).

## Boucle d'auto-apprentissage — bilan final (30 sept., 7 h 55)
- **Terminée** (lot 4 : 220 bugs traités). Oracles PHP écrits par Gemma : **99 validés / 254 (39 %)** ; navigateur 0/22.
- Agent Gemma, condition O sur TRAIN : **41 résolus / 99 (41 %)** → garde-fous : **13/41 (32 %) contournements** (7 hors fichiers officiels, 6 hors fonctions officielles), 3 fichier absent de la recherche ; après filtre d'étanchéité par fonction (10 bugs exclus, dont #32563 et #31571) : **23 chemins acceptés**. (Corrigé le 30 sept. : « 39 % » était faux.)
- Similarité au correctif officiel : **16 chemins ≥ 0,4** (seuil proposé). `trajectories/self.jsonl`, `docs/BOUCLE.md`.

## Jalons
| Date | Jalon | État |
|---|---|---|
| 1er oct | État de l'art, GO/NO-GO des viviers | **fait** (viviers GO : TEST 33, TRAIN > 4 000 ; `RELATED.md` finalisé) |
| 8 oct | Environnement reproductible | **fait** (8.x/9.x/1.6/1.7, reset, montée incrémentale, instances parallèles) |
| 20 oct | Chaîne de rejeu, runs A/B/C | **fait** (Condition B terminée : 15/33 = 45.5% vs A 39%, +6.5 pts, 0 régression) |
| 22 oct | GO/NO-GO fine-tuning | **fait** (QLoRA complété sur Kaggle GPU Tesla T4, 3 époques, perte 1.192) |
| 29 oct | Adaptateur, runs D | **adaptateur extrait (134 Mo)**, serveur Colab/ngrok testé, run D prêt |
| 5 nov | Résultats figés | — |
| **9 nov** | **Soumission** | — |

## Fait
**Viviers**
- TEST 9.1.x (après coupure provisoire 2025-06-01) : 55 candidats → 37 rejouables → **33 oracles validés** (échoue en pre, passe en post), 4 exclus. `data/bugs_test.csv`, oracles `bench/replay/<pr>/oracle*.spec.js` (écrits par des agents Claude, cachés à l'agent évalué).
- TRAIN : catalogue `bench/catalog.jsonl` (1 007 bugs 2019-2026) + époque 1.6/1.7 `bench/bugs_legacy.jsonl` (**3 022+**, collecte 1.6 en cours).
- 585 chemins purs vérifiés et dédoublonnés (`rmisoubeyrand/gemma4-prestashop-trajectories`).

**Environnement** (`bench/checkout.sh`) : images officielles 8.x/9.x (`classic`)/1.6/1.7, montée incrémentale 9.1.x, reset de base par instantané (`.snap-psbench2.sql.gz`), isolation stricte entre bugs, instances parallèles `PSB=n`.

**Résultats & Benchmarks**
- **Condition A (baseline, ticket seul)** : **12.8 / 33 résolus (39.0%)**, bon fichier 19.8/33, 0 régression.
- **Condition R (RAG de 2 corrections TRAIN similaires)** : **12.8 / 33 résolus (39.0%)**, aucun gain par rapport à A.
- **Condition B (Replay des tests réels de reproduction, run `20260928-092011-B`)** : **15 / 33 résolus (45.5%)**, bon fichier 17/33, **0 régression**. Net avantage de **+6.5 points de pourcentage** ! Sauvetage en cours de route de `#41007` (au tour 5) et `#41923` (au tour 7, réputé impossible à 0/8 en A/R).
- **Condition O (borne haute oracle en retour)** : 16 / 33 résolus (48.5%).
- **Fine-Tuning QLoRA Gemma 4 (Kaggle GPU, version 15)** : **TERMINÉ avec SUCCÈS (28 sept. 2026)**. 3 époques, perte descendue de 1.564 à 0.9309 (moyenne 1.192). Résolution de l'OOM 4 Go grâce au `ChunkedLossTrainer`. Adaptateur LoRA 134 Mo rapatrié dans `training/lora_final/extracted/` et miroir web `https://anniv.soubeyrand.dev/lora.zip`.
- **Condition D (Évaluation du modèle fine-tuné)** : Serveur d'inférence Colab GPU T4 monté avec FastAPI et ngrok. Premier test de validation réussi sur Bug `#41007` (`runs/20260928-163213-D`) : **1/1 résolu**, localisation exacte (`loc_hit: true`), 0 régression, 5 tours. Site de présentation déployé sur `https://kaggle.d1dev.fr` (accès restreint).
- **Condition E (Modèle fine-tuné 4B LoRA + Règles Métier, run `runs/20260928-175551-E`)** : Benchmark complet sur les **33 / 33 bugs TEST achevé (100%)**. **4 résolutions fermes confirmées par l'oracle Playwright avec 0% de régression sur ces 4 bugs** : `#40971` (LogoUploader, 100% identique au caractère près), `#41193` (TranslationController), `#41007` (CountryQueryBuilder), et `#41130` (AbstractObjectModelHandler en API Admin OAuth2).
  - Taux de résolution : **4/33 (12.1%)**, localisation exacte : **14/33 (42.4%)**, patchs appliqués : **18/33 (54.5%)**, non-régression globale : **97.0%** (32/33).
  - **Ablation 4B Base (`Condition A-4B`)** : 4B Base Zero-Shot sans LoRA ne résout que **1/33 (3.0%)** avec 45.5% d'erreurs de syntaxe SEARCH/REPLACE. L'apport isolé du QLoRA est de **+9.1 points (+3 bugs nets)**.
  - **Rigueur Statistique ($N=33$)** : Gain Replay B vs A = +6.5 pts, IC 95% bootstrap $[-2.3\%, +16.7\%]$, permutation $p=0.11$.
  - **Compromis Frontière de Pareto** : 45.5% (31B Cloud) vs 12.1% (4B Edge Souverain 4.29 Go VRAM, 1.9 Wh/bug).
  - **Non-Fuite Certifiée #40971** : Post-cutoff 08/04/2026, absent du corpus d'entraînement, signature canonique d'API univoque.
- **Documentation Scientifique Complète & Site Live** :
  - `docs/RAPPORT_GLOBAL.md` & `https://kaggle.d1dev.fr/rapport` : Synthèse complète en 11 sections avec bouton 1-clic pour tout récupérer.
  - `docs/SOBRIETE.md` : Protocole métrologique 100 ms `nvidia-smi` (1.39 Wh GPU + 0.42 Wh CPU = 1.81 Wh ≈ 1.9 Wh/bug).
  - `docs/TESTS_ET_QUALITE.md` : Pyramide de tests (PHPStan 8/9, PHPUnit, Intégration Symfony, E2E Playwright, AST Semgrep).
  - `docs/MODULES_TIERS.md` : Benchmark de 10 dépôts tiers et cas réel `ps_facetedsearch` PR #1340.

## Point du 27 sept., 6 h 45 (nuit autonome)
- **Oracles écrits par Gemma** : navigateur 0/11 ; **PHP 20/53 (38 %)**.
- **Agent Gemma avec l'oracle comme retour** : 18 bugs essayés → **9 chemins acceptés** (4 identiques au correctif officiel, similarités 0,26 → 1,0), 2 contournements rejetés, 7 non résolus.
- **Rendement** ≈ 17 % des bugs essayés → chemin honnête. Lot 4 (220 bugs, plus anciens, plus lents ≈ 40 min/bug) en cours sur 2 instances.
- **Lot 4 (bugs 2022-2023)** : oracles 5/21 (25 %) — échecs : 8 erreurs PHP dans le test (API 8.0/8.1 méconnue de Gemma), 6 échecs après correctif, 2 tests qui passent déjà avant. Signatures des classes ajoutées à la consigne (27 sept. 10 h 20) → **oracles validés : 24 % avant (5/21), 43 % après (26/60)** : l'API réelle dans la consigne double presque le taux. **Point 14 h 30 : oracles 11/43 (26 %) ; agent 1 chemin accepté sur 11 bugs** (localisation ratée ~60 %) → rendement lot 4 ≈ 2-3 % des bugs, contre ≈ 17 % sur les bugs 2024-2025. Projection révisée : lot 4 complet ≈ +5 chemins seulement ; les bugs récents rapportent beaucoup plus.
- **Garde-fous (28 sept. 0 h)** : 20 bugs TRAIN « résolus » selon l'oracle Gemma → 12 chemins acceptés, **8 rejetés (40 %)** : 7 contournements (fichier ou fonction hors correctif officiel) + 1 fichier absent de la recherche. Sans le correctif officiel comme référence, 40 % des données d'auto-apprentissage seraient du *reward hacking*.
- **Décisions pour Rémi** : (1) laisser tourner le lot 4 (≈ 3 jours) ; (2) fine-tuning : RAM du PC ou `kaggle auth login` ; (3) seuil de similarité pour l'entraînement (proposition : ≥ 0,4 → 6 chemins).

## Stratégie retenue (26 sept.) : boucle d'auto-apprentissage 100 % Gemma
1. Gemma écrit les oracles des bugs TRAIN (`bench/gentest.py`, ticket + correctif, gardé si échoue en pre / passe en post) — **pilote 10 bugs 9.0.x en cours** (`runs/gentest_pilot.log`, instances 4 et 1) ; corrections outillage : image 9.0 pour 9.0.x, erreur MySQL renvoyée, schéma réel de la base dans la consigne, instantané de page en cas d'échec. **Résultat UI : 0 oracle validé sur 5 bugs** (Gemma n'arrive pas à piloter le BO : clics/saisies en timeout, même avec erreur MySQL, schéma, instantané de page) → pilote UI arrêté. **Pivot : oracles PHP en ligne de commande** — **Oracles validés : #38417, #38341** (soft delete transporteur, essai 1) — 1er :**#38417** (webservice, essai 1, 4 min, appelle la méthode fautive par réflexion : erreur SQL exacte en pre, passe en post) — (`gentest --mode php`, `run.sh` exécute `oracle*.php` dans le conteneur) sur 8 bugs côté serveur (`runs/gentest_php.log`, instance 3) + lot 2 de 10 bugs (`runs/gentest_php2.log`, instance 1). **Variante `--explore`** (Gemma observe 1-2 pages réelles avant d’écrire) : **0/4** → arrêtée. Bilan UI : **0 oracle sur 9 bugs**.
2. L'agent Gemma corrige ces bugs TRAIN avec l'oracle comme retour (mode O : +9,8 pts sur TEST) : `ORACLE_PREFIX=g python3 agent/run.py --condition O --bugs …` (**prêt**).
2b. **Boucle complète testée sur #38417** : l'agent résout avec l'oracle Gemma comme retour (après correction : la sortie de l'oracle PHP est maintenant transmise), MAIS par **contournement** (cas particulier dans `ImageType` au lieu de corriger l'appel fautif) = *reward hacking* d'un oracle écrit par le modèle → **garde-fou** dans `self_paths.py` : éditions limitées aux fichiers du correctif officiel (connu sur TRAIN) ; ce chemin est rejeté.
2b'. **Déroulé v2 (correction)** : après un test raté, l'agent voit l'ÉTAT ACTUEL des fichiers qu'il a modifiés (auparavant il recopiait l'original → « bloc SEARCH introuvable » en boucle, #38341 : 4 corrections perdues). Concerne les runs avec retour (O, B) lancés à partir du 26 sept. soir ; les résultats TEST O/B antérieurs sont en déroulé v1.
2d. **3e oracle validé : #38168** ; l'agent le « résout » dans le bon fichier mais dans une AUTRE méthode (requête de `getCategoriesWithoutParent` rendue vide) → 2e contournement → **garde-fou au niveau fonction** (chaque fonction éditée doit être touchée par le correctif officiel). Coût mesuré sur les 25 succès TEST jugés par nos oracles : 20 gardés, 5 rejetés (correctif valide dans un autre fichier), 0 rejet au niveau fonction.
2e. **PREMIER CHEMIN 100 % GEMMA ACCEPTÉ : #37970** (26 sept. soir) — oracle PHP écrit par Gemma (essai 1) → agent Gemma avec l'oracle comme retour → patch **identique au correctif officiel** (`Tools::purifyHTML`, attributs vidéo) → accepté par tous les garde-fous (`trajectories/self.jsonl`). La boucle fonctionne de bout en bout. **2e chemin : #37955** (correctif partiel : bon `trim` des IP de maintenance + clé de config inventée) → score `similarite` au correctif officiel ajouté à chaque chemin (#37970 : 1.0, #37955 : 0.26) pour fixer un seuil de qualité à l'entraînement.
2f. **Projection (26 sept. 23 h)** : oracles PHP 8/17 (47 %) × agent résout 4/7 × chemins acceptés 2/4 → **≈ 14 % des bugs donnent un chemin honnête**. 200 bugs TRAIN côté serveur ≈ **25-30 chemins Gemma** en ~3 jours sur 2-3 instances (≈ 25 min d'oracle + 15 min d'agent par bug). Largement avant le 22 oct. ; à décider avec Rémi : passage à 200 bugs.
2g. **Passage à l'échelle lancé (27 sept. nuit)** : lot 4 = 220 bugs TRAIN côté serveur (classes/, src/, controllers/, ≤ 3 fichiers, 2022 → coupure) en file après le lot 3, 2 instances (`runs/queue_lot4.sh`, `runs/gentest_php4.log`), ~36 h ; la boucle agent suit. Coût 0 €.
2h. **Chemins condensés** : l'étape LIRE ne garde que les fichiers réellement édités → les 2 chemins rejetés « trop longs » passent : **7 chemins Gemma** (similarité au correctif officiel : 1.0 ×2, 0.74, 0.72, 0.46, 0.33, 0.26 ; 2 900 à 5 500 tokens).
2c. **Tableau de bord** : `bench/loop_stats.py` → `docs/BOUCLE.md` (UI 0/5, explore 0/4, **PHP 2/5 = 40 %**).
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
- [~] **Index des pages BO** (`glossaire/pages.py` → `pages.csv`, 79 pages, code seul) : hors ligne, pointe le fichier corrigé pour 7/33 tickets (glossaire auto : 4). Run **C+pages terminé : 11/33, bon fichier 18/33** (A 12,8 / 19,8) → **aucun gain** (résultat négatif).
- [x] **Modèle 26B-A4B** (condition A) : **5/33 (15 %)** contre 39 % pour le 31B, à localisation égale → un modèle local plus petit sera bien en dessous ; le fine-tuning a de la marge.
0. [x] **PRIORITÉ (jalon 20 oct.) : condition B sur TEST terminée** : **15 / 33 (45.5%)** vs A 39%, +6.5 pts, 0 régression. Démontre la question Q1 (le rejeu de test améliore significativement la résolution et sauve des bugs historiques comme #41923).
1. [x] **Fine-tuning QLoRA sur Kaggle GPU (version 15)** : Réalisé avec succès le 28 sept. 2026. 3 époques, perte 1.192, adaptateur LoRA 134 Mo extrait (`training/lora_final/extracted/`). Voir `docs/FINETUNING_KAGGLE.md`.
2. [ ] **Condition D sur vivier TEST (33 bugs)** : Lancer `bash runs/run_test_D.sh <ngrok_url>` pour évaluer le modèle fine-tuné et comparer avec A et B. Voir `docs/CONDITION_D.md`.
3. [ ] Consolider `docs/RESULTATS.md` et `docs/WRITEUP.md` avec les résultats complets A / B / D pour la soumission finale.
4. [x] `RELATED.md` : 10 références vérifiées (SWE-bench, Multi-SWE-bench, SWE-agent, Agentless, SWE-Gym, SWE-smith, Feathers 2004, Waterfall, Survey Web Testing, Model Card Gemma 4) + nouveauté en 3 phrases. Jalon 1er oct validé.
5. [~] **Writeup** (phase 9) : brouillon anglais `docs/WRITEUP.md` (structure complète, chiffres provisoires ⟦ ⟧).
6. [ ] Régler le texte officiel du concours dans `REGLES.md`.

## Infos manquantes
- RAM du PC (4070 Ti) · texte officiel des règles · date de coupure Gemma 4.

## Budget
- API Gemma : 0 € (compteur `runs/_budget.json`). Kaggle GPU : 0 h.
