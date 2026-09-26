<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37955, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test for Ticket: PrestaShop don't display Title of product, category meta title, meta description
 * when shop is under maintenance mode but admin is allowed to see FO.
 */

// 1. Setup environment to trigger the bug
// Shop is disabled (Maintenance mode)
Configuration::updateValue('PS_SHOP_ENABLE', 0);
// Admins are allowed to bypass maintenance
Configuration::updateValue('PS_MAINTENANCE_ALLOW_ADMINS', 1);
// Set a dummy IP whitelist that does NOT include the current runner's IP to ensure we test the Admin bypass
Configuration::updateValue('PS_MAINTENANCE_IP', '1.1.1.1');

// 2. Simulate an Admin session
// Tools::isAllowedToBypassMaintenance() instantiates 'new Cookie('psAdmin')'.
// To make this work in CLI, we must create a Cookie object, set the id_employee, 
// and call save(). save() will encrypt the value and store it in $_COOKIE, 
// which the subsequent 'new Cookie('psAdmin')' call inside Tools will be able to decrypt.
$adminCookie = new Cookie('psAdmin');
$adminCookie->id_employee = 1;
$adminCookie->save();

// 3. Simulate a request for a specific product
$idProduct = 1;
$idLang = 1;
$_GET['id_product'] = $idProduct;

// Ensure product 1 exists (demo data)
$product = new Product($idProduct, false, $idLang);
if (!Validate::isLoadedObject($product)) {
    echo "Product 1 not found in demo data.\n";
    exit(1);
}

echo "Shop status: Maintenance mode (PS_SHOP_ENABLE=0)\n";
echo "Admin bypass: Enabled (PS_MAINTENANCE_ALLOW_ADMINS=1)\n";
echo "Simulated User: Employee 1 (via encrypted Cookie)\n";
echo "Target Page: Product $idProduct\n";

try {
    // Call the method touched by the fix.
    // Before the fix, this would return Home metas because it only checked PS_SHOP_ENABLE and IP.
    // After the fix, it calls Tools::isAllowedToBypassMaintenance(), which detects the admin cookie.
    $observedMetas = Meta::getMetaTags($idLang, 'product');
    
    // Get what the metas SHOULD be (Product metas)
    $expectedMetas = Meta::getProductMetas($idProduct, $idLang, 'product');

    echo "Observed Meta Title: " . ($observedMetas['meta_title'] ?? 'NULL') . "\n";
    echo "Expected Meta Title: " . ($expectedMetas['meta_title'] ?? 'NULL') . "\n";

    if ($observedMetas === $expectedMetas) {
        echo "SUCCESS: Meta tags are correctly retrieved for admin in maintenance mode.\n";
        exit(0);
    } else {
        echo "FAILURE: Meta tags were not retrieved (likely fell back to Home metas).\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "ERROR: An exception occurred: " . $t->getMessage() . "\n";
    exit(1);
}
