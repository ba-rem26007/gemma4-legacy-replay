<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35322, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Presenter\Order\OrderDetailLazyArray;
use PrestaShop\PrestaShop\Adapter\Presenter\Locale;
use Symfony\Component\Translation\TranslatorInterface;

try {
    // Setup Context
    Context::getContext()->shop = new Shop(1);
    Context::getContext()->language = new Language(1);
    Context::getContext()->currency = new Currency(1);

    // Use existing Order 1 and modify it to trigger the bug
    $order = new Order(1);
    // tax_calculation_method = 0 usually means "Tax included" in the context of this bug's logic
    // In the old code: (!$order->getTaxCalculationMethod()) ? tax_excl : tax_incl
    // If method is 0, it incorrectly picked tax_excl.
    $order->tax_calculation_method = 0;
    $order->save();

    // Ensure there is a shipping cost associated with this order
    // We create/update an OrderCarrier to have distinct tax-excl and tax-incl prices
    $oc = new OrderCarrier();
    $oc->id_order = (int)$order->id;
    $oc->id_carrier = 1;
    $oc->shipping_cost = 10.00;    // Tax Excl
    $oc->total_shipping = 12.00;   // Tax Incl
    $oc->add();

    // Dependencies for OrderDetailLazyArray
    $lang = new Language(1);
    $curr = new Currency(1);
    $locale = new Locale($lang, $curr);
    
    // Mock TranslatorInterface to avoid Symfony container dependency
    $translator = new class implements TranslatorInterface {
        public function trans($id, array $parameters = [], $domain = null, $locale = null) {
            return $id;
        }
        public function getLocale() {
            return 'fr';
        }
    };

    // Instantiate the presenter directly
    $presenter = new OrderDetailLazyArray($order, $locale, $translator);
    
    // Execute the method under test
    $shippingResults = $presenter->getShipping();
    
    // Get the raw shipping data from the order to determine the expected value
    $rawShipping = $order->getShipping();
    reset($rawShipping);
    $shippingId = key($rawShipping);
    $shippingData = current($rawShipping);
    
    $actualValue = $shippingResults[$shippingId]['shipping_cost'];
    $expectedValue = $locale->formatPrice($shippingData['shipping_cost_tax_incl'], Currency::getIsoCodeById((int)$order->id_currency));

    echo "Tax Calculation Method: " . $order->getTaxCalculationMethod() . "\n";
    echo "Shipping Cost Tax Excl: " . $shippingData['shipping_cost_tax_excl'] . "\n";
    echo "Shipping Cost Tax Incl: " . $shippingData['shipping_cost_tax_incl'] . "\n";
    echo "Observed formatted cost: $actualValue\n";
    echo "Expected formatted cost: $expectedValue\n";

    // The test passes if the observed value is the tax-included price
    exit($actualValue === $expectedValue ? 0 : 1);

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
