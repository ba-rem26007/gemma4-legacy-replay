<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35372, validé pre/post automatiquement
require 'config/config.inc.php';

// Context setup
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->currency = new Currency(1);

try {
    // 1. Setup Products
    // Product 1 & 2: Standard products with stock
    $p1 = new Product(1);
    $p1->price = 10.0;
    $p1->available_for_order = 1;
    $p1->allow_oosp = 0; 
    $p1->save();
    StockAvailable::setQuantity(1, 0, 100);

    $p2 = new Product(2);
    $p2->price = 10.0;
    $p2->available_for_order = 1;
    $p2->allow_oosp = 0;
    $p2->save();
    StockAvailable::setQuantity(2, 0, 100);

    // Product 3: The Pack
    $p3 = new Product(3);
    $p3->price = 15.0;
    $p3->available_for_order = 1;
    $p3->allow_oosp = 0; // Trigger: if stock is 0 and allow_oosp is 0, it should fail without the fix
    $p3->save();
    // Set pack's own stock to 0 in stock_available
    StockAvailable::setQuantity(3, 0, 0);

    // 2. Create Pack relationship in DB
    // We avoid manual DELETE with column names to prevent SQL errors if schema differs slightly
    // The base is reset before each execution anyway.
    Db::getInstance()->insert('pack', [
        'id_product' => 3,
        'id_product_component' => 1,
        'quantity' => 1,
    ]);
    Db::getInstance()->insert('pack', [
        'id_product' => 3,
        'id_product_component' => 2,
        'quantity' => 1,
    ]);

    // 3. Create Cart and add the pack
    $cart = new Cart();
    $cart->id_currency = 1;
    $cart->id_lang = 1;
    $cart->add();

    echo "Adding pack (Product 3) to cart...\n";
    // updateQty will call checkQuantities internally or we check it after
    $cart->updateQty(1, 3);

    // 4. Verify availability
    // Before fix: checkQuantities() returns false because Product 3 has 0 stock and allow_oosp = 0
    // After fix: the stock check is removed/modified for packs in Cart::checkQuantities
    $isValid = $cart->checkQuantities();
    
    // Verify Product::getQuantity (used in CartController to show error messages)
    // It should now return the quantity based on components for packs
    $availableQty = Product::getQuantity(3);
    
    echo "Pack stock in stock_available: 0\n";
    echo "Components stock: 100\n";
    echo "Product::getQuantity(3) returns: $availableQty\n";
    echo "Cart::checkQuantities() returns: " . ($isValid ? 'TRUE' : 'FALSE') . "\n";

    if (!$isValid) {
        echo "FAIL: Pack with 0 stock but available components was blocked by checkQuantities.\n";
        exit(1);
    }

    if ($availableQty <= 0) {
        echo "FAIL: Product::getQuantity did not calculate pack components stock.\n";
        exit(1);
    }

    echo "SUCCESS: Pack is addable and quantity is correctly calculated.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "ERROR: " . $t->getMessage() . "\n";
    exit(1);
}
