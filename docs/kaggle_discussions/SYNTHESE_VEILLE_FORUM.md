# 🧠 Synthèse Stratégique des Discussions Kaggle — Gemma 4 Developer Agent

> *Basée sur le crawl exhaustif des 126 discussions officielles du forum Kaggle (Octobre 2026).*  
> *Réf. locale : `docs/kaggle_discussions/` et `tools/crawl_kaggle_discussions.py`.*

---

## 🎯 1. Vue d'ensemble du Benchmark Kaggle

- **Nombre réel de tâches au Leaderboard Public** : **Exactement 58 tâches** (démontré mathématiquement par l'analyse des centièmes tronqués du LB, topic `#743506`).
- **Score et Tâches Résolues** :
  - `0.06` (notre V4 / V2) = **3 à 4 tâches résolues**.
  - `0.12` (notre **V5 actuelle**, rang 553ᵉ) = **7 tâches résolues**.
  - `0.15` (top 15 mondial) = **9 tâches résolues**.
  - `0.17` (top 10 mondial) = **10 tâches résolues**.
  - `0.24` (n° 1 mondial, ТониСтарк) = **14 tâches résolues**.
- **Distance au Top 10 mondial** : seulement **3 tâches supplémentaires** à débloquer !

---

## ⚠️ 2. Les 6 Pièges Mortels identifiés sur le Forum

### 1. Le massacre de contexte par `search_similar_code` (Topic `#744577`)
- **Problème** : `run_command` et `read_file` sont plafonnés à 5 000 caractères, mais `search_similar_code` renvoyait le code complet des 10 meilleurs nœuds sans limite. Sur FastAPI, la classe `FastAPI` fait 130 000 caractères et `APIRouter` 110 000 caractères. Un seul appel dépassait les 32 768 tokens de contexte, provoquant une `ContextWindowExceededError` et **rejetant le patch même s'il était déjà écrit**.
- **Notre parade V5 (validée)** : Suppression complète de tous les outils de graphe et d'embeddings.

### 2. Le double encodage JSON des sorties d'outils (Topic `#744272`)
- **Problème** : Dans la pile `swegemma` + `adk-submission` + `vLLM 0.19.1`, les retours d'outils arrivent encodés deux fois en JSON. Le modèle échoue à 74 % sur `edit_file` parce qu'il recopie des chaînes échappées avec des backslashes ou fermées par des backticks parasites.
- **Notre parade V5 (validée)** : Édition chirurgicale par script Python heredoc dans `run_command` (`python3 - <<'EOF' ... p.write_text(...)`), testée en rejeu à **82 % de succès** contre 4 % pour `edit_file` standard.

### 3. Les outils non déclarés ou mal formés (Topic `#745028`)
- **Problème** : Si le prompt contient des exemples comme `run_command("python3 ...")`, le modèle invente des noms d'outils. Tout appel à un outil non déclaré dans `agent.yaml` provoque un arrêt immédiat de la tâche avec rejet du patch.
- **Notre parade V5 (validée)** : Prompts en prose pure, aucun exemple de pseudo-code, déclaration stricte des outils dans `agent.yaml`.

### 4. Le bug critique de LoRA dans vLLM 0.19.1 (Topics `#743508` & `#744331`)
- **Problème** : vLLM enregistre les couches du décodeur sous deux noms (`layers.N` et l'alias YOCO `self_decoder.decoder_layers.N`). Lors de l'activation de l'adaptateur, vLLM applique le LoRA sur le premier nom, puis le supprime sur le second alias (`reset_lora`), **effaçant silencieusement les poids LoRA**. De plus, activer LoRA réduit le cache KV à ~7,6k tokens.
- **Notre stratégie** : Aucun adaptateur LoRA soumis à l'aveugle sur Kaggle tant que ce bug n'est pas patché en amont.

### 5. Les dépendances de test manquantes dans la sandbox (Topic `#745775` & `#745850`)
- **Problème** : Au moins **35 tâches FastAPI** échouent dès la phase de collection (`pytest --collect-only`) avec `ModuleNotFoundError` (`inline-snapshot`, `dirty-equals`).
- **Constat chez nous** : Deux de nos tâches locales (`fastapi_14482` et `fastapi_14360`) étaient parfaitement codées par l'agent mais notées 0 à cause de ces imports absents dans le sandbox local.
- **Notre levier V6** : Injecter le complément de wheels sur Colab et immuniser le prompt contre les faux `ModuleNotFoundError`.

### 6. Le piège d'`eval_config.yaml` et des timeouts prématurés (Topics `#743063` & `#743365`)
- **Problème** : Mettre `max_time_minutes: 6` sur 58 tâches disposant de 12h (soit ~12 min/tâche) tue toutes les tâches à mi-parcours.
- **Notre parade V5 (validée)** : Suppression totale d'`eval_config.yaml` ➔ **le score est passé de 0.06 à 0.12** !

---

## 🏆 3. Les Bonnes Pratiques pour atteindre le Top 10 (Score ≥ 0.17)

1. **Exactitude chirurgicale des noms et messages d'erreurs** :
   - Les tests de vérification comparent souvent au caractère près les messages d'exceptions (ex: `AssertionError: match="..."`).
   - Règle dans `system.md` : recopier au mot près les chaînes d'erreurs et types d'exceptions demandés.
2. **Température basse stabilisée (`T=0.2`)** :
   - Évite les erreurs de syntaxe dans les scripts Python générés et fiabilise les assertions `assert s.count(old) == 1`.
3. **Validation résiliente** :
   - Si `pytest` échoue sur un import manquant (`inline_snapshot`, `dirty_equals`), l'agent ne doit pas modifier `pyproject.toml` mais valider par `python3 -c "import ...; ..."` direct.
4. **Discipline de soumission précoce** :
   - Dès que le code compile (`python3 -m py_compile`) et que le test ciblé passe, nettoyer `/tmp` et appeler `submit_patch()` immédiatement sans continuer à boucler.
