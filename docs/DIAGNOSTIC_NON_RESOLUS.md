# Diagnostic des 14 bugs TEST jamais résolus par Gemma 4 31B (2 oct. 2026)

Produit par 14 analyses indépendantes (une par bug : traces A/R/C/B/O, correctif officiel, oracle), une synthèse et une critique sceptique.
**Règle : ces leviers viennent de traces TEST → validation sur TRAIN d'abord, une seule mesure sur TEST ensuite (REGLES.md).**

# Les 14 bugs TEST jamais résolus : diagnostic et leviers

**Réponse courte à ta question : non, on n'a pas testé tous les paramètres.** On a varié les conditions (A, R, C, B, O). Les réglages de l'outillage sont restés fixes : fenêtre de lecture, budget de lignes, 2 retours arrière, top 25 du grep. Or c'est là que se trouve le goulot sur ces 14 bugs. La moitié des échecs vient de l'outil de lecture, pas de Gemma.

Deux limites sur les traces :
- Presque toutes ont été produites avec l'ancien `windows()`, celui d'avant le commit 1e75370 du 29/09. Une partie a aussi tourné avant le commit 578c1e9, qui corrige la pollution d'état en O.
- J'ai simulé hors modèle le `windows()` actuel. Il règle #41611, mais pas #41100, #41457, #40999 ni #41225. Il est même pire sur #41225 et #40999.

## 1) Tableau

| Bug | Cause principale | Oracle équitable ? | Faisable par le 31B ? | En une ligne |
|---|---|---|---|---|
| #40743 | logique fausse | oui | peut-être | Corrige l'appelant (OrderHistory). La cause est dans `getRestPaid()`, visible dans le grep mais jamais lue |
| #40070 | fenêtre de lecture | **douteux** (instable) | **oui** | Hook ajouté au bon endroit mais sans `id_carrier`. L'appel de référence (AdminCarriersController, ligne 461) est hors fenêtre |
| #41100 | fenêtre de lecture | oui | **oui** | getEmailHTML est à la ligne 3031 sur 3081, jamais montrée. Gemma demande « line 261 onwards » et reçoit la même fenêtre |
| #41327 | fenêtre de lecture | **douteux** (correctif défensif, ticket d'enquête) | peut-être | createList n'est jamais affiché. OrderDetail.php est dans le grep mais jamais lu |
| #41412 | logique fausse | oui | peut-être | `htmlentitiesUTF8` est sous ses yeux, mais il s'obstine sur le punycode dans `Mail::send` |
| #40999 | fenêtre de lecture | oui | peut-être | Le mot-clé « Shop » ne fait montrer que les lignes 1-260 ; `copyShopData` n'est jamais lu |
| #41036 | logique fausse | oui | peut-être | Ajoute un trim() en aval de l'exception ; 3 essais coupés alors qu'il demandait le bon fichier |
| #41457 | fenêtre de lecture | oui | **oui** | getFilename (lignes 472-482) coupé sans prévenir à la ligne 455. Les 2 essais qui l'ont vu n'avaient plus de budget |
| #41225 | fenêtre de lecture | **douteux** (l'oracle ne teste que getAttributesParams, absent du ticket) | peut-être | La méthode citée est coupée 5 lignes avant sa signature ; tri ag.position absent |
| #41611 | fenêtre de lecture | oui | **oui** | Cause donnée par le ticket, mais le corps de la méthode n'est jamais montré : 11 relectures identiques sur 12 |
| #41573 | localisation (mots-clés) | **douteux** (nom et type du champ imposés) | peut-être | « CartRule » remplit le top 25 de fichiers legacy ; câblage sur 3 couches |
| #41735 | localisation (mots-clés) | **douteux** (assertion values_count hors ticket) | **oui** | 58 fichiers « featurevalue » saturent le grep. R1 et R4 trouvent la moitié du correctif |
| #41727 | localisation (mots-clés) | oui | **oui** | « index.php » fait remonter 517 fichiers à 0 ligne. Le bon fichier est 1er sans ce mot-clé |
| #41570 | logique fausse | oui | peut-être | Déplace une colonne déjà déclarée ; le tri par défaut (FeatureFilters) n'est jamais lu |

## 2) Répartition des causes et comparaison avec docs/ECHECS.md

| Cause principale (diagnostic manuel) | Bugs |
|---|---|
| Fenêtre de lecture (et relecture identique) | **7** |
| Logique fausse | 4 |
| Localisation (mots-clés ou grep) | 3 |

