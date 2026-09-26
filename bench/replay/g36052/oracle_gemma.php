<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #36052, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\CartRule\Repository\CartRuleRepository;
use PrestaShop\PrestaShop\Core\Domain\CartRule\ValueObject\CartRuleId;

// Context setup
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

try {
    // Create demo CartRules since they are not explicitly provided in the demo data list
    $cr1 = new CartRule();
    $cr1->name = [1 => 'Test Rule 1'];
    $cr1->code = 'RULE1' . uniqid();
    $cr1->quantity = 100;
    $cr1->id_currency = 1;
    $cr1->id_shop = 1;
    $cr1->active = 1;
    $cr1->add();

    $cr2 = new CartRule();
    $cr2->name = [1 => 'Test Rule 2'];
    $cr2->code = 'RULE2' . uniqid();
    $cr2->quantity = 100;
    $cr2->id_currency = 1;
    $cr2->id_shop = 1;
    $cr2->active = 1;
    $cr2->add();

    $id1 = new CartRuleId((int)$cr1->id);
    $id2 = new CartRuleId((int)$cr2->id);

    // Instantiate the repository directly
    // PrestaShop\PrestaShop\Adapter\Entity\Db::getConnection() returns the Doctrine DBAL Connection
    $connection = \PrestaShop\PrestaShop\Adapter\Entity\Db::getConnection();
    $repository = new CartRuleRepository($connection);

    echo "Testing restrictCartRules (triggers removeRestrictedCartRules)...\n";
    // This method calls removeRestrictedCartRules which uses DELETE with an alias 'crc' in the buggy version
    $repository->restrictCartRules($id1, [$id2]);
    echo "restrictCartRules executed successfully.\n";

    // To be thorough, we try to trigger removeRestrictionsByName if setRestrictionsByName is available
    // Based on the diff, setRestrictionsByName calls removeRestrictionsByName
    if (method_exists($repository, 'setRestrictionsByName')) {
        echo "Testing setRestrictionsByName (triggers removeRestrictionsByName)...\n";
        // Use a dummy entity name like 'carrier' and a dummy ID
        $repository->setRestrictionsByName($id1, [1], 'carrier');
        echo "setRestrictionsByName executed successfully.\n";
    }

    echo "No SQL syntax errors detected. The fix is working.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "Caught exception: " . $t->getMessage() . "\n";
    // If the error is a syntax error related to the alias in DELETE, it's the bug
    if (strpos($t->getMessage(), 'syntax error') !== false || strpos($t->getMessage(), '1064') !== false) {
        echo "Bug reproduced: MariaDB does not support aliases in DELETE statements.\n";
    }
    exit(1);
}
