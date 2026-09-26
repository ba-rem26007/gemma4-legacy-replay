# Gemma 4 × PrestaShop : corriger de vrais bugs grâce à des tests rejoués

Projet pour le hackathon Kaggle **Gemma 4**.

**Question** : un petit modèle ouvert (Gemma 4) corrige-t-il mieux un bug réel d'un gros projet legacy (PrestaShop) quand il dispose d'un **vérificateur** ? Ici, le vérificateur, ce sont des tests de bout en bout rejoués, générés automatiquement à partir de clics sur la boutique.

**Cadrage** : un domaine devient automatisable quand le modèle connaît assez le domaine et que la tâche fournit un signal vérifiable. Chez nous, la chaîne de replay joue le rôle du **vérificateur**, et l'outil de contexte PrestaShop apporte la **connaissance métier**.

## Questions de recherche
- **Q1** : les tests de replay générés améliorent-ils le taux de résolution et réduisent-ils les régressions ?
- **Q2** : un contexte PrestaShop (schéma, glossaire) fourni par un outil aide-t-il ?
- **Q3** : un fine-tuning sur des chemins condensés, validés par les replays, améliore-t-il un petit modèle local sur des bugs jamais vus ?

## En bref
- **Bench** : des bugs PrestaShop 8.1.x **déjà corrigés** en amont (la PR officielle sert de vérité terrain), rejoués en Docker.
- **Conditions** : A = ticket seul · B = + tests de replay · C = + contexte PrestaShop · D = C + modèle fine-tuné · R = fine-tuning simulé (corrections similaires injectées).
- **Split temporel** : évaluation sur des bugs corrigés après la coupure de Gemma 4, entraînement sur les plus anciens, avec contrôle d'étanchéité.
- **Agent** : déroulé fixe (localiser → lire → éditer → tester), pas d'agent libre.
- **Données** : aucun contenu généré par un modèle propriétaire. Uniquement les correctifs officiels et les réussites de Gemma.
- **Fine-tuning** : QLoRA de Gemma 12B sur des chemins condensés (Kaggle, 16 Go).

## Documents
- [Protocole](docs/PROTOCOLE.md)
- [Pilote : 3 bugs validés](docs/PILOTE.md)
- [Données de fine-tuning](docs/DONNEES_FT.md)
- [**Plan pour gagner**](docs/PLAN.md)
- [**Procédures** (commandes pas à pas)](docs/PROCEDURES.md) · [Enregistrer une reproduction (expert)](docs/ENREGISTREMENT.md)
- [Résultats](docs/RESULTATS.md) · [Taxonomie des échecs](docs/ECHECS.md)
- [Vocabulaire](docs/VOCABULAIRE.md) · [Glossaire métier](docs/GLOSSAIRE.md) · [Catalogue des bugs](docs/CATALOGUE.md)
- [État](ETAT.md) · [Décisions](DECISIONS.md) · [Règles](REGLES.md) · [Kit](KIT.md)

## Démarrage (après clone)
```bash
./setup.sh                                   # clone PrestaShop (~1 Go) + Playwright
cp .env.local.example .env                   # PC : Gemma en local (Ollama), runs officiels + modèle fine-tuné
# ou cp .env.api.example .env                # API Google AI Studio (mise au point) + GEMMA_API_KEY
```
- **Fine-tuning sur ton GPU** : voir [training/README.md](training/README.md). Les données sont déjà dans `trajectories/train.jsonl` : 569 chemins vérifiés.
- **Agent + évaluation** (nécessite Docker) : `bench/checkout.sh <pr> pre`, puis `python3 agent/run.py --bugs 35902 --condition B`.

## Structure
```
bench/select.py        sélection des bugs (GitHub)
bench/checkout.sh      PrestaShop en Docker, état pre / post / patch
bench/replay/          tests Playwright de replay (un dossier par bug)
bench/analyze.py       catalogue (ticket, résolution, fonctions touchées) → catalog.jsonl
bench/qualify.py       parcours / difficulté, split TEST/TRAIN → data/bugs_*.csv
bench/eval.py          évalue un patch (anti-régression + oracle) ; reeval.py sans LLM
bench/test_pool.py     vivier TEST 9.1.x → data/bugs_test.csv
bench/autooracle.py    oracles par différentiel pre/post (résultat négatif)
bench/replay/<pr>/     oracle*.spec.js (caché à l'agent), replay*.spec.js, setup.sql, STATUS
agent/fewshot.py       condition R : exemples TRAIN similaires (TF-IDF)
agent/flow.py          déroulé fixe localiser → lire → éditer → tester (format commun éval/entraînement)
agent/run.py           agent Gemma (API compatible OpenAI), trajectoires → runs/
trajectories/          chemins reconstruits vérifiés (train.jsonl, STATS.md)
training/              QLoRA (train_qlora.py)
glossaire/             glossaire métier (condition C)
kg.sh                  boucle Kaggle (push / wait / output)
```
