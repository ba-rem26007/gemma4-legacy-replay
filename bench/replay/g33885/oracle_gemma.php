<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #33885, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Wrapper to access protected methods of FrontController
 */
class TestFrontController extends FrontController
{
    public function publicGetAlternativeLangsUrl()
    {
        return $this->getAlternativeLangsUrl();
    }
}

// 1. Setup Environment
$context = Context::getContext();
$context->shop = new Shop(1);
$context->language = new Language(1);
$context->currency = new Currency(1);

// Ensure at least two languages are active for the test
$languages = Language::getLanguages(true, 1);
if (count($languages) < 2) {
    $l2 = new Language();
    $l2->name = 'English';
    $l2->iso_code = 'en';
    $l2->id_parent = 0;
    $l2->active = 1;
    $l2->add();
    // Link to shop 1
    Db::getInstance()->execute('INSERT INTO '._DB_PREFIX_.'language_shop (id_language, id_shop) VALUES ('.(int)$l2->id.', 1)');
}

// 2. Enable routes and simulate a request to a routed module page
Configuration::updateValue('PS_ROUTE_ENABLED', 1);

// Simulate the current request URI and parameters
$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['REQUEST_URI'] = '/blog/category/15_des-conseils.html';
$_GET['slug'] = 'des-conseils';
$_GET['module'] = 'smartblog';
$_GET['controller'] = 'category';

// 3. Setup a custom route to simulate the SmartBlog module behavior
$dispatcher = Dispatcher::getInstance();
$dispatcher->addRoute(
    'blog_category', 
    'blog/category/{id}-{slug}.html', 
    'category', 
    1, 
    ['id' => ['param' => 'id_category', 'required' => true], 'slug' => ['param' => 'slug', 'required' => true]]
);

// 4. Execute the code
$fc = new TestFrontController();
$fc->context = $context;
$fc->context->link = new Link();

try {
    $altUrls = $fc->publicGetAlternativeLangsUrl();
    
    if (empty($altUrls)) {
        echo "No alternative URLs generated. Check language configuration.\n";
        exit(1);
    }

    echo "Alternative URLs found: " . count($altUrls) . "\n";
    
    $bugFound = false;
    foreach ($altUrls as $iso => $url) {
        echo "Lang $iso: $url\n";
        // The URL should be rewritten and NOT contain the redundant query parameters from $_GET
        // because they are already part of the rewritten path.
        if (strpos($url, 'slug=des-conseils') !== false || strpos($url, 'module=smartblog') !== false) {
            $bugFound = true;
        }
    }

    if ($bugFound) {
        echo "BUG: Unwanted parameters from \$_GET found in alternate URLs.\n";
        exit(1);
    } else {
        echo "SUCCESS: Alternate URLs are clean.\n";
        exit(0);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
