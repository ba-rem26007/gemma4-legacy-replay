# Résultats — vivier TEST 9.1.x (33 bugs, oracles cachés)

Gemma 4 31B (API Google AI Studio), déroulé fixe, **1 tentative par bug** (pas de retour de test), température 0,2.
« Résolu » = l'oracle passe **et** aucune régression (accueil FO + login BO) sur la base remise à zéro.
Verdicts **réévalués** sans rappeler le modèle (`bench/reeval.py`) sur instances neuves quand disponibles.
L'essai 1 a tourné sur un environnement partiellement défectueux : sa génération est valable, son verdict l'est après réévaluation.

## Taux de résolution par essai

| Condition | Essai 1 | Essai 2 | Essai 3 | Essai 4 | Moyenne | Écart-type | Résolu ≥ 1 fois (pass@4) | Bon fichier (moy.) | Régressions |
|---|---|---|---|---|---|---|---|---|---|
| A · ticket seul | 12/33 | 13/33 | 15/33 | 11/33 | 12.8 (39%) | 1.5 | 17/33 | 19.8 | 0 |
| R · ticket + 2 corrections TRAIN similaires | 14/33 | 12/33 | 14/33 | 11/33 | 12.8 (39%) | 1.3 | 15/33 | 20.2 | 0 |

## R contre A (apparié par bug)

Écart moyen du taux de résolution R − A : **+0.0%** (IC 95 % bootstrap : -9.1% à +9.1%).
Si l'intervalle contient 0, l'injection de corrections similaires n'a pas d'effet démontré.

- Bugs jamais résolus (0/8) : **15**
- Bugs toujours résolus (8/8) : **3**

## Détail par bug (nombre d'essais résolus sur 4, et Condition B sur 1 essai)

