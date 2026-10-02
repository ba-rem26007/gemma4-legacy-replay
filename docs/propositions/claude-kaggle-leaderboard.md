# Proposition Claude Code → piste Leaderboard (2 oct. 2026)

Enquête en lecture seule (4 angles + synthèse + critique sceptique). Le propriétaire de `kaggle/` (Antigravity) applique ou refuse et l'indique en fin de document.

# Kaggle « Gemma 4 Developer Agent » : ce n'est pas foutu, mais on tire à l'aveugle

## 1. Pourquoi on est à 0,06

| # | Constat | Source |
|---|---|---|
| 1 | 0,06 veut dire 4 tâches réussies sur les 58 du LB public. La médiane est à 0,08 (5/58), la valeur la plus fréquente aussi (248 équipes). Le top 10 est à 0,15 (9/58), le n° 1 à 0,24 (14/58). | `/home/elrems/kaggle/runs/leaderboard/2026-10-02.csv` (recalculé : 1 279 équipes, 672 au-dessus de nous). Taille de 58 tâches : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743506 |
| 2 | Le raisonnement est complètement coupé : `include_thoughts: false` envoie `enable_thinking: false` à vLLM, et le `thinking_budget` de 4096 est ignoré. | `/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:8` ; https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745059 |
| 3 | Nos prompts écrivent les commandes comme des appels d'outil (`run_command("…")`), 11 fois. Selon une mesure publique, ce style fait passer les noms d'outil mal formés de 5 % à 31 %. Or un outil inconnu donne un patch vide, donc 0 sur la tâche. | `/home/elrems/kaggle/kaggle/submission/prompts/system.md:20-42` ; https://github.com/damsolanke/gemma4-swe-kit ; https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028 |
| 4 | `search_similar_code` est exposé à l'agent principal et à l'analyseur. Il peut renvoyer plus de 100 000 caractères, donc dépasser le contexte de 32 k, et la tâche finit avec un patch vide, même quand le correctif était déjà écrit. Le script de repro est imposé dans `/tmp`, que `write_file` refuse. | `/home/elrems/kaggle/kaggle/submission/agent.yaml:12-14`, `/home/elrems/kaggle/kaggle/submission/prompts/system.md:22-24` ; https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744577 et https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744692 |
| 5 | On n'a jamais fait tourner l'agent en local. `eval_task.py` applique un patch fourni et lance pytest, il ne lance pas d'agent. La v2 ne change que 4 lignes, non commitées. La skill « replay » n'est jamais chargée (pas de clé `skills:`). | `/home/elrems/kaggle/harness_transfer/scripts/eval_task.py:21,71,87-91` ; `git diff kaggle/submission/prompts/analyzer.md` |

Deux chiffres des rapports précédents sont faux :
- « 0,06 ≈ 8 tâches sur 129 » : c'est 4 sur 58.
- « 20 tâches d'écart avec le n° 1 » : c'est 10.

## 2. Est-ce rattrapable ?

| Point | Réalité |
|---|---|
| Échéance du Leaderboard | **2 déc. 2026 à 23:59 UTC** (fusions d'équipes jusqu'au 25 nov.). Le 12 nov. est l'échéance de la piste Paper, pas de celle-ci. |
| Quota | 1 soumission par jour, déjà utilisée aujourd'hui. Il reste environ 40 soumissions d'ici le 12 nov. et environ 60 d'ici le 2 déc. On choisit 2 soumissions finales. Un échec de la plateforme consomme aussi le quota du jour. |
| Bruit | Environ ±2 tâches par soumission (écart-type binomial). Un 0,06 contre un 0,10 ne prouve rien. |
| Écart à combler | **+1 tâche pour la médiane, +3 pour la masse à 0,12, +5 pour le top 10.** |
| Ce qui est prouvé publiquement | Aucune méthode publique ne dépasse 0,12 de façon démontrée. Le 0,15 public est une copie octet pour octet d'un bundle à 0,12, donc du bruit (https://www.kaggle.com/code/matterhorn3838/gemma-4-superagent). |
| Rappel | Les tâches cachées viennent de dépôts privés. Les 129 tâches publiques (fastapi, rich, requests) servent seulement d'entraînement. Le score local est mal corrélé au LB (https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744319). |

**Verdict : rejoindre la masse (0,10 à 0,12) est réaliste. Le top 10 est possible mais incertain. Aller au-delà de 0,15 relève du pari (thinking, LoRA), que personne n'a démontré publiquement.**

## 3. Leviers, classés par gain attendu et effort

