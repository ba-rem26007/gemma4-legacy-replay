<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #31667, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\SqlManager\SqlQueryValidator;

/**
 * The bug is that a PrestaShopException is thrown instead of being caught 
 * by the SqlQueryValidator when a malformed query is provided on PHP 8.
 * The fix adds PrestaShopException to the catch block.
 */

$validator = new SqlQueryValidator();

// This specific query triggers the parsing error mentioned in the ticket
$sql = "SELECT * CUST FROM ps_customer WHERE id_customer = 2";

try {
    echo "Testing SQL: $sql\n";
    $errors = $validator->validate($sql);
    
    echo "Validator returned " . count($errors) . " error(s).\n";
    
    $foundBadQueryError = false;
    foreach ($errors as $error) {
        if (isset($error['key']) && $error['key'] === 'Bad SQL query') {
            $foundBadQueryError = true;
            break;
        }
    }

    if ($foundBadQueryError) {
        echo "Success: 'Bad SQL query' error was correctly caught and returned.\n";
        exit(0);
    } else {
        echo "Failure: No 'Bad SQL query' error returned. Errors: " . json_encode($errors) . "\n";
        exit(1);
    }

} catch (\Throwable $t) {
    // If we reach here, the exception was NOT caught by the validator, 
    // which is the exact behavior of the bug.
    echo "Failure: An uncaught exception was thrown: " . get_class($t) . " - " . $t->getMessage() . "\n";
    exit(1);
}
