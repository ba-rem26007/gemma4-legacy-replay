<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34857, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Helper class to expose the protected productImportOne method for testing
 */
class TestImportController extends AdminImportController
{
    public function publicProductImportOne($info, $default_language_id, $id_lang, $force_ids, $regenerate, $shop_is_feature_active, $shop_ids, $match_ref, &$accessories, $validateOnly = false)
    {
        return $this->productImportOne($info, $default_language_id, $id_lang, $force_ids, $regenerate, $shop_is_feature_active, $shop_ids, $match_ref, $accessories, $validateOnly);
    }
}

try {
    // 1. Setup Data
    // Create a product with a reference
    $p = new Product();
    $p->reference = 'IMPORT_TEST_REF';
    $p->price = 10.0;
    $p->id_category_default = 2;
    $p->active = 1;
    $p->add();

    // Ensure it starts with only the default category
    Db::getInstance()->delete('category_product', 'id_product = ' . (int)$p->id);
    Db::getInstance()->insert('category_product', ['id_category' => 2, 'id_product' => (int)$p->id]);

    echo "Product created: ID {$p->id}, Ref {$p->reference}\n";
    echo "Initial categories: " . implode(', ', $p->getCategories()) . "\n";

    // 2. Prepare Import Simulation
    $controller = new TestImportController();
    $controller->separator = ',';

    // The bug: if multiple categories are provided in the CSV, 
    // the old code skips all but the first one because it sees $product->category is already an array.
    $info = [
        'reference' => 'IMPORT_TEST_REF',
        'categories' => '2,3,4', // We want to import these 3 categories
    ];

    $accessories = [];
    $default_lang = 1;
    $id_lang = 1;
    $force_ids = 0;
    $regenerate = 0;
    $shop_active = 1;
    $shop_ids = [1];
    $match_ref = 1; // Match by reference

    // 3. Execute the import logic
    $controller->publicProductImportOne(
        $info,
        $default_lang,
        $id_lang,
        $force_ids,
        $regenerate,
        $shop_active,
        $shop_ids,
        $match_ref,
        $accessories,
        false
    );

    // 4. Verification
    // Reload product to get fresh data from DB
    $p_updated = new Product($p->id);
    $final_categories = $p_updated->getCategories();
    
    echo "Final categories after import: " . implode(', ', $final_categories) . "\n";

    // Expected: categories 2, 3, and 4 should be present.
    // Bugged behavior: Only category 2 (the first one in the list) is processed.
    $expected = [2, 3, 4];
    $missing = array_diff($expected, $final_categories);

    if (empty($missing)) {
        echo "SUCCESS: All categories (2,3,4) were correctly imported.\n";
        exit(0);
    } else {
        echo "FAILURE: Missing categories: " . implode(', ', $missing) . ". Bug still present.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
}
