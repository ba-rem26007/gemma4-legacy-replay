<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30273, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test for Ticket: Error in cart - removing products in debug mode and specific language doesn't work
 * The bug is caused by a PHP Notice when 'id_manufacturer' is missing from the product row array
 * in Product::getProductProperties(). In debug mode, this notice corrupts AJAX responses.
 */

$context = Context::getContext();
$context->shop = new Shop(1);
$context->link = new Link();
$context->language = new Language(1);
$context->currency = new Currency(1);

$id_lang = 1;
$id_product = 1;

// To avoid "Undefined array key" notices for other fields (like 'out_of_stock'),
// we fetch a real product row from the database and then specifically remove 'id_manufacturer'.
$sql = 'SELECT p.*, pl.link_rewrite, pl.name, stock.out_of_stock 
        FROM ' . _DB_PREFIX_ . 'product p 
        LEFT JOIN ' . _DB_PREFIX_ . 'product_lang pl ON (p.id_product = pl.id_product AND pl.id_lang = ' . (int)$id_lang . ')
        LEFT JOIN ' . _DB_PREFIX_ . 'stock stock ON (p.id_product = stock.id_product)
        WHERE p.id_product = ' . (int)$id_product;

$row = Db::getInstance()->getRow($sql);

if (!$row) {
    echo "Error: Demo product 1 not found in database.\n";
    exit(1);
}

// Trigger the bug: remove the key that the old code accesses without checking existence
unset($row['id_manufacturer']);

// In debug mode, PHP notices can break JSON responses. 
// We use a custom error handler to catch the notice and treat it as a failure.
set_error_handler(function($errno, $errstr) {
    throw new Exception($errstr);
});

try {
    // Call the method touched by the fix
    Product::getProductProperties($id_lang, $row, $context);
    
    restore_error_handler();
    echo "Success: No notice triggered for missing id_manufacturer. The bug is fixed.\n";
    exit(0);
} catch (\Throwable $t) {
    restore_error_handler();
    echo "Failure: Notice triggered: " . $t->getMessage() . "\n";
    exit(1);
}
