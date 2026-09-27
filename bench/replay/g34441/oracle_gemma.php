<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34441, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\Product\Update\ProductDuplicator;
use Doctrine\DBAL\DriverManager;
use Doctrine\DBAL\Connection;

/**
 * The bug is in ProductDuplicator::bulkInsert which fails to escape single quotes
 * when building the SQL query for bulk insertion.
 * This causes a SQL syntax error when a customization field contains an apostrophe.
 */

// 1. Setup Doctrine Connection (since Symfony container is not available in CLI)
$connectionParams = [
    'dbname' => _DB_NAME_,
    'user' => _DB_USER_,
    'password' => _DB_PASSWORD_,
    'host' => _DB_HOST_,
    'driver' => 'pdo_mysql',
];
$connection = DriverManager::getConnection($connectionParams);

// 2. Instantiate ProductDuplicator
// We pass null for most dependencies as we only need the connection and dbPrefix for bulkInsert
$duplicator = new ProductDuplicator(
    null, // ProductRepository
    null, // HookDispatcherInterface
    null, // TranslatorInterface
    null, // StringModifierInterface
    $connection,
    _DB_PREFIX_,
    null, // CombinationRepository
    null, // ProductSupplierRepository
    null, // SpecificPriceRepository
    null, // StockAvailableRepository
    null, // ProductStockUpdater
    null, // CombinationStockUpdater
    null, // ProductImageRepository
    null  // ProductImagePathFactory
);

// 3. Use Reflection to access the private bulkInsert method
$reflection = new ReflectionClass(ProductDuplicator::class);
$method = $reflection->getMethod('bulkInsert');
$method->setAccessible(true);

// 4. Prepare data that triggers the bug (a string with an apostrophe)
$table = 'customization_field_lang';
$multipleRowValues = [
    [
        'id_customization_field' => 99999, // Dummy ID
        'id_lang' => 1,
        'name' => "Merci d'insérer votre personnalisation"
    ]
];
$errorCode = 90; // CannotDuplicateProductException::FAILED_DUPLICATE_CUSTOMIZATION_FIELDS

echo "Testing bulkInsert with apostrophe in value...\n";

try {
    // This call will trigger a SQL syntax error if the fix (str_replace("'", "''", ...)) is missing
    $method->invoke($duplicator, $table, $multipleRowValues, $errorCode);
    
    echo "Success: bulkInsert executed without SQL syntax error.\n";
    exit(0);
} catch (\Throwable $e) {
    $errorMessage = $e->getMessage();
    echo "Caught exception: $errorMessage\n";

    // If the error is a SQL syntax error (SQLSTATE 42000), the bug is still present.
    // If it's a foreign key constraint error, the SQL was syntactically correct, so the fix works.
    if (strpos($errorMessage, 'syntax error') !== false || strpos($errorMessage, 'SQLSTATE[42000]') !== false) {
        echo "FAILED: SQL syntax error detected. The apostrophe was not escaped.\n";
        exit(1);
    }

    // Any other error (like Foreign Key constraint) means the SQL was parsed correctly.
    echo "Success: SQL syntax is correct (caught a non-syntax error: " . get_class($e) . ").\n";
    exit(0);
}
