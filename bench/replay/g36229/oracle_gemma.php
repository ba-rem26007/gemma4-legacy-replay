<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36229, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShopBundle\Routing\LegacyRouterChecker;
use PrestaShopBundle\Routing\LegacyControllerConstants;
use Symfony\Component\HttpFoundation\Request;
use PrestaShopBundle\Entity\Repository\TabRepository;
use PrestaShop\Core\Hook\HookDispatcherInterface;
use PrestaShopBundle\Routing\Converter\LegacyParametersConverter;

/**
 * The bug is in LegacyRouterChecker::check().
 * When stripping the 'Controller' suffix from a module controller name,
 * the code used substr($controllerName, strrpos($controllerName, 'Controller')),
 * which returns the string starting FROM 'Controller' (i.e., it returns 'Controller'),
 * instead of removing it.
 */

// 1. Setup a dummy module directory to satisfy Dispatcher::getControllers()
// Dispatcher::getControllers scans the filesystem for .php files in the admin controller folder.
$moduleName = 'test_module';
$controllerName = 'AdminTestController';
$path = _PS_MODULE_DIR_ . $moduleName . '/controllers/admin/';
if (!is_dir($path)) {
    mkdir($path, 0777, true);
}
touch($path . $controllerName . '.php');

// 2. Mock dependencies
// We extend the classes and override constructors to avoid needing a full Symfony Container/EntityManager
$tabRepository = new class extends TabRepository {
    public function __construct() {}
    public function findOneByClassName($name) {
        // Return a dummy Tab object that indicates this controller belongs to a module
        return new class {
            public function getModule() { return 'test_module'; }
        };
    }
};

$hookDispatcher = new class implements HookDispatcherInterface {
    public function dispatchWithParameters($hook, $params) {}
    public function dispatch($hook, $params) {}
};

$legacyParametersConverter = new class extends LegacyParametersConverter {
    public function __construct() {}
};

try {
    $checker = new LegacyRouterChecker($tabRepository, $hookDispatcher, $legacyParametersConverter);
    
    // Simulate a request for the module controller
    $request = new Request(['controller' => $controllerName]);
    
    // Execute the check logic
    $checker->check($request);
    
    // The result of the suffix stripping is stored in the request attributes
    $observed = $request->attributes->get(LegacyControllerConstants::CONTROLLER_NAME_ATTRIBUTE);
    echo "Observed controller name: $observed\n";
    
    /**
     * Expected behavior:
     * Input: 'AdminTestController'
     * Result: 'AdminTest'
     * 
     * Buggy behavior:
     * Input: 'AdminTestController'
     * Result: 'Controller'
     */
    if ($observed === 'AdminTest') {
        exit(0);
    } else {
        echo "Bug detected: expected 'AdminTest', but got '$observed'\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
