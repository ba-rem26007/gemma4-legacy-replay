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

// We simulate a product row as returned by the database.
// To trigger the bug, we omit the 'id_manufacturer' key.
// The old code does: (int) $row['id_manufacturer'] > 0, which triggers a Notice: Undefined index.
// The fixed code does: !empty($row['id_manufacturer']), which does not trigger a notice.
$row = [
    'id_product' => 1,
    'id_category_default' => 2,
    'link_rewrite' => 'product-1',
    'ean13' => '123456789',
];

// In debug mode, PHP notices can break JSON responses. 
// We use a custom error handler to catch the notice and treat it as a failure.
set_error_handler(function($errno, $errstr) {
    throw new Exception($errstr);
});

try {
    // Call the method touched by the fix
    Product::getProductProperties($id_lang, $row, $context);
    
    restore_error_handler();
    echo "Success: No notice triggered. The bug is fixed.\n";
    exit(0);
} catch (\Throwable $t) {
    restore_error_handler();
    echo "Failure: Notice triggered: " . $t->getMessage() . "\n";
    exit(1);
}
