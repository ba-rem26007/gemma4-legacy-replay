<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30962, validé pre/post automatiquement
require 'config/config.inc.php';

use Symfony\Component\Routing\Exception\RouteNotFoundException;

// Setup Context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

$employee = new Employee(1);
if (!Validate::isLoadedObject($employee)) {
    $employee = new Employee();
    $employee->firstname = 'Admin';
    $employee->lastname = 'Admin';
    $employee->email = 'admin@example.com';
    $employee->passwd = 'password';
    $employee->add();
}
$context->employee = $employee;

// Create a Tab that will trigger the RouteNotFoundException.
// The bug occurs when a Tab has a 'route_name' that is not found in the Symfony router.
$tab = new Tab();
$tab->class_name = 'AdminModules';
$tab->module = '';
$tab->id_parent = 0;
$tab->id_shop = 1;
$tab->id_profile = 1;
$tab->route_name = 'non_existent_route_trigger_bug_12345';
$tab->add();

// Instantiate AdminController. 
// We provide a controller name so that the internal logic (token, etc.) doesn't fail.
$controller = new AdminController('AdminModules');

try {
    /**
     * initHeader() calls getTabs(), which iterates through the tabs in the database.
     * For each tab, it calls $this->context->link->getTabLink($tab).
     * If route_name is set but the route doesn't exist in the Symfony cache, 
     * getTabLink throws a RouteNotFoundException.
     */
    $controller->initHeader();
    
    echo "Success: RouteNotFoundException was handled by AdminController.\n";
    exit(0);
} catch (RouteNotFoundException $e) {
    echo "Failure: RouteNotFoundException was NOT handled: " . $e->getMessage() . "\n";
    exit(1);
} catch (\Throwable $t) {
    echo "Failure: An unexpected error occurred: " . $t->getMessage() . "\n";
    exit(1);
}
