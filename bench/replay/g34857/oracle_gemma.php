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
    $p->reference = 'TEST_REF_123';
    $p->price = 10.0;
    $p->id_category_default = 2;
    $p->active = 1;
    $p->add();

    // Associate product with multiple categories (2, 3, 4)
    $p->updateCategory(2);
    $p->updateCategory(3);
    $p->updateCategory(4);

    echo "Product created with reference: {$p->reference}\n";
    echo "Initial categories: " . implode(', ', $p->getCategories()) . "\n";

    // 2. Prepare Import Simulation
    $controller = new TestImportController();
    $controller->separator = ',';

    // We simulate a CSV row that updates the product via reference
    // and adds/updates categories. 
    // The bug occurs when categories are provided in the import.
    $info = [
        'reference' => 'TEST_REF_123',
        'categories' => '2,5', // We want to keep 2 and add 5
    ];

    $accessories = [];
    $default_lang = 1;
    $id_lang = 1;
    $force_ids = 0;
    $regenerate = 0;
    $shop_active = 1;
    $shop_ids = [1];
    $match_ref = 1; // Important: match by reference

    // 3. Execute the code touched by the fix
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
    
    echo "Final categories: " . implode(', ', $final_categories) . "\n";

    // The bug: if the product already had categories, the old code would 'continue' 
    // and not add the new ones from the CSV. 
    // If the import process clears existing associations, we end up only with the default.
    // The fix ensures that categories from the CSV are actually appended/added.
    
    $has_category_5 = in_array(5, $final_categories);
    
    if ($has_category_5) {
        echo "SUCCESS: Category 5 was correctly imported.\n";
        exit(0);
    } else {
        echo "FAILURE: Category 5 was not imported. Bug still present.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
}
