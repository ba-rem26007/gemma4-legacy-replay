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

## Démarrage Rapide & Reproductibilité Clé en Main

### 1. Rejouer l'évaluation sur le bug cible #40971 (LogoUploader)
```bash
# 1. Préparer l'instance Docker déterministe (port 8082 psbench2)
PSB=2 bash bench/checkout.sh 40971 pre

# 2. Exécuter l'agent Gemma 4 (4B LoRA) en local / offline
python3 agent/run.py --bugs 40971 --condition E

# 3. Évaluer le patch généré avec l'oracle Playwright et les sondes HTTP FO/BO
python3 bench/eval.py 40971
```

### 2. Recalculer instantanément les métriques et tableaux officiels (sans modèle payant)
```bash
python3 bench/results.py
```

### 3. Clause « Zero Proprietary AI Policy » & Intégrité
* **100% Modèles Ouverts & Données Réelles** : Aucun modèle propriétaire fermé (OpenAI GPT-4, Anthropic Claude) n'a été utilisé pour distiller des tokens ou créer des données synthétiques. L'ensemble des 585 trajectoires d'apprentissage provient exclusivement de PRs humaines historiques mergées sur PrestaShop.
* **Fonctionnement Offline** : L'adaptateur de 134 Mo (`training/lora_final/extracted/adapter_model.safetensors`) s'exécute en local sans aucun accès internet sortant actif.
* **Coût Récurrent** : 0,00 € vérifié dans `runs/_budget.json`.
* **Plateforme de Démonstration & Rapport Intégral** : [https://kaggle.d1dev.fr/rapport](https://kaggle.d1dev.fr/rapport) (Accès protégé : `d1dev` / `d1dev`).

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
