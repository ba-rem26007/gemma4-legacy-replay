<?php
// Test Oracle pour le bug de fuite de contexte Shop::setContext dans DeleteLanguageHandler
require_once "/var/www/html/config/config.inc.php";

echo "=== TEST PRESTASHOP MULTI-SHOP CONTEXT LEAK ===\n";

// 1. Initialiser le contexte boutique sur Shop 1
Shop::setContext(Shop::CONTEXT_SHOP, 1);
$initialContext = Shop::getContext();
$initialShopId = Shop::getContextShopID();

if ($initialContext !== Shop::CONTEXT_SHOP || $initialShopId !== 1) {
    echo "FAIL: Impossible d'initialiser le contexte sur Shop 1\n";
    exit(1);
}

// 2. Créer une langue de test temporaire
$lang = new Language();
$lang->name = "Test Language Context";
$lang->iso_code = "tl";
$lang->locale = "tl-TL";
$lang->language_code = "tl-tl";
$lang->date_format_lite = "Y-m-d";
$lang->date_format_full = "Y-m-d H:i:s";
$lang->active = 0;
if (!$lang->save()) {
    echo "FAIL: Impossible de creer la langue de test\n";
    exit(1);
}
$langId = $lang->id;

// 3. Exécuter le handler via le container Symfony
global $kernel;
if (!$kernel) {
    require_once '/var/www/html/app/AppKernel.php';
    $kernel = new AppKernel('prod', false);
    $kernel->boot();
}

$commandBus = $kernel->getContainer()->get('prestashop.core.command_bus');
$deleteCommand = new \PrestaShop\PrestaShop\Core\Domain\Language\Command\DeleteLanguageCommand((int)$langId);

try {
    $commandBus->handle($deleteCommand);
} catch (Throwable $e) {
    echo "Erreur execution command: " . $e->getMessage() . "\n";
}

// 4. Vérifier si le contexte a été préservé ou corrompu
$afterContext = Shop::getContext();
$afterShopId = Shop::getContextShopID();

echo "Contexte initial : Context=$initialContext, ShopID=$initialShopId\n";
echo "Contexte après delete : Context=$afterContext, ShopID=" . var_export($afterShopId, true) . "\n";

if ($afterContext === Shop::CONTEXT_ALL || $afterShopId === null) {
    echo "FAIL: FUITE DE CONTEXTE DÉTECTÉE (Le contexte global est resté corrompu à CONTEXT_ALL / NULL)\n";
    exit(1);
}

if ($afterContext === $initialContext && $afterShopId === $initialShopId) {
    echo "PASS: Le contexte boutique a été fidèlement restauré (Isolation garantie)\n";
    exit(0);
}

echo "FAIL: Contexte inattendu\n";
exit(1);
