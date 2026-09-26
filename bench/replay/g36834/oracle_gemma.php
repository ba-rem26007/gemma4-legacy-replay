<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36834, validé pre/post automatiquement
require 'config/config.inc.php';

// Context setup
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->currency = new Currency(1);

// Demo data
$id_product = 1;
$id_product_attribute = 0;
$id_address_delivery = 0;
$id_customization = 100;
$product_price = 10.00;
$customization_price = 5.00;
$quantity = 1;

// We need a product to exist for Price::priceWithTax and other internal calls
$product = new Product($id_product);
if (!Validate::isLoadedObject($product)) {
    $product = new Product();
    $product->id = $id_product;
    $product->price = $product_price;
    $product->id_tax_rules_group = 0; // No tax for simplicity
    $product->add();
}

// Prepare the $products array as it would be passed to addCustomizationPrice
// In the buggy version, the 'unit_price_tax_excl' here is the base product price
$products = [
    [
        'id_product' => $id_product,
        'id_product_attribute' => $id_product_attribute,
        'unit_price_tax_excl' => $product_price,
        'unit_price_tax_incl' => $product_price,
        'quantity' => $quantity,
        'total' => $product_price * $quantity,
        'total_wt' => $product_price * $quantity,
    ]
];

// Prepare the $customized_datas array as returned by Product::getCustomizedDatas
$customized_datas = [
    (int)$id_product => [
        (int)$id_product_attribute => [
            (int)$id_address_delivery => [
                (int)$id_customization => [
                    'quantity' => $quantity,
                    'datas' => [
                        1 => [ // type 1: text
                            [
                                'id_customization' => $id_customization,
                                'price' => $customization_price,
                                'value' => 'Custom Value'
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ]
];

try {
    // Call the method touched by the fix
    Product::addCustomizationPrice($products, $customized_datas);

    $observed_total_custom = $products[0]['total_customization'];
    $observed_total_custom_wt = $products[0]['total_customization_wt'];

    echo "Product Price: $product_price\n";
    echo "Customization Price: $customization_price\n";
    echo "Observed total_customization: $observed_total_custom\n";
    echo "Observed total_customization_wt: $observed_total_custom_wt\n";

    // The bug: total_customization was calculated using the product base price ($product_price)
    // instead of the customization price ($customization_price).
    // Correct: total_customization = 5.00 * 1 = 5.00
    // Buggy: total_customization = 10.00 * 1 = 10.00
    if (abs($observed_total_custom - $customization_price) < 0.0001) {
        exit(0); // Fixed
    } else {
        echo "Error: total_customization is $observed_total_custom, expected $customization_price\n";
        exit(1); // Bug still present
    }
} catch (\Throwable $t) {
    echo "Exception: " . $t->getMessage() . "\n";
    exit(1);
}
