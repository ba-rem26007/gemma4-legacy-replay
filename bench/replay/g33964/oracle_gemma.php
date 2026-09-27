<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #33964, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // Setup context
    Context::getContext()->shop = new Shop(1);
    Context::getContext()->language = new Language(1);
    Context::getContext()->currency = new Currency(1);

    // To trigger the bug, we need Product::getPrice() to return more decimals than the rounding precision.
    // 1. Set currency precision to 3 so getPrice() returns 3 decimals.
    Db::getInstance()->execute('UPDATE `' . _DB_PREFIX_ . 'currency` SET `precision` = 3 WHERE `id_currency` = 1');
    
    // 2. Set computing precision to 2 so the rounding logic (ROUND_ITEM) should round to 2 decimals.
    Configuration::updateValue('PS_PRICE_COMPUTING_PRECISION', 2);
    
    // 3. Set rounding type to ROUND_ITEM (Value 2)
    Configuration::updateValue('PS_ROUND_TYPE', Order::ROUND_ITEM);

    // Product 1: Price 22.944. 
    // With currency precision 3, getPrice() returns 22.944.
    // With ROUND_ITEM and computing precision 2, it should be rounded to 22.94.
    $p1 = new Product(1);
    $p1->price = 22.944;
    $p1->id_tax_rules_group = 0; 
    $p1->save();

    // Product 4: Price 15.48
    $p4 = new Product(4);
    $p4->price = 15.48;
    $p4->id_tax_rules_group = 0;
    $p4->save();

    // Product 19: The Pack
    $pPack = new Product(19);
    $pPack->price = 0;
    $pPack->save();

    // Clear pack cache and add items
    Pack::resetStaticCache();
    Pack::deleteItems(19);
    Pack::addItem(19, 1, 10, 0); // 10 units of Product 1
    Pack::addItem(19, 4, 1, 0);  // 1 unit of Product 4

    /**
     * Calculation:
     * Fixed (ROUND_ITEM): (round(22.944, 2) * 10) + (round(15.48, 2) * 1) 
     *                   = (22.94 * 10) + 15.48 = 229.40 + 15.48 = 244.88
     * 
     * Buggy (Before): (22.944 * 10) + (15.48 * 1) 
     *                = 229.44 + 15.48 = 244.92
     */

    $observedSum = Pack::noPackPrice(19);
    $expectedSum = 244.88;

    echo "Currency Precision: 3\n";
    echo "Computing Precision: 2\n";
    echo "Rounding Type: " . Configuration::get('PS_ROUND_TYPE') . "\n";
    echo "Observed Sum: $observedSum\n";
    echo "Expected Sum: $expectedSum\n";

    if (abs($observedSum - $expectedSum) < 0.0001) {
        exit(0);
    } else {
        echo "Bug detected: The sum is not rounded per item according to computing precision.\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "Fatal Error: " . $t->getMessage() . "\n";
    exit(1);
}
