<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36052, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\CartRule\Repository\CartRuleRepository;
use PrestaShop\PrestaShop\Core\Domain\CartRule\ValueObject\CartRuleId;

// Context setup
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

try {
    // We use arbitrary IDs to trigger the DELETE queries. 
    // We don't need to create full CartRule objects in the DB because 
    // the repository methods perform DELETEs which don't require the ID to exist.
    $id1 = new CartRuleId(1);

    // Instantiate the repository directly
    $connection = \PrestaShop\PrestaShop\Adapter\Entity\Db::getConnection();
    $repository = new CartRuleRepository($connection);

    // The methods containing the bug are private. We use Reflection to call them directly
    // and ensure we trigger the exact SQL statements mentioned in the ticket.
    $ref = new ReflectionClass($repository);

    echo "Testing removeRestrictedCartRules...\n";
    $method1 = $ref->getMethod('removeRestrictedCartRules');
    $method1->setAccessible(true);
    $method1->invoke($repository, $id1);
    echo "removeRestrictedCartRules executed successfully.\n";

    echo "Testing removeRestrictionsByName...\n";
    $method2 = $ref->getMethod('removeRestrictionsByName');
    $method2->setAccessible(true);
    // 'carrier' is a common entity name used in cart rule restrictions
    $method2->invoke($repository, $id1, 'carrier');
    echo "removeRestrictionsByName executed successfully.\n";

    echo "No SQL syntax errors detected. The fix is working.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "Caught exception: " . $t->getMessage() . "\n";
    // MariaDB error 1064 is the specific syntax error for aliases in DELETE
    if (strpos($t->getMessage(), '1064') !== false || strpos($t->getMessage(), 'syntax error') !== false) {
        echo "Bug reproduced: MariaDB does not support aliases in DELETE statements.\n";
    }
    exit(1);
}
