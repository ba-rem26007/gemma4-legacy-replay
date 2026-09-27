<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37030, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
$context = Context::getContext();
$context->employee = new Employee(1);
$context->shop->id = 1;
$context->language = new Language(1);

// We create a ShopGroup object in memory.
// We don't call ->add() to avoid SQL errors since ps_shop_group is not in the provided table list,
// but renderForm() only reads the object properties.
$sg = new ShopGroup();
$sg->id = 1;
$sg->active = 0; // Disabled

// Instantiate the controller
$controller = new AdminShopGroupController();
$controller->context = $context;
$controller->object = $sg;
$controller->display = 'edit';

// Trigger the method that contains the bug
$controller->renderForm();

// The bug is that 'active' is hardcoded to true in fields_value regardless of the object state
$observed = $controller->fields_value['active'];

echo "ShopGroup active status: " . (int)$sg->active . "\n";
echo "Form field 'active' value: " . ($observed ? 'true' : 'false') . "\n";

// If the bug is fixed, $observed should be false (matching $sg->active)
// If the bug is present, $observed will be true.
exit($observed === false ? 0 : 1);
