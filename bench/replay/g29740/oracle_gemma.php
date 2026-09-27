<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29740, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->employee = new Employee(1);

try {
    // Use Reflection to instantiate the controller without calling the constructor.
    // This avoids triggering the full AdminController lifecycle (like renderForm or template loading)
    // which often fails in a CLI environment.
    $reflection = new ReflectionClass('AdminTaxRulesGroupController');
    $controller = $reflection->newInstanceWithoutConstructor();
    
    // Manually inject the context needed for translations and data fetching
    $controller->context = $context;

    // Call the method that defines the form fields
    $controller->initRuleForm();
    
    if (!isset($controller->fields_form[0]['form']['input'])) {
        echo "Error: Form inputs not initialized.\n";
        exit(1);
    }

    $inputs = $controller->fields_form[0]['form']['input'];
    $taxField = null;

    // Find the input field named 'tax'
    foreach ($inputs as $input) {
        if (isset($input['name']) && $input['name'] === 'tax') {
            $taxField = $input;
            break;
        }
    }

    if ($taxField === null) {
        echo "Error: Tax input field not found in the form.\n";
        exit(1);
    }

    // Check if the incorrect hint is present
    $hint = isset($taxField['hint']) ? $taxField['hint'] : '';
    echo "Observed hint for Tax field: '$hint'\n";

    // The bug is the presence of the hint "(Total tax: 9%)"
    // If the hint contains this string, the bug is still present (fail = exit 1)
    if (strpos($hint, 'Total tax: 9%') !== false) {
        echo "Bug found: Incorrect help text is still present.\n";
        exit(1);
    }

    echo "Success: Incorrect help text has been removed.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "Exception caught: " . $t->getMessage() . "\n";
    exit(1);
}
