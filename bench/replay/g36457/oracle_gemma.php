<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36457, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Product\AdminProductWrapper;

try {
    // 1. Setup Languages
    $lang1 = new Language(1);
    $lang2 = new Language(2);
    if (!Validate::isLoadedObject($lang2)) {
        $lang2 = new Language();
        $lang2->name = 'Test Language';
        $lang2->iso_code = 'TL';
        $lang2->add();
    }
    $lang2_id = (int)$lang2->id;

    // 2. Setup Attribute Group and Attribute
    $ag = new AttributeGroup();
    $ag->name = [1 => 'Color', $lang2_id => 'Couleur'];
    $ag->public_name = [1 => 'Color', $lang2_id => 'Couleur'];
    $ag->group_type = 'select';
    $ag->add();

    $attr = new Attribute();
    $attr->id_attribute_group = (int)$ag->id;
    $attr->name = [1 => 'Red', $lang2_id => 'Rouge'];
    $attr->add();

    // 3. Setup Product and Combination
    $product = new Product(1);
    $comb = new Combination();
    $comb->id_product = (int)$product->id;
    $comb->minimal_quantity = 1;
    $comb->add();
    $comb->setAttributes([(int)$attr->id]);

    // 4. Setup Specific Price for this combination
    $sp = new SpecificPrice();
    $sp->id_product = (int)$product->id;
    $sp->id_product_attribute = (int)$comb->id;
    $sp->id_shop = 1;
    $sp->id_shop_group = 1;
    $sp->id_currency = 1;
    $sp->id_country = 1;
    $sp->id_group = 1;
    $sp->id_customer = 0;
    $sp->from_quantity = 1;
    $sp->price = 10.00;
    $sp->reduction = 0;
    $sp->reduction_type = 'amount';
    $sp->from = date('Y-m-d H:i:s');
    $sp->to = date('Y-m-d H:i:s', strtotime('+1 year'));
    $sp->add();

    // 5. Set Context to Language 2
    Context::getContext()->language = $lang2;
    Context::getContext()->shop = new Shop(1);

    // 6. Call the Wrapper method
    $defaultCurrency = new Currency(1);
    $shops = [['id_shop' => 1]];
    $currencies = [['id_currency' => 1]];
    $countries = [['id_country' => 1]];
    $groups = [['id_group' => 1]];

    $wrapper = new AdminProductWrapper();
    $list = $wrapper->getSpecificPricesList($product, $defaultCurrency, $shops, $currencies, $countries, $groups);

    // 7. Verify the attribute name is in Language 2
    $found_name = '';
    $found = false;
    foreach ($list as $item) {
        if ((int)$item['id_product_attribute'] === (int)$comb->id) {
            $found_name = $item['attributes_name'];
            $found = true;
            break;
        }
    }

    echo "Language ID: $lang2_id\n";
    echo "Expected name: Rouge\n";
    echo "Observed name: $found_name\n";

    if (!$found) {
        echo "Specific price not found in list.\n";
        exit(1);
    }

    // The wrapper appends ' - ' to the name
    if (strpos($found_name, 'Rouge') !== false) {
        exit(0); // Corrected
    } else {
        echo "Bug: Attribute name is not in the current language (probably hardcoded to ID 1).\n";
        exit(1); // Still bugged
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
