<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36074, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // 1. Setup Context
    Context::getContext()->shop = new Shop(1);
    Context::getContext()->language = new Language(1);
    Context::getContext()->currency = new Currency(1);

    // 2. Create Zones and Countries
    // Zone 1: Europe, Zone 2: South America
    $zone1 = new Zone();
    $zone1->name = array(1 => 'Europe');
    $zone1->add();
    $id_zone1 = $zone1->id;

    $zone2 = new Zone();
    $zone2->name = array(1 => 'South America');
    $zone2->add();
    $id_zone2 = $zone2->id;

    $country1 = new Country();
    $country1->id_zone = $id_zone1;
    $country1->iso_code = 'FR';
    $country1->contains_states = 0;
    $country1->need_identification_number = 0;
    $country1->display_tax_label = 1;
    $country1->name = array(1 => 'France');
    $country1->active = 1;
    $country1->add();
    $id_country1 = $country1->id;

    $country2 = new Country();
    $country2->id_zone = $id_zone2;
    $country2->iso_code = 'BR';
    $country2->contains_states = 0;
    $country2->need_identification_number = 0;
    $country2->display_tax_label = 1;
    $country2->name = array(1 => 'Brazil');
    $country2->active = 1;
    $country2->add();
    $id_country2 = $country2->id;

    // 3. Create Carriers
    // Carrier 1: Only for Zone 1
    $carrier1 = new Carrier();
    $carrier1->id_reference = 100;
    $carrier1->name = array(1 => 'Carrier Europe');
    $carrier1->active = 1;
    $carrier1->shipping_handling = 1;
    $carrier1->add();
    $id_carrier1 = $carrier1->id;

    // Carrier 2: Only for Zone 2
    $carrier2 = new Carrier();
    $carrier2->id_reference = 101;
    $carrier2->name = array(1 => 'Carrier South America');
    $carrier2->active = 1;
    $carrier2->shipping_handling = 1;
    $carrier2->add();
    $id_carrier2 = $carrier2->id;

    // Define coverage in ps_delivery
    Db::getInstance()->insert('delivery', [
        'id_carrier' => (int)$id_carrier1,
        'id_zone' => (int)$id_zone1,
        'price' => 5.00
    ]);
    Db::getInstance()->insert('delivery', [
        'id_carrier' => (int)$id_carrier2,
        'id_zone' => (int)$id_zone2,
        'price' => 5.00
    ]);

    // 4. Setup Products and Restrictions
    // Product 1 restricted to Carrier 1
    $p1 = new Product(1);
    $p1->price = 10.00;
    $p1->save();
    Db::getInstance()->delete('product_carrier', 'id_product = ' . (int)$p1->id);
    Db::getInstance()->insert('product_carrier', [
        'id_product' => (int)$p1->id,
        'id_carrier' => (int)$id_carrier1
    ]);

    // Product 2 restricted to Carrier 2
    $p2 = new Product(2);
    $p2->price = 10.00;
    $p2->save();
    Db::getInstance()->delete('product_carrier', 'id_product = ' . (int)$p2->id);
    Db::getInstance()->insert('product_carrier', [
        'id_product' => (int)$p2->id,
        'id_carrier' => (int)$id_carrier2
    ]);

    // 5. Setup Customer and Address in Zone 1 (France)
    $customer = new Customer(1);
    $address = new Address();
    $address->id_customer = $customer->id;
    $address->id_country = $id_country1;
    $address->alias = 'Home';
    $address->firstname = 'John';
    $address->lastname = 'Doe';
    $address->address1 = '123 Street';
    $address->city = 'Paris';
    $address->add();

    // 6. Create Cart and add both products
    $cart = new Cart();
    $cart->id_currency = 1;
    $cart->id_lang = 1;
    $cart->id_address_delivery = $address->id;
    $cart->add();
    $cart->updateQty(1, 1); // Product 1 (shippable to Zone 1)
    $cart->updateQty(2, 1); // Product 2 (NOT shippable to Zone 1)
    $cart->update();

    // 7. Test getDeliveryOptionList
    // Because Product 2 is restricted to Carrier 2, and Carrier 2 does not cover Zone 1,
    // getPackageList() will create two packages. One will have no available carrier.
    // The fix should detect this and return an empty list.
    $options = $cart->getDeliveryOptionList();

    echo "Number of delivery options found: " . count($options) . "\n";

    // If the bug is present, it might return options for the first package.
    // If fixed, it must return an empty array because one package is unshippable.
    exit(empty($options) ? 0 : 1);

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
