<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36505, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShopBundle\Model\Product\AdminModelAdapter;
use PrestaShop\PrestaShopBundle\Model\Product\RedirectType;

// Setup context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// Ensure products exist for the test
$p1 = new Product(1);
$p2 = new Product(2);

// We use Reflection to instantiate AdminModelAdapter without its complex constructor
// as we only need to test the logic inside getModelData.
$reflection = new ReflectionClass(AdminModelAdapter::class);
$adapter = $reflection->newInstanceWithoutConstructor();

// Initialize required properties used in getModelData
$adapter->translatableKeys = [];

// Prepare form data as it would be sent from the Back Office
// The bug occurs when id_type_redirected is a simple numeric ID instead of an array ['data' => [id]]
$formData = [
    'id_product' => 1,
    'step1' => [
        'type_product' => 1, // Standard product
    ],
    'step2' => [],
    'step3' => [],
    'step4' => [],
    'step5' => [],
    'step6' => [
        'redirect_type' => RedirectType::TYPE_PRODUCT_PERMANENT,
        'id_type_redirected' => 2, // Redirect to product 2
    ],
];

echo "Testing Product Redirection storage logic...\n";
echo "Input redirect_type: " . RedirectType::TYPE_PRODUCT_PERMANENT . "\n";
echo "Input id_type_redirected: 2\n";

try {
    $result = $adapter->getModelData($formData);
    $observedRedirectType = $result['redirect_type'];
    echo "Observed redirect_type after getModelData: $observedRedirectType\n";

    // The bug: before the fix, it falls back to TYPE_CATEGORY_PERMANENT 
    // because it expects id_type_redirected to be an array.
    if ($observedRedirectType === RedirectType::TYPE_PRODUCT_PERMANENT) {
        echo "SUCCESS: Redirect type preserved.\n";
        exit(0);
    } else {
        echo "FAILURE: Redirect type was changed to " . $observedRedirectType . "\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "ERROR: " . $t->getMessage() . "\n";
    exit(1);
}