Causes secondaires les plus fréquentes :
- Budget de 2 retours arrière brûlé sur des relectures identiques : 13 bugs sur 14.
- Condition B dégénérée (pas de `replay*.spec.js`, donc B équivaut à A) ou test de repro cassé : 12 sur 14.
- **En O, l'oracle n'a jamais tourné** (pas d'édition, le seul retour est « aucune édition applicable ») : **9 sur 14**.

Comparaison avec la taxonomie automatique de `/home/elrems/kaggle/docs/ECHECS.md` :

| Catégorie | Auto | Manuel |
|---|---|---|
| Mauvais fichier | 10 | 3 |
| Aucune édition | 3 | — |
| Correctif faux | 1 | 4 |
| Fenêtre / outillage | n'existe pas | 7 |

La catégorie « mauvais fichier » est **surestimée**, pour trois raisons :
- `loc_hit` ne prenait que les derniers fichiers lus dans les runs A du 25/09. Pour #41412, le bon fichier avait pourtant été lu au tour 1.
- Le bon fichier est souvent lu, mais pas la bonne méthode (#41457, #41611 : `bon_fichier=1` partout).
- Elle confond « jamais montré à cause de l'outil » et « mal choisi par le modèle ».

À ajouter à `bench/taxonomy.py` :
- une catégorie **outillage/fenêtre** ;
- une métrique **« fonction officielle visible dans le contexte »**, c'est-à-dire `loc_hit` au niveau du symbole.

## 3) Leviers génériques, classés par nombre de bugs adressés

| # | Levier | Bugs adressés | Effort | Risque |
|---|---|---|---|---|
| L1 | **Lecture v3** : pagination, lecture par plage ou par symbole, plan du fichier | 11 (#41100, #41327, #41412, #40999, #41457, #41225, #41611, #41735, #41573, #41727, #41570) | 1 j | faible |
| L2 | **Budget et messages explicites** : budget de lecture séparé, lectures exécutées en CORRIGER, chemins introuvables signalés, édition forcée | 10 (#41100, #41327, #40999, #41036, #41457, #41573, #41735, #41727, #41570, #41611) | 0,5 j | faible |
| L3 | **windows() v3** : pondération par rareté, spans plafonnés, couverture par mot-clé, méthode entière, marqueur de coupure | 9 (#40070, #41100, #40999, #41457, #41225, #41611, #41036, #41573, #41735) | 1 j | moyen (ça a déjà régressé une fois) |
| L4 | **Retour serveur enrichi en O/B** : exception PHP, test lancé même sans patch, `php -l` | 9 (#40743, #40070, #41412, #40999, #41036, #41457, #41570, #41327, #41573) | 1,5 j (Docker et éval) | faible (pas de fuite : erreur observée sur la base) |
| L5 | **Grep v2** : pondération par rareté, extraits de lignes, diversité par répertoire, mots-clés à 0 résultat signalés, pas d'inondation par les chemins | 7-8 (#40743, #40070, #41100, #41327, #41573, #41735, #41727, #41225) | 1 j | moyen |
| L6 | **Aller à la définition (1 saut)** | 7 (#40743, #41327, #41412, #40999, #41457, #41570, #41036) | 1 j | moyen (budget de tokens) |
| L7 | **Robustesse du parseur** : parse_json, FILE: hérité, SEARCH tolérant aux espaces, blocs no-op rejetés | 5 (#41727, #41225, #41573, #41611, #41412) | 0,5 j | faible |
| L8 | **Étapes d'invite** : hypothèse vérifiable, édition minimale, composant frère qui marche | ~7 | 0,5 j | **élevé** (sur-ajustement de l'invite, effet sur le 31B incertain) |

### Implémentation concrète (fichiers `/home/elrems/kaggle/agent/flow.py` et `/home/elrems/kaggle/agent/run.py`)

**L1, lecture v3**
- `run.py`, `backtrack()` : tenir à jour `seen[f]`, l'ensemble des plages déjà montrées. Une relecture du même fichier sert les spans suivants encore non vus, et le message le dit (« déjà montré : … »).
- Dans la liste `files`, accepter `"chemin:a-b"` et `"chemin::methode"`.
- Nouvelle fonction `flow.outline(src)` : regex `function\s+(\w+)`, qui produit « plan : l.N nom » avec le nombre total de lignes. Elle est appelée dans `flow.msg_read()`.
- Fichier entier s'il fait au plus ~180 lignes (#41036 : 69 lignes, coupé à 47).

**L2, budget**
- `run.py`, `backtrack()` :
  - remplacer `backtracks < 2` par un budget de lecture (~4 en ÉDITER, +1 par tour CORRIGER) ;
  - ne pas décompter une demande identique ;
  - pour un chemin invalide, ne plus filtrer en silence (`if flow.show(...)`) : renvoyer « introuvable, chemins proches : … » via `difflib.get_close_matches` sur `ls-tree` ;
  - budget épuisé : faire un tour « produis maintenant un SEARCH/REPLACE » au lieu de terminer sans édition.
- Le texte `BACKTRACK` affiche le nombre de retours restants.

**L3, windows()**
- `flow.windows()` :
  - poids de chaque mot-clé = log(lignes / lignes touchées). Un mot-clé présent dans plus de 20 % des lignes pèse 0 (cas de « Shop » ou « CartRule »).
  - supprimer l'exception `or not selected`, qui laisse passer des spans de 366 à 1026 lignes ;
  - couper chaque span à 2×WINDOW autour de sa meilleure ligne ;
  - première passe : 1 span par mot-clé distinct ;
  - bonus pour une ligne `function …kw…` ;
  - étendre le span jusqu'à la fin de la méthode englobante (comptage d'accolades, au plus 80 lignes) ;
  - ajouter le marqueur « [lignes a-b omises : méthodes X, Y] ».
- Mots-clés utilisés : l'union de ceux du ticket et de ceux de la relocalisation (`run.py` l.177).

**L4, retour serveur** (dans `bench/eval.py` plus `run.py`, pas dans `flow.py`)
- Capturer la dernière exception de `var/logs/*.log` (classe, message, 3 frames).
- `run.py` : si `not diff` en O ou B, lancer quand même le test sur la base et montrer l'assertion.
- `php -l` sur les fichiers modifiés avant le rejeu (#41573 : erreur de syntaxe affichée comme « timeout BO »).

**L5, grep v2**
- `flow.grep()` :
  - remplacer le tri `(not name_hit, -len, -lines)` par la somme des poids de rareté des mots-clés trouvés ;
  - `name_hit` seulement si le nom de fichier est rare, à moins de 20 fichiers (cas de « index.php » : 517) ;
  - découper `Classe::methode` en `Classe` et `function methode` ;
  - au plus 6 fichiers par répertoire.
- `flow.msg_grep()` : mots-clés à 0 résultat (cas de « PS_INVOICING_ENABLED : 0 »), plus 1 à 2 lignes `git grep -n` du mot-clé le plus rare pour les 10 premiers fichiers.

**L6, aller à la définition**
- Nouvelle fonction `flow.callees(window_text, commit)` : regex `(->|::)(\w+)\(`, puis `git grep -n "function nom("`. Au plus 3 définitions de 20 lignes au plus, ajoutées dans `msg_read` sous « DÉFINITIONS APPELÉES ».

**L7, parseur**
- `flow.parse_json()` : si le JSON se parse mais que la clé manque, renvoyer `[]`, sans repli regex. Aujourd'hui, `{"keywords"}` donne une lecture de `index.php`.
- `BLOCK` dans `parse_edits` : hériter du `FILE:` précédent.
- `flow.apply_edits()` : correspondance ligne à ligne avec espaces et tabulations normalisés, appliquée seulement si elle est unique ; rejeter les blocs où SEARCH est identique à REPLACE.

## 4) Bugs à exclure ou à signaler

**Oracle douteux : #40070, #41327, #41225, #41573, #41735.** On ne retouche pas ces oracles maintenant : assouplir un oracle TEST après avoir vu les sorties de l'agent est aussi un ajustement sur le TEST. À la place :
- publier le score **avec et sans ces 5 bugs** (analyse de sensibilité) ;
- signaler ces 5 bugs dans le papier ;
- seule exception : la non-déterminisme de #40070 (`[]` contre `[carrier-0]` pour le même patch) est un défaut du banc, à corriger et à documenter comme tel.

**Conditions dégénérées, à marquer dans `eval/results.csv`** :
- B sans repro valide (`STATUS_REPRO=echec`) : 10 bugs, plus 2 avec une repro cassée (#41225, #41573). B mesure A sur ces bugs.
- O sans aucune exécution de l'oracle : 9 bugs.
- O pollué avant 578c1e9 (#40743, #41412) : à relancer.

## 5) Protocole anti-sur-ajustement (obligatoire, voir REGLES.md, décision du 2 oct.)

1. Ces leviers viennent des traces TEST. Avant tout run, on les **gèle et on les date dans DECISIONS.md**, avec le critère de succès.
2. **Validation sur TRAIN uniquement**, sur les 99 bugs TRAIN à oracle Gemma de `/home/elrems/kaggle/docs/BOUCLE.md` (41 résolus et 58 non résolus en O).
   - Il faut une base A sur ces 99 bugs, avec l'ancien outillage et le nouveau, sur les mêmes bugs.
   - Critère : au moins +3 bugs résolus nets en A, et aucun bug résolu perdu au-delà du bruit.
   - Le bruit se mesure par la répétition de l'ancien code. Test apparié de type McNemar.
3. Un levier n'est retenu que s'il aide sur TRAIN. On fait alors **une seule mesure sur TEST** (A×4 plus O), sans itération.
4. Le papier dit explicitement que les leviers ont été identifiés sur des échecs TEST, validés sur TRAIN, puis mesurés une fois sur TEST. Il précise aussi que les gains sur TRAIN peuvent être gonflés par la mémorisation, puisque ces bugs sont antérieurs à la date de coupure de Gemma, mais que la comparaison avant/après reste appariée.

## 6) Plan d'expériences

1. **Exp 1, outillage de lecture** (L1, L2, L3, L7), environ 3 j de dev.
   - TRAIN : 99 bugs × A × 1 essai, ancien et nouveau outillage, soit environ 200 runs, environ 10 h de machine, API Gemma seulement.
   - Gain attendu sur TEST : +3 à 5 bugs sur 33 (#41611, #41457, #41100, #40070 ; peut-être #40999 et #41225).
   - Effet aussi sur les 14 % « aucune édition » du total.
2. **Exp 2, grep v2 et aller à la définition** (L5, L6), environ 2 j, avec le même protocole TRAIN.
   - Gain attendu sur TEST : +1 à 3 (#41727, #41735, #40743, #41412).
3. **Exp 3, retour serveur en O et B** (L4, plus réparation de la génération des repros B), environ 2 j.
   - TRAIN : les 58 bugs non résolus en O.
   - Gain : rendre la borne haute O mesurable (elle ne mesure rien sur 9 de ces 14 bugs) et +2 à 4 bugs en B/O. C'est l'argument central de la thèse.

Ensuite, on gèle l'outillage et on fait une mesure TEST unique. Tout cela passe avant le go/no-go FT du 22 oct. Le fine-tuning (FT) devra utiliser exactement le même `flow.py`, puisque le format des messages est partagé avec `trajectories/reconstruct.py`.

Fichiers de référence : `/home/elrems/kaggle/agent/flow.py` (`grep` l.42, `windows` l.73, `parse_json` l.215), `/home/elrems/kaggle/agent/run.py` (`backtrack` l.164, filtre silencieux l.173, recalcul des fenêtres l.177), `/home/elrems/kaggle/docs/ECHECS.md`, `/home/elrems/kaggle/docs/BOUCLE.md`, `/home/elrems/kaggle/REGLES.md` (l.39).

---

# Critique sceptique (à lire avec la synthèse : elle corrige plusieurs points)

**Critique de la synthèse sur les 14 bugs TEST jamais résolus.** J'ai relu les traces de #41100, #41457, #41611, #41727, #41412 et #40070, ainsi que les oracles de #40070, #41225, #41735, #41573 et #41457. Je n'ai rien modifié.

**Ce qui est faux**
1. **« Les réglages de lecture sont restés fixes. »** C'est faux. Le commit 36a9f7c du 28/09 à 20 h 55 a fait passer `WINDOW` de 30 à 20 et `MAX_LINES_PER_FILE` de 260 à 120. Tous les runs 31B A/R/C/O/B (25-28/09) ont donc tourné avec une lecture séquentielle de 260 lignes ; les traces affichent bien `[lignes 1-260]`.
   - La simulation du « windows() actuel » mélange deux changements : le nouveau classement et un budget divisé par deux. Le « pire sur #41225 et #40999 » vient peut-être seulement du budget.
   - Ce réglage n'a jamais été balayé. Pourtant `MAX_LINES_PER_FILE` se règle par variable d'environnement, sans aucun développement : c'est le premier levier à essayer, sur TRAIN.
   - L'« ancien outillage » doit être figé par commit, comme le font `/home/elrems/kaggle-rep/*/AGENT_COMMIT` (4f649d9 et f7dcbdc).
2. **B dégénérée : c'est 14 bugs sur 14, pas 12.** 11 bugs n'ont aucun `replay*.spec.js`. 3 ont une repro cassée (`passe avec correctif officiel : False`) : #41225, #41573 et aussi **#41457**, absent de la liste de la synthèse. Sur ces 14 bugs, B ne mesure rien.
3. **#41727, « le bon fichier est 1er sans index.php ».** C'est surévalué. J'ai simulé `flow.grep` sur la base :
   - avec `['Entity','unlink','RecursiveDirectoryIterator']`, le bon fichier est **15e** ;
   - il n'est 1er qu'avec `src/Entity`.
4. **#41100, « Gemma demande line 261 onwards ».** C'est exact, mais Gemma demande la suite de `classes/Mail.php`, le **mauvais fichier** (run 20260926-065152-O). C'est donc aussi un problème de localisation.
5. **#40070, oracle « douteux (instable) ».** L'instabilité est réelle : le même patch (e0a9e0), réévalué deux fois à 4 minutes d'écart, donne `[]` puis `[carrier-0]`. Mais les deux valeurs sont des échecs, et à juste titre :
   - le patch omet `id_carrier`, alors que c'est le contrat du hook legacy (`AdminCarriersController.php` l.461), lu par le module de test ;
   - l'oracle est donc équitable. Il faut corriger le défaut du banc, mais ne pas classer ce bug dans l'analyse de sensibilité.
6. **#40070 ne relève pas de l'Exp 1 (fenêtre).** La référence se trouve dans un *autre* fichier. Ce bug relève de L6 ou du « composant frère », pas de L1/L3.
7. **Pollution en O : 5 bugs concernés, pas 2.** Les deux runs O (05:20 et 06:51 le 26/09) sont **tous deux** antérieurs à 578c1e9 (10:36). Les verdicts ont été réévalués (`reevalue=1`). En revanche, le retour vu par Gemma en cours de run a pu être pollué partout où l'oracle a tourné : #40070, #40743, #41225, #41412 et #41573.

**Ce qui est surévalué**
- **L1 « 11 bugs ».** #41412 n'en relève pas : la ligne fautive `Tools::htmlentitiesUTF8($config[...])` est montrée dès l'étape ÉDITER dans 9 essais sur 15, donc c'est de la logique. #41727 non plus : le fichier n'a jamais été ouvert.
- **Le décompte par levier double les bugs.** L1, L2 et L3 couvrent presque les mêmes bugs. Il faut raisonner en gain net combiné, pas additionner.
- **Gain attendu de l'Exp 1 (+3 à 5).** Il est plausible pour #41611 : ma simulation montre bien `getAssociatedRestrictions` (l.1901) dans `[1834-1964]`. Il l'est pour #41457 s'il y a un saut vers la définition, car Gemma demande ensuite `OrderInvoice.php`. Il est incertain pour #41100 et #40070.
- **Durée de l'Exp 1 : « ~10 h, API seulement ».** C'est faux : le verdict TRAIN demande Docker, checkout et oracle pour chaque bug (environ 5 min par bug avec le 31B en A le 25/09), plus le limiteur de quota. Compter plutôt 16 h ou plus.
- **Critère « +3 nets » avec McNemar à 1 essai.** Sur 99 bugs, ce n'est pas significatif ; par exemple 8 contre 5 paires discordantes donne p ≈ 0,58. Il faut 2 ou 3 répétitions, ou bien assumer un seuil fixé à l'avance sans prétendre à la significativité.

**Risques de sur-ajustement au TEST**
- Plusieurs seuils sont calibrés sur des exemples TEST nommés : fichier entier jusqu'à 180 lignes (#41036, 69 lignes), poids nul au-delà de 20 % (« Shop », « CartRule »), nom de fichier compté s'il désigne moins de 20 fichiers (index.php), 6 fichiers par répertoire. Il faut les fixer sur TRAIN, ou les geler dans DECISIONS.md **avant** de les voir agir.
- **Le pool TRAIN n'est pas représentatif.** Les 99 oracles sont tous en mode `php` (0 en UI/BO), alors que les oracles TEST sont en Playwright BO/FO. Un levier validé sur TRAIN peut ne pas se transférer, et inversement.
- **Les verdicts sont asymétriques.** Sur TRAIN, il y a un garde-fou au niveau fonction (`bench/loop_stats.py`) : un correctif dans l'appelant (type #40743) ou dans un callee (#41457 corrigé dans `OrderInvoice`) y est rejeté, alors qu'il passerait sur TEST.
- **Les 14 bugs sont provisoires.** Les répétitions B et O (runs 2-3, `runs/20261002-0824*`) sont en cours. Il faut attendre la fin avant de figer la liste.

**Ce qui manque**
- **Un vrai bug dans `backtrack()`** (`/home/elrems/kaggle/agent/run.py`, environ l.164-178) :
  - si Gemma demande un chemin inexistant, `backtracks += 1` s'applique quand même, `reply` ne change pas et la boucle repart ;
  - les **2 retours sont brûlés sans aucun tour modèle** ;
  - visible sur #41727, où Gemma demande `ModuleEntityManager.php`, un chemin qui n'existe pas, et le run se termine sur « relocaliser ».
  - C'est à corriger en priorité dans L2.
- **`result["feedbacks"]` a disparu de `run.py` depuis 1e75370.** Le constat « l'oracle n'a jamais tourné en O » (9 sur 14, que j'ai confirmé) n'est plus mesurable sur les nouveaux runs. Il faut le restaurer avant l'Exp 3.
- **Le coût sur le fine-tuning n'est pas compté.** Modifier `flow.py` oblige à régénérer `trajectories/reconstruct.py` et à réentraîner avant le 22 oct.
- **L1 est faisable à moindre coût.** `windows(..., extra_lines)` existe déjà, mais n'est jamais appelé avec ce paramètre : la lecture `chemin:a-b` peut passer par là.
- **Règle « jamais de sécurité ».** Le correctif officiel de #41100 étend une vérification de chemin (sa description parle de « path security check »). C'est à confirmer comme acceptable avant d'en faire un exemple vitrine dans le papier.

**Ce qui est confirmé**
- #41611 : 11 relectures identiques sur 12, et la signature est coupée à la ligne 1904.
- #41457 : la fenêtre s'arrête à 455 sans marqueur, alors que `getFilename` est aux lignes 472-482.
- O sans oracle sur 9 bugs : #40999, #41036, #41100, #41327, #41457, #41570, #41611, #41727, #41735.
- `loc_hit` ne regardait que les derniers fichiers lus : #41412 a `bon_fichier=0` alors que le bon fichier est montré au tour 1.
- Oracles douteux #41225 et #41573 : justifié. Pour #41225, le ticket parle de l'ordre des valeurs dans un groupe, l'oracle teste l'ordre des groupes dans l'ancre d'URL. Pour #41573, le nom et l'identifiant du champ sont imposés.
- #41735 : douteux, mais faiblement (le ticket dit « même comportement que PS 8 »).

---

## Annexe : diagnostics par bug (JSON)

```json
[
 {
  "pr": "40743",
  "fix_summary": "Le correctif officiel touche un seul fichier, classes/order/OrderInvoice.php. Dans OrderInvoiceCore::getRestPaid(), il supprime la garde `if (!$this->number) { return 0; }` (4 lignes retirées). Quand les factures sont désactivées, Order::setInvoice() crée quand même un OrderInvoice, avec number = 0. La garde faisait donc renvoyer 0 à getRestPaid(), et OrderHistory::changeIdOrderState() n'enregistrait aucun OrderPayment (`if ($rest_paid > 0)`).",
  "agent_behaviour": "Le scénario est le même dans les 11 essais exploitables (A x4, R x4, C, C+pages, B, O). Mots-clés : OrderHistory, changeIdOrderState, OrderPayment, paid, plus une clé de configuration inventée (PS_INVOICING_ENABLED, PS_INVOICING ou PS_INVOICE_ENABLED ; la vraie est PS_INVOICE). L'agent lit seulement classes/order/OrderHistory.php, parfois avec PaymentModule.php, UpdateOrderStatusHandler.php ou OrderState.php. Il ne lit jamais OrderInvoice.php, alors que ce fichier figure dans les résultats de grep (environ 15e, 41 à 171 lignes). La fenêtre de lecture montre bien la ligne `$rest_paid = $invoice->getRestPaid();` (lignes 251-336). Gemma suppose alors à tort que, factures désactivées, la commande n'a aucune facture. Il réécrit le bloc « set orders as paid » en `if (empty($invoices)) { créer un paiement de total_paid... } else { boucle d'origine }`, sur 30 à 50 lignes qui dupliquent l'existant. Deux raisons rendent ce patch sans effet à l'exécution. D'abord, getInvoicesCollection() renvoie un objet PrestaShopCollection, et empty() sur un objet vaut toujours false. Ensuite, la collection contient de toute façon l'OrderInvoice créé par setInvoice() avec number = 0, donc on passe toujours par la branche d'origine, où getRestPaid() renvoie 0. Le bloc Paiement reste à « (0) ». Autres défauts d'édition : propriété inexistante `$order->total_paid_tax` (A-2) ; en A-1, un SEARCH recopié de mémoire sans le bloc Db::insert, donc introuvable et aucun patch. En O, l'agent reçoit l'échec de l'oracle (« (0) » au lieu de « (1) »). Il ne remet pas en cause son hypothèse : il demande OrderPayment.php (et pas OrderInvoice.php), puis réécrit le même bloc avec des retouches cosmétiques (order_reference non tronqué, appel à Module::getInstanceByName sans condition).",
  "primary_failure": "logique_fausse",
  "secondary_failures": [
   "localisation : la fonction appelée (OrderInvoice::getRestPaid) est visible dans la fenêtre lue et présente dans le grep, mais n'est jamais lue ; l'agent corrige l'appelant à l'aveugle",
   "mots-clés : clé de config inventée (PS_INVOICING_ENABLED) ; son absence de résultat au grep passe inaperçue, ce qui aurait pu mener à PS_INVOICE et Order::setInvoice",
   "format_edition : en A-1, SEARCH non exact (bloc Db::insert omis), aucun patch appliqué",
   "oracle_ou_env_douteux (essai O seulement) : le 2e retour 'Hunk #1 FAILED at 296' est un artefact du banc. Le run (26/09 05:20) est antérieur au commit 578c1e9 (26/09 10:36), qui restaure les fichiers hors correctif officiel touchés par l'agent : OrderHistory.php restait patché par l'évaluation précédente. De plus, msg_test ne montrait pas encore l'état courant des fichiers, d'où le 'SEARCH introuvable' au tour 5. Le patch final appliqué ensuite sur une base saine (result_reeval.json) échoue lui aussi sur l'assertion métier",
   "B : aucun retour utilisable, le test de repro écrit par Gemma est en échec technique (STATUS_REPRO : timeout), feedbacks=[]"
  ],
  "evidence": "Diff officiel (bench/diffs/40743.diff) : OrderInvoice.php, getRestPaid(), retrait de `if (!$this->number) { return 0; }`. Code de base 8f610459 : OrderHistory::changeIdOrderState appelle `$order->setInvoice()` si `$new_os->invoice`. Order::setInvoice crée `new OrderInvoice()` avec `number = 0` et n'attribue de numéro que si `Configuration::get('PS_INVOICE')`. Ensuite `foreach ($invoices as $invoice) { $rest_paid = $invoice->getRestPaid(); if ($rest_paid > 0) {...` : getRestPaid renvoie 0, donc aucun OrderPayment. Traces : files_read vaut ['classes/order/OrderHistory.php'] dans A-1 à A-4 et C, et inclut OrderHistory plus PaymentModule ou UpdateOrderStatusHandler dans R et B. loc_hit=false partout. Dans le grep de 20260925-114612-A et 20260926-052040-O, la ligne 'classes/order/OrderInvoice.php (41)' / '(171)' est présente mais jamais choisie. Patches : 20260925-114612-A `+ if (empty($invoices)) { $rest_paid = $order->total_paid_tax - $order->total_paid;` ; 20260925-142912-A et 20260926-134839-C `if (empty($invoices)) { ... total_paid_tax_incl - total_paid` ; 20260925-165642-A `if (count($invoices) > 0) {...} else {...}` ; 20260925-114712-R `if (empty($invoices)) { $payment->amount = $order->total_paid;`. Erreur oracle identique partout : `expect(header).toContainText('(1)')`, le bloc Paiement reste à (0). O (runs/20260926-052040-O/40743/trace.jsonl) : tour 3, après l'échec de l'oracle, la réponse est {\"files\": [\"classes/order/OrderPayment.php\"]}. Tour 4 : SEARCH copié depuis l'état patché, même logique empty(). Tour 5 : 'Hunk #1 FAILED at 296'. Pourtant `patch --dry-run` de ce patch.diff sur OrderHistory.php du commit de base s'applique proprement (vérifié en local). Il s'agit donc de la pollution d'état corrigée par 578c1e9. result.json de O : edit_errors 'bloc SEARCH introuvable'. Oracle (bench/replay/40743/oracle.bo.spec.js + setup.sql) : PS_INVOICE=0, commande 5 remise en « En attente de virement » sans paiement ni facture, passage au statut 2 « Paiement accepté » via le formulaire BO, puis vérification de « (1) » et d'une ligne de paiement en €. STATUS = valide.",
  "oracle_fair": "oui",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Afficher le corps des fonctions appelées : quand la fenêtre lue contient des appels `->methode(` ou `Classe::methode(` dans la zone éditée, ajouter automatiquement les définitions courtes (moins de 15 lignes) de ces méthodes, résolues par git grep 'function methode'.",
    "why": "La cause est dans une fonction appelée de 4 lignes, lisible depuis la zone éditée : getRestPaid() et sa garde `if (!$this->number) return 0;`. Gemma ne fait jamais la lecture de second niveau de lui-même. Ce levier s'applique à tout bug où l'appelant est le bon point d'entrée mais pas le bon point de correction.",
    "generic": true
   },
   {
    "lever": "Grep diagnostique : renvoyer le nombre de résultats par mot-clé, y compris les zéros (« PS_INVOICING_ENABLED : 0 occurrence »), avec les identifiants proches qui existent (correspondance floue sur les constantes et clés de config).",
    "why": "L'agent invente des identifiants qui ne renvoient rien, sans s'en rendre compte. Ici, signaler l'absence aurait orienté vers PS_INVOICE, donc vers Order::setInvoice, où l'on voit que la facture est créée avec number = 0.",
    "generic": true
   },
   {
    "lever": "Étape « hypothèse vérifiable » avant ÉDITER : faire écrire l'hypothèse sur l'état à l'exécution (« quand X, alors la variable Y vaut Z »), puis exiger une lecture qui la confirme (où Y est produit) avant d'autoriser l'édition.",
    "why": "Les 11 essais reposent sur la même hypothèse fausse et jamais vérifiée (« factures désactivées = pas d'OrderInvoice »). Le code qui la contredit (setInvoice) est à quelques lignes de la zone lue.",
    "generic": true
   },
   {
    "lever": "Contrôle statique du patch avant le test : php -l plus PHPStan (ou des règles maison) sur les fichiers modifiés. Signaler les propriétés inexistantes et les conditions toujours vraies ou fausses (empty() sur un objet, propriété non déclarée).",
    "why": "`$order->total_paid_tax` n'existe pas et `empty($collection)` vaut toujours false : ces patches étaient des no-ops détectables sans Docker. Le retour est moins cher et plus précis que celui de l'oracle.",
    "generic": true
   },
   {
    "lever": "Retour d'exécution côté serveur dans les conditions O et B : joindre au résultat du test les requêtes SQL d'écriture du rejeu (ou une trace des fonctions PHP appelées), par exemple « aucun INSERT dans order_payment ; OrderInvoice::getRestPaid() a renvoyé 0 ».",
    "why": "L'échec de l'oracle ne dit que « (0) au lieu de (1) », sans aucune piste de localisation. Gemma en a conclu qu'il fallait lire OrderPayment.php. Un retour sur le chemin d'exécution distinguerait « mauvaise branche » de « mauvaise valeur ».",
    "generic": true
   },
   {
    "lever": "Après un échec du test, forcer une hypothèse alternative : interdire de rééditer le même bloc sans avoir lu au moins un nouveau fichier (ou une nouvelle fonction appelée), et échantillonner plusieurs hypothèses distinctes au lieu de répéter le même essai.",
    "why": "En O, la réaction à l'échec a été une retouche cosmétique du même bloc. Sur 12 essais, la stratégie n'a jamais varié (convergence totale vers la même fausse piste).",
    "generic": true
   },
   {
    "lever": "Inciter à l'édition minimale : demander le plus petit changement qui corrige la cause, et pénaliser (ou signaler) les réécritures qui dupliquent plus de 20 lignes existantes.",
    "why": "Le correctif officiel retire 4 lignes. L'agent duplique à chaque fois le bloc de paiement complet en if/else, ce qui multiplie les risques d'erreur de SEARCH (A-1) et masque la vraie question : pourquoi rest_paid vaut 0.",
    "generic": true
   },
   {
    "lever": "Relancer l'essai O (et les essais O antérieurs au commit 578c1e9) avec le banc actuel : restauration des fichiers hors correctif et affichage de l'état courant dans msg_test.",
    "why": "Le 2e retour de l'essai O (« Hunk FAILED ») vient d'un état pollué du conteneur, pas du modèle. La réaction à l'oracle n'a donc été mesurée valablement que sur un tour.",
    "generic": true
   }
  ]
 },
 {
  "pr": "40070",
  "fix_summary": "Un seul fichier est touché : src/Adapter/Carrier/CommandHandler/EditCarrierHandler.php. Le correctif injecte HookDispatcherInterface dans le constructeur et ajoute à la fin de handle(), juste avant return $newCarrierId, l'appel dispatchWithParameters('actionCarrierUpdate', ['id_carrier' => (int) $command->getCarrierId()->getValue(), 'carrier' => $newCarrier]). Les paramètres sont exactement ceux de l'appel de l'ancienne page (AdminCarriersController.php:461, AdminCarrierWizardController.php:801).",
  "agent_behaviour": "Avec Gemma 4 31B, deux comportements reviennent dans les 12 essais.\n(1) Dans 6 essais sur 12 (A2, A3, A4, R1, R2, C+pages et O), l'agent localise parfaitement. Il choisit le mot-clé actionCarrierUpdate et le fichier EditCarrierHandler.php, qui est classé 1er ou presque dans le grep, puis édite au bon endroit (après updateAssociatedZones, avant return). Le patch est toujours le même : `\\Hook::exec('actionCarrierUpdate', ['carrier' => $newCarrier]);`. Le hook est donc bien déclenché, mais sans le paramètre `id_carrier`. Ce patch est sorti en 3 tours, bloc SEARCH/REPLACE propre, appliqué.\n(2) Dans 5 essais (A1, R3, R4, C, B), l'agent n'édite rien. Il lit pourtant EditCarrierHandler, puis part relire CarrierRepository.php et classes/Carrier.php. Il redemande ensuite le même fichier, reçoit exactement la même fenêtre (Carrier.php lignes 1-260, ou EditCarrierHandler lignes 1-69 en B), et épuise ses 2 retours arrière.\nIl ne consulte jamais la ligne de l'ancienne page qui appelle `Hook::exec('actionCarrierUpdate', ['id_carrier'=>..., 'carrier'=>...])`. Pourtant AdminCarriersController.php figure dans tous les résultats de grep, et il a même été choisi en R1 et en O. Mais la fenêtre servie était lignes 1-260, et l'appel est à la ligne 461. Le modèle ignore donc le contrat de paramètres du hook.\nEn O, le premier retour vient d'une erreur fatale : il avait écrit `Hook::exec` sans antislash dans un fichier avec namespace, la page n'affiche pas `.alert-success`. L'agent corrige bien en `\\Hook::exec`. Le second retour indique `Received: \"[]\"`, ce qui signifie « hook non reçu ». L'agent conclut que le hook ne se déclenche pas, part lire Carrier.php puis CarrierRepository.php, et finit le budget sans nouvelle édition.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "logique_fausse",
   "boucle_ou_budget_tours",
   "oracle_ou_env_douteux",
   "localisation_mots_cles"
  ],
  "evidence": "**Correctif contre patch Gemma**\n- Officiel : `'id_carrier' => (int) $command->getCarrierId()->getValue(), 'carrier' => $newCarrier`.\n- Gemma, 6 fois à l'identique (md5 e0a9e0f1… dans 114612-A, 142912-A, 165642-A, 052040-O, 065152-O, 134839-C ; variante multi-lignes b651e502 dans 101441-R et 114712-R) : `\\Hook::exec('actionCarrierUpdate', ['carrier' => $newCarrier]);`.\n\n**Ce que vérifie l'oracle**\n- Le module de test benchcarrierhook.zip fait `Configuration::updateValue('BENCHCARRIERHOOK_LAST', 'carrier-' . (int) $params['id_carrier'])`.\n- Résultat sur tous les patchs Gemma réévalués : `Expected \"[carrier-3]\" / Received \"[carrier-0]\"`. Le hook s'exécute donc, mais `id_carrier` est absent.\n- Le bug est corrigé à 95 %. Il ne manque qu'un paramètre.\n\n**Contrat de l'ancienne page, présent dans le dépôt au commit de base 6f1d66f**\n- controllers/admin/AdminCarriersController.php:461 et AdminCarrierWizardController.php:801 : `Hook::exec('actionCarrierUpdate', ['id_carrier' => (int) $current_carrier->id, 'carrier' => $new_carrier])`.\n- AdminCarriersController (145 lignes de correspondance) apparaît dans tous les grep.\n- En O tour 2 et en R1 tour 2, il est lu, mais la trace montre `('controllers/admin/AdminCarriersController.php', 'lignes 1-260')`. La ligne 461 est hors fenêtre.\n\n**Fenêtres et boucles**\n- A1 (092935) : tours 3 et 4 = `{\"files\": [\"classes/Carrier.php\"]}` deux fois, même fenêtre 1-260 ; résultat « aucune édition ».\n- C (103202) : même schéma.\n- B (092011) : la fenêtre par mots-clés de EditCarrierHandler.php donne « lignes 1-69 », car « Carrier » est partout dans l'en-tête. Le point d'insertion est aux lignes 143-148. L'agent redemande le même fichier aux tours 4 et 5, reçoit la même fenêtre, et finit sans édition.\n\n**Grep**\n- Seuls des noms de fichiers et des nombres de lignes sont renvoyés.\n- Les nombres sont gonflés par des mots-clés génériques (« Carrier », « update » : Cart.php 486, Carrier.php 472). Les 2 seuls fichiers contenant vraiment `actionCarrierUpdate` sont noyés parmi les autres.\n\n**Condition O (065152)**\n- Retour 1 : erreur fatale de namespace, corrigée au tour 3 avec `\\Hook::exec`.\n- Retour 2 : `Received: \"[]\"`, auquel l'agent répond par `{\"files\": [\"classes/Carrier.php\"]}` puis CarrierRepository.\n- Le même patch donne `[carrier-0]` en 052040-O reeval et `[]` en 065152-O reeval. Le retour n'est pas déterministe et, en 065152, il est trompeur (il dit « hook non déclenché » au lieu de « id_carrier manquant »).\n\n**Condition B**\n- STATUS_REPRO = echec : le test de repro écrit par Gemma plante sur une erreur SQL 1054. B n'a donc eu aucun retour utile et vaut A.",
  "oracle_fair": "douteux",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "Grep qui renvoie aussi les lignes correspondantes (fichier:ligne: extrait), du mot-clé le plus rare d'abord. Par exemple, les 5 premières occurrences exactes de chaque identifiant CamelCase ou de chaque chaîne entre quotes du ticket, avec ±3 lignes de contexte.",
    "why": "Ici, `Hook::exec('actionCarrierUpdate', ['id_carrier' => ..., 'carrier' => ...])` serait apparu dès le tour 1 et aurait donné le contrat de paramètres sans aucune lecture. Le levier vaut pour tout bug où le code existant contient un appel de référence (hooks, événements, traductions, services).",
    "generic": true
   },
   {
    "lever": "Pondérer les mots-clés par rareté (IDF), dans le classement du grep comme dans le score des fenêtres de lecture. Un mot-clé présent dans plus de N fichiers (« Carrier », « update ») pèse presque zéro ; un identifiant présent dans 2 à 3 fichiers pèse fort.",
    "why": "Les décomptes et les fenêtres sont dominés par les mots-clés génériques. Résultats : la fenêtre 1-69 de EditCarrierHandler en B, une fenêtre de AdminCarriersController qui manque la ligne 461, et les seuls fichiers qui contiennent vraiment le hook noyés parmi d'autres.",
    "generic": true
   },
   {
    "lever": "Lecture paginée ou ciblée. Si un fichier déjà lu est redemandé, servir la fenêtre SUIVANTE (ou permettre {\"files\": [\"f.php:400-480\"]} / {\"symbol\": \"handle\"}) au lieu de la même fenêtre. Toujours inclure la fin de la méthode la plus pertinente.",
    "why": "5 essais sur 12 se terminent sans édition parce que l'agent redemande le même fichier et reçoit des octets identiques (Carrier.php 1-260 deux fois, EditCarrierHandler 1-69 deux fois). Le budget de retours arrière brûle sans aucune information nouvelle.",
    "generic": true
   },
   {
    "lever": "Lecture « voisins de référence » automatique : quand le ticket parle d'ancienne page contre page migrée, ou cite un hook ou un événement, ajouter d'office un extrait des autres sites d'appel du même identifiant (le pendant legacy/Symfony) au message ÉDITER.",
    "why": "La parité avec le comportement existant est le critère implicite de beaucoup de tickets de migration Symfony. Le modèle sait l'appliquer s'il voit la référence : il recopie le style dès qu'il est visible.",
    "generic": true
   },
   {
    "lever": "Message ÉDITER enrichi de règles mécaniques : dans un fichier avec namespace, préfixer les classes legacy par \\\\ ; préférer les services injectés (HookDispatcherInterface) dans src/. Lint php -l, ou vérification `use`/namespace, avant le test.",
    "why": "En O, un tour de retour a été consommé par une erreur fatale `Hook::exec` sans antislash. Un lint local aurait évité ce tour, qui coûte cher en budget.",
    "generic": true
   },
   {
    "lever": "Fiabiliser l'environnement de l'oracle en O et dans l'éval : réinitialiser l'état du module et le cache de hooks avant chaque rejeu, rejouer 2 fois et signaler les résultats instables. Pour les oracles de type « module espion », exposer dans le retour les paramètres réellement reçus (ex. clés de $params).",
    "why": "Le même patch donne `[carrier-0]` dans un run et `[]` dans un autre. Le `[]` dit à tort « hook non déclenché » et lance l'agent sur une fausse piste, alors que `[carrier-0]` ou « params reçus : [carrier] » aurait mené directement à la correction.",
    "generic": true
   },
   {
    "lever": "Écarter ou signaler les tests de repro B qui échouent pour une raison technique (STATUS_REPRO=echec). Ne pas compter la condition B sur ces bugs, ou retomber explicitement sur A.",
    "why": "Ici, B n'a eu aucun retour exploitable (erreur SQL 1054 dans le test de repro). L'essai B mesure donc A et fausse la comparaison A/B.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41100",
  "fix_summary": "Le correctif officiel touche un seul fichier, controllers/admin/AdminTranslationsController.php, et une seule fonction, AdminTranslationsControllerCore::getEmailHTML (ligne 3031 sur 3081, donc tout en fin de fichier). Le test de chemin `strpos(realpath($email_file), _PS_MAIL_DIR_) === 0` refusait les gabarits de modules. Le correctif accepte en plus les chemins sous `_PS_MODULE_DIR_` qui contiennent `/mails/`, avec une garde file_exists/realpath. Cela représente environ 20 lignes dans une seule condition.",
  "agent_behaviour": "Le comportement est le même sur les 12 essais 31B (et aussi pour 4B et pour le modèle affiné E) : aucun bloc SEARCH/REPLACE n'a jamais été produit, les 13 patch.diff 31B sont vides. Déroulé type : (1) Les mots-clés sont génériques et orientés vers l'ENVOI de mails, pas vers l'aperçu : « Mail::Send », « getTemplate »/« getMailTemplate », « Mail », « module », « translations », « email ». Aucun essai n'a choisi « preview », « emailHTML » ou « html » au premier tour. (2) Le grep classe bien AdminTranslationsController.php en tête, et l'agent le choisit dans 10 essais sur 12 (loc_hit). Mais il le prend presque toujours avec classes/Mail.php, qui est une fausse piste tirée de la 1re phrase du ticket (« Customers receive automated emails… empty »). (3) L'ancienne fonction windows() (WINDOW=30, plafond de 260 lignes, extraits pris dans l'ordre du fichier) remplit tout le budget avec les premières occurrences de mots très fréquents (« mail », « module », « translations » : 911 lignes trouvées dans ce fichier). L'agent ne voit donc que l'en-tête du fichier (lignes 1-260, ou 3-68, 107-167, 176-297…). La ligne la plus basse jamais montrée est la 2407 ; getEmailHTML (3031) n'apparaît dans AUCUN des 12 essais. (4) À l'étape ÉDITER, au lieu de proposer une édition, l'agent répond {\"files\": [mêmes fichiers]}. Il espère voir la suite, et en O il le dit explicitement : « Please provide the content from line 261 onwards ». L'outillage renvoie exactement la même fenêtre (mêmes fichiers, mêmes mots-clés, donc la même sortie), et les 2 retours arrière autorisés sont gaspillés dans cette boucle. (5) En O, comme il n'y a aucun patch, le retour reçu est « aucune édition applicable » et pas l'oracle. Le compteur de retours arrière est déjà épuisé, donc les demandes {\"files\"} puis {\"keywords\": [\"getContent\",\"render\",\"preview\",…]} des tours « corriger » sont ignorées. L'agent n'a jamais vu le résultat de l'oracle. (6) 3 essais sur 12 ont perdu un tour entier parce que la réflexion a consommé tout max_tokens=16384 (completion_tokens=0, réponse vide après suppression de <thought>) : A1 au tour localiser, donc aucun mot-clé et aucun résultat de grep ; R1 et R4 au tour éditer.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "localisation_mots_cles",
   "boucle_ou_budget_tours",
   "ticket_insuffisant",
   "autre: réflexion Gemma qui épuise max_tokens (3/12 tours vides)"
  ],
  "evidence": "Correctif officiel : bench/diffs/41100.diff, getEmailHTML au @@ -3036. Au commit de base 89e88504, AdminTranslationsController.php fait 3081 lignes : getEmailHTML est à la l.3031, le strpos(realpath…, _PS_MAIL_DIR_) à la l.3039, displayAjaxEmailHTML à la l.3051 ; l'appel JS action:'emailHTML' est dans translation_mails.tpl:116. Analyse automatique des 14 traces de eval/results.csv : edits=0 et getEmailHTML_shown=0 partout sauf E (1 édition, hors sujet, dans translation_mails.tpl). Lignes maximales montrées : 260 / 995 / 260 / 402 / 1002 (O) / 404 (B) / 409 (C) / 2407 (C+pages). runs/20260925-114612-A : en-têtes des fenêtres « [lignes 1-260] » pour les deux fichiers, assistant aux tours editer, relire et relire = {\"files\": [\"classes/Mail.php\",\"controllers/admin/AdminTranslationsController.php\"]} trois fois de suite, avec un prompt identique (18244 caractères). runs/20260926-065152-O : T3 « I need to see the rest of the file… truncated », T4 « Please provide the content from line 261 onwards », T5/T6 corriger = « aucune édition applicable », puis {\"files\"} et {\"keywords\"} non exécutés (backtracks déjà à 2), result.feedbacks = 2 fois « aucune édition applicable ». Tours vides : 20260925-092935-A localiser (prompt 296 tokens, total 16677, raw_len 43994), 20260925-092934-R et 20260925-171642-R editer (total 22650, completion_tokens 0). B (20260928-092011-B) : il n'existe pas de replay*.spec.js pour 41100 (STATUS_REPRO = echec, timeout), donc B a reçu le même message que A (628 caractères) et aucun retour (feedbacks=[]). Simulation de la windows() ACTUELLE (version du 29/09, plafond de 120) avec les mots-clés des essais : getEmailHTML reste invisible pour les 7 jeux de mots-clés, et le span retenu fait jusqu'à 1026 lignes (1592-2618), car « or not selected » laisse passer un span fusionné géant. Le correctif d'agent du 29/09 ne règle donc pas ce cas. Seul un mot-clé « emailHTML » ferait apparaître les lignes 3011-3075.",
  "oracle_fair": "oui",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "Pagination ou lecture par plage explicite : accepter {\"read\": {\"file\": ..., \"lines\": [a,b]}} ou {\"files\": [...], \"from\": N}, et surtout ne jamais renvoyer une fenêtre identique : quand un fichier est redemandé, servir les spans suivants qui n'ont pas encore été montrés",
    "why": "L'agent a demandé lui-même « content from line 261 onwards », et ses relectures ont renvoyé exactement le même texte, ce qui a brûlé les 2 retours arrière. C'est la cause directe de l'absence d'édition",
    "generic": true
   },
   {
    "lever": "Plan structurel du fichier lu : liste des méthodes et classes avec leurs numéros de ligne (php -l / regex `function \\w+`), ajoutée en tête de chaque bloc CONTENU, plus une action « lire la méthode X »",
    "why": "Sur un fichier de 3000 lignes, un plan où figurent getEmailHTML et displayAjaxEmailHTML permet de faire le lien « aperçu HTML » -> méthode, même avec des mots-clés génériques ; le coût est d'environ 100 lignes",
    "generic": true
   },
   {
    "lever": "Corriger windows() : plafonner chaque span (par ex. couper un span fusionné à 2×WINDOW autour de ses lignes les mieux notées), pondérer les mots-clés par leur rareté (IDF à l'échelle du fichier, pour que « mail » ou « module » pèsent peu) et toujours inclure au moins un extrait pour chaque mot-clé rare",
    "why": "La version actuelle laisse passer un span de 1026 lignes (« or not selected »), et les mots très fréquents écrasent les mots spécifiques ; l'ancienne version montrait seulement le haut du fichier",
    "generic": true
   },
   {
    "lever": "Recherche qui renvoie les LIGNES trouvées (git grep -n, 1 à 2 lignes de contexte, quelques occurrences par fichier) et pas seulement le nombre d'occurrences par fichier",
    "why": "L'agent verrait `getEmailHTML`, `email-html-frame` et `emailHTML` dans les résultats et pourrait choisir ses mots-clés ou sa plage en connaissance de cause",
    "generic": true
   },
   {
    "lever": "Invite LOCALISER : demander des mots-clés tirés des termes d'interface du ticket (preview, l'action ou l'écran nommés dans les étapes) en plus des classes supposées, et décourager les mots génériques (≥ 2 mots-clés distinctifs)",
    "why": "Les 12 essais ont choisi « Mail », « module » et « Mail::Send », qui suivent le symptôme secondaire (envoi de mails) au lieu des étapes de reproduction (aperçu dans Traductions)",
    "generic": true
   },
   {
    "lever": "Budget de réflexion : plafonner la réflexion (reasoning_effort ou budget de réflexion) ou relancer automatiquement quand la réponse nettoyée est vide ou que completion_tokens=0, avec un rappel « réponds maintenant dans le format »",
    "why": "3 essais sur 12 ont perdu un tour entier (localiser ou éditer) parce que la réflexion a consommé les 16384 tokens",
    "generic": true
   },
   {
    "lever": "Forcer une tentative d'édition après N relectures, et compter les retours arrière par étape plutôt qu'au global : en O/B, les demandes {\"files\"}/{\"keywords\"} de l'étape CORRIGER doivent rester exécutables",
    "why": "En O, l'agent a enfin proposé « preview » à T6, mais ce n'était plus exécuté ; et sans aucun patch, il ne reçoit jamais le retour de l'oracle, donc la borne haute O n'a rien mesuré",
    "generic": true
   },
   {
    "lever": "Signaler les conditions dégénérées : quand il n'y a pas de replay*.spec.js, marquer B comme « identique à A » dans les résultats",
    "why": "Pour 41100, B a reçu le même message que A et aucun retour ; le compter comme un essai B indépendant fausse la comparaison A/B",
    "generic": true
   }
  ]
 },
 {
  "pr": "41327",
  "fix_summary": "Le correctif touche uniquement classes/order/OrderDetail.php. OrderDetailCore::create() renvoie désormais le résultat de $this->save() (avant : valeur de retour ignorée, la méthode ne renvoyait rien), et OrderDetailCore::createList() lève une PrestaShopException('Failed to create order detail for product id %d') quand create() échoue. C'est un correctif défensif (une insertion ratée ne doit plus donner une commande validée en silence avec des lignes en moins), pas la correction d'une cause racine identifiée.",
  "agent_behaviour": "Le schéma est le même sur les 12 essais 31B. Mots-clés presque identiques : validateOrder, PaymentModule, Cart::getProducts, OrderDetail/order_detail, parfois Order/Cart. L'agent lit classes/PaymentModule.php, puis classes/Cart.php, parfois classes/order/Order.php. Il ne lit jamais classes/order/OrderDetail.php, alors que grep le propose (rang 3 à 13 sur 25 dans 10 essais sur 12). Les fenêtres affichées sont surtout l'en-tête : PaymentModule [lignes 1-42/1-46] (licence, use, install()), puis 160-377 (début de validateOrder), puis la coupure à 260 lignes ; Cart.php [1-260] (constructeur) ou [969-1029]. La chaîne utile n'a jamais été visible : PaymentModule::createOrderFromCart (l.978), $order->add() vérifié par une exception (l.1131-1135) puis $order_detail->createList() non vérifié (l.1159-1160), et OrderDetail::create/createList (l.731-830). L'agent use ses 2 retours arrière à redemander le même fichier, qui revient à l'identique puisque les fenêtres dépendent des mots-clés initiaux. Sa 3e demande {\"files\":...} est ignorée sans prévenir, et l'essai finit sur « aucune édition » (10 essais sur 12). Dans 2 essais (R3, C1), il produit une édition propre et bien appliquée, mais sur une autre hypothèse : dans PaymentModule, la branche multi-expédition (feature flag) écrase product_list quand plusieurs colis ont le même transporteur ; il la remplace par un array_merge. Cette branche est inactive par défaut et n'existe pas en 1.7.8.9, donc l'oracle reste à 1 article au lieu de 2. En O, aucune édition n'est jamais appliquée : le retour de l'oracle se réduit à « aucune édition applicable » et l'oracle n'a donc jamais tourné. Les dernières demandes de l'agent ({\"files\":[\"classes/Order.php\",...]}, puis {\"keywords\":[\"new OrderDetail\",\"OrderDetail\"]}, qui allait dans la bonne direction) ne sont pas exécutées, car les retours arrière sont déjà épuisés.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "ticket_insuffisant",
   "localisation_mots_cles",
   "boucle_ou_budget_tours",
   "logique_fausse",
   "multi_fichiers"
  ],
  "evidence": "1) Dans aucune des 23 traces de runs/*/41327/trace.jsonl (31B, 26B-A4B, E), les chaînes 'createList', 'function createOrderFromCart' ou 'function create(Order' n'apparaissent dans un message user : le code fautif n'a jamais été montré.\n2) Rang de classes/order/OrderDetail.php dans le grep de l'étape « lire » : 11 (A1, 20260925-092935-A), 7 (A2, 114612-A), 11 (A3), 13 (A4, R1, R3, R4, C1, B), 3 (R2) ; absent en O et C+pages, où les mots-clés génériques « Order » et « Cart » font gonfler Cart.php (1121 lignes) et OrderController (1036). Pour le nom de fichier, « OrderDetail » fait d'abord remonter src/Adapter/Order/OrderDetailUpdater.php (129).\n3) Fenêtres lues, d'après le champ user des tours editer/relire : PaymentModule '[lignes 1-42]' + '[lignes 160-377]' + '[… tronqué …]' ; Cart.php '[lignes 1-260]' (en-tête, resetStaticCache) en A1 et O ; en A2/A4/B, '[lignes 969-1029]'. Le 26B-A4B (20260926-052040-A, bon_fichier=1) a bien lu OrderDetail.php, mais la fenêtre était '[lignes 1-42]' (en-tête), et il n'a fait aucune édition.\n4) Relectures identiques : en B (20260928-092011-B), relire PaymentModule redonne exactement les mêmes 12251 caractères ; en A3, 'PaymentModule.php + Cart.php' revient deux fois avec 22216 caractères identiques.\n5) La 3e demande de lecture est ignorée : run.py backtrack() s'arrête à backtracks<2, puis parse_edits renvoie rien → 'aucune édition'. Pourtant BACKTRACK (« 2 fois au plus ») reste affiché, y compris à l'étape CORRIGER, où il n'est plus honoré (O : tours 'corriger' {\"files\":[\"classes/Order.php\",...]} puis {\"keywords\":[\"new OrderDetail\",...]}, sans effet).\n6) Le chemin classes/Order.php (inexistant) est supprimé sans message par le filtre `if flow.show(base, f)`.\n7) Le mot-clé 'Cart::getProducts', présent dans tous les essais, ne correspond jamais à rien : git grep -F cherche la chaîne littérale « Cart::getProducts », que le code n'écrit pas sous cette forme.\n8) R3/C1 : le patch.diff modifie PaymentModule.php l.363 (productsByCarriers → array_merge) ; verdict de l'oracle 'Expected: 2 Received: 1'.\n9) B équivaut en fait à A : STATUS_REPRO = 'echec' (timeout du test de repro), donc pas de replay*.spec.js et feedbacks=[].\n10) O (20260926-065152-O) tourne avec l'ancien déroulé (avant le commit 4f649d9 « Déroulé v2 », du 26/09 à 19:36), avec MAX_LINES_PER_FILE=260 et des fenêtres séquentielles.",
  "oracle_fair": "douteux",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Fenêtres de lecture structurelles : ne pas noter l'en-tête (licence, use, déclaration de classe, propriétés), et montrer d'abord un plan du fichier (liste des méthodes avec leurs numéros de ligne). L'agent demande ensuite des méthodes précises ({\"read\": \"fichier::méthode\"}) au lieu de recevoir le haut du fichier.",
    "why": "Dans tous les essais, le budget de lecture (120 à 260 lignes) part dans les lignes 1-42 de PaymentModule et 1-260 de Cart ; les méthodes utiles (createOrderFromCart l.978, createList l.799) n'ont jamais été affichées, même quand le bon fichier a été lu (26B-A4B).",
    "generic": true
   },
   {
    "lever": "Outil « suivre l'appel » (aller à la définition) : à partir d'un appel visible (->createList(, $this->createOrderFromCart(), afficher le corps de la méthode appelée, même dans un autre fichier ; ou ajouter d'office les définitions des méthodes appelées dans la fenêtre.",
    "why": "Le bug se trouve deux appels plus loin que le point d'entrée sur lequel l'agent se fixe (validateOrder → createOrderFromCart → OrderDetail::createList → create → save) ; la recherche par mots-clés seule ne fait pas franchir ces sauts.",
    "generic": true
   },
   {
    "lever": "Ne jamais renvoyer deux fois un contenu identique : si le fichier demandé a déjà été lu avec les mêmes fenêtres, répondre « déjà lu : précise une méthode, des lignes ou de nouveaux mots-clés », et recalculer les fenêtres avec les mots-clés de la demande courante.",
    "why": "Les 2 retours arrière autorisés ont été consommés à relire le même PaymentModule/Cart (même taille de message, octet pour octet) ; l'agent tourne en boucle sans rien apprendre.",
    "generic": true
   },
   {
    "lever": "Normaliser et contrôler les mots-clés : découper 'Classe::méthode' en 'Classe' et 'function méthode', signaler à l'agent les mots-clés sans aucun résultat et ceux trop génériques (Order, Cart), et classer en tête les fichiers dont le nom de classe correspond exactement (OrderDetail.php avant OrderDetailUpdater.php).",
    "why": "'Cart::getProducts', présent dans tous les essais, ne trouve jamais rien ; 'Order' et 'Cart' en O et C+pages noient le classement, OrderDetail.php sort du top 25 ou reste derrière OrderDetailUpdater.",
    "generic": true
   },
   {
    "lever": "Résoudre les chemins inexistants : correspondance approchée (classes/Order.php → classes/order/Order.php) ou message d'erreur explicite, au lieu de supprimer la demande en silence.",
    "why": "En O, la demande de classes/Order.php a été écartée sans que l'agent le sache.",
    "generic": true
   },
   {
    "lever": "Rendre le budget de tours explicite et cohérent : afficher les retours arrière restants, retirer le texte BACKTRACK quand ils sont épuisés et demander alors une édition obligatoire ; à l'étape CORRIGER, exécuter réellement les relectures/recherches demandées (budget séparé).",
    "why": "10 essais sur 12 finissent sur « aucune édition » parce que la 3e demande de lecture est ignorée ; en O, la recherche finale {new OrderDetail, OrderDetail}, qui était la bonne direction, n'est pas exécutée alors que le message l'autorisait.",
    "generic": true
   },
   {
    "lever": "Pour les tickets d'investigation sans étapes de reproduction, ajouter une étape HYPOTHÈSES avant LOCALISER : énumérer 2 ou 3 mécanismes candidats (échec silencieux, écrasement, filtre, condition de course), en tirer les mots-clés, puis explorer chaque hypothèse.",
    "why": "Le ticket (« we need your assistance to investigate potential culprits ») ne désigne pas le mécanisme ; l'agent s'est fixé sur une seule hypothèse (le panier, puis l'écrasement multi-transporteur dans une branche inactive) sans envisager les échecs d'insertion non vérifiés.",
    "generic": true
   },
   {
    "lever": "Retour d'exécution dès le départ : lancer le test (oracle en O, replay en B) sur le code de base avant toute édition, et montrer la sortie de l'échec, avec l'erreur SQL ou PHP des logs si possible.",
    "why": "En O, l'oracle n'a jamais tourné (aucune édition applicable), donc la borne haute n'a rien apporté ; ici, le log de base aurait montré « bench41327: order_detail insert refused », qui oriente directement vers l'insertion dans order_detail.",
    "generic": true
   },
   {
    "lever": "Réparer la repro B quand STATUS_REPRO=echec (timeout) : sinon B équivaut à A et la condition ne mesure rien pour ce bug.",
    "why": "Pour #41327, B n'avait aucun replay*.spec.js (feedbacks=[]), donc cet essai ne mesure pas l'effet des tests rejoués.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41412",
  "fix_summary": "The official fix changes one file, src/Adapter/Email/EmailConfigurationTester.php, in testConfiguration(). The recipient address ($config['send_email_to']) and the sender address (PS_SHOP_EMAIL) were passed to Mail::sendMailTest through Tools::htmlentitiesUTF8, which turned an IDN domain like sjöbüren.se into sj&ouml;b&uuml;ren.se and made Symfony Mime reject it with RfcComplianceException. The fix replaces those two calls with a plain (string) cast.",
  "agent_behaviour": "Every trial follows the same pattern. Gemma always picks punycode/validation keywords (Mail::Send, Validate::isEmail, idn_to_ascii, RFC 2822, Swift_*), and grep always ranks classes/Mail.php first. In about 10 of 13 trials it then asks to read Mail.php plus EmailConfigurationTester.php. The window for EmailConfigurationTester.php (lines 29/40-104) always shows the whole testConfiguration() method, including the two buggy lines `Tools::htmlentitiesUTF8($config['send_email_to'])` and `Tools::htmlentitiesUTF8($this->configuration->get('PS_SHOP_EMAIL'))`. Gemma still never edits that file in any trial. It has decided the cause is a missing punycode conversion, because the `idn_to_ascii` keyword brings up Mail::toPunycode. In the editing step it asks to re-read Mail.php only, gets exactly the same windows back (same keywords, so the same deterministic windows), uses up its 2 allowed backtracks, and stops. This happens in A1, A3, A4, B, C+pages, R2 and R3, ending with 'aucune édition' (no edit), or in A2 and R1/R4 with a cosmetic edit (`self::toPunycode($replyTo)` in Mail::send). When it does edit, the edits are always toPunycode calls on from/replyTo/to/bcc in Mail::send (C, O). Mail::send is not on the test-email path at all: that path is Mail::sendMailTest, called from the window it was shown. In C+pages it states the need itself, in English: 'I need to see the code between lines 369 and 497', and the tool returns the same window again. In O, the feedback (500 plus the assertion line that contains `&ouml;|&uuml;`) is ignored. Gemma removes its own `$from = toPunycode` edit, adds `$email->from(new Address(toPunycode($from)))` in Mail::send, writes a no-op block (SEARCH == REPLACE), and then inserts the same block twice.",
  "primary_failure": "logique_fausse",
  "secondary_failures": [
   "fenetre_lecture : impossible de demander une plage de lignes ou une méthode (Mail::sendMailTest, l.767-846, jamais affichée). Relire le même fichier renvoie les mêmes fenêtres, d'où une boucle stérile de 2 retours arrière dans environ 9 essais sur 13",
   "boucle_ou_budget_tours : les 2 retours arrière sont gâchés sur une relecture identique, puis 0 édition (A1, A3, A4, B, C+pages, R2, R3)",
   "oracle_ou_env_douteux : en O, le 2e retour a été pollué par l'environnement. Mail.php était encore patché par l'évaluation précédente ('Hunk #1 succeeded at 299 (offset 4 lines)', soit exactement les 4 lignes ajoutées au 1er essai, et 'Hunk #2 FAILED' sur la ligne replyTo déjà modifiée). Le correctif 578c1e9 (restauration des fichiers hors correctif officiel) date du 26/09 à 10:36 UTC, après le run O de 06:51. Le verdict final O était lui aussi faussé (2 blocs en échec), mais la réévaluation donne un vrai 500",
   "condition B invalide pour ce bug : STATUS_REPRO=echec, aucun replay*.spec.js, donc B équivaut à A sans retour",
   "métrique bon_fichier sous-estimée : les runs A du 25/09 calculaient loc_hit sur les derniers fichiers lus seulement. EmailConfigurationTester.php a pourtant bien été lu au premier tour dans A1 à A4"
  ],
  "evidence": "Correctif officiel : bench/diffs/41412.diff (EmailConfigurationTester::testConfiguration, 2 lignes htmlentitiesUTF8 remplacées par un cast (string)). Le prompt utilisateur du tour 2 'editer' affiche ces lignes mot pour mot dans :\n- runs/20260925-092935-A/41412/trace.jsonl (T2, [lignes 40-100]) ;\n- runs/20260925-114612-A ;\n- runs/20260925-142912-A (T2, [lignes 29-104]) ;\n- runs/20260925-165642-A ;\n- runs/20260928-092011-B ;\n- runs/20260926-103202-C ;\n- runs/20260926-134839-C ;\n- runs/20260926-065152-O (T2, [lignes 40-104]) ;\n- R 114712 et 143833.\n\nRéponse de Gemma à ce tour : `{\"files\": [\"classes/Mail.php\"]}` dans A1, A2, A4, B, R2, R3 ; `{\"files\": [\"classes/Validate.php\"]}` dans A3. Les tours relire T3 et T4 ont des en-têtes de fenêtres identiques, par exemple '[lignes 1-40] | [lignes 60-238] | [lignes 322-362]' deux fois de suite dans A4 et B. C+pages T2 à T4 : '(Note: I need to see the code between lines 369 and 497 to locate the `$email->from()` call...)' trois fois, avec la même fenêtre 208-368/498-558/956-993 à chaque fois.\n\nMots-clés de Gemma : Mail::Send, Validate::isEmail, idn_to_ascii, RFC 2822, Swift_Message, Symfony\\Component\\Mailer, PS_SHOP_EMAIL. Jamais htmlentities, send_email_to, sendMailTest ni EmailConfigurationTester. Le fichier remonte quand même au grep (1 à 10 lignes).\n\nPatchs :\n- A2, R1, R4 : `new Address(self::toPunycode($replyTo), ...)` dans Mail::send, l.532 ;\n- C : toPunycode sur $from, $to et $bcc dans Mail::send ;\n- O, patch final : bloc `if ($from) { $email->from(new Address(self::toPunycode($from), $fromName)); }` inséré deux fois.\n\nRetour O n°1 : 'Expected: 200 Received: 500 ... expect(errors).not.toMatch(/RFC ?2822|does not comply|&ouml;|&uuml;/i)', sans message d'exception PHP. Retour O n°2 : 'Hunk #1 succeeded at 299 (offset 4 lines). Hunk #2 FAILED at 532', ce qui est l'artefact de pollution décrit ci-dessus. result_reeval.json de O : applied true, 500.\n\nMail::sendMailTest (classes/Mail.php l.767-846) fait `->from($from)->to($to)` sans décodage et n'attrape que Mailer ExceptionInterface. RfcComplianceException (exception Mime) remonte donc en 500. git diff 9.1.1..base sur classes/Mail.php est vide : Mail.php est identique entre la release et le commit de base, ce qui confirme que l'échec n°2 vient de la pollution et non d'une divergence de version.",
  "oracle_fair": "oui",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Lecture ciblée : accepter {\"files\": [\"chemin:369-497\"]} ou {\"files\": [\"Classe::methode\"]} et renvoyer exactement cette plage ou ce corps de méthode",
    "why": "Gemma a nommé lui-même la plage voulue (C+pages) et a reçu trois fois la même fenêtre. Mail::sendMailTest n'a jamais été affiché.",
    "generic": true
   },
   {
    "lever": "Pagination des relectures : si un fichier déjà lu est redemandé avec les mêmes mots-clés, renvoyer les fenêtres suivantes du classement (zones non encore vues) et le signaler ('fenêtres déjà montrées : …'), au lieu d'un contenu identique",
    "why": "Environ 9 essais sur 13 gâchent leurs 2 retours arrière sur une relecture strictement identique. Le déroulé déterministe garantit cette boucle.",
    "generic": true
   },
   {
    "lever": "Retour de test enrichi : joindre au verdict le corps de la réponse HTTP, ou la dernière exception PHP du log (classe, message, 3 frames dans src/ ou classes/), en plus de l'assertion Playwright",
    "why": "En O, le seul retour était 'Expected 200 / Received 500'. Le message RfcComplianceException 'info@sj&ouml;b&uuml;ren.se does not comply…' et la frame EmailConfigurationTester auraient montré directement la cause et le fichier.",
    "generic": true
   },
   {
    "lever": "Étape « tracer la donnée » avant ÉDITER : demander en JSON la liste des fonctions traversées par la valeur citée dans le ticket (point d'entrée → échec), avec chaque transformation appliquée, en ne citant que le code affiché",
    "why": "Gemma avait sous les yeux htmlentitiesUTF8 appliqué à l'adresse et l'appel à Mail::sendMailTest. Il a pourtant corrigé Mail::send, qui n'est pas sur ce chemin, parce qu'il partait d'une hypothèse a priori (punycode manquant).",
    "generic": true
   },
   {
    "lever": "Expansion d'appel à 1 saut : pour chaque méthode du projet appelée dans les fenêtres affichées (ex. X::y(...)), ajouter automatiquement sa signature et son corps (limité en lignes)",
    "why": "Le chemin réel (testConfiguration → Mail::sendMailTest) n'était lisible qu'en suivant un appel que l'outil ne sait pas suivre.",
    "generic": true
   },
   {
    "lever": "Garder visibles les fichiers déjà lus lors d'un retour arrière : relire ajoute les nouveaux fichiers au lieu de les remplacer, ou ajoute un rappel compact des fichiers précédents (chemin plus fonctions affichées)",
    "why": "Après relire, EmailConfigurationTester.php disparaissait du message courant, et le modèle se focalisait sur Mail.php seul.",
    "generic": true
   },
   {
    "lever": "Hygiène des éditions en CORRIGER : rejeter avec message les blocs où SEARCH == REPLACE et les insertions déjà présentes, et montrer le diff cumulé courant avant chaque correction",
    "why": "En O, un bloc no-op et une double insertion du même bloc `$email->from(...)` ont abîmé le patch final.",
    "generic": true
   },
   {
    "lever": "Fiabilité du banc : réévaluer les runs antérieurs au commit 578c1e9 (pollution des fichiers hors correctif officiel entre deux retours), recalculer bon_fichier avec files_all_read, et exclure ou marquer la condition B quand il n'y a pas de replay*.spec.js",
    "why": "Le retour O n°2 était un faux 'Hunk FAILED'. bon_fichier=0 pour A alors que le bon fichier avait été lu. B sans test de repro mesure en fait A.",
    "generic": true
   }
  ]
 },
 {
  "pr": "40999",
  "fix_summary": "The official fix adds 5 lines to classes/shop/Shop.php, in ShopCore::copyShopData(), right after the $old_id fallback: if (!isset($tables_import['currency'])) $tables_import['currency'] = 'on'. Without it, a shop created without data import (afterAdd passes importData=[]) only receives category_lang (the `if ($tables_import && !isset(...)) continue` skips every other table), so it has no currency_shop row and its front office returns a 500 (TypeError ComputingPrecision).",
  "agent_behaviour": "Same pattern in 11 of the 12 attempts. Gemma picks keywords that include the generic word \"Shop\" (A1, A2, O, B, C, C+pages, R1, R3, R4), and the grep correctly ranks controllers/admin/AdminShopController.php and classes/shop/Shop.php. But at the time of these runs (flow.py before 1e75370: WINDOW=30, MAX_LINES_PER_FILE=260), windows() marks every line containing \"shop\", merges everything into one span starting at line 1 and cuts it at 260. Both files show up as \"[lignes 1-260]\": the constructor, fields_list and the head of Shop.php. afterAdd (line ~297) and copyShopData (line ~1198 of 1376) are never shown. Gemma then asks for the SAME file again (AdminShopController.php) to see what follows. Each re-read returns exactly the same lines 1-260, and both backtracks are spent this way, so the run ends with \"aucune édition\" (no edit). The one run without the bare \"Shop\" keyword (A3: AdminShopsController, Shop::create, Shop::copyFrom...) gets the window 270-397, containing afterAdd and the call $new_shop->copyShopData(...). Gemma produces a well-formed edit that applies, but its logic is wrong: it rewrites afterAdd to pass PS_SHOP_DEFAULT and [] when useImportData is off. That is functionally identical to before, because copyShopData with [] still copies nothing. Gemma never opened the definition of copyShopData. R2 does the same in afterAdd (calls Category::updateFromShop instead of copyShopData), which is also applied but does not fix the bug. A4 reads Shop.php (loc_hit) but its window is 67-215, re-read twice identically, with no edit. In O, the oracle feedback was never exercised: both backtracks were used up before CORRIGER, so the feedback was only \"aucune édition applicable\" (no applicable edit), and the {\"files\": [...]} requests in CORRIGER were silently ignored because backtracks was already 2. B has no visible replay (STATUS_REPRO=echec), so B is the same as A. C/C+pages are A plus a glossary that points to AdminShopUrl/AdminImport, which does not help.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "boucle_ou_budget_tours: backtracks spent re-reading the identical window (no line range or symbol can be requested); exhausted before CORRIGER in O",
   "logique_fausse: A3/R2 edit afterAdd without reading the copyShopData definition, so the patch is equivalent to the bug",
   "ticket_insuffisant: the symptom ('deprecated method', screenshot only) never names the currency or the error; the root cause can only be deduced by reading copyShopData",
   "outillage: an invalid path (classes/Shop.php in R3) is filtered out silently with no suggestion; the prompt keeps showing '(2 fois au plus)' after the budget is used up",
   "regression_outillage: the current windows() (commit 1e75370) outputs the whole span [lignes 1-919] / [lignes 1-1376], which fit() then truncates blindly by 30% per pass, and the end of Shop.php (copyShopData) is cut first"
  ],
  "evidence": "Keywords: A1/A2 [\"import_data\",\"Shop\",\"AdminShopsController\",\"ShopGroup\",\"createShop\"], O [\"Shop\",\"AdminShopsController\",\"import_data\",\"Shop::create\",\"Shop::setShop\"], A3 (the only one without \"Shop\") [\"AdminShopsController\",\"Shop::create\",\"import_data\",\"Shop::copyFrom\",\"Shop::setShop\"]. Official identifier: copyShopData / $tables_import['currency'], never proposed, never in any window. Windows recorded in the traces: runs/20260925-101441-A, 20260925-114612-A, 20260926-065152-O, 20260928-092011-B, 20260926-103202-C, 20260926-134839-C, 20260925-101441-R, 20260925-143833-R, 20260925-171642-R: AdminShopController.php '[lignes 1-260]' + Shop.php '[lignes 1-260]' at the EDITER step, then 2 RELIRE steps with the same '[lignes 1-260]'. Explicit trace runs/20260925-143833-R/40999/trace.jsonl, EDITER step: \"Wait, I already read it but only up to line 260. I need to see the rest of the file... Since I can't specify lines in the `files` array, I'll just ask for the file again and hope the system provides the rest\", then asks for \"classes/Shop.php\" (nonexistent path, silently dropped). A3 runs/20260925-142912-A: window '[lignes 270-397]' with afterAdd, then patch.diff `$import_data = $useImportData ? Tools::getValue('importData', []) : []; $source_shop_id = ... PS_SHOP_DEFAULT; $new_shop->copyShopData($source_shop_id, $import_data);`, verdict 'Expected: 200 Received: 500'. A4 runs/20260925-165642-A: Shop.php '[lignes 67-215]' x3. O runs/20260926-065152-O: feedbacks = 2 x 'aucune édition applicable'; CORRIGER answers {\"files\": [...]} ignored (backtrack() returns immediately once backtracks>=2). Code: flow.py at 4f649d9, windows() is sequential with truncation at 260 lines. Current simulation (HEAD) with the same keywords: AdminShopController '[lignes 1-919]', Shop.php '[lignes 1-1376]' (whole file, then truncated by fit()).",
  "oracle_fair": "oui",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Keyword-weighted windows based on rarity (IDF within the file / repository): ignore or down-weight a keyword that matches more than ~20% of the file's lines (e.g. the class name), and cap each merged span (e.g. 60 lines around the best-scoring lines) instead of one block starting at line 1 or the whole file",
    "why": "A single generic keyword ('Shop') was enough to show only the header in 9/12 runs; the current version has the opposite failure (whole file, then blind truncation by fit())",
    "generic": true
   },
   {
    "lever": "Prioritize the definitions of functions/methods whose name matches a keyword or appears in the ticket (function NAME line plus its body)",
    "why": "The method at fault is usually a definition; here neither afterAdd nor copyShopData was ever framed",
    "generic": true
   },
   {
    "lever": "Systematic file outline (list of methods with their lines) at the top of each read, plus a targeted read action: {\"read\": [{\"file\": ..., \"symbol\": \"methodName\"}]} or {\"file\": ..., \"lines\": \"300-420\"}",
    "why": "The model explicitly wrote 'I can't specify lines' and asked again for the same file, hoping for the rest",
    "generic": true
   },
   {
    "lever": "Re-reading an already displayed file returns the NEXT unseen windows (pagination), never the same content",
    "why": "Both backtracks were used up getting identical content, a pure waste of the turn budget",
    "generic": true
   },
   {
    "lever": "Automatic one-hop 'go to definition': for methods called in the displayed windows (e.g. $obj->method(...)) that belong to the repository's classes, append their signature and body (or offer them as a menu)",
    "why": "A3/R2 edited the caller without seeing the callee and produced a patch equivalent to the bug",
    "generic": true
   },
   {
    "lever": "Invalid path: suggest the closest existing paths (fuzzy match on the filename) instead of dropping it silently; show the real remaining backtrack count and remove the '(2 fois au plus)' mention once exhausted",
    "why": "R3 lost its last turn on classes/Shop.php; in O the CORRIGER requests were ignored without the model knowing",
    "generic": true
   },
   {
    "lever": "Separate budgets: read backtracks in the EDITER phase vs in the CORRIGER phase (B/O), and force a best-effort edit after N turns without editing so that the test feedback actually runs",
    "why": "In O the oracle never returned anything other than 'aucune édition applicable', so the upper bound measured nothing on this bug",
    "generic": true
   },
   {
    "lever": "Enrich the test feedback with the server-side error (PHP log / stack trace of the 500 response captured during the replay), not just the Playwright assertion",
    "why": "A3's patch would have received 'Expected 200 Received 500'; the TypeError (ComputingPrecision, missing currency) would point to the missing data",
    "generic": true
   },
   {
    "lever": "LOCALISER step: penalize or reject keywords that are too frequent (present in more than N files) and ask for at least one specific method/variable name",
    "why": "'Shop' alone matches hundreds of lines and swamps both the windowing and the ranking",
    "generic": true
   }
  ]
 },
 {
  "pr": "41036",
  "fix_summary": "Le correctif officiel ajoute 3 lignes dans un seul fichier, src/Core/ConstraintValidator/CustomerNameValidator.php, méthode validate() : `if (null === $value || '' === $value) { return; }` avant le `if (!is_string($value)) throw new UnexpectedTypeException(...)`. Cause : le formulaire Symfony (trim) transforme \" \" en null, le validateur CustomerName lève une exception, d'où la 500. Une fois l'exception évitée, la contrainte NotBlank de CustomerType affiche « Ce champ ne peut pas être vide ».",
  "agent_behaviour": "Répartition des 12 essais :\n- **trim() dans Add/EditCustomerHandler (4 essais : A1, B, C, R4).** Le handler s'exécute après la validation du formulaire, l'exception est déjà levée.\n- **Garde vide dans le legacy Validate::isCustomerName (3 essais : R1, R2, R3).** Ce code n'est pas sur le chemin du BO Symfony.\n- **Nouvelle validation dans classes/form/CustomerForm.php (A4).** C'est le formulaire du front-office, mauvaise application.\n- **Bon fichier lu, mauvaise édition (A3).** Il lit CustomerNameValidator.php, mais la fenêtre s'arrête à la ligne 47 sur 69 et masque les corps de isNameValid/isPointSpacedValid. Il réécrit la condition en inlinant ces helpers qu'il n'a pas vus et inverse la logique du point (régression). Le cas null n'est pas traité.\n- **Abandon silencieux en route vers la cible (3 essais : A2, C+pages, O).** Le budget global de 2 retours arrière est consommé (Validate.php, puis CustomerController ou CustomerName.php). La demande suivante, qui visait précisément CustomerNameValidator, est ignorée sans message, d'où « aucune édition ».\n\nMots-clés initiaux, toujours génériques ou inventés : Customer, firstname, lastname, validateFirstname/validateLastname (identifiants inexistants), CustomerForm, CustomerController. Jamais CustomerName, ConstraintValidator, CustomerType, NotBlank ni UnexpectedTypeException. Le grep classe donc en tête classes/Customer.php, classes/form/CustomerForm.php et les CommandHandlers. src/PrestaShopBundle/Form/Admin/Sell/Customer/CustomerType.php, qui porte les contraintes, n'est jamais lu.\n\nModèle causal faux et constant : « l'espace est enregistré, il faut trim() ou valider ». L'agent ne sait jamais qu'une exception est levée, ni laquelle.",
  "primary_failure": "logique_fausse",
  "secondary_failures": [
   "boucle_ou_budget_tours",
   "fenetre_lecture",
   "localisation_mots_cles",
   "ticket_insuffisant"
  ],
  "evidence": "**Essai A3** (runs/20260925-142912-A/41036/trace.jsonl) :\n- Tour 4 : relocalisation sur [\"class CustomerName\",\"CustomerNameValidator\"].\n- Tour 5 : lecture de CustomerNameValidator.php, mais `[lignes 1-47]` seulement alors que le fichier en fait 69 (vérifié au commit b6689411). Les mots-clés ne frappent qu'en tête de fichier ; avec WINDOW=20 la fenêtre s'arrête là.\n- Patch produit : `if (!preg_match(self::PATTERN_NAME, $value) || preg_match(self::PATTERN_DOT_SPACED, $value))`. Or l'original isPointSpacedValid renvoie true s'il n'y a pas de point, puis `(bool)preg_match(DOT_SPACED)` : la sémantique est inversée.\n- Verdict oracle : `Received: 500`. La ligne `if (!is_string($value)) throw new UnexpectedTypeException` était sous ses yeux mais n'a pas été touchée.\n\n**Essai O** (runs/20260926-065152-O) :\n- Tour 3 : demande [\"…/Constraints/CustomerName.php\", \"…/Constraints/CustomerNameValidator.php\"]. Le second chemin n'existe pas ; il est filtré silencieusement par `if flow.show(base, f)` (run.py l.173), sans message « fichier introuvable ».\n- Tour 4 : demande le bon chemin src/Core/ConstraintValidator/CustomerNameValidator.php. Mais `backtracks < 2` (run.py l.167) est déjà atteint : la demande est ignorée, apply_edits ne trouve rien et le retour vaut « aucune édition applicable ».\n- Tours 5-6 : en CORRIGER, il redemande ce fichier puis lance une recherche ; toujours ignoré, car backtrack() sort immédiatement.\n- Bilan : l'oracle n'a jamais tourné sur un patch (feedbacks = 2 × « aucune édition applicable »). La borne haute O ne mesure ici rien d'autre qu'un bug du déroulé.\n\n**Même abandon dans deux autres essais** :\n- A2 (20260925-114612-A), tour 4 : {\"keywords\":[\"CustomerName\",\"CustomerNameValidator\"]} ignoré.\n- C+pages (20260926-134839-C), tour 4 : {\"files\":[\"src/Core/ConstraintValidator/CustomerNameValidator.php\"]} ignoré.\n\n**B et C n'ont reçu aucun retour d'exécution** (feedbacks = []). Aucun replay*.spec.js n'existe : STATUS_REPRO indique « echec … raison technique ». B se réduit donc à A.\n\n**Oracle** : il vérifie seulement status < 500, le retour sur customers/new et le texte « Ce champ ne peut pas être vide ». Même dans les essais où l'oracle a tourné, il ne transmet que « Received: 500 », jamais le message d'exception serveur.",
  "oracle_fair": "oui",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Ne plus ignorer en silence les demandes refusées. Quand un chemin n'existe pas, répondre « X : fichier introuvable » et proposer les chemins proches (même nom de base, via git ls-tree). Quand le budget de retours arrière est épuisé, le dire explicitement (« budget de lecture épuisé, édite maintenant ») au lieu de convertir la demande en « aucune édition applicable ».",
    "why": "3 essais sur 12 (A2, C+pages, O) ont échoué alors que l'agent demandait le bon fichier. En O, l'oracle n'a jamais été exécuté. Le modèle ne savait pas pourquoi sa demande n'était pas servie.",
    "generic": true
   },
   {
    "lever": "Compter le budget en lignes ou en tokens lus plutôt qu'en 2 retours arrière globaux. Autoriser au moins une lecture supplémentaire en phase CORRIGER, la lecture de fichiers étant justement l'action utile après un échec de test.",
    "why": "Le compteur global de 2 est consommé par des lectures exploratoires bon marché (Validate.php, CustomerName.php : 28 lignes). La phase CORRIGER devient alors incapable de lire quoi que ce soit.",
    "generic": true
   },
   {
    "lever": "Montrer le fichier entier quand il fait au plus MAX_LINES_PER_FILE lignes, et ne passer aux fenêtres qu'au-delà. Pour les gros fichiers, toujours inclure les corps des méthodes privées appelées dans la fenêtre retenue.",
    "why": "CustomerNameValidator.php fait 69 lignes et il a été coupé à 47. Le modèle a halluciné le corps des helpers et inversé une condition.",
    "generic": true
   },
   {
    "lever": "Dans le retour de test (B/O, et à terme pour tout rejeu), joindre l'exception côté serveur : classe, message et 3-5 premières frames (var/logs/*.log ou titre de la page d'erreur Symfony en mode dev), en plus du code HTTP.",
    "why": "« Received: 500 » ne dit rien. « UnexpectedTypeException: Expected argument of type string, null given » avec CustomerNameValidator.php:32 suffit à localiser et à comprendre le bug. Ce levier vaut pour tous les tickets de type « erreur 500 ».",
    "generic": true
   },
   {
    "lever": "Ajouter avant LOCALISER une étape « reproduction » optionnelle : rejouer automatiquement les étapes du ticket sur le commit de base et fournir l'erreur serveur observée. C'est l'équivalent d'un développeur qui reproduit le bug avant de chercher.",
    "why": "Le déroulé A ne donne aucun signal d'exécution. Pour les tickets « 500 / page blanche », l'erreur réelle est l'information la plus discriminante, et ce n'est pas une fuite du correctif.",
    "generic": true
   },
   {
    "lever": "Après le grep, ajouter une étape « chemin de la requête » : à partir de l'URL ou du contrôleur BO déduit des étapes du ticket, lister contrôleur → FormType → contraintes → handler, et l'insérer dans les résultats. On peut aussi forcer dans LOCALISER une hypothèse explicite « où l'exécution casse » avant les mots-clés.",
    "why": "Dans 9 essais sur 12, l'agent a corrigé en aval de l'exception (handlers, Validate legacy, formulaire front). Il n'a jamais lu le FormType qui porte les contraintes, faute d'un modèle du flux Symfony.",
    "generic": true
   },
   {
    "lever": "Après une édition, vérifier si elle est un refactor sans effet ou une inversion : diff restreint au chemin lié au symptôme, ou PHP lint suivi d'un test unitaire minimal. Signaler à l'agent « ton édition ne touche pas le chemin d'exécution du symptôme ».",
    "why": "En A3, la seule édition sur le bon fichier inline des helpers sans traiter la cause, avec une régression.",
    "generic": true
   },
   {
    "lever": "Réparer la génération du test de reproduction (condition B) quand elle échoue pour raison technique : nouvelle tentative, ou repli sur un test minimal « statut < 500 » dérivé des étapes du ticket.",
    "why": "B s'est réduit à A faute de replay*.spec.js valide (STATUS_REPRO = echec technique).",
    "generic": true
   }
  ]
 },
 {
  "pr": "41457",
  "fix_summary": "Le correctif officiel ne touche qu'une méthode, HTMLTemplateInvoiceCore::getFilename() (classes/pdf/HTMLTemplateInvoice.php, lignes 472-482 sur 482, tout en fin de fichier). Le numéro formaté renvoyé par OrderInvoice::getInvoiceNumberFormatted contient un « / » quand PS_INVOICE_USE_YEAR=1 (format '%1$s%2$06d/%3$s', OrderInvoice.php:848). Le correctif remplace '/' et '\\' par '-' avant le sprintf('%s.pdf'). Le libellé affiché dans le PDF ne change pas.",
  "agent_behaviour": "Aucun des 14 essais (A×4, R×4, C, C+pages, B, O, A-4B, E) n'a produit d'édition : patch.diff fait 0 octet partout et result.json indique « aucune édition ». La localisation est bonne : mots-clés OrderInvoice / HTMLTemplateInvoice / PDF / filename / invoice_number, et HTMLTemplateInvoice.php sort en tête du grep. Le déroulé est presque toujours le même : 1) l'agent lit OrderInvoicePdfGenerator, AdminPdfController ou PdfInvoiceController (le circuit de génération) ; 2) il demande PDF.php et y voit bien `$template->getFilename()` dans setFilename() ; 3) il demande HTMLTemplateInvoice.php, mais la fenêtre s'arrête à la ligne 455 ou 461 (ou 268) et ne montre jamais getFilename() ; 4) il redemande le même fichier ou HTMLTemplate.php et reçoit exactement la même fenêtre ; 5) les 2 retours arrière sont épuisés et l'essai finit sans édition. L'agent ne tente jamais d'édition « à l'aveugle » : il cherche à lire la méthode avant de toucher au code, ce qui est un comportement correct. Deux essais (A 20260925-165642-A et R 20260925-101441-R) ont relancé la recherche avec les mots-clés exacts [\"HTMLTemplateInvoice\",\"getFilename\"]. La fenêtre 442-482 contenait alors getFilename(). L'agent a demandé ensuite OrderInvoice.php, logiquement, pour voir ce que renvoie getInvoiceNumberFormatted et y trouver le « / ». Mais le budget de 2 retours arrière était épuisé et le run s'est arrêté sans édition. En O et en B, les demandes {\"files\": [...]} faites à l'étape CORRIGER sont ignorées sans avertissement (compteur de retours arrière commun à tout le run). Le retour reçu est la chaîne fixe « aucune édition applicable » : l'oracle n'a jamais été exécuté et O s'est réduit à A.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "boucle_ou_budget_tours",
   "multi_fichiers",
   "autre: retour O/B vide (aucune exécution d'oracle sans patch)"
  ],
  "evidence": "1) Fenêtres vues de HTMLTemplateInvoice.php : [1-98][155-227][285-345][428-455] (A 20260925-101441-A ; R -143833-R et -171642-R ; C 20260926-103202-C ; B 20260928-092011-B), [434-461] (R -114712-R, C+pages), [1-98][107-268] ou [109-270] (A -114612-A, -142912-A, O 20260926-065152-O, A-4B). Le fichier compte 482 lignes et getFilename() occupe les lignes 472-482 : aucune de ces fenêtres ne le montre.\n2) Cause : le windows() en service le 25-28/09 (version du commit a945df8) parcourt les spans dans l'ordre (WINDOW=30, MAX_LINES_PER_FILE=260). Le dernier span fusionné, 428-482, est coupé par `b = min(b, a + MAX_LINES_PER_FILE - total)` à 455. Comme c'est le dernier span, la marque « [… tronqué …] » n'est jamais ajoutée : la troncature est silencieuse. Aucune trace ne contient « tronqué » (vérifié sur 20260925-165642-A).\n3) La relecture d'un même fichier recalcule windows() avec les mêmes kws (run.py:177) et rend une fenêtre identique. Exemples : C+pages renvoie 2 fois [434-461] ; O renvoie [1-98][107-268] 2 fois, puis 2 demandes en CORRIGER ignorées.\n4) Les seuls passages où getFilename() a été vu : relocaliser [\"HTMLTemplateInvoice\",\"getFilename\"] → [1-39][442-482]. L'agent répond alors {\"files\": [\"classes/order/OrderInvoice.php\"]}, mais backtracks vaut 2 et c'est la fin du run.\n5) Le « / » est à OrderInvoice.php:848, qu'aucun essai n'a vu (fenêtres d'OrderInvoice : [1-39][83-234][541-609] ou [55-234][288-328]).\n6) Le windows() actuel (commit 1e75370, MAX=120, WINDOW=20), simulé sur le fichier à fc55c50 : avec les kws de A1 ou de B, il rend [1-88] (en-tête de classe, à cause de la densité OrderInvoice/HTMLTemplateInvoice), sans getFilename. Avec les kws de A2, il rend un seul span [117-482] de 366 lignes : la clause `or not selected` laisse passer un span fusionné géant, au-delà du budget. Les deux versions échouent, chacune à sa façon.\n7) results.csv : bon_fichier=1 et patch_applique=0 sur tous les A/R/O/C. La métrique « bon fichier » cache le fait que la fonction fautive n'a jamais été visible.",
  "oracle_fair": "oui",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "Plan du fichier toujours affiché : nombre total de lignes et liste des signatures `function X` avec leurs numéros de ligne, en tête de chaque fichier fenêtré, plus une marque explicite « [lignes a-b omises] » entre les spans et en fin de fichier.",
    "why": "Ici, la troncature à la ligne 455 était invisible : l'agent ne pouvait pas savoir que getFilename() existait en ligne 472, alors qu'il l'avait repéré comme appel dans PDF.php.",
    "generic": true
   },
   {
    "lever": "Outil de lecture ciblée : {\"read\": {\"file\": f, \"symbol\": \"nomMethode\"}} ou {\"lines\": [a, b]} ; un fichier relu doit renvoyer la suite (pagination) ou la méthode demandée, jamais la même fenêtre.",
    "why": "Dans 8 essais sur 14, l'agent a redemandé le même fichier et reçu un contenu identique : des tours entiers perdus.",
    "generic": true
   },
   {
    "lever": "Corriger windows() : borner la longueur de chaque span (découper les spans fusionnés au lieu d'accepter un premier span géant), classer selon score/longueur plutôt que la somme, donner un bonus aux lignes de déclaration de méthode qui contiennent un mot-clé (`function getFilename` contient « filename ») et une pénalité aux docblocks et en-têtes de classe.",
    "why": "La version actuelle renvoie soit l'en-tête de classe (1-88), soit un span de 366 lignes qui dépasse le budget de 120.",
    "generic": true
   },
   {
    "lever": "Expansion des appelés (« aller à la définition ») : quand une fenêtre lue appelle `->methode(` ou `Classe::methode(` définie dans un autre fichier du dépôt, ajouter automatiquement le corps de cette méthode (git grep \"function methode\"), dans un budget limité.",
    "why": "Le diagnostic demande 2 fichiers : getFilename() appelle getInvoiceNumberFormatted(), qui produit le « / ». L'agent a demandé ce second fichier mais n'avait plus de tour.",
    "generic": true
   },
   {
    "lever": "Budgets séparés et explicites : un budget de lecture (par ex. 4 lectures) distinct des essais de correction, le reste du budget annoncé dans le message, et une édition imposée au dernier tour de lecture (« dernier tour : produis un bloc SEARCH/REPLACE »). Ne jamais ignorer en silence un {\"files\"} à l'étape CORRIGER : soit le servir, soit répondre « budget de lecture épuisé ».",
    "why": "Le compteur commun `backtracks < 2` a coupé les 2 essais qui avaient trouvé la bonne fonction et neutralisé toute l'étape CORRIGER de O et B.",
    "generic": true
   },
   {
    "lever": "En B/O, si le patch est vide, exécuter quand même le test sur le code non modifié et renvoyer son message d'échec (valeur observée vs attendue, par ex. suggestedFilename = 2026.pdf).",
    "why": "Le retour « aucune édition applicable » ne porte aucune information. Le message réel de l'oracle (« 2026.pdf » attendu /FA007706.2026.pdf/) aurait orienté l'agent vers un « / » dans le nom.",
    "generic": true
   },
   {
    "lever": "Recalculer les fenêtres avec l'union cumulée des mots-clés (initiaux, relocalisés et identifiants cités par l'agent dans ses réponses, par ex. `getFilename` vu dans PDF.php).",
    "why": "Après la lecture de PDF.php, l'agent savait que tout passe par `$template->getFilename()`, mais la relecture d'HTMLTemplateInvoice gardait les kws d'origine.",
    "generic": true
   },
   {
    "lever": "Ajouter au journal une métrique « fonction officielle visible dans le contexte » (loc_hit au niveau symbole), à côté de bon_fichier.",
    "why": "bon_fichier=1 sur 12 essais masquait une défaillance qui relève à 100 % de l'outillage, non du modèle.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41225",
  "fix_summary": "Le correctif officiel remplace ou complète les ORDER BY par `ag.position, a.position` dans 5 méthodes de classes/Product.php (getAttributesResume via GROUP_CONCAT, getAttributeCombinations, getAttributeCombinationsById, getAttributesParams, getAttributesInformationsByProduct, ces deux dernières avec un LEFT JOIN attribute_group ajouté) et dans 2 requêtes de classes/Pack.php (getItems, getItemTable). L'oracle (bench/replay/41225/oracle.spec.js + setup.sql) place le groupe Couleur avant Taille, puis vérifie l'ancre du lien produit en page d'accueil `#/8-couleur-blanc/1-taille-s`. Cette ancre est produite UNIQUEMENT par Product::getAttributesParams, donc par le seul hunk aux lignes 7210-7225.",
  "agent_behaviour": "Les 12 essais suivent le même déroulé. LOCALISER : les mots-clés sont les 4 noms de méthodes cités dans le ticket, sans aucune variation (seul E ajoute ps_featuredproducts, position et les noms de tables). LIRE : uniquement classes/Product.php. Les fenêtres sont identiques dans tous les essais, sauf E : [1775-1835], [2433-2493], [2500-2611], [7201-7226]. ÉDITER : les 3 premières requêtes visibles (getAttributesResume, getAttributeCombinations, getAttributeCombinationsById) passent de `ORDER BY pa.id_product_attribute` à `ORDER BY a.position`. Le tri par position de GROUPE (ag.position) n'est jamais ajouté dans A, R ni C. getAttributesParams n'est jamais touchée, getAttributesInformationsByProduct non plus (elle est pourtant nommée dans le ticket). Pack.php n'est jamais trouvé. Aucun retour arrière ({\"keywords\"} ou {\"files\"}) n'est utilisé, même en O après 2 échecs identiques. En O, le retour de l'oracle pousse l'agent à ajouter ag.position, mais toujours dans les mêmes requêtes. En B, le test de reproduction écrit par Gemma est cassé (localisateur introuvable), ce qui donne un retour sans valeur. L'agent tourne alors sur GROUP BY/ORDER BY de getAttributeCombinations.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "oracle_ou_env_douteux",
   "ticket_insuffisant",
   "format_edition",
   "logique_fausse",
   "localisation_mots_cles"
  ],
  "evidence": "1) TRONCATURE SILENCIEUSE : tous les essais ont tourné avec l'ancien windows() (commit 4f649d9 : WINDOW=30, MAX_LINES_PER_FILE=260, coupe séquentielle). Dans Product.php au commit de base, les occurrences tombent aux lignes 1805, 2463, 2530, 2581 et 7231 (`public static function getAttributesInformationsByProduct`). Les spans donnent 61+61+112 = 234 lignes, puis le span [7201-7261] est coupé à 7201-7226 (260-234 = 26 lignes). La signature de getAttributesInformationsByProduct (ligne 7231), méthode nommée dans le ticket, se trouve donc 5 lignes après la coupure. Aucun marqueur « [… tronqué …] » n'apparaît, car le marqueur n'est ajouté qu'à l'itération suivante. Le fragment 7201-7226 contient le CORPS de getAttributesParams (la requête SANS ORDER BY, celle que teste l'oracle), mais sans son en-tête (ligne 7190) : l'agent voit une requête anonyme et ne la relie pas au ticket (« or have no ORDER BY at all »). Vérification dans les traces : 'getAttributesParams' in user = False dans tous les essais, 'function getAttributesInformationsByProduct' = False.\n2) LE windows() ACTUEL EST PIRE (recalculé hors ligne, sans modèle, avec les mêmes 4 mots-clés) : il ne renvoie que [1785-1825] et [2561-2601], soit 82 lignes. La sélection gloutonne garde les 2 spans les mieux notés (4 = mot entier + sous-chaîne `getattributecombinations` comptée deux fois), puis ignore TOUS les spans de 41 lignes, car 82+41 > 120. getAttributesResume, getAttributeCombinations et getAttributesInformationsByProduct disparaissent.\n3) Mots-clés contre correctif : le ticket nomme 4 méthodes. Le correctif en touche 7, dont getAttributesParams (seule observable par l'oracle) et Pack::getItems/getItemTable, qu'aucun mot-clé du ticket ne fait ressortir au grep.\n4) Qualité des éditions : A1/A2/A3/R2/C+pages remplacent `ORDER BY pa.id_product_attribute` par `ORDER BY a.position` dans des requêtes qui ont `GROUP BY pa.id_product_attribute, ag.id_attribute_group`. Ces éditions perdent l'ordre des déclinaisons, et A1 sort en régression à la première évaluation. Le correctif officiel, lui, GARDE pa.id_product_attribute en tête puis ajoute `ag.position, a.position`. A2/A3 changent l'ORDER BY externe de getAttributesResume au lieu de l'ORDER BY interne du GROUP_CONCAT (c'est celui-là qui compte). B écrit `ORDER BY agl.id_attribute_group, a.position` au lieu de ag.position.\n5) O (20260926-065152-O) : au 1er tour ÉDITER, 5 blocs sont produits, mais seul le premier porte `FILE:`. La regex BLOCK de flow.parse_edits jette les 4 autres SANS le signaler. Au tour CORRIGER 1, les blocs 2 à 5 cherchent du texte qui n'a jamais été appliqué (FIELD(...), `a.position, stock.location`), d'où l'erreur `edit_errors: bloc SEARCH introuvable`. Ces erreurs ne sont PAS renvoyées au modèle : msg_test n'affiche que replay_error, et cet essai précède la v2 « état actuel ». Le retour reste identique (`Received: \"/1-taille-s/8-couleur-blanc\"`) et l'agent ne relance aucune recherche (« anchor », « getAttributesParams »). patch.diff final = un seul hunk sur getAttributesResume, avec ORDER BY MIN(ag.position), MIN(a.position).\n6) B (20260928-092011-B) : le test de reproduction échoue sur `expect(product).toBeVisible()` (élément introuvable) avant ET après les éditions. STATUS_REPRO = « passe avec correctif officiel : False ». Le retour ne reflète donc pas le bug. Ce même test invalide est injecté comme « TEST DE REJEU (doit passer après correction) » dans le message ticket de C+pages.\n7) E : la localisation part sur AttributeDataProvider.php et GridPositionUpdater.php (bon_fichier = 0).",
  "oracle_fair": "douteux",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Fenêtres de lecture au niveau de la FONCTION (découpage par accolades/tokenizer PHP) : pour chaque occurrence d'un mot-clé, montrer la méthode englobante en entier, signature comprise. Ne jamais couper au milieu d'un span sans marqueur explicite « [tronqué : N lignes, méthodes X, Y non montrées] ».",
    "why": "Ici la méthode nommée dans le ticket a été coupée 5 lignes avant sa signature, et la méthode testée par l'oracle est apparue sans nom, sans que l'agent soit prévenu.",
    "generic": true
   },
   {
    "lever": "Corriger la sélection gloutonne du windows() actuel : continuer à remplir le budget avec des spans plus courts ou tronqués au lieu de les ignorer, et assurer au moins 1 span par mot-clé distinct (couverture avant densité). Ne pas compter deux fois une sous-chaîne déjà comptée comme mot entier.",
    "why": "Avec 4 mots-clés du ticket, le code actuel ne montre que 2 des 5 occurrences (82 lignes sur les 120 du budget).",
    "generic": true
   },
   {
    "lever": "Joindre à chaque fichier lu un SOMMAIRE (liste des méthodes avec leurs numéros de ligne, en marquant celles qui contiennent un mot-clé) et permettre {\"read\": \"Fichier::methode\"}.",
    "why": "L'agent peut repérer les méthodes voisines (getAttributesParams, getAttributesGroups qui « marche ») et les demander à moindre coût.",
    "generic": true
   },
   {
    "lever": "Signaler à l'agent les blocs SEARCH/REPLACE non reconnus (sans en-tête FILE:) et les erreurs `bloc SEARCH introuvable` dans le message suivant. Option : hériter du dernier FILE: pour les blocs qui n'en ont pas.",
    "why": "En O, 4 éditions sur 5 ont été jetées en silence. Les corrections suivantes visaient du texte inexistant, sans aucun retour.",
    "generic": true
   },
   {
    "lever": "Après un retour de test inchangé (même erreur deux fois), imposer une étape RELOCALISER : demander des mots-clés tirés du message d'échec (valeur reçue/attendue, sélecteur, URL), ou lancer un grep automatique sur ces chaînes.",
    "why": "L'agent n'utilise jamais le retour arrière. Le signal de l'oracle (une ancre d'URL) devait mener vers une autre fonction que celles déjà éditées.",
    "generic": true
   },
   {
    "lever": "Quand le ticket dit qu'un écran se comporte CORRECTEMENT, chercher et montrer l'implémentation de référence (ici la fiche produit) comme modèle à reproduire. Étape « trouver l'analogue qui marche ».",
    "why": "Le bon motif (`ORDER BY ag.position, a.position` de getAttributesGroups) se trouvait dans le dépôt. L'agent a inventé `ORDER BY a.position` sans tri par groupe et a cassé l'ordre des déclinaisons.",
    "generic": true
   },
   {
    "lever": "Étendre le grep aux motifs de code trouvés dans le fichier fautif (ex. la même clause répétée) pour faire apparaître toutes les occurrences sœurs, dans le fichier et ailleurs, après la première édition.",
    "why": "Les correctifs « partout » (ici 7 requêtes, 2 fichiers) demandent de retrouver toutes les copies d'un même motif, pas seulement celles que le ticket nomme.",
    "generic": true
   },
   {
    "lever": "Valider le test de reproduction généré (condition B / C+pages) contre l'état pre ET post avant de le donner comme retour. S'il est invalide, l'écarter ou le marquer comme non fiable.",
    "why": "Le test B échoue sur un localisateur introuvable, quel que soit le patch. Il a fourni un retour trompeur et a été injecté comme « doit passer » dans C+pages.",
    "generic": true
   },
   {
    "lever": "Auditer les oracles dont l'observable passe par une fonction non citée dans le ticket : ajouter un 2e oracle sur le symptôme décrit (ordre des attributs DANS un groupe via getAttributeCombinations/getAttributesResume) et ne compter « résolu » que sur ce qui est décrit.",
    "why": "Ici l'oracle ne teste que l'ordre des GROUPES via getAttributesParams. Un correctif parfait des 4 méthodes nommées échouerait quand même, ce qui fausse la mesure.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41611",
  "fix_summary": "Le correctif officiel ajoute une seule ligne dans classes/CartRule.php, méthode CartRuleCore::getAssociatedRestrictions, branche `!Validate::isLoadedObject($this) || ..._restriction == 0` (ligne 1937 du commit de base). Cette ligne concatène `AND tl.name LIKE \"%'.pSQL($search_cart_rule_name).'%\"` à la requête SQL quand $type == 'cart_rule', que $i18n est vrai et qu'un terme de recherche est fourni. Ces lignes de la requête sont indentées par des tabulations, à l'intérieur d'une chaîne PHP.",
  "agent_behaviour": "La localisation est parfaite dans les 12 essais. Le ticket donne lui-même la cause : « Root cause is in CartRule::getAssociatedRestrictions() (classes/CartRule.php) ». Les mots-clés choisis sont toujours getAssociatedRestrictions, search_cart_rule_name et cart_rule_restriction (plus loadCartRules ou AdminCartRules), et le grep met classes/CartRule.php en tête. L'agent lit le bon fichier (bon_fichier=1 sauf R1). L'échec vient de l'outil de lecture. L'ancien windows(), utilisé jusqu'au commit 1e75370 du 29/09, découpe les spans dans l'ordre du fichier et coupe le dernier pour tenir le budget MAX_LINES_PER_FILE. Le budget part dans des passages sans intérêt : la déclaration des propriétés (lignes 41-158), un passage aux lignes 959-1019, et en R les lignes 1-260 ou 1-47/157-369 à cause du mot-clé « CartRule », présent presque partout. La fenêtre utile s'arrête à « [lignes 1824-1904] », pile sur la signature `public function getAssociatedRestrictions( $type, $active_only, $i18n,`. Le corps de la méthode (lignes 1909-1945, dont la ligne fautive 1937) n'est jamais montré. Gemma voit qu'il manque la suite et redemande `{\"files\": [\"classes/CartRule.php\"]}`. L'outil renvoie exactement la même fenêtre, sans pagination et sans moyen de demander une plage de lignes. Ça se répète jusqu'à l'épuisement des tours : 5 tours, « aucune édition », patch.diff vide dans A×4, R×4, B, C et C+pages. En O, l'oracle n'est jamais exécuté puisqu'il n'y a aucune édition. Le retour se réduit à « aucune édition applicable » et Gemma redemande encore deux fois le même fichier. En E (modèle gemma-4-ft, pas le 31B), la fenêtre 1-37/167-249 ne montre pas la méthode non plus. Le modèle invente alors un corps complet de getAssociatedRestrictions (signature typée, buildRestrictionQuery), ce qui donne « bloc SEARCH introuvable ». La logique de correction n'a donc jamais été mise à l'épreuve.",
  "primary_failure": "fenetre_lecture",
  "secondary_failures": [
   "boucle_ou_budget_tours",
   "format_edition",
   "logique_fausse"
  ],
  "evidence": "- eval/results.csv : patch_applique=0 sur les 14 lignes de #41611 et bon_fichier=1 sur 13. Dans tous les result.json, replay_error vaut « aucune édition », sauf pour E (« classes/CartRule.php : bloc SEARCH introuvable »).\n- /home/elrems/kaggle/runs/20260925-101441-A/41611/trace.jsonl, étape editer : fenêtres CartRule.php `41-158, 959-1019, 1824-1904`. Le message se termine sur `public function getAssociatedRestrictions( $type, $active_only, $i18n,`. Aux étapes relire, la même fenêtre revient deux fois à l'identique (12521 caractères) et la réponse reste `{\"files\": [\"classes/CartRule.php\"]}`.\n- Même schéma dans 20260925-114612-A et 20260925-165642-A. Dans 20260925-142912-A et 20260925-114712-R, la fenêtre est `1-260` ; dans 20260925-143833-R et 171642-R, elle est `1-47, 157-369`.\n- B (/home/elrems/kaggle/runs/20260928-092011-B/41611/trace.jsonl) : Gemma écrit explicitement « I need to read the body of `getAssociatedRestrictions` which starts at line 1904. I will request the lines from 1904 to 2000 », mais le format {\"files\"} ne permet pas de demander une plage. C (20260926-103202-C) : « The previous outputs were truncated ». R (20260925-101441-R) : « Self-correction: I already requested this file, but the output was truncated ».\n- O (/home/elrems/kaggle/runs/20260926-065152-O/41611/) : deux étapes « corriger » avec pour seul retour « RÉSULTAT DU TEST : ÉCHEC / aucune édition applicable ». L'agent redemande deux fois `{\"files\": [\"classes/CartRule.php\"]}`, sans aucune information nouvelle.\n- E (20260928-175551-E) : le bloc SEARCH invente `public function getAssociatedRestrictions(string $type, bool $isPrimary, ...)` et `buildRestrictionQuery`, qui n'existent pas.\n- Vérification hors modèle (lecture seule), avec le windows() actuel (commit 1e75370, classement par densité) sur le commit d9e6cac et les mêmes mots-clés : sortie `[lignes 1834-1964]`, la ligne 1937 est bien montrée. Tous les essais 31B datent des 25-28/09, donc d'avant ce changement. Dans les versions 4f649d9 et 36a9f7c, l'ancien windows() fait `b = min(b, a + MAX_LINES_PER_FILE - total)` : il tronque le dernier span sans aucun marqueur de coupure.\n- Risque restant même avec la bonne fenêtre : la ligne cible 1937 et ses voisines commencent par `\\t\\t\\t` alors que le reste de la méthode est en espaces. apply_edits() exige `s in src` à l'octet près, donc un SEARCH où les tabulations sont rendues en espaces échouerait.",
  "oracle_fair": "oui",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "Ajouter une lecture par symbole ou par plage : {\"files\": [...], \"symbol\": \"methode\"} ou \"chemin:début-fin\". Une méthode dont le nom correspond à un mot-clé est montrée en entier, de la signature à l'accolade fermante, et passe avant les déclarations de propriétés.",
    "why": "Gemma savait exactement ce qui lui manquait (« lines from 1904 to 2000 ») mais le protocole ne lui permettait pas de le demander. La bonne localisation n'a servi à rien.",
    "generic": true
   },
   {
    "lever": "Paginer la relecture : quand l'agent redemande un fichier déjà lu, renvoyer les fenêtres suivantes encore jamais montrées (ou élargir WINDOW et le budget) au lieu du même contenu.",
    "why": "Dans 11 essais sur 12, l'agent a redemandé le même fichier 2 à 4 fois et a reçu 12521 caractères identiques à chaque fois. Ces tours ont été perdus.",
    "generic": true
   },
   {
    "lever": "Signaler explicitement la troncature : « [... coupé, la fonction X continue lignes 1905-1945 : demande-la] » à la fin d'un span coupé par le budget.",
    "why": "L'ancien windows() tronquait sans le dire. Un marqueur donne au modèle de quoi formuler une demande précise.",
    "generic": true
   },
   {
    "lever": "Relancer les essais A/R/O pour tous les bugs dont l'échec est « aucune édition » avec le windows() par densité (commit 1e75370). Garder la version de l'outil de lecture dans result.json pour pouvoir attribuer les écarts.",
    "why": "Rejoué sans modèle sur le commit de base, l'outil actuel montre la ligne 1937 (fenêtre 1834-1964). Les 12 échecs mesurent donc l'ancien outil, pas Gemma.",
    "generic": true
   },
   {
    "lever": "Rendre le matching SEARCH tolérant aux espaces : si la correspondance exacte échoue, comparer ligne à ligne en normalisant tabulations et espaces de fin et de début. N'appliquer que si la correspondance est unique, en conservant l'indentation d'origine du fichier.",
    "why": "Les lignes à modifier mélangent tabulations et espaces dans une chaîne SQL. Le moindre écart d'indentation donne « bloc SEARCH introuvable ».",
    "generic": true
   },
   {
    "lever": "Rendre le retour d'échec diagnostique : « ta réponse ne contenait aucun bloc SEARCH/REPLACE, tu as redemandé un fichier déjà fourni ». En O ou B, ne pas compter comme essai de test un tour sans édition et relancer la lecture élargie.",
    "why": "En O, le retour de l'oracle (borne haute) s'est réduit à « aucune édition applicable ». La condition n'a apporté aucune information, et O ne peut servir de borne que si une édition atteint le test.",
    "generic": true
   },
   {
    "lever": "Détecter les boucles : deux réponses assistant identiques de suite déclenchent un changement d'outil (lecture élargie ou forcée sur la méthode citée dans le ticket) au lieu de rejouer le même message.",
    "why": "Le budget de 5 tours est parti en répétitions strictement identiques.",
    "generic": true
   },
   {
    "lever": "Exclure de la notation des fenêtres les mots-clés trop fréquents dans le fichier lu, comme le nom de la classe ou du fichier (ex. « CartRule » dans CartRule.php, « classes/CartRule.php »), ou les pondérer par un équivalent IDF.",
    "why": "En R, le mot-clé « CartRule » a rempli le budget avec les lignes 1-260 de l'en-tête du fichier.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41573",
  "fix_summary": "Le correctif officiel ajoute du câblage, il ne corrige pas de code existant. Les couches Domaine et Adapter gèrent déjà le champ (AddDiscountCommand/UpdateDiscountCommand::setHighlightInCart, DiscountForEditing::isHighlightInCart, DiscountBuilder/DiscountFiller), mais la couche formulaire Symfony l'ignore. Le correctif touche 3 fichiers en ajoutant des lignes : DiscountInformationType::buildForm reçoit ->add('highlight_in_cart', SwitchType…), DiscountFormDataProvider::getDefaultData/getData exposent information.highlight_in_cart, et DiscountFormDataHandler::fillCommandFromData appelle $command->setHighlightInCart($data['information']['highlight_in_cart']).",
  "agent_behaviour": "Les 12 essais suivent le même schéma.\n(1) LOCALISER : les mots-clés sont toujours [\"highlight\",\"CartRule\",\"DiscountV2\",…]. « CartRule » est en CamelCase, donc compté comme « spécifique » ; le grep classe d'abord les fichiers dont le nom contient un mot-clé. Les 25 résultats sont alors tous des CartRule*.php (V1/legacy) et aucun fichier Discount* V2 n'y figure.\n(2) LIRE : 12/12 premières lectures = classes/CartRule.php + CartRuleController.php, hors sujet.\n(3) Un retour arrière avec CartRuleType/DiscountType fait apparaître les fichiers Discount V2. L'agent lit alors DiscountUsabilityType, AddDiscountCommand et DiscountBuilder (couches Domaine/Adapter, où le setter existe déjà). Il voit le setter mais ne déduit pas qu'il faut le câbler dans le formulaire, le provider et le handler.\n(4) Éditions : le champ est presque toujours ajouté dans le mauvais sous-formulaire (DiscountUsabilityType), sous un nom non conventionnel (highlightInCart ou highlight) et en CheckboxType. Seul A4 câble aussi le DataHandler (sur $data['usability']['highlight']). DiscountFormDataProvider n'est lu dans aucun des 12 essais, DiscountInformationType seulement dans R4 et O.\n(5) Le budget de 2 retours arrière est épuisé avant toute édition dans A1, A3 et R4 (dernière réponse = {\"files\":[…]}, donc « aucune édition »). R1 renvoie « aucune édition » dès son premier tour d'édition (il demandait un CartRuleType.php du namespace Catalog).\n(6) O : l'agent réagit bien au retour de l'oracle. Il relance la recherche sur DiscountInformationType, le lit, retire son ajout fautif et choisit enfin le bon nom et le bon type (highlight_in_cart, SwitchType, sous information). Mais la fenêtre de lecture coupe le fichier (119 lignes) au milieu de la contrainte Length du champ names, et la fin du buildForm (le « ; ») n'est jamais montrée. Il ancre donc son SEARCH en pleine expression : erreur de syntaxe PHP, BO hors service. Le retour suivant est opaque (« RÉGRESSION : connexion BO timeout » au lieu d'une erreur de syntaxe), et le budget de retours arrière est épuisé.",
  "primary_failure": "localisation_mots_cles",
  "secondary_failures": [
   "multi_fichiers",
   "boucle_ou_budget_tours",
   "fenetre_lecture",
   "format_edition",
   "logique_fausse",
   "oracle_ou_env_douteux"
  ],
  "evidence": "- Bug de type « code absent » : au commit de base a7c3d65, `git grep -i highlight` ne trouve rien dans les 3 fichiers officiels. Le mot du symptôme n'existe que dans Domaine/Adapter (AddDiscountCommand.php:173 setHighlightInCart, UpdateDiscountCommand.php:192, DiscountForEditing.php:112, DiscountBuilder.php:33, DiscountFiller.php:44). Un grep sur le symptôme ne peut donc pas trouver l'endroit à éditer.\n- Classement du grep (agent/flow.py grep, l.69) : tri par (not name_hit, …). « CartRule » compte comme spécifique, donc tous les CartRule*.php passent en tête (CartRule.php 134, AddCartRuleToOrderHandler 72…).\n- Premier tour de lecture identique dans A1-A4, R1-R4, O, B, C et C+pages : classes/CartRule.php + CartRuleController.php.\n- A2 patch : DiscountUsabilityType ->add('highlightInCart', CheckboxType…). Oracle : « input[name=\"discount[information][highlight_in_cart]\"] element(s) not found ».\n- A4 patch : Usability ->add('highlight', CheckboxType) + DataHandler `if (array_key_exists('highlight', $data['usability'])) $command->setHighlightInCart(...)`. Architecture à 2/3 juste, mais pas de DataProvider (l'édition ne refléterait pas la valeur et remettrait highlight à 0).\n- O tour 7 : lecture de DiscountInformationType limitée à « [lignes 1-60] » sur 119. Le patch final insère `],\\n])\\n->add('highlight_in_cart', SwitchType::class, [...])` juste après `'maxMessage' => $this->trans(` (ligne 60), d'où une erreur de syntaxe PHP et le message « auth.setup.js connexion BO timeout ». Tour 8 : l'agent redemande {\"files\":[DiscountInformationType]}, mais le budget est épuisé. Avec le code actuel, windows() ne montre plus que les lignes 3-50 de ce fichier : la fin de buildForm n'apparaît jamais, faute de mot-clé.\n- C (103202) : ajoute un second `public function setHighlightInCart(): self` dans AddDiscountCommand alors que le setter existe déjà (redéclaration, fatal, BO hors service).\n- C+pages : le second bloc SEARCH n'a pas d'en-tête « FILE: » et la regex BLOCK l'ignore silencieusement ; seul le `use CheckboxType` est appliqué.\n- B : le test de repro écrit par Gemma est cassé (`a:has-text(/Ajouter une nouvelle|Add new/i)` = sélecteur CSS invalide) et n'active pas le feature flag discount. Le retour échoue quel que soit le patch, c'est du bruit.\n- R4 lit DiscountInformationType au 2e retour arrière puis demande AddDiscountCommand : aucune édition.",
  "oracle_fair": "douteux",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Recherche de références/appelants (« usages <Symbole> ») renvoyant fichier:ligne pour un setter/getter ou une méthode, y compris « 0 appelant dans la couche X ».",
    "why": "Pour les bugs « fonctionnalité non câblée », le symbole du domaine existe (setHighlightInCart) mais n'a pas d'appelant côté formulaire. Lister ses usages révèle directement le trou et l'analogue (setDescription dans fillCommandFromData).",
    "generic": true
   },
   {
    "lever": "Grep : ne plus faire primer name_hit pour les sous-chaînes très fréquentes (pondérer par IDF / rareté du mot-clé), et toujours garantir quelques places aux fichiers qui contiennent le mot-clé le plus rare.",
    "why": "Un mot-clé générique (CartRule) noie le mot-clé discriminant (highlight). 12/12 premières lectures gaspillées sur du legacy.",
    "generic": true
   },
   {
    "lever": "Fenêtres structurelles : montrer la méthode entière qui contient un hit (ou au moins sa fin), annoncer la taille du fichier et les plages omises (« fichier 119 l., lignes 61-119 non montrées »).",
    "why": "Les bugs additifs s'insèrent en fin de chaîne/méthode, là où aucun mot-clé ne matche. La coupure en pleine expression a provoqué l'ancre SEARCH invalide en O.",
    "generic": true
   },
   {
    "lever": "Vérification syntaxique (php -l) des fichiers modifiés avant le rejeu, avec renvoi de l'erreur exacte (fichier:ligne) à l'agent ; refuser les éditions qui cassent la syntaxe.",
    "why": "O et C ont cassé le BO (syntaxe, redéclaration de méthode) et n'ont reçu qu'un « timeout connexion BO », inexploitable. Un retour rapide et précis permettrait la correction au tour suivant.",
    "generic": true
   },
   {
    "lever": "Budget d'exploration découplé du budget d'édition : lectures/recherches supplémentaires (ex. 4-5) et une relance « tu dois maintenant éditer avec ce que tu as lu » quand le budget est épuisé, au lieu de terminer sur « aucune édition ».",
    "why": "A1, A3 et R4 finissent sur une demande de lecture rejetée. Un bug multi-couches (form type + provider + handler) demande plus de 3 tours de lecture après une première lecture hors sujet.",
    "generic": true
   },
   {
    "lever": "Parseur d'édition tolérant : hériter du FILE: précédent pour un bloc SEARCH sans en-tête, et signaler explicitement les blocs ignorés ou les méthodes déjà existantes (doublon).",
    "why": "C+pages a perdu silencieusement son édition principale ; C a ajouté un setter qui existait déjà.",
    "generic": true
   },
   {
    "lever": "Consigne/étape « suivre un champ analogue » : pour une option manquante, identifier un champ frère du même formulaire et lister toutes les couches où il est câblé (type de formulaire, data provider, data handler), puis répliquer.",
    "why": "Rend le schéma form→provider→handler explicite pour tout bug d'option absente dans un formulaire Symfony/legacy, sans connaître le bug.",
    "generic": true
   },
   {
    "lever": "Valider le test de repro de la condition B (doit échouer avant correctif pour la bonne raison, pas sur une erreur de sélecteur, et inclure le setup/feature flag nécessaire) avant de s'en servir comme retour.",
    "why": "En B, le retour était une erreur Playwright de syntaxe de sélecteur, indépendante du patch : bruit pur.",
    "generic": true
   },
   {
    "lever": "Oracle : assouplir le couplage au nom et au type de widget (chercher le champ par libellé « Highlight » ou name*=highlight, vérifier l'état par la BDD) tout en gardant les vérifications fonctionnelles (création, édition reflétée, sauvegarde).",
    "why": "L'oracle exige discount[information][highlight_in_cart] et les ids SwitchType _0/_1, jamais mentionnés dans le ticket. Un correctif fonctionnellement correct avec un autre nom ou un CheckboxType échouerait.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41735",
  "fix_summary": "Le correctif officiel ajoute le filtre `(fv.custom IS NULL OR fv.custom = 0)` dans deux query builders de grille du BO Symfony : src/Core/Grid/Query/FeatureValueQueryBuilder.php::getQueryBuilder (liste des valeurs d'une caractéristique, via andWhere) et src/Core/Grid/Query/FeatureQueryBuilder.php::getSearchQueryBuilder (condition du leftJoin, donc la colonne « values_count » de la liste des caractéristiques). Cela fait 3 lignes au total, du SQL pur, sans toucher au repository ni au contrôleur.",
  "agent_behaviour": "Mots-clés quasi identiques dans les 12 essais : FeatureValue, FeatureValueRepository, (Admin)FeatureValueController, getFeatureValues, custom_*. Le grep renvoie 25 fichiers, dominés par Product/FeatureValue/* et Feature/CommandHandler/*. L'agent lit presque toujours src/Adapter/Feature/Repository/FeatureValueRepository.php, souvent src/Core/Grid/Factory/FeatureValueGridFactory.php (la définition de la grille, voisine du bon fichier) et FeatureValueController.php. Il rate FeatureValueQueryBuilder dans 10 essais sur 12.\n\nTrois scénarios d'échec :\n(1) Boucle de relecture (A3, R2, R3, O, B, C, C+pages, A-4B). Il redemande {\"files\":[\"…FeatureValueRepository.php\"]} et reçoit la même fenêtre [lignes 1-260], qui s'arrête juste avant la méthode privée getFeatureValuesQueryBuilder (ligne 320 sur 368). Les 2 retours arrière partent là-dessus, puis la réponse JSON est ignorée en silence et l'essai finit sans édition.\n(2) Chemin halluciné (A2). Il demande `src/PrestaShop/Core/Grid/Factory/FeatureValueGridFactory.php`, qui n'existe pas. flow.show renvoie vide, la liste est filtrée sans message, la boucle backtrack épuise son compteur sans nouveau tour, et l'essai s'arrête en 3 tours sans édition.\n(3) Édition bien formée mais au mauvais endroit (A1, A4). Après la relance par mot-clé « getFeatureValuesQueryBuilder », la fenêtre se déplace et il ajoute `} else { $qb->andWhere('fv.custom = 0'); }` dans FeatureValueRepository. Le patch s'applique mais ce repository ne sert pas la grille du BO, donc l'oracle échoue.\n\nR1 et R4 sont les seuls essais où le grep classe FeatureValueQueryBuilder (14e puis 17e), grâce aux mots-clés génériques id_feature et custom. L'agent le lit et produit du premier coup l'édition juste `->andWhere('fv.custom = 0')`, soit la moitié du correctif officiel. Il ne touche pas FeatureQueryBuilder, que le ticket ne mentionne pas. Aucun retour d'exécution en R (pas de replay), donc pas d'itération.\n\nO : comme il n'y a jamais d'édition, l'oracle n'est jamais exécuté. Les deux retours sont « aucune édition applicable » et l'agent répond deux fois le même JSON {\"files\":[…Repository]}, ignoré parce que le budget de retours arrière est déjà consommé. La borne haute n'est donc pas mesurée sur ce bug.\n\nB est en pratique identique à A : il n'existe pas de replay*.spec.js (STATUS_REPRO = echec, timeout technique), donc feedbacks=[]. Le premier essai C n'a reçu aucune entrée de glossaire. C+pages n'a reçu que les contrôleurs Feature*Controller.",
  "primary_failure": "localisation_mots_cles",
  "secondary_failures": [
   "fenetre_lecture",
   "boucle_ou_budget_tours",
   "oracle_ou_env_douteux",
   "multi_fichiers",
   "localisation_fichier_hors_recherche"
  ],
  "evidence": "GREP : sur le commit de base, 58 fichiers de code ont « featurevalue » dans leur nom (hors tests/vendor). MAX_GREP_FILES=25 et le tri (name_hit, nb de mots-clés distincts, nb de lignes) relègue FeatureValueQueryBuilder (1 mot-clé, peu de lignes). Position de src/Core/Grid/Query/FeatureValueQueryBuilder.php dans les résultats : absent en A1-A4, R2, R3, O, B, C, C+pages, A-4B, E ; 14e en R1 (mots-clés [AdminFeatureValueController, FeatureValue, custom_value, id_feature]) ; 17e en R4 ([AdminFeaturesController, FeatureValue, id_feature, custom]). Le lien GridFactory → QueryBuilder n'existe que dans du YAML (src/PrestaShopBundle/Resources/config/services/core/grid/grid_data_factory.yml:640/648, doctrine_query_builder.yml:511/519), un format exclu de la recherche (CODE_EXT = php, tpl, twig, js, ts, vue).\n\nFENÊTRE : FeatureValueRepository.php fait 368 lignes et getFeatureValuesQueryBuilder est à la ligne 320. flow.windows renvoie « [lignes 1-260] » : un seul span fusionné, licence et use compris, accepté au-delà de MAX_LINES_PER_FILE=120 à cause de `or not selected`. La fenêtre se termine sur getFeaturesInfoByFeatureValueIds (l. 259). Dans la trace O, les tours 3 et 4 « relire » ont un user_len identique de 9355 et l'assistant renvoie le même JSON.\n\nSILENCES : dans run.py backtrack(), `new = [f for f in … if flow.show(base, f)]`. Si un chemin est invalide, aucun message n'est produit et le compteur est quand même incrémenté (A2, 3 tours). Une fois backtracks==2, une réponse {\"files\":…} est ignorée sans avertir le modèle (O, tours 5 et 6).\n\nÉDITIONS : A1 et A4 ont produit le même patch.diff, dans FeatureValueRepository.php vers la ligne 340 (`} else { $qb->andWhere('fv.custom = 0'); }`), appliqué sans régression mais sans effet sur l'oracle. R1 et R4 ont produit le même patch, dans FeatureValueQueryBuilder.php ligne 73 (`->andWhere('fv.custom = 0')`), identique au hunk officiel n°2 à la gestion du NULL près. La réévaluation de R1 échoue sur oracle.bo.spec.js:22 (« Expected pattern: /^\\s*6\\s*$/ » sur td.values_count), c'est-à-dire sur l'assertion du compteur de la liste des caractéristiques, celle qui dépend de FeatureQueryBuilder. Le premier result.json de R1 indiquait regression=true à cause d'un timeout de connexion BO (environnement instable), corrigé à la réévaluation.\n\nFIXTURES : install-dev/fixtures/fashion/data/feature_value.xml a custom=\"0\" pour toutes les valeurs standard. Le filtre `fv.custom = 0` de R passerait donc la partie « liste des valeurs » de l'oracle.",
  "oracle_fair": "douteux",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "Grep diversifié : plafonner le nombre de fichiers par répertoire ou par motif de nom, et lister ensuite les répertoires tronqués avec leur compte (ex. « src/Core/Grid/Query/ : 2 fichiers de plus ») ; ou passer à environ 40 chemins sans compte de lignes, ce qui coûte peu de tokens.",
    "why": "Le mot-clé principal correspond à 58 fichiers par leur nom. Le top 25 est saturé par un seul sous-domaine (Product/FeatureValue) et la bonne couche (Grid/Query) disparaît. C'est le facteur qui sépare les 2 essais réussis des 10 autres.",
    "generic": true
   },
   {
    "lever": "Pour chaque fichier lu, donner les fichiers voisins du même répertoire et les fichiers reliés (services YAML qui citent la classe, classes injectées, use), ou inclure yml/xml dans la recherche par chemin et par contenu.",
    "why": "Dans les architectures DI/Symfony, le lien entre ce que l'agent lit (GridFactory) et ce qu'il faut corriger (QueryBuilder) passe par la config des services, que la recherche actuelle ignore. L'agent était à un saut du bon fichier dans 9 essais.",
    "generic": true
   },
   {
    "lever": "Fenêtres de lecture : plafond strict (sans l'exception `or not selected`), en-tête licence et use retiré, plan du fichier (signatures de méthodes avec numéros de ligne) toujours fourni, et action de lecture ciblée {\"file\":…, \"lines\":\"300-368\"} ou {\"symbol\":\"Classe::methode\"}.",
    "why": "La méthode pertinente (l. 320/368) n'apparaît jamais dans la fenêtre de 260 lignes à partir de 1. Le modèle n'a aucun moyen de demander la suite autrement qu'en relançant une recherche avec le nom exact de la méthode, qu'il a dû deviner.",
    "generic": true
   },
   {
    "lever": "Détecter une relecture identique : si un fichier déjà montré est redemandé, servir les fenêtres non encore vues (pagination) et l'indiquer, sans consommer de retour arrière.",
    "why": "Une boucle « relire le même fichier, recevoir le même contenu » a tué au moins 8 des 12 essais en épuisant les 2 retours arrière.",
    "generic": true
   },
   {
    "lever": "Retour explicite pour les chemins introuvables, avec suggestion du chemin existant le plus proche (même nom de base), sans décompter le retour arrière.",
    "why": "Le chemin halluciné de A2 (préfixe src/PrestaShop/ en trop) a mis fin à l'essai en silence, alors que src/Core/Grid/Factory/FeatureValueGridFactory.php existe.",
    "generic": true
   },
   {
    "lever": "Budget de retours arrière visible : annoncer le nombre restant à chaque tour, et quand il est épuisé dire clairement « édite maintenant avec ce que tu as » au lieu d'ignorer la réponse. Dans la boucle de retour (B/O), autoriser une lecture par tour de correction.",
    "why": "En O, les deux tours « corriger » ont été perdus : le modèle redemande un fichier, la demande est ignorée, et l'oracle n'est jamais exécuté. La borne haute n'est pas mesurée.",
    "generic": true
   },
   {
    "lever": "Après une première édition, lancer automatiquement un grep des identifiants touchés (table, colonne, méthode : ex. nom de table SQL + nom de colonne) et proposer les autres occurrences du même motif à vérifier.",
    "why": "Les correctifs multi-sites (même filtre à appliquer dans plusieurs requêtes) échappent au déroulé en un seul coup. Les essais R qui ont trouvé la moitié du correctif n'avaient aucun moyen de voir la seconde requête sœur.",
    "generic": true
   },
   {
    "lever": "Hygiène d'évaluation : signaler et exclure les essais dont la condition est dégénérée (B sans replay*.spec.js, C sans entrée de glossaire, O sans aucune édition, donc oracle jamais exécuté), et séparer dans l'oracle les assertions exigées par le ticket des assertions supplémentaires (crédit partiel).",
    "why": "Sur ce bug, B et C équivalent à A et O n'a jamais reçu de retour de l'oracle. Les essais R réussissent la partie décrite par le ticket mais échouent sur une assertion (le compteur values_count) que le ticket ne demande pas explicitement.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41727",
  "fix_summary": "Un seul fichier change : src/PrestaShopBundle/DependencyInjection/PrestaShopExtension.php, méthode preprendApiConfig. Le correctif remplace `if (file_exists($entitiesRessourcesPath.'/index.php')) unlink(...)` par une suppression récursive, `(new Filesystem())->remove(Finder::create()->files()->in($entitiesRessourcesPath)->name('index.php'))`, et ajoute 2 `use` (Filesystem, Finder). Cette suppression a lieu avant le scan API Platform (require_once), pas avant le scan Doctrine.",
  "agent_behaviour": "Le scénario est le même dans presque tous les essais. Au tour 1, Gemma propose `index.php` parmi ses mots-clés (12/12 essais), souvent avec `src/Entity`, `unlink`, `Entity` et `RecursiveDirectoryIterator`. Ce choix est raisonnable, puisque le titre du ticket cite « src/Entity/index.php ». Mais grep() traite tout mot-clé contenant un '.' comme « précis » et le cherche aussi dans les noms de fichiers. Les 517 index.php du dépôt passent alors en tête du classement (critère name_hit placé en premier), avec 0 ligne trouvée chacun. Les 25 résultats affichés sont donc tous admin-api/index.php, admin-dev/.../index.php, etc. Gemma voit que ces résultats sont inutiles : soit il relance une recherche au lieu de choisir des fichiers, soit il invente un chemin (ModuleEntityManager.php, ModuleValidator.php, EntityManager.php, qui n'existent pas, d'où un CONTENU vide). Il remet presque toujours `index.php` dans ses nouveaux mots-clés, ce qui reproduit l'inondation. Deuxième bogue d'outillage : à l'étape relocaliser, le harnais attend `{\"files\"}`. Si Gemma répond `{\"keywords\":[...]}`, parse_json(...,'files') lève une KeyError et le repli par regex récupère toutes les chaînes entre guillemets. La chaîne « index.php » existe à la racine, donc le harnais lit le contrôleur front index.php au lieu de relancer la recherche, et un des 2 retours arrière est perdu. Le budget de 2 retours arrière s'épuise ainsi sans aucune édition, en A1, A2, A3, R1, R2, B et O. Quand l'agent arrive à éditer (A4 et C), il a suivi la piste « Doctrine entities scan » du ticket jusqu'à ModulesDoctrineCompilerPass::createAnnotationMappingDriver. Ce fichier contient le même motif (un seul index.php traité) pour l'AnnotationDriver Doctrine. L'édition SEARCH/REPLACE est propre et s'applique (Finder récursif + addExcludePaths), mais elle vise le mauvais mécanisme : la sortie (exit) vient du require_once d'API Platform. Le BO redirige donc toujours vers le front. En R3, R4 et C+pages, l'agent relit ModuleManager.php 2 ou 3 fois parce que la fenêtre ne lui montre que les lignes 5-65, et il n'a aucun moyen de demander une autre plage. En O, le retour de l'oracle n'est jamais atteint : les deux retours disent « aucune édition applicable », sans le message Playwright. O se comporte donc exactement comme A.",
  "primary_failure": "localisation_mots_cles",
  "secondary_failures": [
   "outil grep : mot-clé avec '.' recherché dans les chemins, name_hit prioritaire, 517 index.php à 0 ligne qui évincent le bon fichier (bogue du harnais, pas seulement un mauvais choix du modèle)",
   "parse_json : une réponse {\"keywords\"} à l'étape LIRE devient la lecture du fichier racine index.php (repli regex sur les chaînes entre guillemets), ce qui consomme un retour arrière",
   "piège du ticket : 'Doctrine entities scan' mène au fichier jumeau ModulesDoctrineCompilerPass (même motif index.php) au lieu de PrestaShopExtension (API Platform)",
   "fenetre_lecture : impossible de demander une plage de lignes, relectures en boucle de ModuleManager.php (R3, R4, C+pages)",
   "chemins inventés (ModuleEntityManager.php, ModuleValidator.php, EntityManager.php) : CONTENU vide sans message d'erreur",
   "boucle_ou_budget_tours : 2 retours arrière seulement, épuisés par des recherches stériles",
   "O et B sans effet : pas d'édition, donc pas de retour d'oracle ; en B le test de repro écrit par Gemma échoue pour une raison technique (mauvais nom de conteneur docker), donc pas de retour non plus"
  ],
  "evidence": "1) Résultat de recherche identique dans A1, A2, A3, R, B et O : « admin-api/index.php (0) … admin-dev/themes/default/fonts/index.php (0) », 25 fichiers à 0 ligne. Reproduction en lecture seule avec flow.grep sur le commit de base 458f109 : avec ['index.php','Entity','unlink','recursive','Module','Doctrine'], PrestaShopExtension.php n'est pas dans le top 25 ; avec ['Entity','unlink','recursive','Doctrine'] (index.php retiré), il est 1er (rang 0) ; avec ['entitiesRessourcesPath'], 1er ; avec ['ApiPlatform','unlink','Entity'], 2e. git ls-tree compte 517 index.php. Code en cause, agent/flow.py:61 `specific = [... re.search(r\"[A-Z/_.]\", k[1:]) ...]` et flow.py:69 `sorted(found, key=lambda f: (not name_hit(f), ...))`. 2) En A1, relocaliser : l'assistant répond `{\"keywords\": [\"src/Entity\", \"unlink\", \"RecursiveDirectoryIterator\", \"index.php\"]}` et le tour suivant est « relire » avec « ===== index.php ===== » (contrôleur front). Cause : agent/flow.py:215-221, parse_json tombe dans `except: return re.findall(r'\"([^\"]{3,80})\"', text)`, puis run.py:173 garde 'index.php' parce que show() le trouve. 3) En O, tour relocaliser avec ['Entity/index.php','unlink','RecursiveDirectoryIterator','Module'] (sans « index.php » seul) : « src/PrestaShopBundle/DependencyInjection/PrestaShopExtension.php (21) » apparaît au 10e rang, mais Gemma choisit classes/module/Module.php (1066) et ModuleManager.php (207), gonflés par le mot-clé générique « Module ». 4) Patch A4 = patch C sur ModulesDoctrineCompilerPass.php:88-90 : `$finder->files()->in($moduleEntityDirectory)->name('index.php')` puis addExcludePaths. Il s'applique, sans régression, et l'oracle échoue ligne 69 (`toHaveURL(/admin-dev/)`, reçu « http://localhost:8081/ »). 5) Message de R3 (en anglais dans la trace) : « I only got lines 5-65. I need to see the rest of the file… Since I can't specify line numbers ». 6) O result.json : feedbacks = 2 × « aucune édition applicable », files_read=['index.php'], loc_hit=false. 7) Le fichier officiel n'a été lu dans aucun des 12 essais (loc_hit=false partout, bon_fichier=0 dans eval/results.csv).",
  "oracle_fair": "oui",
  "fixable_31b": "oui",
  "levers": [
   {
    "lever": "grep : ne jamais classer un fichier trouvé seulement par son chemin devant un fichier qui contient les mots-clés ; exclure la recherche par chemin pour un nom de fichier très fréquent (si plus de N fichiers ont ce nom, comme index.php, on cherche ce mot-clé seulement dans le contenu)",
    "why": "Un mot-clé banal comme index.php ou config.php inonde le top 25 avec des fichiers à 0 ligne et fait disparaître le bon fichier, qui contenait pourtant 3 mots-clés distincts.",
    "generic": true
   },
   {
    "lever": "Pondérer le classement grep par rareté (IDF) : un mot-clé présent dans des centaines de fichiers (Module, Entity) compte peu, un mot-clé rare (unlink combiné à Entity, src/Entity) compte beaucoup",
    "why": "En O, le bon fichier était 10e derrière Module.php (1066 lignes), gonflé par le mot générique « Module ».",
    "generic": true
   },
   {
    "lever": "Afficher pour chaque fichier trouvé quels mots-clés correspondent et 1 à 2 lignes d'exemple (celle du mot-clé le plus rare), avec le nombre total de fichiers trouvés et une mention de troncature",
    "why": "Gemma aurait vu `unlink($entitiesRessourcesPath . '/index.php')` directement dans la liste ; un nombre de lignes seul (0, 21, 1066) ne permet pas de choisir.",
    "generic": true
   },
   {
    "lever": "Corriger parse_json : chercher la clé attendue sans repli regex qui transforme n'importe quelle chaîne en chemin de fichier, et accepter {\"keywords\"} à l'étape LIRE comme une vraie nouvelle recherche",
    "why": "Une demande de recherche était convertie en lecture du index.php racine et consommait un des 2 retours arrière (A1, A2, A3, O).",
    "generic": true
   },
   {
    "lever": "Signaler explicitement un chemin inexistant (« fichier introuvable, voici les chemins proches : … » par correspondance floue du nom de base) au lieu d'un CONTENU vide",
    "why": "Gemma invente des chemins plausibles (ModuleEntityManager.php, ModuleValidator.php) ; une correction vers le vrai voisin évite de gaspiller un tour.",
    "generic": true
   },
   {
    "lever": "Recherche de « sites jumeaux » : après une édition, chercher dans tout le dépôt le motif littéral remplacé (ex. le fragment `'/index.php'` ou l'appel modifié) et proposer les autres occurrences avant de tester",
    "why": "Le même défaut existe souvent à plusieurs endroits ; ici l'agent a corrigé le jumeau Doctrine sans voir l'occurrence API Platform qui provoquait réellement le bug.",
    "generic": true
   },
   {
    "lever": "Lecture par plage ou par symbole : permettre {\"files\": [\"f.php:200-320\"]} ou {\"symbol\": \"Classe::methode\"}, et ne pas relire une fenêtre déjà montrée",
    "why": "En R3, R4 et C+pages l'agent relit 3 fois les lignes 5-65 de ModuleManager.php, faute de pouvoir demander une autre plage.",
    "generic": true
   },
   {
    "lever": "Retour arrière : avertir quand des mots-clés reproduisent une recherche déjà stérile (résultats identiques), et suggérer de retirer le mot-clé responsable",
    "why": "Gemma remettait index.php dans chaque relance et obtenait exactement la même liste à 0 ligne, ce qui épuisait le budget.",
    "generic": true
   },
   {
    "lever": "En O et B, si aucune édition n'a été produite, forcer au moins une tentative d'édition sur le meilleur fichier lu avant d'appeler le test, pour que le retour (oracle ou repro) ait quelque chose à évaluer",
    "why": "Le retour « aucune édition applicable » ne contient aucune information : la borne haute O ne mesure rien tant que la localisation échoue.",
    "generic": true
   }
  ]
 },
 {
  "pr": "41570",
  "fix_summary": "Le correctif officiel tient en une ligne dans src/Core/Search/Filters/FeatureFilters.php, fonction FeatureFilters::getDefaults : 'orderBy' => 'name' devient 'orderBy' => 'position'. La colonne PositionColumn existe déjà dans FeatureGridDefinitionFactory. Mais GridPresenter::getColumns ne crée la colonne poignée (id position_handle, td.js-drag-handle) que si le tri courant porte sur la colonne position. Le bug vient donc du tri par défaut, pas de la définition des colonnes.",
  "agent_behaviour": "Il y a 12 essais au total : A×4, R×4, C, C+pages, B et O. L'essai E (modèle gemma-4-ft) est hors décompte. Deux schémas reviennent.\n(1) Quatre essais (A1, A2, C, C+pages) lisent FeatureGridDefinitionFactory.php avec la fenêtre 1-220, grâce au mot-clé « position ». Gemma y voit la PositionColumn déjà déclarée et formule une fausse hypothèse : la colonne existerait mais serait mal placée. Le ticket parle de « first column ». Gemma déplace donc la PositionColumn avant values_count (A1) ou avant id_feature (A2, C, C+pages). Les blocs SEARCH/REPLACE sont propres et s'appliquent, mais l'oracle échoue (th position_handle : 0).\n(2) Huit essais (A3, A4, O, B, R1 à R4) finissent sans aucune édition, enfermés dans une boucle déterministe. Le contrôleur FeatureController ne donne rien, Gemma relance une recherche (FeatureGridFactory, grid_factory.feature…) puis demande FeatureGridDefinitionFactory.php. Comme windows() reçoit les NOUVEAUX mots-clés, le fichier n'est montré que sur les lignes 2-62 : 60 lignes sur un budget de 120. L'extrait s'arrête à l'entrée de getColumns, avant les colonnes. Gemma redemande le même fichier, reçoit exactement le même extrait, et épuise les 2 retours arrière. A3 boucle de la même façon sur FeatureController (lignes 9-95 et 169-239, identiques à chaque fois). R2 relance trois recherches à la suite.\nLe fichier officiel FeatureFilters.php n'est jamais lu, ni par les mots-clés initiaux ni par les mots-clés relancés (aucun ne contient Filters, orderBy, sort ou getDefaults). Pourtant il apparaît 6 fois dans les résultats de relocalisation (« src/Core/Search/Filters/FeatureFilters.php (2) ») et n'est jamais choisi. Le passage de fichier en fichier est même visible : dans indexAction, on lit « FeatureFilters $filters » puis « $featureGridFactory->getGrid($filters) ».",
  "primary_failure": "logique_fausse",
  "secondary_failures": [
   "fenetre_lecture",
   "boucle_ou_budget_tours",
   "localisation_mots_cles",
   "oracle_ou_env_douteux"
  ],
  "evidence": "Diff officiel : un seul hunk dans FeatureFilters.php, @@ -25,7 : - 'orderBy' => 'name', + 'orderBy' => 'position'.\nMécanisme vérifié au commit de base 13c69d5 : dans src/Core/Grid/Presenter/GridPresenter.php l.105-116, la colonne 'position_handle' n'est ajoutée en tête (array_unshift) que si strtolower($positionColumn->getId()) == strtolower($searchCriteria->getOrderBy()).\n- A1 (runs/20260925-101441-A) : mots-clés [AdminFeaturesController, Feature, position, FeatureGrid, features]. Lecture de FeatureGridDefinitionFactory, lignes 1-220. Édition : déplacement du bloc PositionColumn au-dessus de values_count. Le patch s'applique (applied=true) ; oracle : « Expected: 1 Received: 0 » sur th[data-column-id=\"position_handle\"]. Le premier verdict « regression » venait d'un timeout d'auth.setup, corrigé à la réévaluation (regression=false).\n- A2 (runs/20260925-114612-A) : même fichier, PositionColumn déplacée avant id_feature, même échec. C et C+pages produisent le même patch.\n- A3 (runs/20260925-142912-A) : T2 lit la définition de grille, puis T3 et T4 demandent deux fois FeatureController.php et reçoivent deux fois [lignes 9-95] et [lignes 169-239] à l'identique. Résultat : « aucune édition ».\n- A4 (runs/20260925-165642-A), T3 relocaliser : FeatureFilters.php (2) figure dans 3 résultats seulement ; Gemma choisit FeatureGridDefinitionFactory. T4 et T5 montrent [lignes 2-62] à l'identique.\n- O (runs/20260926-065152-O) : même boucle en T4 et T5 ([lignes 2-62]), puis T6 et T7 « corriger » ne renvoient que « RÉSULTAT DU TEST : ÉCHEC / aucune édition applicable ». Gemma répond encore {\"files\": [FeatureGridDefinitionFactory]}. Le message de l'oracle (sélecteur position_handle) n'a donc JAMAIS été montré au modèle. feedbacks = 2 × « aucune édition applicable ».\n- B (runs/20260928-092011-B) : même boucle 2-62, feedbacks=[]. Aucun replay*.spec.js n'est valide (STATUS_REPRO=echec, timeout de clic), donc pour ce bug B = A.\n- R1, R3, R4 : même boucle 2-62. R2 : trois relocalisations sans lecture.\nCode en cause : agent/run.py l.177, contents = flow.windows(flow.show(base, f), kws), avec kws remplacé par les mots-clés de relocalisation. agent/flow.py windows() ne remplit pas le budget MAX_LINES_PER_FILE et n'a ni pagination ni dédoublonnage des relectures.",
  "oracle_fair": "oui",
  "fixable_31b": "peut-etre",
  "levers": [
   {
    "lever": "Relecture sans répétition : si un fichier déjà montré est redemandé, montrer les plages pas encore vues (pagination), ou le fichier entier s'il fait moins de ~250 lignes. Remplir toujours le budget MAX_LINES_PER_FILE au lieu de s'arrêter à 60 lignes.",
    "why": "8 essais sur 12 meurent sur un extrait identique renvoyé deux fois (2-62 ou 9-95). Le modèle n'a jamais pu sortir de la boucle, alors que le budget de lignes n'était utilisé qu'à moitié.",
    "generic": true
   },
   {
    "lever": "Calculer les fenêtres de relecture sur l'union des mots-clés du ticket et de ceux de la relocalisation (pas seulement les nouveaux), et permettre une lecture ciblée {\"files\":[{\"path\":...,\"lines\":\"a-b\"}]} ou par symbole {\"symbol\":\"getColumns\"}.",
    "why": "Après relocalisation, les nouveaux mots-clés (noms de classe, id de service) ne touchent que l'en-tête du fichier. Le corps utile (getColumns) disparaît alors qu'il avait été vu avec le mot-clé « position ».",
    "generic": true
   },
   {
    "lever": "Détecter l'absence de progrès : une demande identique à une précédente ne consomme pas de retour arrière, mais reçoit le message « déjà lu ; voici la suite / passe à l'édition ». Une fois les retours arrière épuisés, exiger une édition plutôt que de terminer sans patch.",
    "why": "Les retours arrière (2 au plus) sont gaspillés sur des répétitions, et l'essai se termine en « aucune édition » sans aucun verdict exploitable.",
    "generic": true
   },
   {
    "lever": "Conditions avec retour (O, B) : même sans édition applicable, exécuter le test sur le code non modifié et montrer l'assertion qui échoue (sélecteur, valeur attendue/reçue), idéalement dès avant la première édition.",
    "why": "En O, le seul retour reçu a été « aucune édition applicable » : la borne haute n'a pas mesuré l'apport de l'oracle sur ce bug. L'assertion sur position_handle aurait donné un identifiant concret à rechercher.",
    "generic": true
   },
   {
    "lever": "Rechercher automatiquement dans le code les identifiants littéraux de l'assertion en échec (data-column-id, classes CSS, clés), puis ajouter les fichiers trouvés à la liste proposée.",
    "why": "Chercher position_handle mène directement au fichier qui décide de l'affichage (GridPresenter) et à sa condition. C'est valable pour tout bug d'interface vérifié par un sélecteur.",
    "generic": true
   },
   {
    "lever": "Panorama des dépendances : quand une méthode de contrôleur est lue, ajouter le chemin et la signature des classes de ses paramètres typés et des objets transmis à l'appel principal (ex. getDefaults() d'un objet Filters).",
    "why": "Le fichier fautif se trouvait à un seul saut du contrôleur lu (paramètre typé passé à getGrid), mais le modèle ne l'a jamais suivi, même quand il apparaissait dans les résultats.",
    "generic": true
   },
   {
    "lever": "Comparaison avec un composant frère : quand le ticket dit « comme dans X » / « marche ailleurs », proposer les fichiers frères par motif de nom (FooX ↔ FooY) et montrer leur diff.",
    "why": "Comparer le composant qui marche (attributs) avec celui qui ne marche pas révèle les écarts de configuration (ici le tri par défaut) sans connaître le framework. Ce schéma revient souvent dans les tickets PrestaShop.",
    "generic": true
   },
   {
    "lever": "Invite de diagnostic avant l'édition : « si l'élément décrit comme manquant est déjà déclaré dans le code, cherche la condition qui l'affiche ou le masque avant de modifier sa déclaration ».",
    "why": "Les 4 éditions appliquées déplacent une colonne déjà présente. Le modèle n'interroge jamais la condition d'affichage.",
    "generic": true
   }
  ]
 }
]
```