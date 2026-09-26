<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #38552, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Presenter\Order\OrderLazyArray;
use PrestaShop\PrestaShop\Adapter\Presenter\Cart\CartPresenter;
use PrestaShop\PrestaShop\Adapter\Presenter\Cart\CartLazyArray;
use PrestaShop\PrestaShop\Adapter\Presenter\PriceFormatter;

// --- Setup Context ---
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->currency = new Currency(1);

// --- Mock Classes with correct signatures ---
class MockCartPresenter extends CartPresenter
{
    public function present($cart, bool $shouldSeparateGifts = false): CartLazyArray
    {
        // We return a CartLazyArray containing two different customizations for the same product
        return new CartLazyArray([
            'products' => [
                [
                    'id_product' => 1,
                    'id_product_attribute' => 0,
                    'id_customization' => 10,
                    'attributes' => 'CustomAttr10',
                ],
                [
                    'id_product' => 1,
                    'id_product_attribute' => 0,
                    'id_customization' => 20,
                    'attributes' => 'CustomAttr20',
                ],
            ]
        ]);
    }
}

class MockPriceFormatter extends PriceFormatter
{
    public function format($price, $currency = null)
    {
        return (string)$price;
    }
}

try {
    // --- Data Setup ---
    // Use existing Product 1
    $p = new Product(1);
    
    // Create a Customer
    $c = new Customer();
    $c->firstname = 'Test';
    $c->lastname = 'User';
    $c->email = 'test@example.com';
    $c->passwd = 'password';
    $c->add();

    // Create a Cart
    $cart = new Cart();
    $cart->id_customer = $c->id;
    $cart->id_currency = 1;
    $cart->id_lang = 1;
    $cart->id_address_delivery = 1;
    $cart->id_address_invoice = 1;
    $cart->add();

    // Create an Order
    $order = new Order();
    $order->id_address_invoice = 1;
    $order->id_address_delivery = 1;
    $order->id_currency = 1;
    $order->id_lang = 1;
    $order->id_customer = $c->id;
    $order->id_carrier = 1;
    $order->payment = 'Check';
    $order->module = 'ps_checkpayment';
    $order->total_paid = 20;
    $order->total_paid_real = 20;
    $order->total_products = 20;
    $order->total_products_wt = 20;
    $order->conversion_rate = 1;
    $order->add();

    // Create two OrderDetails for the same product but different customizations
    // This ensures $order->getProducts() returns two distinct entries
    $od1 = new OrderDetail();
    $od1->id_order = $order->id;
    $od1->product_id = 1;
    $od1->product_attribute_id = 0;
    $od1->id_customization = 10;
    $od1->product_quantity = 1;
    $od1->product_name = 'Product 1 - Cust 10';
    $od1->product_price = 10;
    $od1->total_price = 10;
    $od1->add();

    $od2 = new OrderDetail();
    $od2->id_order = $order->id;
    $od2->product_id = 1;
    $od2->product_attribute_id = 0;
    $od2->id_customization = 20;
    $od2->product_quantity = 1;
    $od2->product_name = 'Product 1 - Cust 20';
    $od2->product_price = 10;
    $od2->total_price = 10;
    $od2->add();

    // --- Execution ---
    $mockPresenter = new MockCartPresenter();
    $mockFormatter = new MockPriceFormatter();
    
    $lazyArray = new OrderLazyArray($order, $mockPresenter, $mockFormatter);
    $products = $lazyArray->getProducts();

    echo "Order Product 0 attributes: " . ($products[0]['attributes'] ?? 'null') . "\n";
    echo "Order Product 1 attributes: " . ($products[1]['attributes'] ?? 'null') . "\n";

    // --- Validation ---
    // Before fix: $products[0] and $products[1] both match the first cart product (id_product 1)
    // and get 'CustomAttr10'.
    // After fix: $products[0] matches id_cust 10 ('CustomAttr10') and $products[1] matches id_cust 20 ('CustomAttr20').
    if (isset($products[0]['attributes']) && $products[0]['attributes'] === 'CustomAttr10' && 
        isset($products[1]['attributes']) && $products[1]['attributes'] === 'CustomAttr20') {
        echo "SUCCESS: Customizations are correctly matched.\n";
        exit(0);
    } else {
        echo "FAILURE: Customizations are not correctly matched.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
