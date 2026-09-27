<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34351, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

// Ensure product 1 exists
$product = new Product(1);
if (!Validate::isLoadedObject($product)) {
    $product = new Product();
    $product->price = 10.0;
    $product->id_category_default = 2;
    $product->name = [1 => 'Test Product'];
    $product->link_rewrite = [1 => 'test-product'];
    $product->add();
}

// Create a dummy image file to upload
$tmpFile = tempnam(sys_get_temp_dir(), 'ps_img');
$imgContent = imagecreatetruecolor(100, 100);
imagejpeg($imgContent, $tmpFile);
imagedestroy($imgContent);

// Mock $_FILES for HelperImageUploader
$_FILES['file'] = [
    'name' => 'test_image.jpg',
    'type' => 'image/jpeg',
    'tmp_name' => $tmpFile,
    'error' => 0,
    'size' => filesize($tmpFile),
];

// Mock Tools::getValue for legends
$_POST['legend'] = ['1' => 'Test Legend'];

try {
    $controller = new AdminProductsController();
    
    // We call the method that is the subject of the fix
    // In the "Before" state, $this->get(ImageFormatConfiguration::class) fails in CLI/Legacy context
    $controller->ajaxProcessaddProductImage(1, 'file');

    // Get the ID of the image just created
    $idImage = (int) Db::getInstance()->getValue('SELECT MAX(id_image) FROM ' . _DB_PREFIX_ . 'image');
    
    if ($idImage <= 0) {
        echo "Error: No image was created in the database.\n";
        exit(1);
    }

    // Determine the path to the image
    // PrestaShop stores images in img/p/1/2/3/123.jpg
    $path = 'img/p/';
    $idStr = (string)$idImage;
    for ($i = 0; $i < strlen($idStr) - 1; $i++) {
        $path .= $idStr[$i] . '/';
    }
    $path .= $idStr;

    echo "Original image path: $path.jpg\n";
    
    // Check if the original image exists
    if (!file_exists($path . '.jpg')) {
        echo "Original image file not found on disk.\n";
        exit(1);
    }

    // Check for thumbnails. 
    // If the fix is working, files like product_1_1-small_default.jpg (or similar) should exist.
    // We look for any file in that directory containing a hyphen (which denotes the size suffix).
    $files = glob($path . '-*.jpg');
    $thumbnailCount = count($files);
    
    echo "Thumbnails found: $thumbnailCount\n";

    // If thumbnails are created, the bug is fixed.
    if ($thumbnailCount > 0) {
        exit(0);
    } else {
        echo "No thumbnails were generated. Bug is still present.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Exception caught: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
} finally {
    if (file_exists($tmpFile)) {
        unlink($tmpFile);
    }
}
