<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35587, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
$employee = new Employee(1);
Context::getContext()->employee = $employee;

/**
 * Dummy AdminController to trigger the bug.
 * We override init() to avoid heavy lifting (like checkAccess or initHeader) 
 * that would fail or be too slow in a CLI environment.
 */
class TestAdminController extends AdminController
{
    public function __construct()
    {
        $this->controller_name = 'TestAdminController';
        parent::__construct();
    }

    public function init()
    {
        // Override to avoid calling checkAccess() and initHeader() in CLI
        // This also ensures $this->action remains null if we don't set it here.
    }

    public function ajaxProcessTest()
    {
        return 'success';
    }
}

// Simulate the request parameters
$_GET['action'] = 'test';

// Initialize the controller
$controller = new TestAdminController();
$controller->ajax = true;
$controller->action = null; // Explicitly ensure it's null to trigger the bug

// Error handler to capture the PHP 8.1 deprecation notice
$deprecationTriggered = false;
set_error_handler(function ($errno, $errstr) use (&$deprecationTriggered) {
    if ($errno === E_DEPRECATED || $errno === E_USER_DEPRECATED) {
        $deprecationTriggered = true;
    }
    return true;
});

try {
    echo "Executing postProcess()...\n";
    $result = $controller->postProcess();
    echo "Result: $result\n";
} catch (\Throwable $t) {
    echo "Exception caught: " . $t->getMessage() . "\n";
    exit(1);
}

restore_error_handler();

if ($deprecationTriggered) {
    echo "Bug detected: ucfirst() received null from \$this->action\n";
    exit(1);
} else {
    echo "No deprecation notice observed. Bug fixed.\n";
    exit(0);
}