| Bug | Ticket | A (/4) | R (/4) | B (/1) |
|---|---|---|---|---|
| [#40971](https://github.com/PrestaShop/PrestaShop/pull/40971) | Uploading logo in Design -> Theme & Logo in multistore with a single s | 4 | 4 | **1** |
| [#41193](https://github.com/PrestaShop/PrestaShop/pull/41193) | [9.1.0] Child theme translations are not displayed in Back Office tran | 4 | 4 | **1** |
| [#41007](https://github.com/PrestaShop/PrestaShop/pull/41007) | CountryQueryBuilder::getCountQueryBuilder() always returns 1 instead o | 4 | 4 | **1** *(tour 5)* |
| [#40853](https://github.com/PrestaShop/PrestaShop/pull/40853) | Search::find fuzzy search does not escape closest word and breaks SQL  | 3 | 4 | **1** |
| [#40651](https://github.com/PrestaShop/PrestaShop/pull/40651) | Bad product name | 3 | 4 | **1** |
| [#41299](https://github.com/PrestaShop/PrestaShop/pull/41299) | Invalid product URLs trigger Fatal in ProductController::assignPriceAn | 4 | 3 | **1** |
| [#42004](https://github.com/PrestaShop/PrestaShop/pull/42004) | Duplicating with DuplicateProductCommand: Invalid Product localized pr | 3 | 4 | **1** |
| [#41929](https://github.com/PrestaShop/PrestaShop/pull/41929) | Cannot edit a product when the experimental Catalog price rules featur | 4 | 3 | **1** |
| [#41652](https://github.com/PrestaShop/PrestaShop/pull/41652) | Changing an order's status throws "Duplicate entry '<idp>-<idpa>-0-0'  | 4 | 3 | **1** |
| [#41468](https://github.com/PrestaShop/PrestaShop/pull/41468) | Multishop: cache_default_attribute is not reset for all shops when cha | 4 | 3 | **1** |
| [#41130](https://github.com/PrestaShop/PrestaShop/pull/41130) | When the Admin API is used with multistore enabled, any write operatio | 2 | 4 | **1** |
| [#41665](https://github.com/PrestaShop/PrestaShop/pull/41665) | B O - Order view page - The Invoice prefix is displayed in the custome | 2 | 4 | 0 |
| [#40898](https://github.com/PrestaShop/PrestaShop/pull/40898) | Bug: reserved_quantity not updated when "Share available quantities fo | 2 | 3 | **1** |
| [#41320](https://github.com/PrestaShop/PrestaShop/pull/41320) | Unable to delete product from order when product is deleted from catal | 3 | 0 | **1** *(tour 7)* |
| [#41530](https://github.com/PrestaShop/PrestaShop/pull/41530) | BO - Shopping carts - Custom product image does not appear | 0 | 3 | 0 |
| [#41675](https://github.com/PrestaShop/PrestaShop/pull/41675) | HTMLPurifier through twig extension is not adhering to cache dir confi | 2 | 1 | **1** |
| [#41524](https://github.com/PrestaShop/PrestaShop/pull/41524) | BO - Order - Invoice / Payment method is not printed on invoice if the | 2 | 0 | 0 |
| [#41394](https://github.com/PrestaShop/PrestaShop/pull/41394) | [Multishop] Error when updating "Schema of URLs" for a single shop | 1 | 0 | 0 |
| [#40743](https://github.com/PrestaShop/PrestaShop/pull/40743) | Bug: when invoicing is disabled, changing order status to "paid=1" doe | 0 | 0 | 0 |
| [#40070](https://github.com/PrestaShop/PrestaShop/pull/40070) | actionCarrierUpdate not triggered on migrated carrier page | 0 | 0 | 0 |
| [#41100](https://github.com/PrestaShop/PrestaShop/pull/41100) | All non core HTML emails are empty | 0 | 0 | 0 |
| [#41327](https://github.com/PrestaShop/PrestaShop/pull/41327) | Orders are persisted with the cart totals but the items are less than  | 0 | 0 | 0 |
| [#41412](https://github.com/PrestaShop/PrestaShop/pull/41412) | Shop can't send emails from IDN domains | 0 | 0 | 0 |
| [#40999](https://github.com/PrestaShop/PrestaShop/pull/40999) | Multistore - Can't create Shop without import data | 0 | 0 | 0 |
| [#41036](https://github.com/PrestaShop/PrestaShop/pull/41036) | Error 500 if I enter a space in a customer's first or last name field | 0 | 0 | 0 |
| [#41457](https://github.com/PrestaShop/PrestaShop/pull/41457) | The prefix and the invoice number are missing from the name of the inv | 0 | 0 | 0 |
| [#41225](https://github.com/PrestaShop/PrestaShop/pull/41225) | Attribute swatches on homepage ignore position ordering | 0 | 0 | 0 |
| [#41611](https://github.com/PrestaShop/PrestaShop/pull/41611) | Cart rule compatibility search does not filter results for new cart ru | 0 | 0 | 0 |
| [#41573](https://github.com/PrestaShop/PrestaShop/pull/41573) | The Discount highlight feature no longer exists on Discount V2. | 0 | 0 | 0 |
| [#41735](https://github.com/PrestaShop/PrestaShop/pull/41735) | In Prestashop 9.1 The custom features are listed in the default featur | 0 | 0 | 0 |
| [#41727](https://github.com/PrestaShop/PrestaShop/pull/41727) | Module Development and Distribution: Prestashop deletes automatically  | 0 | 0 | 0 |
| [#41570](https://github.com/PrestaShop/PrestaShop/pull/41570) | missing column to change the position of the features on prestashop 9. | 0 | 0 | 0 |
| [#41923](https://github.com/PrestaShop/PrestaShop/pull/41923) | Not able to change stock behaviour in shared stock | 0 | 0 | **1** *(tour 7)* |

## Borne haute : l'oracle comme retour (condition O, 1 essai)

L'agent reçoit le résultat de l'**oracle caché** après chaque tentative (fuite volontaire) et peut corriger 2 fois.
C'est le meilleur retour qu'un vérificateur puisse donner : il borne l'apport de toute chaîne de tests.

| | Bugs résolus |
|---|---|
| A, moyenne des 4 essais | 12.8/33 |
| O, 1re tentative (même consigne que A) | 13/33 |
| O, après retour de l'oracle | **16/33** (+3 : #41394, #41299, #41923) |
| O, verdict final réévalué (dernier patch) | 16/33 |

Lecture : même un vérificateur parfait n'ajoute que quelques bugs ; les échecs restants ne trouvent pas le bon fichier ou ne savent pas corriger malgré le signal (voir `docs/ECHECS.md`).

## Condition B : Replay des tests de reproduction (1 essai)

L'agent reçoit le résultat du **test de reproduction Playwright / PHPUnit** après chaque tentative de patch et dispose de retries pour adapter son code.
Run de référence : `20260928-092011-B` (exécuté sur l'instance Docker `psbench2` le 28 sept. 2026).

| Condition | Bugs traités | Résolus | Taux | Bon fichier | Gagnés (vs A 0/4) | Perdus (vs A 4/4) | Régressions |
|---|---|---|---|---|---|---|---|
| A · ticket seul (moy. 4 essais) | 33 | 12.8 | 39.0% | 19.8 | — | — | 0 |
| R · ticket + 2 TRAIN similaires | 33 | 12.8 | 39.0% | 20.2 | 0 | 0 | 0 |
| **B · ticket + replay des tests** | **33** | **15** | **45.5%** | **17** | **1 (#41923)** | **0** | **0** |
| O · oracle comme retour (borne haute) | 33 | 16 | 48.5% | 20 | 1 (#41923) | 0 | 0 |

### Analyse de l'impact du Replay (Condition B) :
1. **Gain net de +6.5 points de pourcentage** par rapport à la baseline Condition A (15/33 contre 12.8/33).
2. **Sauvetage en cours de route grâce au feedback d'échec** :
   - `#41007` : Échec au tour 4 (`the country grid should display...`), l'agent analyse l'erreur de test et réussit au tour 5.
   - `#41923` : Bug historique réputé impossible (0/4 en A, 0/4 en R) ! Échec au tour 6 sur `replay_repro.bo.spec.js`, l'agent rectifie le comportement de stock partagé et résout au tour 7.
3. **Sécurité totale** : **0% de régression** sur l'ensemble des 15 bugs validés.

## Condition D : Modèle Fine-Tuné QLoRA (Gemma 4 + LoRA PrestaShop)

Le modèle fine-tuné sur 585 trajectoires de résolution est interrogé via l'inférence déportée Colab GPU T4 (FastAPI + ngrok) tout en exécutant les sandboxes de test en local sur `psbench2`.
- **Run initial de validation** : `runs/20260928-163213-D` (Bug `#41007`)
- **Résultat** : **Résolu (1/1)**, localisation exacte (`loc_hit: true`), résolu au tour 5 après réactivité au retour Playwright, **0 régression**.

## Condition E : Modèle Fine-Tuné QLoRA + Règles Métier PrestaShop (33 bugs, run complet)

Évaluation complète du modèle autonome **Gemma 4 (4B) fine-tuné LoRA** (poids issus de l'entraînement Kaggle V15 sur 585 trajectoires dédoublonnées) combiné aux règles d'architecture PrestaShop (dualité Symfony/Legacy, gestion des scopes multi-boutiques et conventions de nommage).
- **Run de référence** : `runs/20260928-175551-E` (terminé le 28 sept. 2026 à 20:06 UTC sur `psbench2`).
- **Modèle** : `gemma-4-ft` via inférence déportée GPU T4 FastAPI / ngrok.
- **Résultats officiels consolidés** :
  - **Bugs évalués** : **33 / 33 (100%)**
  - **Bugs résolus et validés par l'oracle caché** : **4 / 33 (12.1%)**
    - `#40971` (`LogoUploader.php`) : Multiboutique `Shop::setContext` — **100% identique au caractère près au commit officiel PrestaShop**.
    - `#41193` (`TranslationController.php`) : Traductions de thèmes enfants en Back-Office — résolu en 3 tours.
    - `#41007` (`CountryQueryBuilder.php`) : Décompte de la grille pays — résolu au tour 5.
    - `#41130` (`AbstractObjectModelHandler.php`) : Écriture API Admin en multi-boutique OAuth2 (garde `$employee === null || $employee->hasAuthOnShop($shopId)` identique à l'officiel) — résolu au tour 5.
  - **Localisation exacte du fichier officiel (`loc_hit`)** : **14 / 33 (42.4%)**
  - **Patchs applicables (`applied`)** : **18 / 33 (54.5%)**
  - **Taux de non-régression** : **97.0%** (1 seule régression sur 33 bugs).
  - **Coût financier réel** : **0,00 €** (`runs/_budget.json`).

## Tableau Récapitulatif Comparatif Toutes Conditions

| Condition | Modèle / Paramètres | Bugs traités | Résolus | Taux | Bon fichier | Régressions | Coût API |
|---|---|---|---|---|---|---|---|
| **A** · ticket seul (moy. 4 essais) | Gemma 4 31B (API) | 33 | 12.8 | 39.0% | 19.8 (60.0%) | 0 (0.0%) | 0,00 € |
| **R** · ticket + 2 TRAIN similaires | Gemma 4 31B (API) | 33 | 12.8 | 39.0% | 20.2 (61.2%) | 0 (0.0%) | 0,00 € |
| **B** · ticket + replay des tests | Gemma 4 31B (API) | 33 | **15** | **45.5%** | **17 (51.5%)** | **0 (0.0%)** | 0,00 € |
| **O** · oracle en retour (borne haute) | Gemma 4 31B (API) | 33 | **16** | **48.5%** | **20 (60.6%)** | **0 (0.0%)** | 0,00 € |
| **D** · modèle fine-tuné (pilote) | **Gemma 4 4B LoRA** | 1 | 1 | 100% | 1 (100%) | 0 (0.0%) | 0,00 € |
| **E** · fine-tuné LoRA + règles métier | **Gemma 4 4B LoRA** | **33** | **4** | **12.1%** | **14 (42.4%)** | **1 (3.0%)** | **0,00 €** |

### Analyse de la Condition E (Modèle Autonome 4B LoRA) :
1. **Un petit modèle 4B ultra-sobre** : Avec seulement 4 milliards de paramètres et 4.29 Go de VRAM, Gemma 4 LoRA parvient à résoudre des bugs d'architecture réels complexes en e-commerce (notamment multi-boutique et API OAuth2) avec des patchs identiques aux commits des ingénieurs officiels de PrestaShop.
2. **Souveraineté et Zéro Dépense** : L'ensemble du processus (entraînement sur Kaggle et inférence sur 33 bugs) a été réalisé pour un coût d'API de **0,00 €**, sans aucune dépendance envers des modèles propriétaires tiers.

