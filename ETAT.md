# ÉTAT : reprise avec « Lis ETAT.md et reprends »

**Phase courante : 0 (contexte et règles)**. Il reste à coller le texte officiel dans `REGLES.md`.
Référence : `KIT.md` · Décisions : `DECISIONS.md` · Site (derrière auth) : https://kaggle.d1dev.fr
Mis à jour le 2026-09-24.

## Jalons
| Date | Jalon | État |
|---|---|---|
| 1er oct | État de l'art, GO/NO-GO des deux viviers | viviers : collecte faite, split temporel à faire |
| 8 oct | Environnement reproductible | ~70 % en avance (8.1.x) |
| 20 oct | Chaîne de rejeu fonctionnelle, runs A/B/C lancés | — |
| 22 oct | GO/NO-GO fine-tuning (≥ 150 chemins) | — |
| 29 oct | Adaptateur entraîné, runs D terminés | — |
| 5 nov | Résultats et figures figés | — |
| **9 nov** | **Soumission** (officiel : 12 nov., 23:59 UTC) | — |

## Fait (en avance sur le kit)
- **Phase 2 (partiel)** : `bench/select.py` (PR Bug fix mergées ; filtres ≤ 60 lignes, ≤ 3 fichiers, issue avec repro, pas de sécurité, touche l'interface).
  - `bench/bugs.jsonl` : 106 candidats 8.1.x (sur 206 PR).
  - `bench/bugs_all.jsonl` : **435 candidats** sur les 1000 dernières PR, toutes branches (9.0.x 106, develop 97, 8.1.x 97, 9.1.x 55, 8.2.x 54, 8.0.x 14, 9.2.x 12 ; BO 242, FO 70, ? 123).
  - Diffs officiels : `bench/diffs/<pr>.diff`.
- **Phase 3 (partiel)** : clone PrestaShop `bench/ps` (blobless) ; `bench/env/docker-compose.yml` (PrestaShop release + MySQL, 127.0.0.1:8081) ; `bench/checkout.sh <pr> pre|post|patch` (image release la plus proche + fichiers touchés ; **8.1.x uniquement** pour l'instant).
- **Phase 4 (amorce)** : `bench/replay/` en Playwright, avec 3 replays écrits à la main et validés (échec en pre, réussite en post) : #35902, #35384, #35322 → vivier **TRAIN** (2024). Session BO partagée (`auth.setup.js`).
- **Catalogue** : `bench/analyze.py` → `bench/catalog.jsonl` (435 bugs : ticket, résolution, fonctions touchées, `merged_at` de 2023-03 à 2026-09) + `docs/CATALOGUE.md`.
- **Qualification** : `bench/qualify.py` → `bench/qualified.csv` (colonnes du kit + parcours et difficulté estimés) ; `--cutoff` produit directement `data/bugs_test.csv` et `data/bugs_train.csv`. Simulation : TEST largement couvert, **TRAIN juste** (202 à 333 selon la coupure) → élargir l'historique.
- **Glossaire** : format fixé, `glossaire/glossaire.csv` (4 graines), `docs/GLOSSAIRE.md`. `bench/glossary_mine.py` (modes bugs et gitlog) → `glossaire/candidats_gitlog.csv` (1 723 paires, coupure provisoire au 2025-06-01), **à relire par Rémi**.
- Outils : `tmux.sh` (session tmux avec Claude), `kg.sh` (boucle Kaggle), site `site/`.

## Démo 1 (2026-09-24) : voir docs/DEMO.md
- `agent/flow.py` (déroulé fixe, format commun éval/entraînement), `agent/run.py` (API compatible OpenAI, politique `reconstruit`), `bench/eval.py`.
- Chaîne de bout en bout validée sur #35322 et #35902 (patch appliqué, replay OK, aucune régression).
- `trajectories/reconstruct.py` : **573 chemins vérifiés** (coupure provisoire au 2025-06-01, 58 exclus pour étanchéité) → `trajectories/train.jsonl`.
- `training/train_qlora.py` : QLoRA, loss sur les tours assistant uniquement, reprise auto.
- Dépôt privé : https://github.com/ba-rem26007/gemma4-legacy-replay (`./setup.sh` après clone).
- Catalogue étendu : **1 007 bugs** (2019-07 → 2026-09).

## TODO (ordre)
0. [ ] **Clé Gemma dans .env** → runs A/B réels sur la démo.
1. [ ] Phase 0 : texte officiel des 2 compétitions dans `REGLES.md` (Rémi colle le texte), puis signaler les points qui touchent le plan.
2. [ ] Phase 1 : `RELATED.md` (liens vérifiés uniquement) ; date de coupure de Gemma 4 (model card).
3. [ ] Phase 2 : `mergedAt` dans `select.py`, split TEST/TRAIN, `data/bugs_*.csv` (sortir `data/` du `.gitignore` pour les CSV), `data/ETANCHEITE.md`.
4. [ ] Phase 3 : `checkout.sh` pour les images 9.x, `reset.sh` (snapshot de la base), test sur 3 bugs TEST et 3 TRAIN.
5. [ ] Glossaire : relecture de `candidats_gitlog.csv` par Rémi, relance avec la vraie coupure, outil de la condition C.
6. [ ] Phase 5 : `agent/` en déroulé fixe, traces JSONL complètes dès le début (réutilisables en phase 6).

## Infos manquantes
- RAM du PC (4070 Ti) : **À COMPLÉTER**
- Fournisseur de l'API Gemma 4 + `GEMMA_API_KEY` dans `.env`

## Budget GPU Kaggle
| Semaine | Heures | Usage |
|---|---|---|
| — | 0 | — |
