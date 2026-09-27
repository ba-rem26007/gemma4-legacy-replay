<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #33930, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->currency = new Currency(1);

try {
    // 1. Setup Product
    $p = new Product(1);
    $p->price = 10.0; // Base price in EUR
    $p->update();

    // 2. Setup Currency (CZK)
    $c2 = new Currency();
    $c2->iso_code = 'CZK';
    $c2->numeric_iso_code = '208';
    $c2->conversion_rate = 25.0; // 1 EUR = 25 CZK
    $c2->add();
    $id_currency_czk = (int)$c2->id;

    // 3. Setup Specific Price for CZK
    // We want a fixed price of 200.0 CZK for this product.
    $sp = new SpecificPrice();
    $sp->id_product = 1;
    $sp->id_shop = 1;
    $sp->id_shop_group = 1;
    $sp->id_currency = $id_currency_czk;
    $sp->id_country = 1;
    $sp->id_group = 1;
    $sp->id_customer = 0;
    $sp->id_product_attribute = 0;
    $sp->price = 200.0; // This should be the final price in CZK
    $sp->from_quantity = 1;
    $sp->reduction = 0;
    $sp->reduction_tax = 1;
    $sp->reduction_type = 'amount';
    $sp->from = '2020-01-01 00:00:00';
    $sp->to = '2030-01-01 00:00:00';
    $sp->add();

    Product::resetStaticCache();

    // 4. Execute price calculation for the target currency (CZK)
    // Parameters: id_shop, id_product, id_product_attribute, id_country, id_state, zipcode, id_currency, id_group, quantity, usetax, decimals
    $calculatedPrice = Product::priceCalculation(
        1, 
        1, 
        0, 
        1, 
        0, 
        '00000', 
        $id_currency_czk, 
        1, 
        1, 
        false, 
        2
    );

    echo "Base Price: 10.0 EUR\n";
    echo "Target Currency Rate: 25.0\n";
    echo "Specific Price set for CZK: 200.0\n";
    echo "Calculated Price: $calculatedPrice\n";

    /**
     * BUG ANALYSIS:
     * Before fix: The code sees the specific price is for currency 2, but because 
     * $id_currency !== $specific_price['id_currency'] is FALSE, it enters the 
     * Tools::convertPrice block.
     * It converts 200.0 (the specific price) using the rate 25.0 -> 5000.0.
     * 
     * After fix: It recognizes that the specific price is already in the target 
     * currency and does NOT call Tools::convertPrice.
     * Result: 200.0.
     */
    if (abs($calculatedPrice - 200.0) < 0.0001) {
        exit(0);
    } else {
        echo "Error: Price was converted incorrectly. Expected 200.0, got $calculatedPrice\n";
        exit(1);
    }

} catch (\Throwable $e) {
    echo "Exception: " . $e->getMessage() . "\n";
    exit(1);
}
