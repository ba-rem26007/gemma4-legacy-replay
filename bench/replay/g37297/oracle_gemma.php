<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37297, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShopBundle\Form\Admin\Improve\Shipping\Carrier\Type\CostsZoneType;
use Symfony\Component\Form\Forms;
use Symfony\Contracts\Translation\TranslatorInterface;

/**
 * Test for Ticket: Feature flag Carrier page - Exception displayed when deleting a range for a specific zone
 * 
 * The bug occurs because 'allow_delete' is missing in the CollectionType configuration of CostsZoneType.
 * When a user deletes a range in the UI, Symfony receives a payload like ['ranges' => ['0' => ['_delete' => true]]].
 * If 'allow_delete' is false (default), Symfony does not treat '_delete' as a special instruction to remove 
 * the element. Instead, it tries to map the array ['_delete' => true] to the entry_type (CostsRangeType).
 * This causes a PHP 8 type error ("cannot be interpreted as a number") when the form tries to 
 * validate or transform the data into the expected numeric fields of the range.
 */

// 1. Mock the TranslatorInterface required by TranslatorAwareType
$translator = new class implements TranslatorInterface {
    public function trans($id, array $parameters = [], string $domain = null, string $locale = null): string {
        return $id;
    }
    public function getLocale(): string {
        return 'fr';
    }
};

// 2. Setup minimal data for the form payload
$id_zone = 1;
$zone = new Zone($id_zone);
if (!Validate::isLoadedObject($zone)) {
    $zone = new Zone();
    $zone->name = 'Test Zone';
    $zone->active = 1;
    $zone->add();
    $id_zone = (int)$zone->id;
}

try {
    // 3. Instantiate the Form
    // Since we are in CLI and the Symfony container is not available, we instantiate the type manually.
    // CostsZoneType extends TranslatorAwareType, which requires (TranslatorInterface, string $domain).
    $factory = Forms::createFormFactory();
    $type = new CostsZoneType($translator, 'Admin.Shipping.Feature');
    $form = $factory->create($type);

    // 4. Simulate the payload sent by the JS when deleting a range.
    // The 'ranges' field is a CollectionType. 
    // The key '0' represents the index of the range, and '_delete' => true is the Symfony signal for deletion.
    $formData = [
        'zoneId' => $id_zone,
        'ranges' => [
            '0' => [
                '_delete' => true,
            ],
        ],
    ];

    echo "Submitting form with range deletion payload (['_delete' => true])...\n";
    
    // This call triggers the mapping process. 
    // If 'allow_delete' => true is missing in CostsZoneType, Symfony will attempt to process 
    // the array ['_delete' => true] as a range object, triggering the type error.
    $form->submit($formData);
    
    echo "Success: Form submitted without exception. The fix (allow_delete => true) is working.\n";
    exit(0);
} catch (\Throwable $t) {
    echo "Caught exception: " . $t->getMessage() . "\n";
    
    // The bug manifests as a PHP 8 type error during data transformation/validation
    // typically mentioning that a value (the array or empty string) cannot be interpreted as a number.
    if (strpos($t->getMessage(), 'cannot be interpreted as a number') !== false) {
        echo "Bug reproduced: Exception 'cannot be interpreted as a number' detected.\n";
        exit(1);
    }
    
    // Any other exception during form submission also indicates a failure in the form configuration
    echo "An unexpected exception occurred: " . $t->getMessage() . "\n";
    exit(1);
}
