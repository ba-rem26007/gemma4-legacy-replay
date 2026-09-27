<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34370, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test controller to expose the protected displayMaintenancePage method.
 */
class TestFrontController extends FrontController {
    public function triggerMaintenance() {
        $this->displayMaintenancePage();
    }

    // Override to prevent any automatic redirections or exits during init/constructor
    public function canonicalRedirection($url = '') {}
    public function geolocationManagement($defaultCountry) {}
}

// Setup Context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// Ensure shop is in maintenance mode (though we call the method directly)
Configuration::updateValue('PS_MAINTENANCE', 1);

$controller = new TestFrontController();

// We use output buffering to capture the HTML output of displayMaintenancePage
// and prevent it from polluting the CLI output.
ob_start();
try {
    // This call executes:
    // 1. $this->setMedia() (The fix: registers theme core CSS)
    // 2. $this->registerStylesheet('theme-error', ...) (Registers error CSS)
    // 3. Smarty fetch and echo
    $controller->triggerMaintenance();
} catch (\Throwable $t) {
    // We catch exceptions (e.g. missing template) because the stylesheets 
    // are registered BEFORE the template is fetched.
}
ob_end_clean();

$stylesheets = $controller->getStylesheets();
$count = count($stylesheets);

echo "Number of registered stylesheets: $count\n";
foreach ($stylesheets as $id => $data) {
    echo " - $id\n";
}

/**
 * DIAGNOSTIC:
 * Before fix: displayMaintenancePage() only calls registerStylesheet('theme-error', ...).
 *             The stylesheets array contains only 1 element.
 * After fix: displayMaintenancePage() calls setMedia() first.
 *            setMedia() registers the theme's main CSS files (e.g., theme.css, custom.css).
 *            Then 'theme-error' is added.
 *            The stylesheets array contains > 1 element.
 */
exit($count > 1 ? 0 : 1);
