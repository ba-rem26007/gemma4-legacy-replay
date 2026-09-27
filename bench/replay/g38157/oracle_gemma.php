<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #38157, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShopBundle\Translation\PrestaShopTranslatorTrait;
use Symfony\Component\Translation\Translator;
use Symfony\Component\Translation\Catalogue\Catalogue;

/**
 * Mock class to test the PrestaShopTranslatorTrait.
 * It extends the Symfony Translator to satisfy the trait's parent::trans calls
 * and implements getCatalogue to simulate different translation states.
 */
class TestTranslator extends Translator
{
    use PrestaShopTranslatorTrait;

    public $mockCatalogues = [];

    /**
     * Overriding getCatalogue to return our mock catalogues.
     * The trait calls this method to check if a translation exists in the modern system.
     */
    protected function getCatalogue($locale = null)
    {
        // If no locale is provided, we simulate the default context locale (en-US)
        $locale = $locale ?: 'en-US';
        return $this->mockCatalogues[$locale] ?? new Catalogue();
    }
}

// Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

try {
    // 1. Instantiate the translator with a default locale (English)
    $translator = new TestTranslator('en-US');

    // 2. Setup Mock Data:
    // We simulate a scenario where the translation exists in English (modern system)
    // but is MISSING in Italian (modern system).
    // In this case, it SHOULD fallback to the legacy system for Italian.
    
    $message = 'Message ENG';
    $domain = 'Modules.Translationtest.Home';
    $localeEn = 'en-US';
    $localeIt = 'it-IT';

    $catEn = new Catalogue();
    $catEn->setMessage($message, 'Translated ENG', $domain);
    
    $catIt = new Catalogue(); // Empty catalogue for Italian

    $translator->mockCatalogues[$localeEn] = $catEn;
    $translator->mockCatalogues[$localeIt] = $catIt;

    // 3. Use Reflection to test the private method 'shouldFallbackToLegacyModuleTranslation'
    // This method decides whether to use the Symfony translator or the Legacy system.
    $reflection = new ReflectionClass($translator);
    $method = $reflection->getMethod('shouldFallbackToLegacyModuleTranslation');
    $method->setAccessible(true);

    /**
     * TEST CASE:
     * Current Locale: en-US
     * Requested Locale: it-IT
     * 
     * Before fix: The method ignored the requested locale and checked the default (en-US).
     * Since 'Message ENG' exists in en-US, it returned FALSE (no fallback), 
     * and then parent::trans(..., 'it-IT') returned the original ID because it was missing in it-IT.
     * 
     * After fix: The method uses the requested locale (it-IT).
     * Since 'Message ENG' is missing in it-IT, it returns TRUE (fallback to legacy).
     */
    
    // We pass 3 arguments. On old versions, the 3rd is ignored. On new, it's used.
    $shouldFallback = $method->invokeArgs($translator, [$message, $domain, $localeIt]);

    echo "Message: $message\n";
    echo "Domain: $domain\n";
    echo "Requested Locale: $localeIt\n";
    echo "Should fallback to legacy: " . ($shouldFallback ? 'YES' : 'NO') . "\n";

    // The test passes if it correctly identifies that it should fallback to legacy for the Italian locale
    exit($shouldFallback ? 0 : 1);

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
