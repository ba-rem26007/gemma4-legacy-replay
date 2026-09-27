<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30158, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // Setup Context
    $context = Context::getContext();
    $context->shop = new Shop(1);
    $context->language = new Language(1);
    $context->employee = new Employee(1);

    // Mock Smarty to avoid crashes when the fix calls $this->context->smarty->assign()
    // We access the global context directly to avoid "protected property" errors
    $context->smarty = new class {
        public function assign($data) {}
    };

    // Disable the Customers Groups feature
    // Group::isFeatureActive() checks this configuration value
    Configuration::updateValue('PS_CUSTOMERS_GROUPS_FEATURE_ACTIVE', 0);

    $controller = new AdminGroupsController();
    $controller->token = Tools::getAdminTokenLite('AdminGroups');
    $controller->display = ''; // Ensure we are on the list page to trigger the button logic

    // 1. Test initPageHeaderToolbar: 'new_group' button should be absent when feature is disabled
    $controller->initPageHeaderToolbar();
    $hasButton = isset($controller->page_header_toolbar_btn['new_group']);

    // 2. Test postProcess: Actions should be blocked when feature is disabled
    // Setup: Ensure customer 1 exists and is inactive
    $customer = new Customer(1);
    if (!Validate::isLoadedObject($customer)) {
        $customer = new Customer();
        $customer->firstname = 'Test';
        $customer->lastname = 'Test';
        $customer->email = 'test@example.com';
        $customer->passwd = 'password123';
        $customer->add();
    }
    $customer->active = 0;
    $customer->update();

    // Simulate POST request to enable customer (Bulk action)
    $_POST['customer_groupBox'] = [(int)$customer->id];
    $_POST['submitBulkenableSelectioncustomer_group'] = 1;

    $controller->postProcess();

    // Check if the customer was updated (it should NOT be updated if feature is disabled)
    $customer = new Customer((int)$customer->id);
    $wasUpdated = ($customer->active == 1);

    // 3. Test initContent: A warning should be displayed and parent::initContent should NOT be called
    // In CLI, parent::initContent() crashes because it tries to load templates.
    // If the fix is applied, it returns early and does NOT crash.
    $hasWarning = false;
    try {
        $controller->initContent();
        $hasWarning = !empty($controller->warnings);
    } catch (\Throwable $t) {
        // If it crashes, it means parent::initContent() was called -> Fix not applied
        echo "initContent crashed (expected on old code): " . $t->getMessage() . "\n";
    }

    echo "Feature Disabled: PS_CUSTOMERS_GROUPS_FEATURE_ACTIVE = 0\n";
    echo "New Group Button Present: " . ($hasButton ? 'YES' : 'NO') . "\n";
    echo "Warning Displayed: " . ($hasWarning ? 'YES' : 'NO') . "\n";
    echo "Customer Updated via postProcess: " . ($wasUpdated ? 'YES' : 'NO') . "\n";

    // The behavior is CORRECTED if:
    // - The button is NOT present
    // - The warning IS present
    // - The customer was NOT updated
    if (!$hasButton && $hasWarning && !$wasUpdated) {
        exit(0);
    } else {
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Fatal Error: " . $t->getMessage() . "\n";
    exit(1);
}
