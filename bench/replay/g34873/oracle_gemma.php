<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #34873, validé pre/post automatiquement
require 'config/config.inc.php';

use PrestaShop\PrestaShop\Adapter\EntityMapper;

/**
 * Dummy class extending ObjectModel to satisfy the type hint in EntityMapper::load
 */
class DummyObjectModel extends ObjectModel
{
    public $name;
}

try {
    // We use the 'category' table because it exists and has a corresponding '_lang' table.
    // The bug occurs when a field is marked as TYPE_BOOL and translatable ('lang' => true),
    // and the EntityMapper loads the object without a specific language ID (loading all languages).
    $entity = new DummyObjectModel();
    $entity_defs = [
        'classname' => 'DummyObjectModel',
        'table' => 'category',
        'primary' => 'id_category',
        'multilang' => true,
        'fields' => [
            // We pretend 'name' (which is a string in ps_category_lang) is a boolean.
            // This will force the mapper to attempt a (string) cast on the array of names.
            'name' => [
                'type' => \ObjectModel::TYPE_BOOL, 
                'lang' => true
            ],
        ],
    ];

    $mapper = new EntityMapper();
    
    // $id_lang = null triggers the loading of all languages, which results in 
    // translatable fields being populated as arrays.
    $mapper->load(
        1,      // id_category 1 exists in demo data
        null,   // id_lang = null to trigger the array-to-string bug
        $entity, 
        $entity_defs, 
        1,      // id_shop
        false   // should_cache_objects
    );

    echo "Value of entity->name: " . print_r($entity->name, true) . "\n";

    // BEFORE FIX: $entity->name becomes the string "Array" due to (string) $value
    // AFTER FIX: $entity->name remains an array of strings
    if (is_array($entity->name)) {
        echo "Success: Field is an array.\n";
        exit(0);
    } else {
        echo "Failure: Field was cast to string (likely 'Array').\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
