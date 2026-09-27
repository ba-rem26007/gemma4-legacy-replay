<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35439, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->currency = new Currency(1);

/**
 * Mock Smarty to avoid template loading errors in CLI
 */
class MockSmarty {
    public function assign($data) {
        if (is_array($data)) {
            return;
        }
    }
    public function fetch($template) {
        return '';
    }
}

try {
    // 1. Use existing demo data
    $id_order = 1;
    $id_customer = 1;
    $order = new Order($id_order);
    if (!Validate::isLoadedObject($order)) {
        echo "Order 1 not found\n";
        exit(1);
    }

    // 2. Create an OrderSlip that refunds ONLY delivery fees
    // amount = 0 triggers the 'else' block in HTMLTemplateOrderSlip::getContent()
    $os = new OrderSlip();
    $os->id_order = (int)$id_order;
    $os->id_customer = (int)$id_customer;
    $os->amount = 0.000000; 
    $os->shipping_cost = 1;
    $os->shipping_cost_amount = 10.000000;
    $os->partial = 1;
    $os->date_add = date('Y-m-d H:i:s');
    $os->date_upd = date('Y-m-d H:i:s');
    
    if (!$os->add()) {
        echo "Failed to create OrderSlip\n";
        exit(1);
    }

    // 3. Instantiate the PDF template
    $smarty = new MockSmarty();
    $pdf = new HTMLTemplateOrderSlip($os, $smarty);

    // 4. Execute the method containing the bug
    // Before fix: if amount == 0, $this->order->products is set to null
    // After fix: if amount == 0, $this->order->products is set to []
    $pdf->getContent();

    $products = $pdf->order->products;

    echo "Value of order->products: " . (is_null($products) ? 'NULL' : (is_array($products) ? 'ARRAY' : gettype($products))) . "\n";

    if (is_null($products)) {
        echo "Bug detected: order->products is NULL\n";
        exit(1);
    } elseif (is_array($products)) {
        echo "Fixed: order->products is an ARRAY\n";
        exit(0);
    } else {
        echo "Unexpected type: " . gettype($products) . "\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Exception caught: " . $t->getMessage() . "\n";
    exit(1);
}
