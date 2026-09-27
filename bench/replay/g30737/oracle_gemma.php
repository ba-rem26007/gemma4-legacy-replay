<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30737, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test for BO Monitoring page: Exception when enabling a product with empty name.
 * The fix adds a mapping for ProductConstraintException::INVALID_ONLINE_DATA 
 * in ProductController::getErrorMessages().
 */

// Context setup
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);

// 1. Setup: Use existing product 1, make it disabled and give it an empty name
// In PrestaShop legacy Product class, name is handled as an array indexed by language ID
$p = new Product(1);
$p->active = 0;
$p->name = [1 => '']; 
$p->save();

echo "Product 1 set to disabled with empty name for language 1.\n";

try {
    // We instantiate the ProductController. 
    // Since it's a Symfony controller, we don't need the container just to call a private method via reflection.
    $controller = new \PrestaShopBundle\Controller\Admin\ProductController();

    // getErrorMessages is a private method, we use Reflection to access it.
    $reflection = new \ReflectionClass(\PrestaShopBundle\Controller\Admin\ProductController::class);
    $method = $reflection->getMethod('getErrorMessages');
    $method->setAccessible(true);
    
    $messages = $method->invoke($controller);

    $exceptionClass = \PrestaShop\PrestaShop\Core\Domain\Product\Exception\ProductConstraintException::class;
    $errorCode = \PrestaShop\PrestaShop\Core\Domain\Product\Exception\ProductConstraintException::INVALID_ONLINE_DATA;

    echo "Checking for exception mapping: $exceptionClass with code $errorCode\n";

    if (!isset($messages[$exceptionClass])) {
        echo "FAIL: ProductConstraintException class mapping is missing in getErrorMessages().\n";
        exit(1);
    }

    if (!isset($messages[$exceptionClass][$errorCode])) {
        echo "FAIL: INVALID_ONLINE_DATA error code mapping is missing for ProductConstraintException.\n";
        exit(1);
    }

    echo "SUCCESS: The error mapping is correctly defined. The exception will be handled with a user-friendly message.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "An unexpected error occurred: " . $t->getMessage() . "\n";
    exit(1);
}
