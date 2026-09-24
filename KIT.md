# KIT CLAUDE CODE v2 : « Legacy vérifiable + auto-apprentissage » (Gemma 4 Developer Agent, Paper Track)

> Référence fournie par Rémi le 2026-09-24, copiée telle quelle.
> Adaptations locales : voir `DECISIONS.md` (dossier `/home/elrems/kaggle` conservé, mise au point sur serveur + API).
> Une phase par session. Relancer avec : « Lis ETAT.md et reprends. »
> v2 : split temporel entraînement / évaluation, trajectoires condensées, fine-tuning QLoRA.

=====================================================================
PHASE 0 : CONTEXTE ET RÈGLES DU JEU
=====================================================================

Tu travailles avec moi (Rémi, dev PHP/Symfony/PrestaShop 20+ ans, IA appliquée) sur une soumission au **Paper Track** du concours Kaggle « Google - The Gemma 4 Developer Agent ».

**Deadline officielle : 12 novembre 2026, 23:59 UTC. Deadline interne : 9 novembre.**
Raison : en cas d'égalité de points, le papier soumis le plus tôt l'emporte.
Aujourd'hui : 24 septembre 2026. Je suis à mi-temps sur ce projet.

**Ce que dit le règlement (vérifié)**
- 5 critères à poids égal, notés de 0 à 5, note finale = moyenne : nouveauté, qualité, pertinence, vérifiabilité, clarté
- 3 papiers récompensés ; la grille de notation n'est pas communiquée
- interdiction de soumettre du contenu qui viole des droits de tiers ou des obligations de confidentialité
- aucune version de Gemma 4 imposée pour le Paper Track (à reconfirmer dans l'onglet Rules)

**À vérifier en phase 0 (non confirmé officiellement)**
- compétition principale : modèle `gemma-4-31b-it-qat-w4a16`, 4 GPU L4, évaluateur officiel « swegemma » avec 9 outils et compilation ADK
- si la doc des 9 outils est publiée : notre agent les reprend à l'identique (comparabilité avec le leaderboard)

**Thèse du papier**
Un agent de code local échoue sur du legacy pour deux raisons : il ne peut pas vérifier ses correctifs (pas de tests), et il ne connaît pas les réflexes du code (PrestaShop ici). On propose :
1. une chaîne qui rend le legacy vérifiable sans écrire de tests à la main (instrumentation, pilotage d'interface, capture, rejeu)
2. une boucle d'auto-apprentissage : ces tests valident les tentatives de l'agent, on condense les réussites en chemins directs, on entraîne le modèle dessus

**Questions de recherche**
- Q1 : les tests de rejeu générés améliorent-ils le taux de résolution et réduisent-ils les régressions ?
- Q2 : un contexte PrestaShop (schéma, glossaire) fourni par outil aide-t-il ?
- Q3 : un fine-tuning sur des chemins condensés, validés par les tests de rejeu, améliore-t-il un petit modèle local sur des bugs jamais vus ?

**Matériel**
- PC Windows, RTX 4070 Ti 12 Go VRAM, RAM système : [À COMPLÉTER]
- serveur Linux en ligne sans GPU
- Kaggle : ~30 h GPU / semaine (P100 16 Go ou 2×T4), sessions de 12 h, pas de Docker
  → Kaggle sert UNIQUEMENT à l'entraînement ; PrestaShop et les runs d'agent tournent sur le PC

**Règles non négociables pour toi**
- AUCUN code client ou privé. Uniquement du public. Tout finira en public.
- Aucune citation inventée. Chaque référence a un lien vérifié, sinon elle n'entre pas.
- Pas de recherche de failles de sécurité. On corrige des bugs connus et publiés.
- Aucun modèle propriétaire pour générer des données d'entraînement (pas de distillation depuis Claude, GPT, etc.).
- ÉTANCHÉITÉ : aucun bug du jeu d'évaluation ne doit apparaître, de près ou de loin, dans les données d'entraînement. Tu vérifies à chaque étape.
- `ETAT.md` à jour à la fin de chaque étape ; `DECISIONS.md` pour chaque choix structurant.
- Tu demandes avant toute commande destructive ou tout téléchargement > 5 Go.
- Une phase à la fois. Tu t'arrêtes et tu présentes le livrable.

**Livrable phase 0**
- `ETAT.md`, `DECISIONS.md`, `README.md`
- `REGLES.md` : je te colle le texte officiel des onglets Overview, Evaluation, Rules et Data (des deux compétitions). Tu signales tout ce qui touche notre plan.

=====================================================================
PHASE 1 : ÉTAT DE L'ART (semaine 1)
=====================================================================

Axes :
- benchmarks d'agents SWE (SWE-bench et variantes multilingues : couverture PHP ?)
- entraînement d'agents SWE sur trajectoires (vérifier notamment SWE-Gym et SWE-smith : nombre de trajectoires utilisées, gains obtenus)
- auto-distillation / rejection sampling sur trajectoires vérifiées ; citer l'adaptateur Hugging Face « gemma-4-31b-condensed-selfdistill-lora » (condensation d'une résolution vérifiée avant entraînement, preuve de concept sur une seule tâche)
- mise en place automatique d'environnements d'exécution pour agents
- tests de caractérisation, golden master, record/replay
- génération de tests par exploration d'interface

**Livrable** : `RELATED.md` (titre, auteurs, année, lien, résumé 2 lignes, différence avec nous) + « Notre nouveauté en 3 phrases ».
Si un travail fait déjà exactement notre boucle sur du legacy sans tests : STOP, tu me préviens.

=====================================================================
PHASE 2 : DEUX VIVIERS DE BUGS, SÉPARÉS DANS LE TEMPS (semaine 1-2) : GO / NO-GO
=====================================================================

Principe : on remonte l'historique PrestaShop. Les bugs ANCIENS servent à l'entraînement, les bugs RÉCENTS à l'évaluation. Jamais de mélange.

**Date de coupure** : postérieure à la sortie de Gemma 4 et à sa date de connaissance déclarée (chercher dans la model card). Les bugs corrigés après cette date n'ont pas pu être vus par le modèle.

Vivier TEST (évaluation) :
- 30 à 40 bugs corrigés APRÈS la date de coupure
- reproductibles par un parcours d'interface ou un appel HTTP
- correctif localisé (1 à 5 fichiers PHP), pas de faille de sécurité
- une seule branche / version cible, dockerisable

Vivier TRAIN (entraînement) :
- bugs corrigés AVANT la date de coupure, sur la même branche majeure si possible
- critères plus souples : issue claire + PR mergée + correctif localisé
- cible : 300 à 1 000 candidats (le filtrage en perdra beaucoup)
- exclure tout bug qui touche les mêmes lignes qu'un bug du vivier TEST

**Livrables**
- `data/bugs_test.csv`, `data/bugs_train.csv`
  colonnes : id_issue, url_issue, url_pr, commit_avant, commit_correctif, date_correctif, fichiers_touches, zone, parcours_repro, difficulte_estimee
- `data/ETANCHEITE.md` : méthode et résultat du contrôle de non-recouvrement

**Seuil GO** : ≥ 20 bugs TEST valides et ≥ 200 bugs TRAIN exploitables. Sinon, 2 alternatives proposées.

=====================================================================
PHASE 3 : ENVIRONNEMENT REPRODUCTIBLE (semaine 2)
=====================================================================

- Docker Compose : PrestaShop, MariaDB, données de démo
- `reset.sh` : état initial en < 1 min (snapshot base)
- `checkout_bug.sh <id>` : code à l'état d'avant le correctif
- Windows (Docker Desktop / WSL2) et serveur Linux

**Livrable** : `env/` + procédure testée sur 3 bugs TEST et 3 bugs TRAIN.

=====================================================================
PHASE 4 : CHAÎNE « LEGACY → VÉRIFIABLE » (semaines 3-4)
=====================================================================

4.1 Instrumentation : trace des points d'entrée exécutés, activable par variable d'environnement
4.2 Pilotage : Playwright, parcours front et back-office déclarés en YAML
4.3 Capture : HTTP (requêtes / réponses) + SQL ; normalisation des timestamps, tokens CSRF, identifiants auto-incrémentés, ordres non déterministes
4.4 Rejeu : un test par parcours, comparaison au golden master, sortie lisible par un agent (quel test casse, quel diff)

**Livrable** : `replay/` + taux de couverture (fichiers touchés par les correctifs ET par au moins un parcours).

=====================================================================
PHASE 5 : AGENT GEMMA 4 LOCAL + CONDITIONS DE BASE (semaine 4)
=====================================================================

- modèle de base : Gemma 4 12B QAT 4 bits (tient sur 12 Go) ; 26B A4B en option si la RAM suit
- serveur local (llama.cpp ou Ollama) ; contexte fixé et documenté
- scaffold minimal identique pour toutes les conditions ; si les 9 outils officiels sont documentés, on les reprend
- traçage complet de chaque tour : entrée, décision, outil, résultat, temps, tokens

Conditions (sur le vivier TEST) :
- **A** : ticket seul
- **B** : ticket + tests de rejeu
- **C** : ticket + tests de rejeu + outil « contexte PrestaShop » (schéma de base, glossaire : tables `_lang` / `_shop`, déclinaisons, ObjectModel, hooks, overrides, legacy vs Symfony)
  - [ajout 2026-09-24] le glossaire = **vocabulaire du ticket → symboles du code** (`glossaire/glossaire.csv`, voir `docs/GLOSSAIRE.md`) ; apport mesuré par la localisation B vs C

Paramètres figés : température, seed, budget de tours et de tokens, timeout. 3 runs par bug et par condition.

**Livrable** : `agent/`, `runs/` (un dossier par run).

=====================================================================
PHASE 6 : FABRIQUE DE CHEMINS CONDENSÉS (semaines 4-5)
=====================================================================

Uniquement sur le vivier TRAIN. Deux sources de chemins :

6.1 Chemins AUTO (auto-distillation)
- l'agent (condition C) tente chaque bug TRAIN, jusqu'à 4 essais
- une tentative est VALIDÉE si : le test dérivé du correctif officiel passe ET aucun test de rejeu ne casse
- chaque tentative validée est CONDENSÉE : on ne garde que les étapes utiles (recherches qui ont mené au bon fichier, lectures nécessaires, édition finale, vérification), dans le format exact des appels d'outils de l'agent
- la condensation est faite par script déterministe + par Gemma lui-même si besoin ; jamais par un modèle propriétaire

6.2 Chemins RECONSTRUITS (depuis l'historique git)
- pour les bugs TRAIN non résolus par l'agent : on reconstruit un chemin direct plausible à partir du correctif officiel
  ticket → recherche des symboles clés → lecture des fichiers touchés → édition = diff officiel → lancement des tests
- ces chemins sont étiquetés `source=reconstruit` et analysés séparément

Contrôles qualité :
- longueur max d'un chemin : [à fixer selon la mémoire d'entraînement, viser < 8 000 tokens]
- dédoublonnage, contrôle d'étanchéité avec le vivier TEST
- échantillon de 20 chemins relu par moi

**Livrable** : `trajectories/train.jsonl` + `trajectories/STATS.md` (nombre par source, longueur, taux de validation).
**Cible** : ≥ 200 chemins au total, idéalement 500. Si < 150 au 22 octobre : on bascule le fine-tuning en « Perspectives ».

=====================================================================
PHASE 7 : FINE-TUNING QLoRA SUR KAGGLE (semaine 5-6)
=====================================================================

- Gemma 4 12B, QLoRA 4 bits, sur P100 ou T4 16 Go (Unsloth ou PEFT, choix dans DECISIONS.md)
- notebook Kaggle poussé par `kaggle kernels push`, checkpoints réguliers (sessions de 12 h)
- hyperparamètres de départ documentés ; 1 à 3 époques ; un seul run principal, pas de recherche d'hyperparamètres coûteuse
- export de l'adaptateur, conversion pour le serveur local

Conditions supplémentaires (vivier TEST) :
- **D** : condition C + modèle fine-tuné (chemins auto + reconstruits)
- **D-auto** (si le temps le permet) : fine-tuné sur chemins auto seuls → mesure l'apport des chemins reconstruits

Budget GPU Kaggle : consigner les heures consommées dans ETAT.md.

**Livrable** : `training/` (notebook, config, courbes de perte), adaptateur publié sur Hugging Face ou Kaggle Models.

=====================================================================
PHASE 8 : ÉVALUATION (semaine 6)
=====================================================================

ORACLE INDÉPENDANT : pour chaque bug TEST, test « échoue avant / passe après » dérivé du correctif officiel, CACHÉ à l'agent.

Métriques par condition (A, B, C, D) :
- taux de résolution, taux de régression
- temps, tokens, tours par résolution
- classification des échecs à partir des traces (boucles, mauvais fichier, outil inexistant, arrêt prématuré, correctif partiel…)
- 5 cas commentés

**Livrable** : `eval/results.csv`, figures, `eval/ANALYSE.md`. Résultats négatifs rapportés tels quels.

=====================================================================
PHASE 9 : RÉDACTION ET PUBLICATION (semaine 7)
=====================================================================

- Kaggle Writeup, 3 000 mots max : titre, sous-titre, résumé, introduction, travaux et expériences, travaux connexes, citations
- positionnement « Best New Resource » : la chaîne de rejeu (outil) + les viviers de bugs et chemins (données)
- section Perspectives : tests de rejeu comme récompense vérifiable pour RL
- dépôt GitHub public + notebook Kaggle public qui rejoue l'évaluation + adaptateur publié
- auto-évaluation sur les 5 critères (note sur 5 + point faible de chacun)
- soumission au plus tard le **9 novembre**

=====================================================================
JALONS
=====================================================================

| Date | Jalon |
|---|---|
| 1er oct | État de l'art, GO/NO-GO des deux viviers |
| 8 oct | Environnement reproductible |
| 20 oct | Chaîne de rejeu fonctionnelle, runs A/B/C lancés |
| 22 oct | GO/NO-GO fine-tuning (≥ 150 chemins condensés) |
| 29 oct | Adaptateur entraîné, runs D terminés |
| 5 nov | Résultats et figures figés |
| 9 nov | Soumission |
