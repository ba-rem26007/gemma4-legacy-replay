# Matrice paramètres × résultats (générée par `python3 tools/matrix.py`)

Source : tous les dossiers `runs/2026*` (verdicts réévalués si disponibles ; « résolu » = oracle OK et aucune régression).
Les runs partiels (interrompus puis repris dans un autre dossier) apparaissent séparément : pour les chiffres officiels du
papier (essais fusionnés) voir `docs/RESULTATS.md`, `docs/RESULTATS_E4B.md` et `notebook/verification.ipynb`.

## Synthèse par expérience (TEST et validation TRAIN ; runs d'au moins 5 bugs)

| Jeu | Modèle | Cond. | Adaptateur | Agent | Lecture (lignes) | Runs (bugs traités) | Résolus / run | Taux moyen | Bon fichier moy. | Régr. |
|---|---|---|---|---|---|---|---|---|---|---|
| TEST | gemma-4-26b-a4b-it | A | aucun | `62f3f67` | 260 | 1 (8) | 2 | 25.0% | 75% | 0 |
| TEST | gemma-4-26b-a4b-it | A | aucun | `f7dcbdc` | 260 | 1 (25) | 3 | 12.0% | 60% | 0 |
| TEST | gemma-4-31b-it | A | aucun | `e16051f` | 260 | 1 (9) | 2 | 22.2% | 44% | 0 |
| TEST | gemma-4-31b-it | A | aucun | `e23cb3e` | 260 | 4 (24, 33, 33, 33) | 10, 13, 15, 11 | 40.0% | 61% | 0 |
| TEST | gemma-4-31b-it | B | aucun | `4f649d9` | 260 | 3 (33, 26, 26) | 15, 8, 8 | 35.7% | 52% | 0 |
| TEST | gemma-4-31b-it | B | aucun | `62f3f67` | 260 | 2 (10, 10) | 4, 3 | 35.0% | 70% | 0 |
| TEST | gemma-4-31b-it | C | aucun | `5bbc491` | 260 | 1 (33) | 13 | 39.4% | 55% | 1 |
| TEST | gemma-4-31b-it | C | aucun | `e6cd662` | 260 | 1 (33) | 11 | 33.3% | 55% | 0 |
| TEST | gemma-4-31b-it | O | aucun | `f7dcbdc` | 260 | 3 (29, 16, 5) | 13, 6, 2 | 40.8% | 60% | 3 |
| TEST | gemma-4-31b-it | R | aucun | `e16051f` | 260 | 1 (5) | 3 | 60.0% | 80% | 0 |
| TEST | gemma-4-31b-it | R | aucun | `e23cb3e` | 260 | 4 (28, 33, 33, 33) | 11, 12, 14, 11 | 37.9% | 60% | 0 |
| TEST | gemma-4-e4b-base | E | aucun | `1e75370` | 120 | 3 (33, 33, 33) | 3, 4, 4 | 11.1% | 44% | 3 |
| TEST | gemma-4-e4b-lora-v15 | E | v15 | `1e75370` | 120 | 3 (33, 33, 33) | 1, 1, 2 | 4.0% | 36% | 3 |
| TEST | gemma-4-e4b-lora-v16 | E | v16 | `1e75370` | 120 | 3 (33, 33, 33) | 0, 0, 0 | 0.0% | 33% | 3 |
| TEST | gemma-4-ft | E | v15 | `4f649d9` | 260 | 1 (33) | 4 | 12.1% | 42% | 1 |
| TRAIN-validation | gemma-4-e4b-base | E | aucun | `419f5c4` | 120 | 2 (30, 28) | 3, 1 | 6.8% | 51% | 4 |
| TRAIN-validation | gemma-4-e4b-lora-v16 | E | v16 | `419f5c4` | 120 | 2 (30, 6) | 1, 0 | 1.7% | 52% | 3 |
| TRAIN-validation | gemma-4-e4b-lora-v17 | E | v17 | `419f5c4` | 120 | 2 (30, 17) | 1, 1 | 4.6% | 24% | 4 |

