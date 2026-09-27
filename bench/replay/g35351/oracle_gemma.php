<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35351, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test de non-régression pour le bug de conversion des chaînes vides en NULL
 * lors de la sauvegarde de la base de données (PrestaShopBackup).
 */

// S'assurer que la constante _PS_ADMIN_DIR_ est définie pour éviter le crash
if (!defined('_PS_ADMIN_DIR_')) {
    define('_PS_ADMIN_DIR_', _PS_ROOT_DIR_ . 'admin/');
}

// 1. Préparation des données : on utilise le produit 1
$p = new Product(1);
$p->reference = 'REGRESSION_BACKUP_TEST';
$p->isbn = ''; // Champ nullable : doit rester '' et non devenir NULL
$p->upc = '';  // Champ nullable
$p->mpn = '';  // Champ nullable
$p->save();

// 2. Configuration de l'environnement de backup
// On utilise un dossier temporaire pour éviter les problèmes de permissions sur /admin/
$tmpBackupDir = '/tmp/ps_backup_test/';
if (!is_dir($tmpBackupDir)) {
    mkdir($tmpBackupDir, 0777, true);
}

$backup = new PrestaShopBackup();
$backup->id = 'test_regression_nulls';
$backup->psBackupAll = true;
$backup->psBackupDropTable = true;
$backup->customBackupDir = $tmpBackupDir;

try {
    // 3. Exécution du backup
    // La méthode add() génère le fichier SQL et retourne son nom
    $filename = $backup->add();
    $filePath = $tmpBackupDir . $filename;

    if (!file_exists($filePath)) {
        echo "Erreur : Le fichier de backup n'a pas été créé : $filePath\n";
        exit(1);
    }

    $content = file_get_contents($filePath);
    
    // 4. Analyse du résultat
    $foundLine = false;
    $hasEmptyString = false;
    $hasNull = false;

    $lines = explode("\n", $content);
    foreach ($lines as $line) {
        // On cherche la ligne d'insertion du produit de test via sa référence
        if (strpos($line, 'INSERT INTO `' . _DB_PREFIX_ . 'product`') !== false && strpos($line, 'REGRESSION_BACKUP_TEST') !== false) {
            $foundLine = true;
            
            // On vérifie si la ligne contient des chaînes vides '' ou des NULL
            // Le bug remplace '' par NULL pour les champs nullable (isbn, upc, mpn).
            if (strpos($line, "''") !== false) {
                $hasEmptyString = true;
            }
            if (strpos($line, "NULL") !== false) {
                $hasNull = true;
            }
            break;
        }
    }

    if (!$foundLine) {
        echo "Erreur : La ligne d'insertion du produit de test n'a pas été trouvée dans le backup.\n";
        exit(1);
    }

    echo "Ligne trouvée : " . ($hasEmptyString ? "Contient ''" : "Ne contient pas ''") . " | " . ($hasNull ? "Contient NULL" : "Ne contient pas NULL") . "\n";

    /**
     * Diagnostic :
     * - Si le bug est présent : isbn='' devient NULL. La ligne contiendra NULL et PAS de ''.
     * - Si le bug est corrigé : isbn='' reste ''. La ligne contiendra ''.
     */
    if ($hasEmptyString) {
        echo "Succès : Les chaînes vides sont préservées.\n";
        exit(0);
    } else {
        echo "Échec : Les chaînes vides ont été converties en NULL (Bug présent).\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Exception capturée : " . $t->getMessage() . "\n";
    exit(1);
}
