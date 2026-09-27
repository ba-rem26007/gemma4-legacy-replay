# DÉCISIONS

Une entrée par choix structurant : date, décision, raison.

- **2026-09-24 : Terrain = PrestaShop (8.x / 9.x).** Public, énorme, legacy, et Rémi le maîtrise. Des milliers d'issues fermées avec une PR de correction liée.
- **2026-09-24 : Tâche = correction de bugs connus.** Pas de détection de bugs : non mesurable et hors sujet.
- **2026-09-24 : Aucune faille de sécurité.** Exclusion par mots-clés et labels, plus revue manuelle. #35530 exclu (contrôle d'accès secure_key des factures).
- **2026-09-24 : Claude construit la fabrique, pas les données.** Les conditions d'Anthropic interdisent d'entraîner un modèle concurrent sur ses sorties. Les données viennent des correctifs officiels et des réussites de Gemma. Les replays écrits à la main ne servent qu'à valider le harness.
- **2026-09-24 : Split temporel TEST / TRAIN** (kit v2). TEST = corrigés après la coupure Gemma 4. Les 3 bugs pilotes 8.1.x (2024) passent en TRAIN.
- **2026-09-24 : Exécution.** Mise au point sur le serveur (sans GPU) avec l'API Gemma 4. Runs officiels possibles sur le PC (4070 Ti, 12B QAT local) via la même interface. Toutes les traces sont journalisées dès maintenant pour l'entraînement futur.
- **2026-09-24 : Environnement = image officielle de la release la plus proche + remplacement des fichiers touchés.** Beaucoup plus léger que de compiler depuis les sources. Chaque bug est validé par un test qui échoue en pre et passe en post.
- **2026-09-24 : Agent en déroulé fixe** (localiser → lire → éditer → tester). Dans SWE-Gym, l'auto-apprentissage n'a marché qu'avec un déroulé simple et court (7B : 7 % contre 1 % en agent libre).
- **2026-09-24 : Données FT = qualité > quantité.** 2 chemins max par bug, bugs résolus à chaque essai exclus (SWE-smith), masquage de la loss hors tours de l'assistant.
- **2026-09-24 : Site https://kaggle.d1dev.fr derrière auth + noindex** jusqu'à la publication.
- **2026-09-24 : Dossier `/home/elrems/kaggle` conservé.** Le dépôt public s'appellera `gemma4-legacy-replay`.
- **2026-09-24 : Glossaire métier = contenu de la condition C.** Vocabulaire du ticket (FR/EN) → symboles du code. Format unique `glossaire/glossaire.csv` (terme, synonymes, phonetique, symboles, source). Le papier n'utilise pas la colonne phonétique, réservée à la transcription vocale et au RAG souverain, hors papier. Construit à partir des graines de Rémi et d'une extraction sur TRAIN uniquement. Apport mesuré par la localisation B vs C.
- **2026-09-24 : Catalogue déterministe des bugs** (`bench/analyze.py` → `catalog.jsonl`) : ticket, résolution, fonctions touchées, date de merge. Aucun modèle dans l'extraction.
- **2026-09-25 : Condition R = fine-tuning simulé.** Avant tout fine-tuning, on injecte dans le prompt les 2 chemins TRAIN les plus proches (TF-IDF sur le ticket, sans modèle, `agent/fewshot.py`) + glossaire. Comparaison A vs R sur le vivier TEST (oracles cachés).
- **2026-09-25 : Budget ≤ 30 €.** Gemma 4 sur l'API Gemini est gratuit (pas d'offre payante, seulement des quotas) ; garde-fou `--budget-eur` (compteur cumulé `runs/_budget.json`, prix via LLM_PRICE_IN/OUT) pour toute API payante.
- **2026-09-25 : Tests écrits par Claude = oracles uniquement** (jugent un correctif), jamais données d'entraînement.
- **2026-09-25 : Époque 1.6/1.7 → vivier TRAIN** (tickets 1.6 = description de PR, l'ancienne forge Jira n'étant plus en ligne). Oracles par différentiel automatique pre/post (`bench/autooracle.py`).
- **2026-09-25 : Rattrapage de code DÉSACTIVÉ par défaut** (`DRIFT=1` pour l'activer). Recopier les classes PHP postérieures à la release casse le conteneur Symfony (dépendances Composer / services absents de l'image : BO 500/308). Les évaluations faites avec (checkout v2) sont à **réévaluer** (`bench/reeval.py`) après réinstallation des instances.
- **2026-09-27 : Hyperparamètres stricts Gemma 4 pour QLoRA.** `max_grad_norm = 0.1` et `learning_rate = 5e-5` en `bfloat16`. La sensibilité de Gemma 4 au facteur d'échelle d'attention et à la normalisation QK-RMSNorm impose ce seuil de découpage strict pour prévenir les pics numériques lors de l'entraînement sur les chemins condensés.
- **2026-09-27 : Architecture Hybride Non-Hallucinatoire & Edge-First.** Alignement de notre positionnement pour le Writeup : l'agent associe le raisonnement d'un petit modèle ouvert (Gemma 4 E4B/12B) à des vérificateurs déterministes d'exécution (oracles réels PHP en bac à sable Docker). Ce choix garantit le respect de la vie privée (*Privacy-by-Design*, zéro fuite de code d'entreprise) et la faisabilité sur GPU grand public (RTX 4070 Ti 12 Go).

