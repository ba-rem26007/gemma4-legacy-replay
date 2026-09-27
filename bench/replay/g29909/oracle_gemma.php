<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29909, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShopBundle\Entity\Repository\StockRepository;
use PrestaShop\PrestaShop\Adapter\Context\ContextAdapter;
use PrestaShop\PrestaShop\Adapter\Image\ImageManager;
use PrestaShop\PrestaShop\Adapter\Stock\StockManager;

// 1. Setup Multishop environment
Configuration::updateValue('PS_MULTISHOP', 1);

$idShop1 = 1;
$idLang = 1;
$idProduct = 1;

// Ensure Shop 2 exists with required fields
$shop2 = new Shop(2);
if (!Validate::isLoadedObject($shop2)) {
    $shop2 = new Shop();
    $shop2->id_shop_group = 1;
    $shop2->name = 'Test Shop 2';
    $shop2->active = 1;
    $shop2->id_category = 2; 
    $shop2->add();
}
$idShop2 = (int)$shop2->id;

// 2. Prepare Product data
// Ensure Product 1 exists and is valid
$p = new Product($idProduct);
if (!Validate::isLoadedObject($p)) {
    $p = new Product();
    $p->price = 10;
    $p->add();
    $idProduct = (int)$p->id;
} else {
    $p->price = 10;
    $p->save();
}

// Associate product with both shops in product_shop
Db::getInstance()->execute('DELETE FROM '._DB_PREFIX_.'product_shop WHERE id_product = '.(int)$idProduct);
Db::getInstance()->insert('product_shop', [
    'id_product' => $idProduct,
    'id_shop' => $idShop1,
    'id_shop_default' => 1,
    'active' => 1,
    'visibility' => 'both'
]);
Db::getInstance()->insert('product_shop', [
    'id_product' => $idProduct,
    'id_shop' => $idShop2,
    'id_shop_default' => 0,
    'active' => 1,
    'visibility' => 'both'
]);

// Create distinct names for the product in each shop
Db::getInstance()->execute('DELETE FROM '._DB_PREFIX_.'product_lang WHERE id_product = '.(int)$idProduct);
Db::getInstance()->insert('product_lang', [
    'id_product' => $idProduct,
    'id_shop' => $idShop1,
    'id_lang' => $idLang,
    'name' => 'Name Shop 1',
    'link_rewrite' => 'name-shop-1'
]);
Db::getInstance()->insert('product_lang', [
    'id_product' => $idProduct,
    'id_shop' => $idShop2,
    'id_lang' => $idLang,
    'name' => 'Name Shop 2',
    'link_rewrite' => 'name-shop-2'
]);

// 3. Instantiate StockRepository
// We use a proxy to access protected methods and avoid dependency on Doctrine Connection in CLI
class TestStockRepository extends StockRepository {
    public function publicSelectSql($andWhere = '', $having = '', $orderBy = null) {
        return $this->selectSql($andWhere, $having, $orderBy);
    }
    // Override to avoid potential DBAL calls in the original method
    protected function orderByProductIds() {
        return 'p.id_product ASC';
    }
}

$repo = new TestStockRepository(
    null, // ContainerInterface
    null, // Connection (not used by selectSql)
    null, // EntityManager
    new ContextAdapter(),
    new ImageManager(),
    new StockManager(),
    _DB_PREFIX_
);

// 4. Execute the query for Shop 2
// We pass a filter for our specific product to isolate the test
$sql = $repo->publicSelectSql(' AND p.id_product = ' . (int)$idProduct);

// Replace Symfony/Doctrine placeholders with actual values
$sql = str_replace(':shop_id', $idShop2, $sql);
$sql = str_replace(':language_id', $idLang, $sql);
$sql = str_replace(':stock_shop_id', $idShop2, $sql);
$sql = str_replace(':stock_group_id', 1, $sql);

$results = Db::getInstance()->executeS($sql);

// 5. Analysis
$foundNames = [];
foreach ($results as $row) {
    if (isset($row['name'])) {
        $foundNames[] = $row['name'];
    }
}

echo "Shop 2 query results names: " . implode(', ', $foundNames) . "\n";

// The bug: without the pl.id_shop filter, the JOIN on product_lang returns 
// all translations for that product across all shops.
// If the fix is applied, we should get exactly 1 row with the name for Shop 2.
$isCorrect = (count($foundNames) === 1 && $foundNames[0] === 'Name Shop 2');

if (!$isCorrect) {
    echo "BUG: Expected exactly 1 result ('Name Shop 2'), but found " . count($foundNames) . " results.\n";
    exit(1);
}

echo "SUCCESS: Only the correct name for Shop 2 was retrieved.\n";
exit(0);
