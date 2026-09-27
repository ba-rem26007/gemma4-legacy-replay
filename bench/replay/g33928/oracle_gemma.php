<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #33928, validé pre/post automatiquement
require 'config/config.inc.php';

// Ensure the controller is loaded
require_once 'controllers/front/listing/CategoryController.php';

$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->customer = new Customer(1);

// Setup Category 2 with an additional description (description_short)
$cat = new Category(2, false, 1);
$cat->active = 1;
$cat->description_short = 'Additional Description Test Content';
$cat->update();

// Ensure products are associated with this category to trigger pagination logic
// Using Category::addProduct() which is the correct static method in PrestaShop
for ($i = 1; $i <= 19; $i++) {
    $p = new Product($i, false, 1);
    if (Validate::isLoadedObject($p)) {
        Category::addProduct($i);
    }
}

/**
 * Wrapper to expose the protected method getAjaxProductSearchVariables
 */
class TestCategoryController extends CategoryController {
    public function publicGetAjaxProductSearchVariables() {
        return $this->getAjaxProductSearchVariables();
    }
}

$controller = new TestCategoryController();
$context->controller = $controller;
$controller->category = $cat;

try {
    // This method is responsible for returning the data used to update the category page via AJAX
    $data = $controller->publicGetAjaxProductSearchVariables();

    echo "Checking for 'rendered_products_footer' in AJAX response...\n";

    if (isset($data['rendered_products_footer']) && !empty($data['rendered_products_footer'])) {
        echo "SUCCESS: 'rendered_products_footer' is present and rendered.\n";
        
        // Verify that the additional description is actually inside the rendered HTML
        if (strpos($data['rendered_products_footer'], 'Additional Description Test Content') !== false) {
            echo "SUCCESS: Additional description found in the footer HTML.\n";
            exit(0);
        } else {
            echo "FAILURE: 'rendered_products_footer' is present but does not contain the description.\n";
            exit(1);
        }
    } else {
        echo "FAILURE: 'rendered_products_footer' is missing from the response. The footer will not be updated on paginated pages.\n";
        exit(1);
    }
} catch (\Throwable $t) {
    echo "EXCEPTION: " . $t->getMessage() . "\n";
    exit(1);
}