| Rang | Levier | Gain attendu | Effort | Preuve |
|---|---|---|---|---|
| 1 | **Évaluation locale de l'agent** (gemma4-swe-kit plus API Gemma 31B), uniquement sur les tâches dont le patch de référence passe chez nous. On compte les patchs vides, les dépassements de contexte, les outils mal formés, les boucles et la durée. On ne cherche pas à prédire le score. | Indirect, mais rend tout le reste mesurable | 2 à 3 j | https://github.com/damsolanke/gemma4-swe-kit ; en local, 54 tâches FastAPI sur 67 échouent même avec le patch de référence (wheels) : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743973 |
| 2 | **Prompts réécrits en prose courte** : aucun pseudo-appel, repro optionnelle via heredoc dans `run_command`, `{problem_description}` dans les deux agents, respect exact des noms d'API, messages et exceptions demandés, interdiction de modifier les tests existants. | +1 à 3 tâches | 0,5 j | Black Cat v8 (règles longues) : 0,05, contre 0,10 à 0,12 pour les prompts courts (notebook Superagent, cellule 2) ; 31 % contre 5 % d'outils mal formés (gemma4-swe-kit) |
| 3 | **Retirer `search_similar_code`** (et les autres outils de graphe), plafonner l'analyseur, ou l'enlever (agent unique). | +0,5 à 2 tâches | 0,5 h | https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744577, https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744692 ; grep trouve le bon fichier 67 fois sur 129, contre 35 pour les embeddings (https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744040) ; agent unique 14/44 contre 13/44 (https://www.kaggle.com/code/dmitriigluzdov/gemma-4-measure-before-you-tune) |
| 4 | **Repartir d'un bundle public à 0,12** (Rozen ou Black Cat « anchor ») comme base, plutôt que du nôtre. | On rejoint la masse | 0,5 j | https://www.kaggle.com/code/lucifer19/black-cat-swe-agent-pack-instinct ; notebook Superagent |
| 5 | **Lecture ciblée** : d'abord le plan du fichier (`grep -n "def \|class"`), puis `read_file` sur la plage exacte, sans relire une plage déjà lue. Transfert de notre recherche : quand le fichier corrigé est lu, 55,7 % de réussite, sinon 13,2 %. | +0 à 2 tâches (non mesuré) | 0,5 h | `/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:107-126` ; `/home/elrems/kaggle/docs/DIAGNOSTIC_NON_RESOLUS.md:14-41` |
| 6 | **Thinking activé** (`include_thoughts: true`, `max_output_tokens` à 8192 et non 16384) **avec un eval_config.yaml** obligatoire comme garde-fou de temps. | Pari : entre −2 et +3 | 0,5 j plus des mesures de durée | Corrections du harness le 30/09 (https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794) ; mesure locale 7/12 avec contre 9/12 sans (gemma4-swe-kit) ; 16384 en sortie refuse les prompts de plus de 16 k tokens (https://www.kaggle.com/code/dariushafshar/gemma-4-a-16384-output-cap-refuses-long-prompts) |
| 7 | Échantillonnage : température autour de 1,0, top_p 0,95, top_k 64, contre les boucles. | Incertain | Trivial | https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743964 (les boucles sont l'échec n° 1) ; plus d'outils mal formés à haute température (https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028) |
| 8 | LoRA 31B entraîné sur des trajectoires Gemma 31B. | Inconnu, aucune preuve publique | Élevé | Chez nous, sur E4B : −7,1 et −11,1 points (`/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:169-179`) |

## 4. Plan sur 2 semaines (du 3 au 16 oct.)

Règle générale : **pas de soumission sans critère local atteint.** Un jour sans candidat validé, on ne soumet pas.

| Jours | Étape | Critère local avant de soumettre |
|---|---|---|
| J1-J2 | Monter l'éval locale : gemma4-swe-kit, wheels officielles, Gemma 31B via l'API. Construire le lot propre (tâches dont le patch de référence passe en local), environ 30 tâches, mélange rich, requests et fastapi. Faire tourner le bundle actuel comme référence (2 passes). | Référence mesurée : taux de patchs vides, de dépassements de contexte, d'outils mal formés, durée p50 et p95 par tâche. Pas de soumission. |
| J3 | **V3 = notre bundle avec les leviers 2, 3 et 5** (prose, sans graphe, `{problem_description}`, lecture ciblée, repro optionnelle). | Patchs vides et outils mal formés au moins divisés par 2 par rapport à la référence. Aucun dépassement de contexte. p95 × 120 + installation ≤ 9 h. Puis soumission n° 1. |
| J4 | Faire tourner le bundle public à 0,12 (levier 4) sur le même lot. | Si ses métriques battent la V3, il devient la base. Sinon, on garde la V3. Pas de soumission obligatoire. |
| J5-J7 | Ajustements de la base retenue, **une seule modification par variante** : agent unique contre codeur plus analyseur, puis l'échantillonnage. | Chaque variante sur 2 passes du lot. Elle doit faire mieux que la base au-delà de l'écart observé entre les 2 passes, sans hausse des patchs vides. 1 soumission par variante validée. |
| J8-J10 | **Thinking** : `include_thoughts: true`, sortie à 8192, eval_config.yaml avec `max_time_minutes` réglé sur la p95 mesurée (environ 6). Le `timeout_seconds` doit rester assez haut pour le pytest de validation (https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743365). | Tâches résolues au moins égales à la base, aucune tâche au-delà du plafond, durée totale projetée ≤ 9 h. Puis soumission. |
| J11-J14 | Resoumettre les 2 meilleures configurations (2 tirages chacune) pour réduire le bruit. Choisir les 2 finales : la meilleure, plus un agent **différent** et non une quasi-copie (https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie). | Moyenne sur au moins 2 soumissions. Go/no-go sur le LoRA seulement si le prompt plafonne à 0,12 ou plus. |

## 5. Ce qu'il ne faut pas faire

| À éviter | Pourquoi |
|---|---|
| Soumettre une variante qu'on n'a pas fait tourner en local | C'est ce qui a donné deux 0,06 sans rien apprendre. |
| Comparer deux variantes sur une soumission chacune | ±2 tâches de bruit. |
| Optimiser le score local sur FastAPI ou rich | Les tâches cachées viennent de dépôts privés, et le score local est mal corrélé au LB (CV 0,316 pour LB 0,03). |
| Allonger le prompt avec des règles tirées des tâches publiques | Black Cat v8 l'a fait et est tombé à 0,05. |
| Mettre des exemples `run_command("…")` dans un prompt | Ils font inventer des noms d'outil, et un nom inconnu donne un patch vide. |
| Activer le thinking sans eval_config, ou mettre `max_output_tokens` à 16384 | Une tâche qui boucle peut faire dépasser les 12 h, ce qui fait échouer toute la soumission. Avec 16384 en sortie, les prompts de plus de 16 k tokens sont refusés. |
| Mettre un plafond par tâche trop serré (4 à 5 min) | Les bundles plafonnés ainsi sont tombés à 0,08. Un plafond de 12 min a dépassé le budget. |
| Utiliser `search_similar_code` ou laisser des lectures non bornées | Ils provoquent des dépassements de contexte, donc des patchs vides. |
| Croire `/home/elrems/kaggle/docs/SCALING_LAWS_REPORT.json` | Ce sont des valeurs simulées par une formule codée en dur (`/home/elrems/kaggle/harness_transfer/scripts/run_scaling_loop.py:157-164`, pass_at_1 = 0,13 + 0,03 × taille). Il ne doit servir ni à une décision ni au papier. |
| Suivre `/home/elrems/kaggle/kaggle/README.md:39` (« supprimer eval_config ») et `/home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md:16` (« le LB porte sur les 129 tâches ») | Les deux sont faux et sont à corriger. |
| Viser le LoRA en priorité | Aucune preuve publique de gain. Chez nous, le fine-tuning a fait perdre des points. Les adaptateurs ont longtemps été cassés côté harness. |
| Mettre des sorties Claude ou GPT dans des données d'entraînement | C'est interdit par nos règles (`/home/elrems/kaggle/REGLES.md`), même si Kaggle tolère la distillation sous licence compatible. |

Aucun fichier n'a été modifié et rien n'a été soumis.

---

# Critique sceptique (corrige plusieurs points de la synthèse)

Le plan tient dans les grandes lignes : diagnostic juste, priorités raisonnables. Mais il fait l'impasse sur le LB privé, s'appuie sur des preuves trop bruitées et compte sur une éval locale difficile à monter sur ce serveur. J'ai vérifié les points ci-dessous dans les fichiers et les pages citées. Rien n'a été modifié ni soumis.

**Vérifié, exact**
- **Thinking coupé.** `include_thoughts: false` est bien à `/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:8`. Le README officiel le confirme : « use `0` or `include_thoughts: false` to disable thinking » (HARNESS_README.md:148, alors que le harness active le thinking par défaut, l.168 et 198). Point 2 du constat confirmé.
- **Calculs du classement exacts** (recalculés sur `/home/elrems/kaggle/runs/leaderboard/2026-10-02.csv`) : 1 279 équipes, médiane 0,08, valeur la plus fréquente 0,08 (248 équipes), 672 équipes au-dessus de 0,06, top 10 à 0,15. Kaggle tronque le score au lieu de l'arrondir : 4/58 = 0,069 s'affiche 0,06. Toutes les valeurs du classement collent avec n = 58 tronqué, donc « 4/58 » et « +1/+3/+5/+10 » sont justes. Ce CSV est périmé : `kaggle competitions list` donne aujourd'hui 1 357 équipes et nous classe **931ᵉ**, pas 673ᵉ.
- **Calendrier et règles de soumission** : échéance le 2 déc. 23:59, fusions jusqu'au 25 nov., 1 soumission par jour, 2 finales (pages_gemma-4-developer-agent.md:165-166, 243-244 dans le scratchpad).
- **Fichiers locaux**
  - `skills:` est absent de `/home/elrems/kaggle/kaggle/submission/agent.yaml`, alors que la clé existe dans le schéma (HARNESS_README.md:114).
  - `search_similar_code` est bien exposé (agent.yaml:13 et sub_agents/code_analyzer.yaml).
  - `eval_task.py` ne fait qu'appliquer un patch fourni (`--agent-patch`). Sa docstring (l.7) prétend l'inverse.
  - `/home/elrems/kaggle/harness_transfer/scripts/run_scaling_loop.py:163-164` est bien une formule codée en dur.
  - `kaggle/README.md:39` (« supprimer eval_config ») et `PLAN_STRATEGIQUE_KAGGLE_FINAL.md:16` (« 129 tâches ») sont bien faux.

**Faux ou surestimé**
1. **« `run_command("…")` 11 fois » est faux.** `system.md` en contient 5. Il y a 12 pseudo-appels toutes formes confondues (5 run_command, 3 submit_patch, 2 get_status, 1 edit_file, 1 read_file), plus 2 dans `skills/replay/SKILL.md` (jamais chargée). Le fond reste valable.
2. **Thinking « 7/12 avec contre 9/12 sans ».** D'après la page de gemma4-swe-kit, cette variante tournait avec un `thinking_budget` de **256**, et non avec un vrai thinking. Ce n'est donc pas une preuve contre le thinking au budget 4096, et 2 tâches sur 12 restent du bruit.
3. **« `/tmp` que `write_file` refuse ».** C'est imprécis. `write_file` écrit sous `/workspace/<filepath>` (HARNESS_README.md:470-471), et le README officiel *recommande* `/tmp/repro.py` via `run_command` (l.666-667). Le vrai défaut est que le prompt ne dit pas avec quel outil écrire le fichier, pas l'emplacement `/tmp`.
4. **Preuves trop bruitées pour l'échelle du plan.** « Agent unique 14/44 contre 13/44 » et « Black Cat v8 à 0,05 contre 0,10-0,12 » sont des écarts de 1 à 4 tâches sur une seule mesure. C'est sous le ±2 que le plan pose lui-même. Les gains de « +1 à 3 » ou « +0,5 à 2 » tâches ne reposent sur rien de mesuré.
5. **« Patch vide dès que le contexte déborde »** est à nuancer. Le harness compacte l'historique dès 14 336 tokens (HARNESS_README.md, §7.2). Seule une sortie d'outil énorme casse vraiment. Le kit mesure environ 1 tâche sur 12 perdue par débordement : c'est réel, mais pas massif.
6. **Plafonds par défaut.** Sans `eval_config.yaml`, une tâche a 60 min et 100 appels d'outil (HARNESS_README.md, §7.1). Le plafond de 12 h inclut la mise en place des sandbox (pages l.130), sur environ 120 tâches au total (l.81). Le plan a raison d'exiger un `eval_config`, y compris *sans* thinking, et pas seulement à J8-J10. La V3 de J3 devrait déjà en avoir un.

**Contraire au règlement : rien de bloquant**
- Le plan reste conforme. Seule vigilance : « repartir d'un bundle public » est permis, puisque le code est partagé sur le forum (pages l.282). En revanche, deux finales quasi identiques à un notebook public n'apportent rien, et la règle Claude/GPT de REGLES.md:38 s'applique aussi aux prompts.

**Ce qui manque**
1. **Le LB privé.** Le classement final se fait sur l'autre moitié des environ 120 tâches (pages l.81, 290). Le plan ne parle que du public à 58 tâches. Il faut l'écrire : choisir les finales sur les métriques locales et la robustesse, pas sur le meilleur score public, sinon on surapprend à 58 tâches.
2. **La faisabilité de l'éval locale.**
   - D'après sa page, gemma4-swe-kit tourne sur **Ollama ou MLX**.
   - Ce serveur n'a pas de GPU, et une 4070 Ti de 12 Go ne fait pas tourner le 31B confortablement.
   - Il faut vérifier que le kit (via `g4kit-proxy`) accepte l'API Gemma, et que l'API rend les appels d'outil comme vLLM 0.19 (format `<|tool_call>`, parser gemma4). Sinon, le taux d'outils mal formés mesuré en local ne vaudra rien.
   - Il faut aussi chiffrer le quota de l'API : 30 tâches × 2 passes × environ 6 variantes, avec jusqu'à 100 appels d'outil par tâche.
   - J1-J2 me paraît optimiste.
3. **Le harness officiel `swegemma eval`.** Il existe (HARNESS_README.md, §9.1, avec `--task-ids` et `--skip-agent-patch`). Le plan saute directement au kit tiers sans dire si `swegemma` est installable chez nous. Le kit dit lui-même l'utiliser.
4. **Le packaging.** On ne vérifie jamais le zip réellement soumis. `kaggle/submission.zip` ne contient pas d'`eval_config.yaml`, et `submissions.jsonl` indique « direct_zip » pour la v2. Il faut ajouter au plan une étape qui vérifie le contenu du zip avant chaque soumission, et lancer `validate.py`.
5. **Le critère « outils mal formés divisés par 2 ».** Sur 30 tâches, il n'est mesurable que si la référence en produit assez. Il faut fixer des seuils absolus en plus du ratio.
6. **`{problem_description}`.** Le placeholder est bien supporté (HARNESS_README.md:293-296). Mais l'analyseur reçoit déjà l'énoncé par `agent_tool`. Il faut vérifier qu'on ne le duplique pas, car cela coûte du contexte.

Sources :
- `/home/elrems/kaggle/kaggle/submission/{agent.yaml,configs/sampling.yaml,prompts/system.md,sub_agents/code_analyzer.yaml}`
- `/home/elrems/kaggle/harness_transfer/scripts/{eval_task.py,run_scaling_loop.py}`
- `/home/elrems/kaggle/kaggle/README.md`
- `/home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md`
- `/home/elrems/kaggle/REGLES.md`
- HARNESS_README.md et pages_gemma-4-developer-agent.md, copies locales dans `/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/`
- https://github.com/damsolanke/gemma4-swe-kit
- `kaggle competitions list` et `kaggle competitions submissions`, consultés le 2 oct. 2026

---

## Annexe : constats bruts par angle

```json
[
 {
  "key": "regles-evaluation",
  "findings": [
   {
    "claim": "Le score est le taux de résolution (pass@1, PASS/FAIL façon SWE-bench) sur environ 120 tâches cachées, coupées en deux : 58 en public, environ 60 en privé. Nos 0,06 valent 4 tâches sur 58. Le n° 1 (0,24) en résout 14, le top 10 (0,15) 9, et la valeur la plus fréquente (0,08 à 0,10) correspond à 5 ou 6 tâches. Il nous manque donc 2 tâches pour rejoindre la masse et 5 pour le top 10. Ce n'est pas foutu.",
    "evidence": "Page Evaluation : « percentage of patched repositories that pass the validation tests » (scratchpad/pages_gemma-4-developer-agent.md:126-128). « about 120 tasks in the test set, evenly divided between the public and private splits » (même fichier, l.81). Le sujet 743506 démontre, à partir des paliers 0,01/0,03/0,05…, que le public compte exactement 58 tâches avec un score tronqué. J'ai reproduit le calcul sur notre CSV : n=58 est la seule valeur possible sous 78. Répartition dans /home/elrems/kaggle/runs/leaderboard/2026-10-02.csv : 0,24 ×1, 0,17 ×1, 0,15 ×10, 0,13 ×45, 0,12 ×145, 0,10 ×222, 0,08 ×248, 0,06 ×197, 0,00 ×133. Notre rang : 931 sur 1 356 (kaggle competitions list).",
    "importance": "haute"
   },
   {
    "claim": "Les tâches cachées viennent de dépôts privés, pas de fastapi/rich/requests/httpx. Les 129 tâches publiques servent seulement d'entraînement. Un agent réglé sur ces 129 tâches (prompts truffés de FastAPI, par exemple) ne se transpose pas forcément. Plusieurs équipes constatent que leur CV locale et le LB ne sont pas corrélés. Nos docs se trompent quand elles disent que le LB porte sur « 129 tâches Python (FastAPI, etc.) ».",
    "evidence": "Réponse de l'hôte, sujet 744951 : « No, the test set draws from private repositories not available publicly » (scratchpad/topics.md:933). data-description l.81 : « The test set was curated from a set of private repositories ». Sujet 744319 : CV 0,316 pour LB 0,03, CV 0,211 pour LB 0,10. Erreur dans /home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md:16 et l.58.",
    "importance": "haute"
   },
   {
    "claim": "Le jeu de test est filtré. Tous les correctifs de référence passent, et chaque tâche est résolue, ou presque, par un modèle de pointe. En local, en revanche, la plupart des correctifs de référence FastAPI échouent, à cause des wheels (typing_inspection, inline_snapshot, dirty_equals manquants ; starlette 1.6.0 imposée). Plusieurs tâches requests ou rich ne peuvent pas passer en Python 3.13. Une CV locale brute est donc très bruitée : il faut d'abord écarter les tâches dont le correctif de référence échoue chez nous.",
    "evidence": "Hôte, sujets 744259 et 744370 : « hidden tasks validate at 100% with a gold patch » (topics.md:891, l.906). data-description l.79 : « Near Completion with Frontier Models ». Sujet 743973 : 8 tâches requests (SSL), fastapi_14186/15745 et rich_3486 (skip en 3.13), rich_3472, 54 FastAPI sur 67 en échec avec starlette 1.6.0 (topics.md:850-883).",
    "importance": "haute"
   },
   {
    "claim": "Contraintes de soumission : 1 soumission par jour (le quota d'aujourd'hui est épuisé), 2 soumissions finales à choisir, échéance le 2 déc. 2026 à 23:59 UTC (fusions d'équipes jusqu'au 25 nov.). Un échec côté plateforme consomme aussi le quota du jour. Avec 58 tâches publiques, une seule soumission a un bruit d'environ ±2 tâches (écart-type binomial à p≈0,1, environ 0,04 en score), et nous sommes à température 0,2. Passer de 0,06 à 0,10 peut donc venir du seul hasard : on ne peut pas trancher entre deux variantes sur une soumission chacune.",
    "evidence": "rules § 2.2 : « maximum of one (1) Submission per day », « up to two (2) Final Submissions » (pages_gemma-4-developer-agent.md:164-166). Timeline l.239-244. `kaggle competitions submission-limits gemma-4-developer-agent` renvoie « Remaining today: 0 ». Sujets 744807 et 743213 : slots perdus sur des pannes.",
    "importance": "haute"
   },
   {
    "claim": "Modèle imposé : gemma-4-31b-it-qat-w4a16-ct pour tous les agents et sous-agents. Serveur vLLM sur 4×L4 (TP=4, max_model_len=32 768, gpu_mem 0,80). Les adaptateurs LoRA en .safetensors sont autorisés (rang ≤ 128, 8 au maximum, archive < 3 Gio au total). Aucun code Python libre : seulement du YAML ADK 1.x, avec les 9 outils du harness, des AgentTool, des skills (run_skill_script) et les classes Sequential, Parallel et Loop. Les appels en parallèle ne sont pas pris en charge. Les adaptateurs ont longtemps été cassés (cache KV réduit à 7,6 k tokens, adaptateurs remis à zéro). L'hôte dit avoir corrigé, mais aucun succès n'est prouvé publiquement : la LoRA reste un pari risqué.",
    "evidence": "Page « Model Selection, Budget, and Harness Rules » (pages_gemma-4-developer-agent.md:378-406). HARNESS_README §2.4 et §3 (scratchpad/HARNESS_README.md:127-210). Sujet 744331 : cache KV de 46 048 tokens sans LoRA contre 7 600 avec (topics.md:569-599). Réponse de l'hôte : « LoRA params dynamically based on what you actually submit » (topics.md:270). Sujet 743964 : « we don't support parallel calls ». Sujet 743800 : ADK 1.x seulement.",
    "importance": "moyenne"
   },
   {
    "claim": "Budget de temps : 12 h au total pour environ 120 tâches exécutées une par une, installation des sandboxes comprise (la validation n'est pas comptée), soit environ 6 min par tâche en moyenne. Dépasser les 12 h fait échouer toute la soumission : la correction annoncée (tâches inachevées notées 0) n'est pas confirmée en ligne. Sans eval_config.yaml, le scoreur n'applique aucune limite par tâche. L'hôte conseille de fixer un max_time_minutes modéré par sécurité. Notre soumission n'a pas d'eval_config, et kaggle/README.md recommande à tort de le supprimer.",
    "evidence": "Page Evaluation : « limit of 12 hours to submit patches for all tasks, inclusive of sandbox setup time » (pages_gemma-4-developer-agent.md:130). Sujet 743063 : « 1. Sequentially. … default is no limit … hitting the 12-hour limit will error … set max_time_minutes to something moderate as a failsafe » (topics.md:3-5). Sujet 743964 : « 12h overrun: Not yet. Budget per task using eval_config.yaml ». Sujet 744258 : public et privé dans le même run de 12 h. Notre archive /home/elrems/kaggle/kaggle/submission.zip ne contient pas d'eval_config.yaml. Conseil erroné : /home/elrems/kaggle/kaggle/README.md:39.",
    "importance": "haute"
   },
   {
    "claim": "Notre réglage include_thoughts: false coupe complètement le raisonnement (enable_thinking: false). Le thinking_budget de 4096 est alors ignoré. La doc (README, PLAN) présente le thinking comme actif : c'est faux pour notre agent. C'est un levier à tester, à arbitrer avec le budget de 6 min par tâche et le contexte de 32 k.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:8 (`include_thoughts: false`). Sujet 745059 : « include_thoughts: false → enable_thinking: false → no reasoning generated » (topics.md:423-431). Sujet 743365 : « include_thoughts: false sends enable_thinking: false, so thinking is fully off » (topics.md:107). Les correctifs de transmission du raisonnement et de thinking_budget sont dans la wheelhouse du 30 sept. (hôte, topics.md:271, l.409).",
    "importance": "haute"
   },
   {
    "claim": "Plusieurs défauts du harness mettent une tâche à 0 alors que le correctif est bon. (1) Un dépassement de contexte (ContextWindowExceededError, y compris dans un sous-agent AgentTool) abandonne le patch au lieu de récupérer le git diff. (2) Un outil non déclaré ou halluciné, ou un argument mal typé pour run_skill_script, termine la tâche sans patch. (3) Modifier un fichier de test existant fait échouer test_patch, car la remise à zéro est inopérante. (4) search_similar_code peut renvoyer plus de 100 k caractères ; l'hôte promet un plafond à 5 000. (5) La compaction ne garde que le texte et perd les résultats d'outils. Comme tout se règle dans le prompt, il faut des réponses courtes, peu d'appels au graphe et aucune modification de test.",
    "evidence": "Sujet 744692 : « 44 of 44 overflowed sessions had an empty patch, 14 of them after successful edits » (topics.md:627). Sujet 745028 : ValueError « Tool not found » qui termine la tâche, et le cas run_skill_script (topics.md:501-518). Sujet 744825 : `git checkout` qui avorte sur sitecustomize.py (topics.md:532-548). Sujet 744577 : FastAPI à 130 k caractères (topics.md:637-648). Sujet 744794 § 1 sur la compaction (topics.md:255). Compaction à token_threshold 14 336 (HARNESS_README.md:553-561).",
    "importance": "moyenne"
   },
   {
    "claim": "Notre skill « replay » n'est jamais chargée : agent.yaml n'a pas de clé `skills:`, et skills/replay/SKILL.md est un fichier mort de l'archive. Le sous-agent code_analyzer reçoit run_command et les outils de graphe, dont search_similar_code sans plafond, ce qui l'expose au dépassement de contexte qui vide le patch.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/agent.yaml : aucune clé `skills` (grep vide). HARNESS_README.md:114 : `skills (list[str])` doit lister les dossiers. Le contenu de l'archive submission.zip inclut skills/replay/SKILL.md. /home/elrems/kaggle/kaggle/submission/sub_agents/code_analyzer.yaml : outils run_command, read_file et graphe.",
    "importance": "moyenne"
   },
   {
    "claim": "Sur le graphe et les embeddings fournis : seulement des arêtes « calls », aucune fonction async, et des embeddings quasi effondrés (cosinus moyen entre 0,78 et 0,90). search_similar_code n'accepte qu'un nom de nœud existant. Sur les tâches publiques, un grep sur les identifiants trouve le bon fichier deux fois plus souvent (67 contre 35 sur 129). Le harness annonce pourtant ces outils au modèle dans le message de la tâche.",
    "evidence": "Sujets 742911 et 744040 (topics.md:1122-1175). HARNESS_README.md:333-340 et 494-497. Réponse de l'hôte : « missing async functions are still missing » (topics.md:1150).",
    "importance": "basse"
   },
   {
    "claim": "Règles sur les données : la distillation de modèles externes est autorisée si leur licence le permet (réponse de l'hôte), et l'entraînement sur des sorties de gemma-4-31b est explicitement accepté. La règle interne du projet, qui exclut Claude et GPT, reste plus stricte et inchangée. Le gagnant doit publier son travail sous licence open source (Apache 2.0) et fournir le code d'entraînement.",
    "evidence": "Sujet 742807, réponse de l'hôte (topics.md:795). Sujet 743964 : « Training on gemma-4-31b itself is fine ». rules § 1.6 et § 2.5/2.8 (pages_gemma-4-developer-agent.md:153, 181-191). /home/elrems/kaggle/REGLES.md (règle « Aucun modèle propriétaire »).",
    "importance": "basse"
   }
  ],
  "summary": "Ce n'est pas foutu, mais le classement ne laisse presque aucune marge. Le score est le taux de tâches résolues (PASS/FAIL façon SWE-bench) sur environ 120 tâches cachées venant de dépôts privés. 58 tâches comptent pour le LB public, environ 60 pour le privé, qui fait le classement final.\n\n**Où on en est**\n- Nos 0,06 valent 4 tâches sur 58.\n- La valeur la plus fréquente (0,08 à 0,10) correspond à 5 ou 6 tâches, le top 10 (0,15) à 9, le n° 1 (0,24) à 14.\n- On est 931e sur 1 356. Il manque 2 tâches pour rejoindre la masse et 5 pour le top 10.\n- Avec 58 tâches et une température de 0,2, le bruit d'une soumission est d'environ ±2 tâches.\n\n**Contraintes qui bornent le score**\n- **Modèle et matériel imposés :** gemma-4-31b-it-qat-w4a16-ct pour tous les agents, vLLM sur 4×L4, contexte de 32 768 tokens.\n- **Format :** submission.zip contenant du YAML ADK 1.x déclaratif (agent.yaml, prompts, sous-agents, skills, LoRA en .safetensors, archive < 3 Gio). Aucun code Python libre, seulement les 9 outils du harness « swegemma ».\n- **Temps :** 12 h au total pour environ 120 tâches exécutées une par une, installation des sandboxes comprise, soit environ 6 min par tâche. Dépasser les 12 h fait échouer toute la soumission. Sans eval_config.yaml, il n'y a aucune limite par tâche.\n- **Quota :** 1 soumission par jour (épuisée aujourd'hui), 2 soumissions finales, échéance le 2 déc. 2026.\n- **Vérification :** dans un conteneur propre, les tests du test_patch doivent tous passer. Les fichiers de test modifiés par l'agent sont censés être remis à zéro, mais le mécanisme est actuellement cassé.\n\n**Leviers et défauts propres à notre soumission**\n- `include_thoughts: false` dans `/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:8` coupe complètement le raisonnement. Le `thinking_budget` de 4096 est donc ignoré.\n- Il n'y a pas d'eval_config.yaml, alors que l'hôte conseille un `max_time_minutes` modéré comme garde-fou. `/home/elrems/kaggle/kaggle/README.md:39` recommande à tort de supprimer ce fichier.\n- La skill « replay » n'est jamais chargée, faute de clé `skills:` dans `agent.yaml`.\n- Le sous-agent code_analyzer peut dépasser le contexte, ce qui vide le patch : un dépassement de contexte ou un outil inconnu met la tâche à 0 sans récupérer le diff.\n\n**À corriger dans nos docs et notre CV locale**\n- `/home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md:16` se trompe quand il dit que le LB porte sur « 129 tâches FastAPI ». Ces 129 tâches servent seulement d'entraînement.\n- Les tâches cachées passent toutes avec le correctif de référence. En local, en revanche, la plupart des tâches FastAPI échouent même avec ce correctif, à cause de wheels manquantes ou de mauvaise version. Plusieurs participants constatent d'ailleurs que leur CV locale et le LB ne sont pas corrélés.\n- Avant toute mesure locale, il faut donc écarter les tâches dont le correctif de référence échoue chez nous.\n\n**Sources**\n- Pages officielles de la compétition, récupérées par l'API Kaggle : `/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/pages_gemma-4-developer-agent.md`\n- Guide du harness `/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/HARNESS_README.md`, téléchargé depuis les fichiers de la compétition\n- 40 discussions du forum, dont les réponses de l'organisateur (Ryan Holbrook) : `/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/topics.md`. Exemples : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063, …/743506, …/744951, …/745059, …/744692\n- Rien n'a été modifié ni soumis."
 },
 {
  "key": "notre-pipeline",
  "findings": [
   {
    "claim": "0,06 = 4 tâches résolues sur 58 (LB public). La médiane est à 5-6/58 et le top 10 à 9/58. On n'est donc pas « foutus » : il manque 1 à 2 tâches pour la médiane et environ 5 pour le top 10. L'écart-type binomial est d'environ ±2 tâches, si bien que deux soumissions à 0,06 ne départagent rien.",
    "evidence": "Forum (topic 743506) : les scores sont tronqués, et 58 est la seule taille de test compatible avec les paliers 0,01/0,03/0,05/0,06/0,08… Je l'ai revérifié sur /home/elrems/kaggle/runs/leaderboard/2026-10-02.csv (paliers observés : 0, 1, 3, 5, 6, 8, 10, 12, 13, 15, 17, 24 → seul N=58 avec troncature colle). Répartition : 197 équipes à 0,06, 248 à 0,08, 222 à 0,10, 145 à 0,12, 133 à 0,00. Kaggle : `kaggle competitions submissions` → 56757960 = 0,06 et 56765392 = 0,06.",
    "importance": "haute"
   },
   {
    "claim": "Le raisonnement (thinking) est COMPLÈTEMENT DÉSACTIVÉ dans nos deux soumissions, contrairement à ce que croyait Antigravity. Avec `include_thoughts: false`, le harness envoie `enable_thinking: false` à vLLM, et le `thinking_budget: 4096` ne sert à rien. Les bugs qui rendaient le thinking peu utile (pensées perdues entre deux appels d'outil, thinking_budget non transmis) sont corrigés dans le wheelhouse du 30 sept. Le levier n'a jamais été testé.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:6-8 (`thinking_budget: 4096`, `include_thoughts: false`). L'intention erronée est écrite dans /home/elrems/kaggle/kaggle/scripts/build_notebook.py:33 (« include_thoughts: false to keep thought overhead outside conversation context »). La sample_submission officielle met `include_thoughts: true` et `max_output_tokens: 16384`. Forum, topic 743365 et scratchpad topics.md:107 : « include_thoughts: false sends enable_thinking: false, so thinking is fully off » ; topic 745059 (adk_submission 0.2.12, toujours vrai) ; topic 744794 réponse de l'organisateur (01/10) : « thoughts dropped, thinking_budget / seed not sent … fixed in the latest wheelhouse ».",
    "importance": "haute"
   },
   {
    "claim": "Les deux soumissions sont quasi identiques : v2 n'ajoute que 4 lignes au prompt de l'analyseur, et ce changement n'est même pas commité. Le skill « replay » n'est jamais chargé, car agent.yaml n'a pas de clé `skills:`. Le soi-disant passage « Replay + AST Blast Radius » n'a donc rien testé de ce qui compte (thinking, budget, échantillonnage, prompt racine).",
    "evidence": "`git diff kaggle/submission/prompts/analyzer.md` : +3 lignes « Crash Site vs Root Cause / Blast Radius » et +1 ligne `BLAST RADIUS:`, le fichier étant encore marqué M dans git status. Aucun autre fichier de submission/ n'a changé depuis 77379ae. /home/elrems/kaggle/kaggle/submission/agent.yaml:1-18 ne contient pas de champ `skills`, alors que HARNESS_README (/home/elrems/kaggle-python/docs/HARNESS_README.md:114) exige `skills: [chemins]`. /home/elrems/kaggle/kaggle/submission/skills/replay/SKILL.md est donc du poids mort. kaggle/submissions.jsonl : v2 envoyée en « direct_zip ».",
    "importance": "haute"
   },
   {
    "claim": "Aucune évaluation locale de l'agent n'a jamais tourné. L'« évaluateur » de harness_transfer ne lance pas d'agent : il applique un patch donné, clone FastAPI depuis GitHub et lance pytest sur tout le dépôt, ce qui ne reproduit pas le harness swegemma. runs/ ne contient que des runs PrestaShop (piste Paper). Chaque soumission est donc un tir à l'aveugle, sans trace pour diagnostiquer les échecs : débordement de contexte, appels malformés, boucles.",
    "evidence": "/home/elrems/kaggle/harness_transfer/scripts/eval_task.py:21 (FASTAPI_REPO_URL), :71 (`pytest -q` sur tout le dépôt), :87-91 (application d'un --agent-patch fourni, pas d'agent). `grep -rl submit_patch runs/` ne renvoie rien. Les dossiers runs/20261002-*-A contiennent des numéros de PR PrestaShop (27175, 27698…). Outil public qui comble ce manque : https://github.com/damsolanke/gemma4-swe-kit (proxy vLLM/gemma4, fake-llm, compteur de boucles et de débordements, estimation du temps scoreur ; forum topic 745143).",
    "importance": "haute"
   },
   {
    "claim": "Nos prompts écrivent les commandes shell comme des appels d'outil (`run_command(\"python3 -m pytest …\")`, `git grep … | head -30`). D'après une mesure publique, ce style fait passer les noms d'outil malformés de 5 % à 31 % aux points de décision difficiles. Or un nom d'outil inconnu ou malformé lève une ValueError qui termine la tâche avec un patch vide (score 0), même si un bon correctif était déjà appliqué.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/prompts/system.md:20,24,32-35,42 et /home/elrems/kaggle/kaggle/submission/prompts/analyzer.md:4. Forum topic 745143 (gemma4-swe-kit) : « with shell commands written as examples in the prompt, 31% of replayed calls … malformed tool names, against 5% with the commands described in prose ». Topic 745028 : un outil non déclaré ou halluciné → `ValueError` → session terminée → patch vide (agent_runner.py L799-801, patch de secours non capturé).",
    "importance": "haute"
   },
   {
    "claim": "Le contexte de 32K peut déborder, ce qui donne un patch vide. Hypothèse plausible mais non vérifiée faute de traces : l'analyseur appelé en premier a des lectures non bornées et utilise `search_similar_code`, dont les sorties ont pu dépasser 100K caractères, sans compaction prouvée dans le sous-agent. Côté racine, l'énoncé n'est pas injecté via `{problem_description}` : après la compaction (seuil 14 336 tokens, qui ne garde que le texte), l'agent peut perdre l'énoncé et boucler.",
    "evidence": "analyzer.md:5-7 : pas de plafond du nombre d'appels, `search_similar_code` encouragé ; agent.yaml:13 et code_analyzer.yaml:10 l'exposent aussi. Forum topic 744577 : 6/6 appels `search_similar_code` de plus de 100K caractères ont fini en ContextWindowExceededError (plafond promis le 30/09, sans confirmation). Topic 744692 : un débordement vide le patch, « 44 of 44 overflowed sessions had an empty patch, 14 after successful edits ». Topic 744794 : la compaction perd les résultats d'outil et Gemma répète son dernier appel. Topic 743365 : un participant à 0,10 répète l'énoncé dans les instructions des deux agents. HARNESS_README:296 (`{problem_description}` disponible). Aucune occurrence de `{problem_description}` dans system.md ni dans analyzer.md.",
    "importance": "moyenne"
   },
   {
    "claim": "Nos prompts supposent un bug à reproduire, alors que les tâches cachées sont des PR de dépôts privés : des fonctionnalités, refactorings ou docs autant que des bugs, avec des énoncés courts. Le flux imposé (analyseur → /tmp/repro.py → py_compile → repro → pytest → git status → rm) dépense des appels et du contexte sans dire à l'agent l'essentiel : respecter exactement les noms d'API, messages et exceptions demandés, puisque les tests cachés les importent.",
    "evidence": "system.md:1 (« fixing one issue »), :22-24 (reproduction obligatoire), :42 (rm de /tmp/repro.py, inutile car /tmp est hors du diff). Données : /tmp/kaggle_data/tasks.jsonl compte 129 tâches, sans hints_text, avec un énoncé médian de 418 caractères (38 font moins de 200 caractères) ; une heuristique sur les titres classe environ 56 tâches sur 129 hors « bug ». pages_gemma-4-developer-agent.md:81 (scratchpad) : « test set curated from a set of private repositories ». La sample_submission (system.md:15,38) insiste sur « Strictly adhere to specified error strings, exception types, … API signatures » et « Every task requires concrete source modifications ».",
    "importance": "moyenne"
   },
   {
    "claim": "Aucun eval_config.yaml, donc aucune limite par tâche (le scoreur n'en applique pas par défaut). Comme une seule tâche qui boucle peut faire dépasser les 12 h, et que dépasser 12 h fait échouer toute la soumission, c'est sans risque avec le thinking coupé mais dangereux dès qu'on l'active. Il faudra alors un garde-fou, par exemple max_time_minutes entre 5 et 6 et timeout_seconds à 300. Le README affirme aussi à tort que « les meilleures soumissions suppriment ce fichier ».",
    "evidence": "/home/elrems/kaggle/kaggle/submission/ ne contient pas d'eval_config.yaml, choix revendiqué dans /home/elrems/kaggle/kaggle/README.md:38-39 et build_notebook.py:32. Forum topic 743063 (organisateur) : tâches séquentielles, « the default is no limit », dépassement de 12 h = erreur de toute la soumission, correctif « unfinished = 0 » pas encore en ligne. Topic 743365 : `timeout_seconds` sert aussi au pytest de vérification, donc une valeur basse peut faire échouer un bon patch. Environ 120 tâches en 12 h ≈ 6 min par tâche, setup compris.",
    "importance": "moyenne"
   },
   {
    "claim": "L'échantillonnage (température 0,2, top_k 40, seed 42) est quasi déterministe et favorise les boucles de répétition, l'échec le plus fréquent de Gemma 4 31B d'après le forum. Le passage à environ 1,0 / top_p 0,95 / top_k 64 (réglages habituels de Gemma, à vérifier sur la fiche modèle) reste à tester. Le seed n'est réellement transmis que depuis le dernier wheelhouse.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:1-5. Forum topic 743964 : « the most common failure of gemma-4-31b is repeating the same tool call many times until the time budget runs out ». Topic 744794 : seed non transmis avant le correctif. Topic 745028 : appels malformés plus fréquents à température élevée, compromis à mesurer.",
    "importance": "basse"
   },
   {
    "claim": "La validation maison est superficielle : elle ne lit le modèle que dans agent.yaml racine, ne résout pas `!include`, ne compile pas avec adk-submission et ne vérifie pas les extensions autorisées. Elle n'a pas causé d'échec (les deux soumissions sont COMPLETE), mais elle ne protège de rien.",
    "evidence": "/home/elrems/kaggle/kaggle/scripts/validate.py:22-25 (`!include` renvoyé comme simple chaîne), :67-95 (agent.yaml racine seulement), :54 (rejette tout « .. » dans les noms du zip mais ignore le `!include ../prompts/analyzer.md` des sous-agents, que la sample_submission officielle utilise aussi). Le validateur officiel parcourt sub_agents et agent_tool : HARNESS_README:183.",
    "importance": "basse"
   }
  ],
  "summary": "Non, ce n'est pas foutu : 0,06 correspond à 4 tâches sur 58 au LB public. La médiane est à 5-6, le top 10 à 9 et le n° 1 à 14 ; il manque 1 à 2 tâches pour la médiane, mais un bruit d'environ ±2 tâches rend toute comparaison à une soumission près illusoire.\n\nCe que fait notre soumission (/home/elrems/kaggle/kaggle/submission) : c'est la sample_submission sans LoRA ni eval_config.yaml, avec des prompts réécrits (agent racine, sous-agent code_analyzer et ses 9 outils). Les deux versions envoyées ne diffèrent que par 4 lignes du prompt de l'analyseur, et ces lignes ne sont pas commitées. Le skill « replay » n'est jamais chargé : agent.yaml n'a pas de clé `skills:`. On n'a donc jamais testé ce qui compte.\n\nLes causes probables du plafond, de la plus sûre à la plus incertaine :\n1. Le thinking est complètement coupé. `include_thoughts: false` envoie `enable_thinking: false` à vLLM, contrairement à ce qu'Antigravity croyait (build_notebook.py:33). Les bugs du harness sur le thinking sont corrigés depuis le 30/09.\n2. Les prompts écrivent les commandes shell comme des appels d'outil (`run_command(\"…\")`). Une mesure publique montre que ce style multiplie les noms d'outil malformés (31 % contre 5 %), et un nom malformé termine la tâche avec un patch vide.\n3. Le contexte de 32K peut déborder et vider le patch : lectures non bornées de l'analyseur, `search_similar_code`, énoncé non injecté via `{problem_description}` alors que la compaction ne garde que le texte.\n4. Les prompts supposent un bug à reproduire, alors que les tâches cachées sont des PR de dépôts privés (fonctionnalités, refactorings), avec des énoncés courts et des tests qui importent des noms d'API précis.\n5. L'échantillonnage (température 0,2) favorise les boucles.\n\nSurtout, aucune évaluation locale de l'agent n'a jamais tourné. harness_transfer/scripts/eval_task.py n'exécute pas d'agent : il applique un patch et lance pytest. Chaque soumission est donc un tir à l'aveugle, sans trace.\n\nCe que je propose, par ordre :\n- **(a) Évaluation locale avant tout envoi.** Monter une éval avec les wheels officiels sur les tâches publiques qui passent avec le patch de référence, par exemple avec https://github.com/damsolanke/gemma4-swe-kit. Compter les débordements de contexte, les appels malformés et les boucles.\n- **(b) Thinking activé.** Passer à `include_thoughts: true`, `max_output_tokens` à 16384, et ajouter un eval_config.yaml avec max_time_minutes entre 5 et 6 et timeout_seconds à 300 : avec le thinking, une tâche qui boucle peut faire dépasser les 12 h, ce qui fait échouer toute la soumission.\n- **(c) Prompts réécrits.** Décrire les commandes en prose, mettre `{problem_description}` dans les instructions des deux agents, ne plus imposer de script de reproduction, insister sur le respect exact des noms d'API, des messages et des exceptions, et plafonner l'analyseur (peu d'appels, pas de recherche sur les grosses classes avec `search_similar_code`).\n- **(d) Échantillonnage.** Tester ensuite une température plus haute.\n\nToutes ces pistes reposent sur la lecture du code et du forum (/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/topics.md), pas sur des traces de nos propres runs.\n\nFichiers clés :\n- /home/elrems/kaggle/kaggle/submission/configs/sampling.yaml\n- /home/elrems/kaggle/kaggle/submission/prompts/system.md\n- /home/elrems/kaggle/kaggle/submission/prompts/analyzer.md\n- /home/elrems/kaggle/kaggle/submission/agent.yaml\n- /home/elrems/kaggle-python/docs/HARNESS_README.md (identique à la version Kaggle actuelle)"
 },
 {
  "key": "etat-de-l-art-public",
  "summary": "Ce n'est pas perdu. La compétition ferme le 2 déc. 2026 (API Kaggle GetCompetition : deadline 2026-12-02, 1 soumission/jour), il reste donc environ 60 soumissions. Le classement public ne porte que sur 58 tâches (https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie ; discussion 743506). Notre 0,06 correspond à 4 tâches résolues. Le gros du peloton est à 0,12 (7 tâches) : 145 équipes à 0,12, 222 à 0,10, 248 à 0,08. 0,15 = 9 tâches et le n° 1 à 0,24 = 14 tâches. L'écart-type d'une soumission est d'environ 2,3 tâches. Nous sommes 864e sur 1 279 (/home/elrems/kaggle/runs/leaderboard/2026-10-02.csv).\n\nAucune technique publique n'atteint de façon prouvée plus de 0,15. Le 0,15 public est une copie à l'octet près du bundle Rozen, qui avait fait 0,12 : c'est du bruit de tirage (https://www.kaggle.com/code/matterhorn3838/gemma-4-superagent, cellule 2). Les deux seules équipes au-dessus de 0,15 (samson8 à 0,24, sslasme à 0,17) n'ont rien publié sur cette compétition.\n\nCe qui est établi publiquement :\n1. Un prompt court et générique bat les longues listes de règles. Black Cat v8 (règles tirées du public) a fait 0,05 contre 0,10–0,12 pour les versions courtes.\n2. Les plafonds de temps courts coûtent. Avec 4–5 min par tâche, les scores tombent à 0,08. Les bundles à 0,10–0,12 n'avaient aucun eval_config. Attention : dépasser 12 h fait échouer la soumission entière, sans score.\n3. Toute erreur de contexte vide le patch de la tâche, même si les modifications étaient déjà faites. Cela arrive avec search_similar_code (réponses non tronquées de plus de 100 000 caractères) et avec un prompt plus max_output_tokens supérieur à 32 768.\n4. Écrire des appels d'outils sous forme d'exemples de code dans le prompt fait inventer des noms d'outils au modèle : 31 % d'appels mal formés, contre 5 % si on les décrit en prose (mesure de https://github.com/damsolanke/gemma4-swe-kit).\n5. Le score local sur les 129 tâches publiques corrèle mal avec le classement (discussion 744319), car les tâches cachées viennent de dépôts privés.\n\nNotre bundle (/home/elrems/kaggle/kaggle/submission/) est structurellement proche du Black Cat à 0,12, avec trois écarts :\n- 11 pseudo-appels `run_command(\"…\")` dans le prompt principal ;\n- les outils de graphe, dont search_similar_code, exposés à l'agent principal et à l'analyseur ;\n- un script de reproduction à écrire dans /tmp, alors que les outils de fichiers refusent les chemins hors de /workspace.\n\nLa piste la moins risquée : repartir du bundle public 0,12 (Rozen ou Black Cat), retirer search_similar_code et réécrire les prompts en prose courte, une seule modification par soumission. Les vrais paris pour dépasser 0,15 restent risqués et non démontrés publiquement : la réflexion activée (thinking) depuis la mise à jour du harnais du 30 sept., et un LoRA entraîné sur des trajectoires de Gemma 31B elle-même.\n\nEn dehors de la compétition, la littérature (Agentless, mini-swe-agent) va dans le même sens : une boucle simple « localiser → reproduire → corriger → filtrer par les tests ». En revanche, le best-of-N n'y est pas faisable : environ 6 min par tâche, pas d'appels parallèles, environ 25 tokens/s.",
  "findings": [
   {
    "claim": "Rien n'est perdu : la compétition dure jusqu'au 2 déc. 2026 avec 1 soumission par jour. Notre 0,06 correspond à 4 tâches sur 58, contre 7 pour le gros du peloton à 0,12 : environ 1,3 écart-type, donc en partie du bruit.",
    "evidence": "API Kaggle GetCompetition : deadline 2026-12-02T23:59, maxDailySubmissions 1, leaderboardPercentage 50. Calcul des 58 tâches publiques et écart-type d'environ 2,3 tâches : https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie et https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743506. Distribution : /home/elrems/kaggle/runs/leaderboard/2026-10-02.csv (0,24×1, 0,17×1, 0,15×10, 0,13×45, 0,12×145, 0,10×222 ; nous sommes 864e). Nos 2 soumissions à 0,06 : `kaggle competitions submissions` (refs 56757960 et 56765392).",
    "importance": "haute"
   },
   {
    "claim": "Aucune technique publique n'atteint de façon prouvée plus de 0,15. Le 0,15 public est le bundle Rozen (0,12) resoumis à l'identique, donc du bruit. Le leader (0,24, samson8) et le n° 2 (0,17, sslasme) n'ont aucun notebook public sur cette compétition.",
    "evidence": "Tableau « Leaderboard evidence » (cellule 2) de https://www.kaggle.com/code/matterhorn3838/gemma-4-superagent : « romanrozen's bundle 0.12 / kozykappa's copy byte-identical 0.15 ». `kaggle kernels list --user samson8` et `--user sslasme` : rien sur gemma-4-developer-agent. Le plafond public reste autour de 0,12 selon https://www.kaggle.com/code/hitarthjain0/gemma-4-dev-agent-what-moves-the-leaderboard.",
    "importance": "haute"
   },
   {
    "claim": "Un prompt court et générique bat les longues listes de règles. Notre system.md écrit en plus 11 pseudo-appels `run_command(\"…\")` / `read_file(...)`. Or les exemples de commandes dans le prompt font monter les noms d'outils mal formés de 5 % à 31 %, et un outil inconnu termine la tâche avec un patch vide.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/prompts/system.md:24,32,33,35,42 (`run_command(\"python3 /tmp/repro.py\")`, etc.). Mesure « malformed tool names 30/96 (31%) … 5/96 (5%) with the commands rewritten as prose » : https://github.com/damsolanke/gemma4-swe-kit. Outil non déclaré ou halluciné → ValueError et tâche à 0 : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745028 et /745052. Black Cat v8 (longues règles) à 0,05 contre 0,10–0,12 pour les prompts courts : notebook Superagent, cellule 2. Le prompt du bundle 0,12 n'a aucun pseudo-appel : bundle « anchor » extrait de https://www.kaggle.com/code/lucifer19/black-cat-swe-agent-pack-instinct.",
    "importance": "haute"
   },
   {
    "claim": "Les débordements de contexte vident le patch (score 0 même après des modifications réussies). Notre bundle expose search_similar_code à l'agent principal et à l'analyseur. Un seul appel peut renvoyer plus de 100 000 caractères et tuer la tâche.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/agent.yaml:12-14 et sub_agents/code_analyzer.yaml:10 ; prompts/analyzer.md:7 encourage l'outil. Les 6 appels de plus de 100 000 caractères ont tous fini en ContextWindowExceededError : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744577 (l'hôte promet une troncature, non confirmée en production). « 44 of 44 overflowed sessions had an empty patch, 14 of them after successful edits » : /discussion/744692. Embeddings quasi effondrés (fichier gold dans le top 10 pour 35 tâches sur 129, contre 67 pour un grep) : /discussion/744040. Zhukov v3 et le toggle `analyzer_search_similar=False` de Superagent retirent l'outil.",
    "importance": "haute"
   },
   {
    "claim": "Notre prompt fait écrire le script de reproduction dans /tmp/repro.py. Or les outils de fichiers (write_file / edit_file) refusent les chemins hors de /workspace : appels gaspillés. Il faut créer les fichiers temporaires via run_command (heredoc).",
    "evidence": "/home/elrems/kaggle/kaggle/submission/prompts/system.md:23. « The file tools reject paths outside /workspace, so write_file to /tmp/repro.py fails » : section Version 3 de https://www.kaggle.com/code/zhukovoleksiy/gemma-4-walkthrough-first-submission.",
    "importance": "moyenne"
   },
   {
    "claim": "Le harnais a changé le 30 sept. (pensées conservées entre appels d'outils, un seul niveau d'encodage JSON, edit_file retente sans échappements, thinking_budget transmis). Mais `include_thoughts: false` (notre config) coupe toujours entièrement la réflexion. Tous les bundles notés 0,10–0,12 étaient sans réflexion et antérieurs à cette mise à jour. Activer la réflexion est une expérience, pas un gain assuré.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/configs/sampling.yaml:8. https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745059 (adk_submission 0.2.12 : include_thoughts:false → enable_thinking:false). Corrections confirmées par Ryan Holbrook : /discussion/744354, /744272, /744794. Mesure locale « 7/12 avec réflexion contre 9/12 sans » : https://github.com/damsolanke/gemma4-swe-kit. Le starter officiel utilise include_thoughts:true et max_output_tokens 16384 : https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent. Avec 16384, tout prompt de plus de 16 384 tokens est refusé : https://www.kaggle.com/code/dariushafshar/gemma-4-a-16384-output-cap-refuses-long-prompts. Garder 8192 en sortie.",
    "importance": "moyenne"
   },
   {
    "claim": "Budget de temps : les tâches tournent l'une après l'autre (environ 120, dans une fenêtre de 12 h) et un dépassement fait échouer toute la soumission. Les plafonds durs de 4–5 min ont donné 0,08. Les bundles à 0,10–0,12 n'avaient pas d'eval_config. 12 min par tâche a dépassé la limite.",
    "evidence": "Réponse de Ryan Holbrook (« Sequentially », lecture des 4 champs, dépassement = erreur) : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063. Environ 120 tâches en un seul passage : /discussion/744258. « Hard time caps hurt » (Pathfinder et Black Cat v5 à 0,08) : notebook Superagent, cellule 2. Zhukov v3 à 12 min : « Notebook Exceeded Allowed Compute ». Coût mesuré : environ 0,6 s + tokens/25,5 tok/s par appel (gemma4-swe-kit), environ 98 % du temps passé à générer (notebook Afshar 16384).",
    "importance": "moyenne"
   },
   {
    "claim": "La séparation codeur + analyseur n'est pas un gain démontré. En local, l'agent unique fait aussi bien ou mieux, et l'option skip_summarization:true termine le tour du codeur après chaque appel à l'analyseur.",
    "evidence": "« 14/44 for v4 [agent unique] and 13/44 for coder + analyzer » sur Rich mis de côté : https://www.kaggle.com/code/dmitriigluzdov/gemma-4-measure-before-you-tune. « One agent or coder plus analyzer … 0.06 versus 0.12 is only about 4 versus 7 tasks, close to noise » et « skip_summarization: true ends the coder's turn after every analyzer call, which triggers a harness nudge » : notebook Zhukov.",
    "importance": "moyenne"
   },
   {
    "claim": "Le score local (CV) sur les 129 tâches publiques corrèle mal, voire négativement, avec le classement public, car les tâches cachées viennent de dépôts privés. Notre évaluateur local doit servir à mesurer plantages, débordements, appels mal formés et durée, pas à prédire le score.",
    "evidence": "Tableaux CV/LB : CV 0,316 → LB 0,03 et CV 0,211 → LB 0,10 : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744319. « the test set draws from private repositories not available publicly » (Ryan Holbrook) : /discussion/744951.",
    "importance": "moyenne"
   },
   {
    "claim": "La compaction de l'historique ne garde que le texte du modèle et perd les sorties d'outils. Contre-mesure publique, non encore notée : répéter `{problem_description}` dans l'instruction de chaque agent et faire écrire au modèle des notes courtes.",
    "evidence": "/discussion/744794 (« Compaction loses tool results ») ; seuil de 14 336 tokens : notebook Afshar 16384 et HARNESS_README §7.2. Tableau Version 3 de Zhukov (« issue text repeated … `{problem_description}` », « writes each important finding as a short note »). Variable de gabarit autorisée : HARNESS_README.md:112 (copie téléchargée dans le scratchpad).",
    "importance": "moyenne"
   },
   {
    "claim": "Références générales : les scaffolds simples (localisation → reproduction → correction → filtrage par tests de régression) sont les plus robustes. Le best-of-N avec vote majoritaire d'Agentless n'est pas transposable ici (environ 6 min par tâche, pas d'appels parallèles).",
    "evidence": "Agentless, 3 phases, jusqu'à 40 patchs par issue, filtrage par tests de régression puis vote majoritaire, 32 % sur SWE-bench Lite : https://arxiv.org/abs/2407.01489. mini-swe-agent, bash seul, boucle ReAct d'environ 100 lignes : https://github.com/SWE-agent/mini-swe-agent. « Parallel: we don't support parallel calls » : /discussion/743964.",
    "importance": "basse"
   },
   {
    "claim": "Le LoRA est le seul levier structurel pour viser au-delà du plafond des prompts, mais aucun bundle public avec adaptateur n'a été noté. Entraîner sur les trajectoires de gemma-4-31b elle-même est autorisé. Les sorties de modèles propriétaires sont exclues par nos propres règles (et la position de Kaggle reste floue).",
    "evidence": "« Training on gemma-4-31b itself is fine » : /discussion/743964. LoRA effacés puis corrigés (/743508), cache KV réduit avec un adaptateur, désormais dimensionné dynamiquement (/744331, /744794). Distillation externe toujours « en discussion » : /discussion/742807. Règle du projet : /home/elrems/kaggle/CLAUDE.md (« aucune sortie de modèle propriétaire dans les données d'entraînement »).",
    "importance": "basse"
   },
   {
    "claim": "Pour les 2 soumissions finales, prendre comme second choix un agent différent plutôt qu'une quasi-copie du meilleur (gain privé attendu de 1,02 tâche contre 0,80).",
    "evidence": "Section « What to do with it » de https://www.kaggle.com/code/dariushafshar/gemma-4-lb-58-tasks-bronze-is-a-124-team-tie.",
    "importance": "basse"
   },
   {
    "claim": "Le skill skills/replay/SKILL.md de notre bundle n'est jamais chargé : aucune clé `skills:` dans agent.yaml. Son nom déclaré, `test_driven_replay`, ne correspond pas non plus au nom du dossier, `replay`. Le cycle de rejeu annoncé ne vit donc que dans le prompt.",
    "evidence": "/home/elrems/kaggle/kaggle/submission/agent.yaml:1-18 (pas de `skills:`) ; /home/elrems/kaggle/kaggle/submission/skills/replay/SKILL.md (frontmatter `name: test_driven_replay`). Le validateur Black Cat exige que le nom du skill égale le nom du dossier (notebook lucifer19, cellule 7).",
    "importance": "basse"
   }
  ]
 },
 {
  "key": "notre-recherche",
  "findings": [
   {
    "claim": "La localisation est LE levier transférable n°1 : dans nos échecs, le fichier corrigé n'est jamais lu dans 57 % des cas. Quand il est lu, Gemma 31B réussit 55,7 % du temps ; sinon 13,2 %. Les 129 tâches Kaggle ont le même profil que notre banc (petits correctifs ciblés), donc le budget d'outils doit aller d'abord à trouver le bon fichier et la bonne fonction.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:107-126 (46 échecs sur 81 en condition A : fichier jamais lu ; 44/79 contre 7/53). Profil des tâches (/tmp/kaggle_data/tasks.jsonl, 129 tâches : 67 fastapi, 48 rich, 13 requests, 1 httpx) : correctif médian = 1 fichier et 8 lignes ajoutées ; 115/129 touchent 3 fichiers au plus, comme notre filtre (≤ 3 fichiers, bench/select.py). Gain mesuré chez nous : écart de 42 points entre « bon fichier lu » et « raté ». Ce n'est pas un gain d'intervention.",
    "importance": "haute"
   },
   {
    "claim": "Les fenêtres de lecture tronquées sans prévenir sont la cause principale de 7 de nos 14 bugs jamais résolus, et les relectures identiques ont brûlé le budget sur 13 de ces 14 bugs. Le harness Kaggle a la même faille : read_file coupe à 150 lignes, run_command garde les 5 000 premiers caractères. À transposer dans le prompt : plan du fichier (grep -n '^\\s*def \\|^class') puis read_file sur la plage exacte de la fonction, interdiction de relire une plage déjà vue, tail sur les sorties. Gain NON mesuré : l'expérience L3 (120 contre 260 lignes, 40 bugs TRAIN) vient d'être figée et n'a pas de résultat.",
    "evidence": "/home/elrems/kaggle/docs/DIAGNOSTIC_NON_RESOLUS.md:14-41 et :187-200 (#41457 coupé à la ligne 455 alors que getFilename est aux lignes 472-482 ; #41611 : 11 relectures identiques sur 12). /home/elrems/kaggle/DECISIONS.md:60-61 (L3 figée, pas de résultat). /home/elrems/kaggle/kaggle/README.md:24-25 (troncatures du harness). Le gain attendu de +3 à 5 bugs sur 33 (DIAGNOSTIC:149-152) est une estimation, que la critique sceptique juge surévaluée.",
    "importance": "haute"
   },
   {
    "claim": "Le retour de test (condition B) n'a pas de gain démontré, et nos répétitions récentes ne reproduisent pas le +6,8 points. L'apport venait de « voir un test qui précise le comportement attendu », pas de la boucle d'exécution. Or notre prompt Kaggle IMPOSE un /tmp/repro.py et des relances à chaque tâche : cela coûte des appels d'outils et du contexte, alors que dépasser 32K tokens donne 0 à la tâche. À transférer : rendre la repro optionnelle et bornée (2 corrections maximum, comme notre déroulé), de préférence un test ciblé dans le style des tests existants du dépôt.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:96-97 : B 15/33, +6,8 pts, IC [−2,3 ; +16,7], p≈0,11 ; 1 test sur 10 passe avec le correctif officiel ; sur #41923, le patch final = la 1re édition, écrite avant toute sortie de test. Répétitions B : 15/33, 8/26, 8/26 (/home/elrems/kaggle/docs/MATRICE.md, ligne B `4f649d9`, runs partiels), contre une moyenne A de 40 %. Plafond O (oracle caché comme retour) : +9,8 pts, IC [+0,8 ; +20,5], soit 3 bugs (WRITEUP:98). Prompt Kaggle : /home/elrems/kaggle/kaggle/submission/prompts/system.md:22-24 et 33 (repro obligatoire) ; risque de note 0 au-delà de 32K : kaggle/README.md:46.",
    "importance": "haute"
   },
   {
    "claim": "Reward hacking : faire passer un test qu'il a écrit lui-même ne garantit rien. Avec ses propres oracles, Gemma « résout » 41 bugs, mais 13 (32 %) touchent du code hors du correctif officiel : cas spéciaux, mauvaise méthode. Transposition Kaggle : les tests cachés (FAIL_TO_PASS et PASS_TO_PASS) sanctionnent ces patches symptomatiques et les régressions. Règles à mettre dans le prompt : corriger dans la fonction en cause, aucun cas spécial calé sur l'entrée de la repro, lancer les tests existants du module modifié avant submit_patch.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:130-155 (#38417 : `if ($type === 'customizations') $type = 'products';`) ; /home/elrems/kaggle/docs/BOUCLE.md:121. La condition O a cassé le smoke check sur 2 bugs (#41225, #41573) : WRITEUP:98. Le 13/41 est une borne haute : le garde-fou est conservateur (WRITEUP:155).",
    "importance": "moyenne"
   },
   {
    "claim": "Contexte injecté et RAG : gain nul. Les corrections historiques similaires (R) et les glossaires (C) n'apportent rien, ce qui rejoint l'audit du harness (search_similar_code ne marche que sur des symboles exacts, similarités cosinus écrasées à 0,999). Levier transférable par la négative : ne pas compter sur search_similar_code ni sur les outils de graphe, privilégier git grep sur des symboles exacts et retirer les outils inutiles pour économiser appels et contexte.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:84-85 et 94 : R − A = 0,0 pt, IC [−9,1 ; +9,1] ; C 13/33 contre 12,8. /home/elrems/kaggle/docs/RESULTATS.md:13-18. /home/elrems/kaggle/kaggle/README.md:31 et 43-44 ; /home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md:47-50. Le prompt Kaggle propose encore les 3 outils de graphe (agent.yaml, prompts/analyzer.md:6-8).",
    "importance": "moyenne"
   },
   {
    "claim": "Le fine-tuning est inutile, voire nuisible, dans nos mesures contrôlées. Les adaptateurs E4B font perdre 7,1 et 11,1 points : ils appliquent autant de patches, mais localisent moins bien. Les « lois d'échelle LoRA Python » de /home/elrems/kaggle/docs/SCALING_LAWS_REPORT.json ne sont PAS mesurées : elles sortent d'une formule codée en dur. Elles ne doivent servir ni à décider un LoRA 31B pour le Leaderboard, ni à alimenter le papier.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:169-179 : base E4B 3,67/33 ; v15 1,33, IC [−16,2 ; 0,0] ; v16 0, IC [−23,2 ; −2,0]. /home/elrems/kaggle/harness_transfer/scripts/run_scaling_loop.py:157-164 : commentaire « Simulation d'évaluation », `\"pass_at_1\": round(0.13 + (size_mb * 0.03), 3)` et `\"syntax_reject_rate\": max(0.02, 0.20 - (size_mb * 0.04))`. Les valeurs du rapport (0,16 ; 0,19 ; 0,22 ; 0,25 ; 0,287 sur 30 tâches) ne sont d'ailleurs pas des multiples de 1/30.",
    "importance": "haute"
   },
   {
    "claim": "Variance et méthode : le même agent varie de 11 à 15 bugs sur 33 d'un essai à l'autre (écart-type 1,5). Nos deux soumissions à 0,06 (≈ 8 tâches sur 129) ne diffèrent que par une retouche du prompt de l'analyseur, sans aucune mesure locale avant. Il n'existe aujourd'hui aucune boucle d'évaluation locale de l'agent Kaggle : eval_task.py ne lance pas l'agent, clone FastAPI pour toutes les tâches et lance pytest sur tout le dépôt au lieu des tests FAIL_TO_PASS. Écart avec le n° 1 (0,24) : environ 20 tâches, largement au-delà du bruit, ce qui suggère un problème structurel (tâches à patch vide, dépassement des 32K, quota d'outils épuisé) plutôt qu'un réglage de prompt.",
    "evidence": "/home/elrems/kaggle/docs/RESULTATS.md:12 (A : 12, 13, 15, 11) ; /home/elrems/kaggle/kaggle/submissions.jsonl (A0 et A1, aucune mesure locale) ; git diff de kaggle/submission/prompts/analyzer.md (+BLAST RADIUS seulement) ; `kaggle competitions submissions` : 0,06 et 0,06. /home/elrems/kaggle/harness_transfer/scripts/eval_task.py:21, :41 et :71. Classement /home/elrems/kaggle/runs/leaderboard/2026-10-02.csv : 0,24 (1 équipe), 0,15 (10), 0,10 (222), 0,08 (248), 0,06 (197), 0,00 (133). Nous sommes dans la masse centrale.",
    "importance": "haute"
   },
   {
    "claim": "Le déroulé fixe façon Agentless (localiser, lire, éditer, tester) donne 38,6 % avec le 31B sur notre banc. Le harness ADK impose une boucle à outils libre. On peut le transposer en imposant les étapes dans le prompt, ou en construisant l'agent comme une chaîne fixe de sous-agents (à vérifier que le harness l'accepte). Gain mesuré du déroulé fixe contre une boucle libre : aucun, nous n'avons jamais comparé les deux. Notre seul indice est l'échec du 26B (localise bien, mais n'applique un patch que 12 fois sur 33) : la discipline de format d'édition compte autant que la localisation.",
    "evidence": "/home/elrems/kaggle/docs/KAGGLE_FINAL_WRITEUP.md:53-73 (déroulé) et :99 (26B : bon fichier 21 contre 19,8, patch appliqué 12/33). Catégorie « fichier lu, aucune édition applicable » : 23,5 % des échecs (WRITEUP:114). edit_file du harness = notre SEARCH/REPLACE (/home/elrems/kaggle/docs/PLAN_STRATEGIQUE_KAGGLE_FINAL.md:14). Chaîne fixe de sous-agents : hypothèse non vérifiée dans le harness.",
    "importance": "moyenne"
   },
   {
    "claim": "Ce qui ne se transfère pas : les oracles Playwright avec remise à zéro de la base, le contexte métier PrestaShop (multiboutique, glossaires), les réglages de windows() et grep de notre flow.py (les outils Kaggle sont figés), la boucle d'auto-apprentissage (elle exige le correctif officiel) et les chiffres absolus. Côté tâches : les problem_statement Kaggle sont souvent des descriptions de PR, pas des tickets utilisateur. Une partie sont des ajouts de fonctionnalités : 11/129 créent un fichier, environ 14 sont marquées ✨/feat. Les tâches datent de 2023-07 à 2026-06, beaucoup avant la coupure de Gemma (janv. 2025), donc mémorisation possible. Nos taux PrestaShop post-coupure sont pessimistes pour Kaggle.",
    "evidence": "Statistiques calculées sur /tmp/kaggle_data/tasks.jsonl (129 tâches, uniquement .py, created_at 2023-07-29 → 2026-06-20). Nos oracles écrits par Gemma : 0 % validés en mode UI, 39 % en PHP CLI (/home/elrems/kaggle/docs/BOUCLE.md:7-11). Côté transfert : écrire un test pytest est plus proche du mode CLI. Cutoff : WRITEUP:38. Le pool TRAIN n'est pas représentatif du TEST : DIAGNOSTIC_NON_RESOLUS.md:184.",
    "importance": "moyenne"
   }
  ],
  "summary": "Ce n'est pas foutu, mais nos deux soumissions (0,06 et 0,06, soit environ 8 tâches sur 129, dans la masse centrale du classement) ont été envoyées à l'aveugle. Il n'existe aucune évaluation locale de l'agent Kaggle (/home/elrems/kaggle/harness_transfer/scripts/eval_task.py ne lance pas l'agent, clone FastAPI pour toutes les tâches et lance pytest sur tout le dépôt). La v2 ne changeait qu'une ligne du prompt de l'analyseur. L'écart avec le n° 1 (0,24, environ 20 tâches) dépasse largement le bruit (nos essais varient de 11 à 15 sur 33) : on cherche un défaut structurel (patch vide, contexte au-delà de 32K, quota d'outils épuisé), pas un réglage de prompt.\n\nCe qui se transfère de notre recherche, avec ce qu'on a mesuré :\n- **Localisation** : 57 % des échecs viennent d'un fichier jamais lu. Fichier lu : 55,7 % de réussite ; sinon 13,2 %. Les tâches Kaggle ont le même profil que notre banc (correctif médian : 1 fichier, 8 lignes).\n- **Fenêtres de lecture** : elles bloquent 7 de nos 14 bugs jamais résolus ; les relectures identiques ont brûlé le budget sur 13 d'entre eux. Le harness tronque aussi (read_file à 150 lignes, run_command à 5 000 caractères). Pas de gain mesuré : l'expérience L3 (taille de lecture) n'a pas encore de résultat.\n- **Retour de test (B)** : +6,8 points, non significatif (p ≈ 0,11), et les répétitions ne le reproduisent pas (8/26 deux fois). L'apport venait de voir le test, pas de l'exécuter. Or notre prompt Kaggle rend la repro obligatoire, ce qui coûte du contexte alors qu'au-delà de 32K la tâche vaut 0.\n- **Plafond avec l'oracle caché** : +3 bugs sur 33.\n- **Reward hacking** : 32 % des bugs « résolus » avec ses propres tests sont hors du correctif officiel. Il faut interdire les cas spéciaux et relancer les tests existants du module avant de soumettre.\n- **Contexte injecté (corrections similaires, glossaires)** : gain nul. Cohérent avec des outils de recherche sémantique du harness inopérants : mieux vaut git grep sur des symboles exacts.\n- **Fine-tuning** : −7,1 et −11,1 points sur E4B. Point grave : les « lois d'échelle LoRA Python » de /home/elrems/kaggle/docs/SCALING_LAWS_REPORT.json ne sont pas mesurées. Elles sortent d'une formule codée en dur (/home/elrems/kaggle/harness_transfer/scripts/run_scaling_loop.py:157-164, pass_at_1 = 0,13 + 0,03 × taille) et ne doivent servir ni pour une décision ni pour le papier.\n\nCe qui ne se transfère pas : PHP, Playwright, base de données, le métier PrestaShop, nos réglages internes de lecture et de grep, et la boucle d'auto-apprentissage. Les tâches Kaggle incluent aussi des ajouts de fonctionnalités et beaucoup sont antérieures à la coupure de Gemma.\n\nPriorités :\n1. Monter une évaluation locale réelle (agent + tests FAIL_TO_PASS/PASS_TO_PASS) sur une trentaine de tâches, et compter les patches vides et les dépassements de 32K.\n2. Alléger le prompt : repro optionnelle et bornée, plan du fichier puis lecture ciblée, pas de relecture, outils de graphe retirés.\n3. Ne soumettre qu'une variante mesurée localement au-dessus du bruit."
 }
]
```
