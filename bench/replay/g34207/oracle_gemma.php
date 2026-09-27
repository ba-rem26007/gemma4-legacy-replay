<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34207, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);
$context->customer = new Customer(1);

// Ensure products exist and have limited stock
$p1 = new Product(1, false, 1);
$p2 = new Product(2, false, 1);
StockAvailable::setQuantity(1, 0, 10);
StockAvailable::setQuantity(2, 0, 10);

// Create a cart and add Product 1 with a quantity exceeding stock
$cart = new Cart();
$cart->id_currency = 1;
$cart->id_lang = 1;
$cart->id_customer = 1;
$cart->add();
$cart->updateQty(1, 9999, 0); // Product 1, Qty 9999, Attribute 0

// Simulate "Add to Cart" request for Product 2 (which is in stock)
$_POST['add'] = 1;
$_POST['id_product'] = 2;
$_POST['qty'] = 1;
$_POST['token'] = 'test_token';

// Instantiate CartController
$controller = new CartController();
$controller->context = $context;
$controller->context->cart = $cart;

// Manually set properties that init() would normally set from Tools::getValue
// to avoid potential fatal errors in FrontController::init() in CLI
$controller->id_product = 2;
$controller->qty = 1;
$controller->ErrorKey = 'errors';

try {
    // postProcess() calls updateCart() -> processChangeProductInCart()
    $controller->postProcess();
} catch (\Throwable $e) {
    echo "Exception caught: " . $e->getMessage() . "\n";
    exit(1);
}

$errors = $controller->errors;
$errorCount = count($errors);

echo "Product 1 qty in cart: 9999 (Stock: 10)\n";
echo "Attempting to add Product 2 qty: 1 (Stock: 10)\n";
echo "Errors observed: $errorCount\n";

if ($errorCount > 0) {
    foreach ($errors as $error) {
        echo "Error: $error\n";
    }
}

/**
 * BUG: Before the fix, areProductsAvailable() is called even during 'add' mode.
 * It detects that Product 1 is over stock and adds an error to the response,
 * preventing the successful addition of Product 2.
 * 
 * FIX: areProductsAvailable() is only called if mode !== 'add'.
 * Therefore, adding Product 2 should not trigger errors related to Product 1.
 */
exit($errorCount === 0 ? 0 : 1);
