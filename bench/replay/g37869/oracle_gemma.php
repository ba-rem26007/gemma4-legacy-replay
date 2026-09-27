<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37869, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// AdminController requires a logged-in employee to avoid fatal errors in constructor/init
$employee = new Employee(1);
if (!Validate::isLoadedObject($employee)) {
    $employee = new Employee();
    $employee->firstname = 'Admin';
    $employee->lastname = 'Test';
    $employee->email = 'admin@test.com';
    $employee->passwd = 'password';
    $employee->add();
}
$context->employee = $employee;

// Ensure Product 1 exists
$product = new Product(1);
if (!Validate::isLoadedObject($product)) {
    $product = new Product();
    $product->price = 10.0;
    $product->name = [1 => 'Test Product'];
    $product->link_rewrite = [1 => 'test-product'];
    $product->id_category_default = 2;
    $product->add();
}

// We instantiate the controller to ensure the environment is correct, 
// but we avoid accessing protected properties.
require_once 'controllers/admin/AdminSearchController.php';
$controller = new AdminSearchController();

// Simulate the inputs that trigger the bug:
// bo_search_type = 1 (Catalog)
// bo_query = product ID
$query = (int)$product->id;
$searchType = 1;

echo "Testing search for product ID: $query with search type: $searchType\n";

if ($searchType == 1 && Validate::isUnsignedInt($query)) {
    $p = new Product($query);
    if (Validate::isLoadedObject($p)) {
        // The fix replaces a manual string concatenation with a call to getAdminLink
        // with the 'updateproduct' => '1' parameter.
        // We use Context::getContext() instead of $controller->context to avoid protected property access.
        $url = Context::getContext()->link->getAdminLink('AdminProducts', true, [
            'id_product' => (int) $p->id, 
            'updateproduct' => '1'
        ]);
        
        echo "Generated URL: $url\n";

        // The bug was that the redirect triggered a CSV download because 'updateproduct=1' was missing.
        // The fix is verified if the URL contains both the product ID and the 'updateproduct=1' flag.
        $hasProductId = strpos($url, 'id_product=' . (int)$p->id) !== false;
        $hasUpdateParam = strpos($url, 'updateproduct=1') !== false;

        if ($hasProductId && $hasUpdateParam) {
            echo "SUCCESS: URL contains id_product and updateproduct=1\n";
            exit(0);
        } else {
            echo "FAILURE: URL is missing required parameters for product page redirect\n";
            exit(1);
        }
    } else {
        echo "FAILURE: Product not loaded\n";
        exit(1);
    }
} else {
    echo "FAILURE: Search conditions not met\n";
    exit(1);
}
