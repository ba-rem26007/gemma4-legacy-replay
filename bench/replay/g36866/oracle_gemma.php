<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36866, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * The goal is to trigger the PHP 8.3 deprecation warning:
 * "Creation of dynamic property Address::$back is deprecated"
 * and "Creation of dynamic property Address::$token is deprecated".
 * 
 * This happens in CustomerAddressForm::submit() when iterating over formFields
 * and assigning values to the Address object without checking if the property exists.
 */

// 1. Setup error handler to capture deprecations
$deprecations = [];
set_error_handler(function($errno, $errstr) use (&$deprecations) {
    if ($errno === E_DEPRECATED || $errno === E_USER_DEPRECATED) {
        $deprecations[] = $errstr;
        return true;
    }
    return false;
});

// 2. Mock FormField to simulate the form input
class MockFormField {
    private $name;
    private $value;
    public function __construct($name, $value) {
        $this->name = $name;
        $this->value = $value;
    }
    public function getName() { return $this->name; }
    public function getValue() { return $this->value; }
    public function isRequired() { return false; }
}

// 3. Mock Persister to avoid actual database persistence errors
class MockPersister {
    public function save($address, $token) { return true; }
}

// 4. Create a testable version of CustomerAddressForm
// We override the constructor to avoid the "Too few arguments" error
class TestCustomerAddressForm extends CustomerAddressForm {
    public function __construct() {
        // Bypass parent constructor to avoid needing 5 dependencies
    }

    public function validate() { 
        return true; 
    }

    protected function getPersister() {
        return new MockPersister();
    }

    public function setFields($fields) {
        $this->formFields = $fields;
    }
}

try {
    // Initialize the form
    $form = new TestCustomerAddressForm();
    
    // Set required properties for submit()
    $form->language = new Language(1);
    $form->translator = Context::getContext()->translator;
    
    // Set a dummy id_address in Tools to avoid nulls in Address constructor
    Tools::setValue('id_address', 1);

    // Inject fields that do NOT exist in the Address class definition.
    // These will trigger the dynamic property deprecation in PHP 8.3.
    $form->setFields([
        new MockFormField('token', 'some_token_value'),
        new MockFormField('back', 'some_back_value')
    ]);

    // Call the method containing the bug
    $form->submit();
} catch (\Throwable $t) {
    echo "Fatal error encountered: " . $t->getMessage() . "\n";
    exit(1);
}

restore_error_handler();

// Diagnostic output
if (empty($deprecations)) {
    echo "No deprecations observed. The fix is working.\n";
    exit(0);
} else {
    echo "Deprecations detected:\n";
    foreach ($deprecations as $d) {
        echo "- $d\n";
    }
    exit(1);
}
