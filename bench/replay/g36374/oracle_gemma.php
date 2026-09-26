<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36374, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Core\Context\ContextStateManagerInterface;
use PrestaShop\PrestaShop\Adapter\Order\OrderDetailUpdater;

/**
 * Mock for ContextStateManager since we are in CLI and cannot use the Symfony container.
 */
class MockContextStateManager implements ContextStateManagerInterface
{
    public function saveCurrentContext()
    {
        // No-op
    }
    public function restorePreviousContext()
    {
        // No-op
    }
}

try {
    // Setup Context
    Context::getContext()->shop = new Shop(1);
    Context::getContext()->language = new Language(1);
    Context::getContext()->currency = new Currency(1);

    // Ensure Product 1 has a tax rule group to trigger tax calculation
    $product = new Product(1);
    $product->id_tax_rules_group = 1; 
    $product->save();

    // Use existing Order 1 from demo data
    $order = new Order(1);
    if (!Validate::isLoadedObject($order)) {
        echo "Order 1 not found in demo data\n";
        exit(1);
    }

    // Ensure the order has a delivery address for the tax calculator
    $order->id_address_delivery = 1;
    $order->update();

    // Get an OrderDetail associated with this order
    $products = $order->getProducts();
    if (empty($products)) {
        echo "Order 1 has no products\n";
        exit(1);
    }
    $orderDetail = new OrderDetail((int)$products[0]['id_order_detail']);
    
    // Set a known base price to make calculations predictable
    $basePriceExcl = 10.00;
    $qty = 1;
    $orderDetail->unit_price_tax_excl = $basePriceExcl;
    $orderDetail->total_price_tax_excl = $basePriceExcl * $qty;
    $orderDetail->product_quantity = $qty;
    $orderDetail->update();

    // Calculate expected tax based on PrestaShop's tax rules for this product/address
    $taxRate = Tax::getProductTaxRate(1, 1); // product 1, address 1
    $expectedTaxAmount = $basePriceExcl * ($taxRate / 100);
    $expectedTotalTaxIncl = $basePriceExcl + $expectedTaxAmount;

    echo "Base Price Excl: $basePriceExcl\n";
    echo "Tax Rate: $taxRate%\n";
    echo "Expected Total Tax Incl: $expectedTotalTaxIncl\n";

    // Instantiate the updater directly with its dependency
    $updater = new OrderDetailUpdater(new MockContextStateManager());
    
    // Trigger the bug: update taxes for the order
    $updater->updateOrderDetailsTaxes($order);

    // Reload OrderDetail to check the value saved in DB
    $orderDetail = new OrderDetail($orderDetail->id);
    $observedTotalTaxIncl = (float)$orderDetail->total_price_tax_incl;

    echo "Observed Total Tax Incl: $observedTotalTaxIncl\n";

    // The bug doubles the tax addition if it's added both inside and outside the loop.
    // If fixed, observed should be very close to expected.
    if (abs($observedTotalTaxIncl - $expectedTotalTaxIncl) < 0.01) {
        echo "SUCCESS: Price calculation is correct.\n";
        exit(0);
    } else {
        echo "FAILURE: Price calculation is incorrect (likely doubled tax).\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
}
