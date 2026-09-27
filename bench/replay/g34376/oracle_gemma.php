<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34376, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Presenter\Product\ProductLazyArray;
use PrestaShop\PrestaShop\Adapter\Presenter\Product\ProductPresentationSettings;
use PrestaShop\PrestaShop\Adapter\Presenter\Product\ImageRetriever;
use PrestaShop\PrestaShop\Adapter\Presenter\Product\PriceFormatter;
use PrestaShop\PrestaShop\Adapter\Presenter\Product\ProductColorsRetriever;
use PrestaShop\PrestaShop\Adapter\Presenter\TranslatorInterface;

// Mock for TranslatorInterface
class MockTranslator implements TranslatorInterface
{
    public function trans($id, $locale = null, $domain = null)
    {
        return $id;
    }
}

// Setup Context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

try {
    // Instantiate dependencies for ProductLazyArray
    $settings = new ProductPresentationSettings();
    $language = new Language(1);
    $link = new Link();
    $imageRetriever = new ImageRetriever();
    $priceFormatter = new PriceFormatter();
    $productColorsRetriever = new ProductColorsRetriever();
    $translator = new MockTranslator();

    /**
     * The bug is triggered when 'attributes' is set and not empty, but is NOT an array.
     * In the original code: if (!isset($this->product['attributes']) || empty($this->product['attributes']))
     * If 'attributes' is a string "some_value", isset is true and empty is false.
     * The code then proceeds to treat it as an array, causing a crash (TypeError in PHP 8).
     */
    $productData = [
        'id_product' => 1,
        'attributes' => 'trigger_bug_string', // Not an array, but not empty
        'reference' => 'REF123',
    ];

    $lazyArray = new ProductLazyArray(
        $settings,
        $productData,
        $language,
        $imageRetriever,
        $link,
        $priceFormatter,
        $productColorsRetriever,
        $translator
    );

    echo "Testing getCombinationSpecificData with non-array attributes...\n";
    $result = $lazyArray->getCombinationSpecificData();

    // If the fix is applied, it should return null because !is_array($this->product['attributes']) is true.
    if ($result === null) {
        echo "Success: Method returned null for non-array attributes.\n";
        exit(0);
    } else {
        echo "Failure: Method did not return null.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Bug triggered: Caught exception/error: " . $t->getMessage() . "\n";
    // If we catch a Throwable, it means the code crashed as expected before the fix.
    exit(1);
}
