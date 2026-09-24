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
