<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36607, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Module\AdminModuleDataProvider;
use Module;
use Db;

try {
    // 1. Setup: Create a disabled module to trigger the bug
    // We create a dummy module because we need one that is specifically disabled
    $module = new Module();
    $module->name = 'test_regression_module';
    $module->version = '1.0';
    $module->active = 0; // Disabled
    $module->add();

    // 2. Instantiate dependencies for AdminModuleDataProvider
    // The provider requires a RouterInterface. We use a mock/anonymous class to avoid 
    // complex Symfony container setup in CLI.
    $router = new class implements \Symfony\Component\Routing\RouterInterface {
        public function generate($name, array $parameters = [], array $options = []) { return ''; }
        public function match($path) { return []; }
        public function compile($name, array $parameters = [], array $options = []) { return ''; }
    };

    $provider = new AdminModuleDataProvider($router);

    // 3. Call the method that determines which action to display
    // The bug is that ACTION_CONFIGURE was prioritized over ACTION_ENABLE in the $moduleActions array.
    $actions = $provider->getModuleActions($module);
    
    if (empty($actions)) {
        echo "No actions returned for the module.\n";
        exit(1);
    }

    // The first action in the array is the one displayed as the primary button in the UI
    $firstAction = key($actions);
    echo "Module state: disabled\n";
    echo "First action observed: $firstAction\n";

    // Expected: The first action should be 'enable' (Module::ACTION_ENABLE)
    // Before fix: It was 'configure' (Module::ACTION_CONFIGURE)
    if ($firstAction === Module::ACTION_ENABLE) {
        exit(0);
    } else {
        echo "Bug still present: Action is '$firstAction' instead of '" . Module::ACTION_ENABLE . "'\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
