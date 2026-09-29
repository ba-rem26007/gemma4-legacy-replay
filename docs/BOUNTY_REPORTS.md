# Upstream Security & Bug Bounty Reports (Ready-to-Submit)

This document contains publication-ready Pull Request descriptions and Security Advisories for the two Zero-Day residual vulnerabilities discovered and verified by our Gemma 4 autonomous agent.

---

## 1. PrestaShop Security Advisory & PR Report

- **Target Repository**: [PrestaShop/PrestaShop](https://github.com/PrestaShop/PrestaShop)
- **Component**: `src/Core/Domain/Language/CommandHandler/DeleteLanguageHandler.php` & `BulkDeleteLanguagesHandler.php`
- **Severity**: Moderate (Multi-Tenant Context Poisoning / State Leakage)
- **Affected Versions**: PrestaShop 8.0.0 → 8.1.x, 9.0.x, develop
- **Verification Oracle**: [`kaggle/bench/test_context_leak_language.php`](../bench/test_context_leak_language.php)
- **Certified Patch**: [`kaggle/bench/diffs/residual_multishop_context_leak.diff`](../bench/diffs/residual_multishop_context_leak.diff)

### Title
`[FIX] Restore active Shop context in DeleteLanguageHandler and BulkDeleteLanguagesHandler to prevent multi-store state poisoning`

### Description
In multi-store environments, `DeleteLanguageHandler::handle()` alters the global context to perform language removal across all shops:
```php
$tmpContext = Shop::getContext();
$tmpShop = Shop::getContextShopID();
Shop::setContext(Shop::CONTEXT_ALL);
// ... language deletion logic ...
```
However, the handler **never restores** the original context upon successful completion, nor if an exception is thrown.

#### Impact
In web servers using persistent worker pools (such as PHP-FPM, RoadRunner, FrankenPHP, or Swoole), the global `Shop` singleton remains poisoned in `CONTEXT_ALL` with `Shop::getContextShopID() === null` for subsequent requests served by the same worker. This causes:
1. Cart calculations and localized product pricing to silently miscalculate without store-specific tax rules.
2. Back-office administrative actions performed after a language deletion to execute under `CONTEXT_ALL` instead of the administrator's selected shop group.
3. Silent data corruption across multi-store merchants.

### How to Reproduce
Run the provided standalone oracle script against a live PrestaShop instance:
```bash
php bench/test_context_leak_language.php
# Output before patch:
# [!] FAILURE: Context was NOT restored! (Left at CONTEXT_ALL)
```

### Proposed Resolution
Wrap the cross-shop deletion logic in a `try ... finally` block ensuring guaranteed restoration regardless of return path or exceptions:
```diff
--- a/src/Core/Domain/Language/CommandHandler/DeleteLanguageHandler.php
+++ b/src/Core/Domain/Language/CommandHandler/DeleteLanguageHandler.php
@@ -48,6 +48,7 @@ class DeleteLanguageHandler extends AbstractLanguageHandler
         $tmpContext = Shop::getContext();
         $tmpShop = Shop::getContextShopID();
+        try {
             Shop::setContext(Shop::CONTEXT_ALL);
             $language = $this->getLanguage($command->getLanguageId());
             // ... deletion steps ...
+        } finally {
+            Shop::setContext($tmpContext, $tmpShop);
+        }
```

---

## 2. Dolibarr Bug Bounty & PR Report

- **Target Repository**: [Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr)
- **Component**: `htdocs/comm/propal/class/supplier_proposal.class.php` (lines 1097-1113)
- **Severity**: Medium (Unhandled Fatal Crash / Denial of Service on REST API)
- **Affected Versions**: Dolibarr 18.0.x, 19.0.x, 20.0.x
- **Verification Oracle**: [`bench/oracles/test_supplier_proposal_stdclass.php`](../../dolibarr-gemma4/bench/oracles/test_supplier_proposal_stdclass.php)
- **Certified Patch**: [`bench/diffs/residual_supplier_proposal.diff`](../../dolibarr-gemma4/bench/diffs/residual_supplier_proposal.diff)

### Title
`FIX: supplier proposal created from REST API loses its lines / fatal error on stdClass::getPriceBaseType()`

### Description
Upstream PR [#41005](https://github.com/Dolibarr/dolibarr/pull/41005) fixed customer proposals (`propal.class.php`) by replacing:
```php
if (!is_object($this->lines[$i])) {
```
with:
```php
if (!($this->lines[$i] instanceof PropaleLigne)) {
```
However, the exact identical defect was left unpatched in `supplier_proposal.class.php` (lines 1097-1113).

When a supplier proposal containing lines is submitted via the REST API (`POST /api/index.php/supplierproposals`), PHP's `json_decode()` deserializes line arrays into generic `stdClass` instances.
Because `is_object(stdClass)` evaluates to `true`, the loop skips instantiating the domain entity `SupplierProposalLine`. Subsequent operations attempting to call methods on the line trigger an unhandled fatal crash:
```text
PHP Fatal error: Uncaught Error: Call to undefined method stdClass::getPriceBaseType() 
in /var/www/html/comm/propal/class/supplier_proposal.class.php:1112
```

### How to Reproduce
Run the verified oracle script:
```bash
docker exec dolibench-doli-1 php /var/www/html/test_supplier_proposal_stdclass.php
# Output before patch:
# PHP Fatal error: Call to undefined method stdClass::getPriceBaseType()
```

### Proposed Resolution
```diff
--- a/htdocs/comm/propal/class/supplier_proposal.class.php
+++ b/htdocs/comm/propal/class/supplier_proposal.class.php
@@ -1098,2 +1098,2 @@
-				if (!is_object($this->lines[$i])) {
+				if (!($this->lines[$i] instanceof SupplierProposalLine)) {
```
Applying this fix ensures incoming REST data is safely hydrated into `SupplierProposalLine`, passing all oracles with 100% compliance.
