<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35530, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// Use existing demo data: Order 1 and Customer 2
$order = new Order(1);
if (!Validate::isLoadedObject($order)) {
    echo "Order 1 not found in demo data\n";
    exit(1);
}

// Ensure the order has an invoice and is in a state that allows it
$order->invoice_number = 'INV-123';
$order->current_state = 2; // Payment accepted
$order->update();

// Simulate a different customer being logged in (Customer 2)
$customer_wrong = new Customer(2);
if (!Validate::isLoadedObject($customer_wrong)) {
    echo "Customer 2 not found in demo data\n";
    exit(1);
}
$context->customer = $customer_wrong;

// Set request parameters to trigger the bug
// We provide a valid secure_key for the order, but we are logged in as the wrong customer
$_GET['id_order'] = (int)$order->id;
$_GET['secure_key'] = $order->secure_key;

// Capture output to detect 'die()' calls
ob_start();
register_shutdown_function(function() {
    $output = ob_get_contents();
    if (strpos($output, 'The invoice was not found.') !== false) {
        echo "Observed: Access denied (The invoice was not found.)\n";
        exit(1);
    }
});

try {
    // Instantiate the controller directly
    // We use the Core class as defined in the diff
    require_once 'controllers/front/PdfInvoiceController.php';
    $controller = new PdfInvoiceControllerCore();
    $controller->context = $context;
    
    // Execute the logic touched by the fix
    $controller->postProcess();
    
    echo "Observed: Access granted\n";
    ob_end_clean();
    exit(0);
} catch (\Throwable $t) {
    echo "Exception: " . $t->getMessage() . "\n";
    exit(1);
}
