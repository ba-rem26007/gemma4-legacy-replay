# Kaggle Discussion #745977 : Missing FastAPI test dependencies in evaluation sandbox

> Source : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745977  
> Auteur : babycare & Emilio Dávola (Octobre 2026)  
> Contexte : Découverte majeure sur les échecs de collection pytest (Exit Code 2).

---

## 1. Résumé du problème
Lors de l'évaluation locale des tâches fournies, plusieurs tests FastAPI échouent dès la phase de collection (`pytest --collect-only`) avec une `ModuleNotFoundError`, car certaines dépendances de test (`inline-snapshot`, `dirty-equals`, etc.) ne sont pas incluses dans les 124 wheels fournies par l'organisation.

Au moins **35 tâches FastAPI** sont affectées par ces dépendances manquantes.

---

## 2. Dépendances de test manquantes identifiées

Emilio Dávola a résolu la fermeture complète des dépendances de test pour `fastapi`, `requests` et `rich` sur Python 3.13 :

- `inline-snapshot` (>=0.21.1)
- `dirty-equals` (>=0.9.0)
- `asttokens`, `executing`, `typing-extensions`
- `sqlmodel` (+ `SQLAlchemy`, `greenlet`)
- `flask` (+ `werkzeug`, `blinker`)
- `anyio`, `trio` (+ `outcome`, `sortedcontainers`)
- `PyJWT`, `pyyaml`
- `pwdlib` (+ `argon2-cffi`, `cffi`)
- `python-multipart`, `itsdangerous`, `ujson`, `orjson`
- `email-validator` (+ `dnspython`)
- `uvicorn[standard]` (+ `uvloop`, `httptools`, `watchfiles`, `websockets`, `python-dotenv`)
- `fastapi-cli`
- `pydantic-settings`, `pydantic-extra-types`
- `pytest-httpbin` (+ `httpbin`), `trustme`, `PySocks`, `attrs`

---

## 3. Impact vérifié sur nos propres runs locaux (Preuve directe)

Dans nos résultats locaux (`runs/leaderboard_local/v4/runs/v4r2/`) :
- **`fastapi_14482`** (patch de 437 caractères généré par l'agent) :
  `ERROR collecting tests/test_arbitrary_types.py`
  `ModuleNotFoundError: No module named 'inline_snapshot'` ➔ Exit code 2 (noté 0 alors que le patch est bon !)
- **`fastapi_14360`** (patch de 635 caractères généré par l'agent) :
  `ERROR collecting tests/test_request_param_model_by_alias.py`
  `ModuleNotFoundError: No module named 'dirty_equals'` ➔ Exit code 2 (noté 0 !)

---

## 4. Conséquences & Actions pour V6
1. **Évaluation locale fidèle (Colab)** : Ajouter ce lot de wheels complémentaires dans le dossier wheels du Colab pour que l'évaluation locale ne rejette plus faussement les 35 tâches FastAPI résolues.
2. **Consigne agent (`system.md`)** : Si `pytest` échoue avec `ModuleNotFoundError` sur des bibliothèques de test externes (`inline_snapshot`, `dirty_equals`), l'agent ne doit pas croire que son patch est faux ni tenter de modifier les dépendances, mais valider par exécution directe (`python3 -c "import ...; ..."`).
3. **Exactitude textuelle** : Sur les autres échecs (ex: `fastapi_14479`), l'erreur vient d'une discordance mineure dans le texte de l'exception levée (`AssertionError`). Renforcer l'instruction de recopier au mot près les messages d'erreur spécifiés dans l'issue.
