<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30387, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Dummy class to handle the HelperList callback
 */
class HelperListCallbackHandler
{
    public function myCustomCallback($data, $row)
    {
        return 'CALLBACK_EXECUTED';
    }
}

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

// 1. Prepare data: a list where one column value is explicitly NULL
// This is the condition that triggers the bug (isset(null) is false)
$list = [
    [
        'id' => 1,
        'test_column' => null,
    ],
    [
        'id' => 2,
        'test_column' => 'some value',
    ],
];

// 2. Define fields for HelperList
// We define a callback for 'test_column'
$callbackHandler = new HelperListCallbackHandler();
$fields_display = [
    'id' => [
        'title' => 'ID',
        'width' => 'auto',
    ],
    'test_column' => [
        'title' => 'Test Column',
        'callback' => 'myCustomCallback',
        'callback_object' => $callbackHandler,
        'width' => 'auto',
    ],
];

try {
    $helper = new HelperList();
    
    // generateList calls displayListContent(), which processes the callbacks
    $helper->generateList($list, $fields_display);

    // The processed values are stored in the public property _list
    $observedValueNull = $helper->_list[0]['test_column'];
    $observedValueNotNull = $helper->_list[1]['test_column'];

    echo "Value for NULL entry: " . var_export($observedValueNull, true) . "\n";
    echo "Value for non-NULL entry: " . var_export($observedValueNotNull, true) . "\n";

    // The test passes if the callback was executed even for the NULL value
    if ($observedValueNull === 'CALLBACK_EXECUTED' && $observedValueNotNull === 'CALLBACK_EXECUTED') {
        exit(0);
    } else {
        echo "Error: Callback was not called for the NULL value.\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "Exception: " . $t->getMessage() . "\n";
    exit(1);
}
