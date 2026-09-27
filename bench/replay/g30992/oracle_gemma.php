<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30992, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Presenter\Object\ObjectPresenter;

/**
 * Test for Ticket: is_logged property in FO is true even for guests
 * 
 * The bug: FrontController::getTemplateVarCustomer() uses isLogged(true).
 * isLogged(true) returns true if the session is alive (id_guest or id_customer in cookie),
 * even if the user is not actually authenticated (id_customer = 0 in cookie).
 * 
 * To trigger the bug:
 * 1. Session must be alive (id_guest > 0).
 * 2. User must NOT be logged in (id_customer = 0 in cookie).
 * 3. isLogged(true) will return true -> is_logged = true (BUG).
 * 4. isLogged() will return false -> is_logged = false (CORRECT).
 */

$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// 1. Setup a Customer object. 
// We use a real customer from demo data to ensure the object is fully initialized.
$customer = new Customer(1); 
$context->customer = $customer;

// 2. Simulate a Guest session:
// id_guest is set (session is alive), but id_customer is 0 (not logged in).
$context->cookie->id_guest = 1;
$context->cookie->id_customer = 0;

// FrontController::$context and FrontController::$objectPresenter are protected.
$fc = new class extends FrontController {
    public function setPresenter($p) {
        $this->objectPresenter = $p;
    }
};

// The Controller constructor assigns Context::getContext() to $this->context
$fc->setPresenter(new ObjectPresenter());

try {
    $vars = $fc->getTemplateVarCustomer();
    $isLogged = $vars['is_logged'];
} catch (\Throwable $e) {
    echo "Error during execution: " . $e->getMessage() . "\n";
    exit(1);
}

echo "Customer ID: " . $customer->id . "\n";
echo "Cookie id_guest: " . (int)$context->cookie->id_guest . "\n";
echo "Cookie id_customer: " . (int)$context->cookie->id_customer . "\n";
echo "Observed is_logged: " . ($isLogged ? 'true' : 'false') . "\n";

// The test should FAIL (exit 1) if is_logged is true for a guest visitor.
// The test should PASS (exit 0) if is_logged is false.
exit($isLogged === false ? 0 : 1);
