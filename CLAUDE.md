# Projet : Gemma 4 × PrestaShop — correction de bugs guidée par tests rejoués

Hackathon Kaggle Gemma 4 Paper Track (soumission interne **9 nov.**, officielle 12 nov. 2026 ; go/no-go FT le 22 oct.).
Thèse : un agent Gemma 4 corrige mieux un **bug PrestaShop connu** quand il dispose de **tests rejoués**
générés automatiquement (clics front/BO → appels enregistrés → replay).

**Reprise : « Lis ETAT.md et reprends ». Une phase du kit à la fois, puis on s'arrête et on présente le livrable.**

- `KIT.md` — kit v2 (9 phases, jalons) : la référence
- `ETAT.md` — phase courante, fait, TODO, budget GPU (à tenir à jour à chaque étape)
- `DECISIONS.md` — chaque choix structurant, daté
- `REGLES.md` — règlement officiel + règles non négociables
- `docs/PROCEDURES.md` — **toutes les commandes** (collecte, checkout, oracles, éval, agent, entraînement)
- `docs/PROTOCOLE.md`, `docs/DONNEES_FT.md`, `docs/PILOTE.md`, `docs/VOCABULAIRE.md`, `docs/DEMO.md`

## Travail à 3 IA (Claude Code, Antigravity, Codex) — règle de coordination (2 oct. 2026)
Trois IA travaillent en parallèle sur ce dépôt (`./tmux.sh` choisit claude, agy ou codex). Pour ne pas s'écraser :
- **Un fichier partagé = un seul propriétaire à la fois.** Avant de modifier un fichier partagé, ajouter en tête d'`ETAT.md`
  (section « EN COURS ») une ligne `EN COURS : <IA> — <fichier> — <heure de Paris>` ; la retirer à la fin.
  Si une autre IA y figure pour ce fichier : ne pas le modifier.
- **Répartition** :
  - **Antigravity (agy)** : piste Leaderboard (`kaggle/`, `harness_transfer/`) ;
  - **Claude Code** : papier (`docs/KAGGLE_FINAL_WRITEUP.md`), évaluations (`runs/`, `bench/`), entraînements, `notebook/verification.ipynb` ;
  - **Codex** : à définir par Rémi (proposition : relectures, tests, revue de code).
- **Writeup : un seul rédacteur.** Les autres IA proposent leurs modifications sous forme de diff dans `docs/propositions/<IA>-<sujet>.diff`.
- **Tout chiffre du papier doit passer `notebook/verification.ipynb`** (recalcul depuis le dépôt, `assert`). Ne jamais réintroduire un
  chiffre retiré pour défaut de source (voir `ETAT.md`, recheck pré-soumission).
- Avant de commencer : `git pull`, lire la section « EN COURS » d'`ETAT.md` ; committer petit et souvent.

## Règles clés (voir REGLES.md)
- Tâche = **corriger** un bug connu. Pas de chasse aux bugs, **jamais de sécurité**.
- **Claude construit la fabrique, pas son contenu** : aucune sortie de modèle propriétaire dans les données d'entraînement.
- **Étanchéité** TEST / TRAIN (split temporel sur la date de coupure de Gemma 4).
- Aucun code privé, aucune citation sans lien vérifié, demander avant toute action destructive ou tout téléchargement > 5 Go.

## Architecture
- **Ce serveur** (sd-187494, sans GPU) : Docker PrestaShop, replay, mise au point de l'agent via l'**API Gemma 4** (`GEMMA_API_KEY` dans `.env`).
- **PC de Rémi** (4070 Ti 12 Go) : runs officiels possibles en 12B QAT local, via la même interface. Traces complètes journalisées dès le début.
- **Kaggle** (P100/T4 16 Go, ~30 h/sem.) : uniquement fine-tuning QLoRA de Gemma 12B. Pas de Docker.

## Arborescence
- `tmux.sh` — lance/reprend la session tmux `kaggle` avec Claude (`claude --continue`)
- `kg.sh` — boucle Kaggle : `init | push | wait | output | run | submit` (lit `.env` : `COMP`, `KAGGLE_USER`)
- `notebook/main.ipynb` — notebook Kaggle ; `/kaggle/working/` revient dans `output/`
- `bench/select.py` → `bench/bugs.jsonl` (+ `bench/diffs/<pr>.diff` = correctif officiel)
- `bench/ps/` — clone blobless PrestaShop (branche 8.1.x supprimée upstream, commits accessibles)
- `bench/env/docker-compose.yml` — PrestaShop release + MySQL, `127.0.0.1:8081`
- `bench/checkout.sh <pr> pre|post|<patch.diff>` — image release la plus proche + fichiers touchés dans l'état voulu
- `bench/replay/` — Playwright : `run.sh <pr>`, `<pr>/setup.sql`, `<pr>/replay.spec.js`
- `site/` — https://kaggle.d1dev.fr (nginx + Traefik, auth+noindex ; affiche README.md et docs/ en direct)
- À venir : `bench/eval.py`, `bench/agent.py`, `bench/runs/<run>/`

## Commandes
```
./tmux.sh
bench/checkout.sh 35902 pre && bench/replay/run.sh 35902    # doit échouer
bench/checkout.sh 35902 post && bench/replay/run.sh 35902   # doit passer
```
BO : http://localhost:8081/admin-dev (demo@prestashop.com / prestashop_demo) — tunnel SSH `-L 8081:localhost:8081`.
