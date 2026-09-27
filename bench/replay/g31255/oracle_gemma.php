<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #31255, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Core\Domain\Product\Exception\ProductNotFoundException;
use PrestaShopBundle\Controller\Admin\Sell\Catalog\Product\ProductController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\RedirectResponse;

/**
 * We create an anonymous class extending ProductController to mock the Symfony container
 * and the methods called within the catch block.
 */
$controller = new class extends ProductController {
    // Mock the container's get() method to trigger the exception
    public function get($id)
    {
        // To trigger the catch block in editAction, we throw the exception 
        // as soon as the controller tries to fetch a dependency.
        throw new ProductNotFoundException();
    }

    // Mock Symfony controller methods with EXACT signatures to avoid Fatal Errors
    public function addFlash($type, $message) {
        echo "Flash message added: $type - $message\n";
    }

    public function redirectToRoute($route, array $parameters = []) {
        echo "Redirecting to route: $route\n";
        return new RedirectResponse('/');
    }

    public function trans($key, $domain, array $parameters = []) {
        return "Translated string for $key";
    }

    public function getErrorMessageForException(\Throwable $e, array $messages) {
        return "Mocked error message";
    }

    public function getErrorMessages(\Throwable $e) {
        return ['error' => 'Mocked error'];
    }
};

$request = new Request();
$productId = 999;

try {
    echo "Calling ProductController::editAction for non-existent product $productId...\n";
    
    // The editAction method contains the try/catch block we are testing.
    // If the fix is applied, it will catch ProductNotFoundException and return a Response.
    // If the fix is NOT applied, the exception will bubble up.
    $response = $controller->editAction($request, $productId);

    if ($response instanceof \Symfony\Component\HttpFoundation\Response) {
        echo "Success: ProductNotFoundException was caught and a Response was returned.\n";
        exit(0);
    } else {
        echo "FAIL: editAction did not return a Response.\n";
        exit(1);
    }
} catch (ProductNotFoundException $e) {
    // This block is reached if the controller DOES NOT catch the exception (Bug present)
    echo "FAIL: ProductNotFoundException bubbled up to the test script (not caught by controller).\n";
    exit(1);
} catch (\Throwable $t) {
    // Any other error indicates a setup problem
    echo "Unexpected error: " . get_class($t) . " - " . $t->getMessage() . "\n";
    exit(1);
}
