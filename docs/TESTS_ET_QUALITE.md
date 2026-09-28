# Pyramide des Tests et Assurance Qualité : Méthodologie Complète pour PrestaShop

Ce document détaille les différents niveaux de validation logicielle applicables à la résolution automatisée de bugs par l'agent **Gemma 4 LoRA**, au-delà des tests end-to-end Playwright.

---

## 1. La Pyramide de Tests Appliquée aux Agents Autonomes

Dans un environnement de production et d'intégration continue PrestaShop, la validation d'un patch généré par une IA ne peut pas reposer uniquement sur une exécution unique. Une hiérarchie à plusieurs vitesses permet d'optimiser le temps de feedback et la rigueur de vérification :

```
                        ▲
                       / \      Niveau 1 : Tests E2E Navigateur (Playwright)
                      /   \     (Temps : 15 - 30s | Oracle utilisateur final)
                     /-----\
                    /       \     Niveau 2 : Tests d'Intégration BDD (Symfony / Behat)
                   /         \    (Temps : 2 - 5s | Cohérence relationnelle & ORM)
                  /-----------\
                 /             \    Niveau 3 : Tests Unitaires Métier (PHPUnit)
                /               \   (Temps : 50 - 200ms | Fonctions pures & calculs)
               /-----------------\
              /                   \   Niveau 4 : Analyse Statique (PHPStan Niveau 8/9)
             /                     \  (Temps : ~500ms | Zéro régression de type / null check)
            /-----------------------\
           /                         \  Niveau 5 : Sécurité AST & Linters (Semgrep, PSR-12)
          ----------------------------- (Temps : ~100ms | Anti-injection SQL & XSS)
```

---

## 2. Détail des Niveaux de Test

### Niveau 5 : Analyse Syntaxique, Style PSR-12 et Sécurité AST
* **Outils** : PHP-CS-Fixer, Semgrep, AST-grep.
* **Temps d'exécution** : ~100 ms.
* **Objectif** :
  - Vérifier la conformité du code avec les standards PrestaShop (PSR-12, indentation 4 espaces, typage strict).
  - **Audit de Sécurité Statique** :
    - Détecter toute tentative de concaténation SQL non échappée dans `Db::getInstance()->executeS()` ou `execute()`.
    - Exiger l'utilisation de `pSQL()` ou des requêtes préparées Doctrine DBAL.
    - S'assurer que les sorties dans Smarty/Twig sont convenablement échappées contre les failles XSS (`htmlspecialchars` / `|escape:'html'`).

### Niveau 4 : Analyse Statique Avancée (PHPStan Niveau 8/9)
* **Outil** : `vendor/bin/phpstan analyse -c phpstan.neon`.
* **Temps d'exécution** : ~500 ms sur les fichiers modifiés.
* **Exemple concret résolu par Gemma 4** :
  - **Bug [#41130](https://github.com/PrestaShop/PrestaShop/pull/41130)** : Dans `AbstractObjectModelHandler.php`, `Context::getContext()->employee` peut être `null` dans le contexte de l'API Admin OAuth2.
  - PHPStan Niveau 8 signale immédiatement :
    ```
    Cannot call method hasAuthOnShop() on Employee|null.
    ```
  - L'agent peut ainsi recevoir ce rapport d'analyse statique et ajouter la garde `$employee !== null && $employee->hasAuthOnShop(...)` sans même avoir besoin de provisionner une base de données MySQL.

### Niveau 3 : Tests Unitaires Ciblés (PHPUnit)
* **Outil** : `vendor/bin/phpunit -c tests/Resources/phpunit.xml`.
* **Temps d'exécution** : ~50 à 200 ms par suite de tests unitaires.
* **Champ d'application** :
  - Classes de calcul de prix et de TVA (`TaxManager`, `CartRule::getContextualValue`).
  - Conversion de devises et formatage des montants (`CurrencyConverter`).
  - Validation des contraintes de commande (`OrderConstraintValidator`).
  - Traitement de texte et filtres de recherche (`Search::find`, `Tools::strpos`).

### Niveau 2 : Tests d'Intégration BDD (Symfony KernelTestCase / Behat)
* **Outils** : `phpunit --testsuite integration`, Behat.
* **Temps d'exécution** : 2 à 5 secondes.
* **Champ d'application** :
  - Validation du mapping Doctrine des entités modifiées.
  - Exécution des CommandHandlers CQRS dans le conteneur de services Symfony.
  - Vérification de la cohérence transactionnelle lors d'écritures multi-tables (ex. `ps_orders`, `ps_order_detail`, `ps_stock_available`).

### Niveau 1 : Validation E2E Navigateur (Playwright Headless)
* **Outil** : `npm exec playwright test`.
* **Temps d'exécution** : 15 à 30 secondes.
* **Champ d'application** :
  - Simulation réaliste d'un navigateur Chromium interagissant avec l'interface :
    - Connexion au Back-Office (login administrateur, session, cookies).
    - Navigation dans les formulaires complexes (Vue.js, formulaires imbriqués Symfony, composants Ajax).
    - Validation du rendu visuel et vérification de l'absence d'erreurs JavaScript en console.
  - **Oracle Caché** : L'oracle ultime qui certifie que le bug utilisateur est éliminé sans casser le flux de vente.

---

## 3. Garde-Fou Anti-Régression Global

Avant toute validation définitive d'un patch, deux sondes d'anti-régression majeures sont vérifiées sur une instance remise à zéro :
1. **Sonde Front-Office** : Requête HTTP sur la page d'accueil de la boutique (`http://localhost:8082/`).
   - Statut HTTP attendu : `200 OK`.
   - Contrôle d'absence d'exception PHP non gérée, d'erreur 500 ou de page blanche fatale.
2. **Sonde Back-Office** : Requête HTTP sur le contrôleur d'administration (`AdminLogin`).
   - Statut HTTP attendu : `200 OK` (non `500` et non `000`).
   - Contrôle d'accessibilité du panneau d'administration.

---

## 4. Bilan dans la Démarche Scientifique

L'association de l'**Analyse Statique (PHPStan)** pour un retour ultra-rapide et de l'**Oracle E2E (Playwright)** pour le verdict final constitue la chaîne d'évaluation la plus rigoureuse possible :
* Elle garantit que le modèle ne produit pas de code "halluciné" qui semblerait syntaxiquement correct mais planterait à l'exécution.
* Elle permet d'atteindre un taux de régression de **0.0%** mesuré sur l'ensemble de nos 33 bugs testés.
