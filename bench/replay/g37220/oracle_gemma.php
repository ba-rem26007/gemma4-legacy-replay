<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37220, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
Context::getContext()->employee = new Employee(1);

/**
 * Wrapper class to expose protected methods of AdminTranslationsController
 */
class TestTranslationsController extends AdminTranslationsController
{
    public function callFindAndFillTranslations($theme_name)
    {
        // Trigger the method with null theme_name to check for TypeError
        return $this->findAndFillTranslations([], $theme_name, 'testmodule', '');
    }

    public function callFindAndWriteTranslationsIntoFile($theme_name)
    {
        // Trigger the method with null theme_name to check for TypeError
        return $this->findAndWriteTranslationsIntoFile('test.php', [], $theme_name, 'testmodule', '');
    }
}

$controller = new TestTranslationsController();

try {
    echo "Testing findAndFillTranslations with null theme...\n";
    $controller->callFindAndFillTranslations(null);
    echo "findAndFillTranslations: OK (no TypeError)\n";

    echo "Testing findAndWriteTranslationsIntoFile with null theme...\n";
    $controller->callFindAndWriteTranslationsIntoFile(null);
    echo "findAndWriteTranslationsIntoFile: OK (no TypeError)\n";

    echo "Both methods accepted null theme_name. Bug is fixed.\n";
    exit(0);
} catch (\TypeError $e) {
    echo "Caught expected TypeError: " . $e->getMessage() . "\n";
    echo "The code is still using strict 'string' type hint instead of '?string'.\n";
    exit(1);
} catch (\Throwable $e) {
    echo "Caught unexpected exception: " . $e->getMessage() . "\n";
    exit(1);
}
