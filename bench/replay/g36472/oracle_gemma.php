<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36472, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // 1. Setup Global Context
    $context = Context::getContext();
    $context->shop = new Shop(1);
    $context->language = new Language(1);
    $context->currency = new Currency(1);
    $context->customer = new Customer(1);
    $context->link = new Link();

    // 2. Setup Data
    $id_product = 1;
    $product = new Product($id_product, false, 1);
    if (!Validate::isLoadedObject($product)) {
        echo "Product 1 not found\n";
        exit(1);
    }

    // Create a cart and add the product with a specific quantity
    $cart = new Cart();
    $cart->id_currency = 1;
    $cart->id_lang = 1;
    $cart->id_customer = $context->customer->id;
    $cart->add();
    
    $quantity_in_cart = 5;
    $cart->updateQty($quantity_in_cart, $id_product);
    
    // Assign cart to the global context so ProductController can find it via $this->context
    $context->cart = $cart;

    // 3. Simulate Request for ProductController
    // ProductController::getProduct() relies on $_GET['id_product']
    $_GET['id_product'] = (string)$id_product;

    // 4. Instantiate ProductController
    // The constructor of FrontController (parent) initializes $this->context = Context::getContext();
    $controller = new ProductController();

    // Populate $this->product inside the controller
    $controller->getProduct();

    // 5. Execute the target method
    $product_vars = $controller->getTemplateVarProduct();

    $observed_qty = isset($product_vars['cart_quantity']) ? (int)$product_vars['cart_quantity'] : -1;

    echo "Expected cart_quantity: $quantity_in_cart\n";
    echo "Observed cart_quantity: $observed_qty\n";

    // The bug: $product['id_product'] is used instead of $this->product->id.
    // In the array returned by Product::getProductProperties, the key is 'id', not 'id_product'.
    // Thus, $product['id_product'] is null, and getProductQuantity(null, ...) returns 0.
    if ($observed_qty === $quantity_in_cart) {
        exit(0);
    } else {
        echo "Bug detected: cart_quantity is $observed_qty instead of $quantity_in_cart\n";
        exit(1);
    }

} catch (\Throwable $e) {
    echo "Error: " . $e->getMessage() . "\n";
    exit(1);
}
