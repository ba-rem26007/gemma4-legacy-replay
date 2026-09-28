# Écosystème des Modules Tiers et Communautaires PrestaShop : Analyse et Benchmark

Ce document répertorie une sélection de **10 dépôts GitHub majeurs** de l'écosystème communautaire PrestaShop, analyse leurs typologies de bugs et détaille le protocole de test comparatif entre le patch généré par **Gemma 4 LoRA** et la résolution officielle des mainteneurs.

---

## 1. Catalogue des 10 Modules Clés de la Communauté

| # | Dépôt GitHub | Rôle & Usage Écosystème | Technologies Clés | Typologie Fréquente de Bugs |
|---|---|---|---|---|
| **1** | [`PrestaShop/ps_facetedsearch`](https://github.com/PrestaShop/ps_facetedsearch) | Navigation à facettes, filtres dynamiques catalogue | PHP 8.x, SQL complexe, Indexation | Dépréciations PHP (null array offset), cache d'attributs |
| **2** | [`PrestaShop/blockwishlist`](https://github.com/PrestaShop/blockwishlist) | Gestion des listes d'envies clients | PHP, Vue.js, Endpoints REST | Conflits session invité / utilisateur connecté |
| **3** | [`PrestaShop/productcomments`](https://github.com/PrestaShop/productcomments) | Avis, notes produits et microdonnées SEO | PHP, Ajax, Modération BO | Validation CSRF sur soumission Ajax, pagination |
| **4** | [`PrestaShop/contactform`](https://github.com/PrestaShop/contactform) | Formulaire de contact sécurisé | PHP, Mailer, reCAPTCHA | Gestion multi-boutique des adresses cibles, UTF-8 |
| **5** | [`PrestaShop/ps_checkout`](https://github.com/PrestaShop/ps_checkout) | Passerelle officielle PayPal / PrestaShop Checkout | PHP, API REST PayPal, Webhooks | Synchronisation d'état des commandes asynchrones |
| **6** | [`PrestaShop/psgdpr`](https://github.com/PrestaShop/psgdpr) | Conformité RGPD (droit à l'oubli, export JSON) | PHP, Hooks de suppression | Suppression en cascade sans casser l'historique comptable |
| **7** | [`PrestaShop/ps_emailalerts`](https://github.com/PrestaShop/ps_emailalerts) | Alertes marchands & clients (ruptures, commandes) | PHP, Hooks de mise à jour stock | Non-déclenchement en mode stock partagé multi-boutique |
| **8** | [`friends-of-presta/fop_console`](https://github.com/friends-of-presta/fop_console) | Boîte à outils CLI indispensables (Friends of Presta) | Symfony Console, PHP | Invalidation de cache CLI, compatibilité multi-versions PS |
| **9** | [`mollie/PrestaShop`](https://github.com/mollie/PrestaShop) | Module officiel de paiement Mollie (Leader UE) | PHP, SDK Mollie, Webhooks | Gestion des remboursements partiels et statuts 3D Secure |
| **10** | [`Packeta/prestashop`](https://github.com/Packeta/prestashop) | Expédition et sélection de points relais (Mondial Relay / Packeta) | PHP, JavaScript Maps, Carrier API | Injection de carte sur le tunnel One Page Checkout (OPC) |

---

## 2. Cas d'Étude Concret : `PrestaShop/ps_facetedsearch` (PR #1340)

### Fiche d'Identité du Bug
* **Dépôt** : `PrestaShop/ps_facetedsearch`
* **Pull Request** : [#1340](https://github.com/PrestaShop/ps_facetedsearch/pull/1340)
* **Date de fusion** : 19 septembre 2026
* **Titre officiel** : *Fix PHP 8.5 null array offset deprecation in converter*
* **Fichier affecté** : `src/Filters/Converter.php`
* **Test associé** : `tests/php/FacetedSearch/Filters/ConverterTest.php`

### Description du Problème
Sous les versions récentes de PHP (notamment lors de la préparation à PHP 8.5), l'accès à un offset de tableau avec une clé `null` génère une notice de dépréciation :
```
Deprecated: Passing null to parameter #1 ($offset) of type string|int is deprecated
```
Dans `Converter::createFacetedSearchFiltersFromQuery()`, si `$feature['url_name']` ou `$attributeGroup['url_name']` est `null`, l'évaluation `isset($receivedFilters[$feature['url_name']])` déclenche cette dépréciation.

### Comparaison Code Officiel vs Résolution Attendue par Gemma 4

```diff
--- a/src/Filters/Converter.php
+++ b/src/Filters/Converter.php
@@ -411,7 +411,7 @@ public function createFacetedSearchFiltersFromQuery(ProductSearchQuery $query)
                             continue;
                         }
 
-                        if (isset($receivedFilters[$feature['url_name']])) {
+                        if ($feature['url_name'] !== null && isset($receivedFilters[$feature['url_name']])) {
                             $featureValueLabels = $receivedFilters[$feature['url_name']];
                         } elseif (isset($receivedFilters[$feature['name']])) {
                             $featureValueLabels = $receivedFilters[$feature['name']];
@@ -443,7 +443,7 @@ public function createFacetedSearchFiltersFromQuery(ProductSearchQuery $query)
                             continue;
                         }
 
-                        if (isset($receivedFilters[$attributeGroup['url_name']])) {
+                        if ($attributeGroup['url_name'] !== null && isset($receivedFilters[$attributeGroup['url_name']])) {
                             $attributeLabels = $receivedFilters[$attributeGroup['url_name']];
                         } elseif (isset($receivedFilters[$attributeGroup['attribute_group_name']])) {
                             $attributeLabels = $receivedFilters[$attributeGroup['attribute_group_name']];
```

---

## 3. Protocole d'Évaluation sur les Modules Tiers

Pour benchmarker l'agent Gemma 4 sur n'importe quel module de la communauté sans altérer le cœur de PrestaShop :

1. **Isolation dans le Conteneur** :
   - Le module est présent dans `/var/www/html/modules/<nom_module>/` sur l'instance Docker dédiée (`psbench2`).
2. **Injection du Ticket Bug** :
   - L'agent reçoit le titre de l'issue GitHub, la description du bug et les étapes de reproduction.
3. **Exploration Autonome** :
   - L'agent utilise `grep` et `read` pour localiser le contrôleur ou le repository du module.
4. **Validation Double Niveau** :
   - **Niveau 1** : Exécution de la suite unitaire du module :
     ```bash
     docker exec -i psbench2-ps-1 vendor/bin/phpunit -c modules/<nom_module>/phpunit.xml
     ```
   - **Niveau 2** : Test Playwright simulant l'utilisation du module en boutique (ex. sélection d'un filtre à facettes sur une catégorie).
5. **Vérification Anti-Régression** :
   - L'accueil de la boutique et la navigation catalogue doivent répondre en `200 OK`.
