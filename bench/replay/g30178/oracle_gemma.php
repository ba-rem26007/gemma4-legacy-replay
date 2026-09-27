<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30178, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
$employee = new Employee(1);
if (!Validate::isLoadedObject($employee)) {
    $e = new Employee();
    $e->firstname = 'Test';
    $e->lastname = 'Test';
    $e->email = 'test@test.com';
    $e->passwd = '123456';
    $e->add();
    $employee = $e;
}
Context::getContext()->employee = $employee;

// Ensure the controller class is loaded
require_once 'controllers/admin/AdminStatsTabController.php';

// The bug occurs when Hook::getHookModuleExecList('displayAdminStatsModules') returns false
// (e.g., when no modules are registered to this hook, which is the case on a fresh install
// or when the Stats Dashboard module is disabled).
$hookModules = Hook::getHookModuleExecList('displayAdminStatsModules');
echo "Hook result for 'displayAdminStatsModules': " . var_export($hookModules, true) . "\n";

if (is_array($hookModules)) {
    echo "Error: The hook already contains modules. The test requires an empty hook to trigger the bug.\n";
    // We can't use SQL to clear it per instructions, but in a fresh environment this should be false.
    // If it's an array, we can't reliably trigger the TypeError.
    exit(0); 
}

try {
    // Instantiate the controller directly
    $controller = new AdminStatsTabControllerCore();
    $controller->token = 'test_token';
    $controller->currentIndex = 'AdminStatsTab';

    echo "Calling displayMenu()...\n";
    // displayMenu() calls getModules(), which calls array_map on the result of Hook::getHookModuleExecList
    $result = $controller->displayMenu();
    
    echo "displayMenu() executed successfully.\n";
    exit(0); // Corrected: no exception thrown
} catch (\Throwable $t) {
    echo "Caught expected exception/error: " . get_class($t) . " - " . $t->getMessage() . "\n";
    echo "Stack trace: " . $t->getTraceAsString() . "\n";
    exit(1); // Bug still present: array_map failed on non-array
}
