<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29821, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // 1. Setup: Use existing demo data (Category 2, Product 1)
    $cat = new Category(2);
    $cat->active = 1;
    $cat->update();

    $p = new Product(1);
    $p->id_category_default = 2;
    $p->update();
    $p->addToCategories([2]);

    // 2. Create a restricted group and assign the category only to this group
    // This ensures that a visitor (who is in the default group) normally wouldn't have access
    $group = new Group();
    $group->name = 'Restricted Group';
    $group->add();
    $id_restricted_group = (int)$group->id;

    $cat->cleanGroups();
    $cat->addGroupsIfNoExist($id_restricted_group);

    // 3. Disable the "Customer groups" feature in Performance settings
    // This is the trigger for the bug: when disabled, access checks should be skipped.
    Configuration::updateValue('PS_CUSTOMER_GROUPS', 0);

    // 4. Test Category access for a visitor (id_customer = 0)
    // Before fix: returns false because the visitor group is not assigned to the category.
    // After fix: returns true because Group::isFeatureActive() is false.
    $catAccess = $cat->checkAccess(0);
    echo "Category access for visitor (feature disabled): " . ($catAccess ? 'ALLOWED' : 'DENIED') . "\n";

    // 5. Test Product access for a visitor (id_customer = 0)
    // Before fix: returns false because it checks the category access.
    // After fix: returns true because Group::isFeatureActive() is false.
    $prodAccess = Product::checkAccessStatic(1, 0);
    echo "Product access for visitor (feature disabled): " . ($prodAccess ? 'ALLOWED' : 'DENIED') . "\n";

    // The test passes if both are allowed despite the restriction
    if ($catAccess && $prodAccess) {
        exit(0);
    } else {
        echo "Bug still present: Access is still restricted even when feature is disabled.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