## Paramètres fixes (tous les runs)

Déroulé fixe LOCALISER → LIRE (≤ 3 fichiers) → ÉDITER (SEARCH/REPLACE) → test ; 2 reprises (`--retries 2`) ;
température 0,2 ; recherche : 25 fichiers max. Conditions : A ticket seul · R +2 correctifs TRAIN · C +glossaire ·
B +test de repro écrit par Gemma comme retour · O +oracle comme retour (plafond) · E +règles métier/glossaire/spec (petits modèles).

## Détail par dossier de run

| Run | Jeu | Modèle | Cond. | Adapt. | Agent | Lecture | Bugs | Résolus | Bon fichier | Patch appliqué | Régr. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20260925-000132-B | TRAIN-boucle | reconstruit | B | aucun | `b208a3f` | 260 | 3 | 3 | 3 | 3 | 0 |
| 20260925-053823-A | TRAIN-boucle | gemma-4-31b-it | A | aucun | `648a450` | 260 | 2 | 1 | 1 | 1 | 0 |
| 20260925-055234-B | TRAIN-boucle | gemma-4-31b-it | B | aucun | `648a450` | 260 | 3 | 0 | 2 | 2 | 0 |
| 20260925-092934-R | TEST | gemma-4-31b-it | R | aucun | `e16051f` | 260 | 5 | 3 | 4 | 4 | 0 |
| 20260925-092935-A | TEST | gemma-4-31b-it | A | aucun | `e16051f` | 260 | 9 | 2 | 4 | 3 | 0 |
| 20260925-101441-A | TEST | gemma-4-31b-it | A | aucun | `e23cb3e` | 260 | 24 | 10 | 16 | 15 | 0 |
| 20260925-101441-R | TEST | gemma-4-31b-it | R | aucun | `e23cb3e` | 260 | 28 | 11 | 14 | 18 | 0 |
| 20260925-114612-A | TEST | gemma-4-31b-it | A | aucun | `e23cb3e` | 260 | 33 | 13 | 20 | 22 | 0 |
| 20260925-114712-R | TEST | gemma-4-31b-it | R | aucun | `e23cb3e` | 260 | 33 | 12 | 19 | 23 | 0 |
| 20260925-142912-A | TEST | gemma-4-31b-it | A | aucun | `e23cb3e` | 260 | 33 | 15 | 20 | 21 | 0 |
| 20260925-143833-R | TEST | gemma-4-31b-it | R | aucun | `e23cb3e` | 260 | 33 | 14 | 21 | 22 | 0 |
| 20260925-165642-A | TEST | gemma-4-31b-it | A | aucun | `e23cb3e` | 260 | 33 | 11 | 19 | 23 | 0 |
| 20260925-171642-R | TEST | gemma-4-31b-it | R | aucun | `e23cb3e` | 260 | 33 | 11 | 23 | 20 | 0 |
| 20260926-022702-B | TEST | gemma-4-31b-it | B | aucun | `62f3f67` | 260 | 10 | 4 | 8 | 6 | 0 |
| 20260926-035528-B | TEST | gemma-4-31b-it | B | aucun | `62f3f67` | 260 | 10 | 3 | 6 | 5 | 0 |
| 20260926-052040-A | TEST | gemma-4-26b-a4b-it | A | aucun | `62f3f67` | 260 | 8 | 2 | 6 | 3 | 0 |
| 20260926-052040-O | TEST | gemma-4-31b-it | O | aucun | `62f3f67` | 260 | 4 | 3 | 3 | 4 | 0 |
| 20260926-065152-A | TEST | gemma-4-26b-a4b-it | A | aucun | `f7dcbdc` | 260 | 25 | 3 | 15 | 9 | 0 |
| 20260926-065152-O | TEST | gemma-4-31b-it | O | aucun | `f7dcbdc` | 260 | 29 | 13 | 16 | 18 | 2 |
| 20260926-103202-C | TEST | gemma-4-31b-it | C | aucun | `5bbc491` | 260 | 33 | 13 | 18 | 24 | 1 |
| 20260926-134839-C | TEST | gemma-4-31b-it | C | aucun | `e6cd662` | 260 | 33 | 11 | 18 | 18 | 0 |
| 20260926-182408-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `9c93d24` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260926-184142-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `9c93d24` | 260 | 1 | 1 | 0 | 1 | 0 |
| 20260926-190632-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `9c93d24` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260926-191905-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `9c93d24` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260926-193601-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `9c93d24` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260926-193740-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-195641-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-200233-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260926-201731-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-203717-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260926-205706-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260926-212516-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-220642-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260926-221333-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260926-222343-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-223141-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-224923-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260926-234331-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-003701-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-011259-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-020217-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-043441-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-044515-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-050733-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260927-055648-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-082126-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-090847-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-095639-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-110828-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-113003-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-114538-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260927-124311-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-133050-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-135509-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-143102-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-144650-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-145640-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-150533-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-154406-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-155521-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-161016-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-163942-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 0 | 1 | 0 |
| 20260927-170159-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-170920-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-171602-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-172156-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-173447-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-182538-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 0 | 1 | 0 |
| 20260927-183837-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-184304-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-185001-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260927-185627-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-191213-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260927-195645-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-200152-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-211908-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-214755-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-222215-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260927-223951-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-224021-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260927-230529-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260927-235125-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-012431-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-012800-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-013829-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260928-014720-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-025910-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-030810-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260928-032617-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260928-034424-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-035002-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-040035-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-040121-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-043923-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260928-053849-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-071755-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-081449-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-082530-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-083100-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260928-084652-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-090119-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260928-091230-B | TEST | gemma-4-31b-it | B | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260928-091433-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-092011-B | TEST | gemma-4-31b-it | B | aucun | `4f649d9` | 260 | 33 | 15 | 17 | 19 | 0 |
| 20260928-093101-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260928-103417-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-104314-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260928-105012-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-110708-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 0 | 1 | 0 |
| 20260928-110909-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-111851-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 1 |
| 20260928-112304-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260928-122946-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-130023-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-131032-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-143458-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-151701-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-153906-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-161425-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 0 | 0 |
| 20260928-162147-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 1 | 1 | 0 |
| 20260928-163213-D | TEST | gemma-4-ft | D | v15 | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-165710-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-170254-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-171805-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 0 | 0 | 1 | 0 |
| 20260928-172541-O | TRAIN-boucle | gemma-4-31b-it | O | aucun | `4f649d9` | 260 | 1 | 1 | 1 | 1 | 0 |
| 20260928-173019-D | TEST | gemma-4-ft | D | v15 | `4f649d9` | 260 | 2 | 0 | 1 | 0 | 0 |
| 20260928-175253-E | TEST | gemma-4-ft | E | v15 | `4f649d9` | 260 | 1 | 0 | 0 | 0 | 0 |
| 20260928-175551-E | TEST | gemma-4-ft | E | v15 | `4f649d9` | 260 | 33 | 4 | 14 | 18 | 1 |
| 20260930-101308-A | TEST | gemma-4-31b-it | A | aucun | `1e75370` | 120 | 1 | 1 | 1 | 1 | 0 |
| 20261001-152110-E | TEST | gemma-4-e4b-base | E | aucun | `1e75370` | 120 | 1 | 0 | 1 | 1 | 1 |
| 20261001-152112-E | TEST | gemma-4-e4b-lora-v15 | E | v15 | `1e75370` | 120 | 1 | 0 | 1 | 1 | 0 |
| 20261001-152114-E | TEST | gemma-4-e4b-lora-v16 | E | v16 | `1e75370` | 120 | 1 | 0 | 1 | 1 | 0 |
| 20261001-153951-E | TEST | gemma-4-e4b-base | E | aucun | `1e75370` | 120 | 33 | 3 | 16 | 18 | 1 |
| 20261001-153953-E | TEST | gemma-4-e4b-lora-v15 | E | v15 | `1e75370` | 120 | 33 | 1 | 12 | 18 | 2 |
| 20261001-153955-E | TEST | gemma-4-e4b-lora-v16 | E | v16 | `1e75370` | 120 | 33 | 0 | 11 | 17 | 3 |
| 20261001-184740-E | TEST | gemma-4-e4b-base | E | aucun | `1e75370` | 120 | 33 | 4 | 13 | 13 | 0 |
| 20261001-184742-E | TEST | gemma-4-e4b-lora-v15 | E | v15 | `1e75370` | 120 | 33 | 1 | 13 | 16 | 0 |
| 20261001-184744-E | TEST | gemma-4-e4b-lora-v16 | E | v16 | `1e75370` | 120 | 33 | 0 | 11 | 20 | 0 |
| 20261001-210006-E | TEST | gemma-4-e4b-base | E | aucun | `1e75370` | 120 | 33 | 4 | 15 | 19 | 2 |
| 20261001-215229-E | TEST | gemma-4-e4b-lora-v16 | E | v16 | `1e75370` | 120 | 33 | 0 | 11 | 17 | 0 |
| 20261001-220448-E | TEST | gemma-4-e4b-lora-v15 | E | v15 | `1e75370` | 120 | 33 | 2 | 11 | 19 | 1 |
| 20261002-062346-A | TEST | gemma-4-31b-it | A | aucun | `1e75370` | 120 | 1 | 1 | 1 | 1 | 0 |
| 20261002-080237-A | TEST | gemma-4-31b-it | A | aucun | `1e75370` | 120 | 1 | 1 | 1 | 1 | 0 |
| 20261002-082406-B | TEST | gemma-4-31b-it | B | aucun | `4f649d9` | 260 | 26 | 8 | 12 | 16 | 0 |
| 20261002-082409-B | TEST | gemma-4-31b-it | B | aucun | `4f649d9` | 260 | 26 | 8 | 15 | 16 | 0 |
| 20261002-082412-O | TEST | gemma-4-31b-it | O | aucun | `f7dcbdc` | 260 | 16 | 6 | 7 | 9 | 0 |
| 20261002-103752-E | TRAIN-validation | gemma-4-e4b-base | E | aucun | `419f5c4` | 120 | 30 | 3 | 18 | 15 | 0 |
| 20261002-103755-E | TRAIN-validation | gemma-4-e4b-lora-v16 | E | v16 | `419f5c4` | 120 | 30 | 1 | 11 | 9 | 3 |
| 20261002-103758-E | TRAIN-validation | gemma-4-e4b-lora-v17 | E | v17 | `419f5c4` | 120 | 30 | 1 | 11 | 15 | 2 |
| 20261002-124423-E | TRAIN-validation | gemma-4-e4b-lora-v16 | E | v16 | `419f5c4` | 120 | 6 | 0 | 4 | 3 | 0 |
| 20261002-124653-E | TRAIN-validation | gemma-4-e4b-base | E | aucun | `419f5c4` | 120 | 28 | 1 | 12 | 11 | 4 |
| 20261002-130616-E | TRAIN-validation | gemma-4-e4b-lora-v17 | E | v17 | `419f5c4` | 120 | 4 | 0 | 2 | 1 | 0 |
| 20261002-132120-E | TRAIN-validation | gemma-4-e4b-lora-v17 | E | v17 | `419f5c4` | 120 | 17 | 1 | 2 | 7 | 2 |
| 20261002-132120-O | TEST | gemma-4-31b-it | O | aucun | `f7dcbdc` | 260 | 5 | 2 | 4 | 5 | 1 |
| 20261002-144755-A | TRAIN-boucle | gemma-4-31b-it | A | aucun | `419f5c4` | 120 | 4 | 0 | 4 | 2 | 0 |
