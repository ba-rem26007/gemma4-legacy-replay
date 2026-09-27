<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #35023, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

try {
    // 1. Create a Store contact
    // We use an array for 'name' because Store is a multi-lang object (ObjectModel)
    $store = new Store();
    $store->name = [1 => 'Test Store']; 
    $store->id_country = 1;
    $store->city = 'Paris';
    $store->postcode = '75000';
    $store->active = 1;
    $store->date_add = date('Y-m-d H:i:s');
    $store->date_upd = date('Y-m-d H:i:s');
    
    // We set hours as a JSON string in the database to simulate existing data
    $store->hours = '["Mon: 09:00-18:00", "Tue: 09:00-18:00"]';
    $store->add();

    // 2. Instantiate the controller
    $controller = new AdminImportController();

    // 3. Prepare import data that DOES NOT contain 'hours'
    // We only want to update the city.
    $info = [
        'id' => $store->id,
        'city' => 'Lyon',
    ];

    // 4. Execute the import logic for one row
    // Signature: storeContactImportOne($info, $shop_is_feature_active, $regenerate, $force_ids, $validateOnly)
    $controller->storeContactImportOne($info, true, false, false, false);

    // Reload the store from DB to see what was actually saved
    $updatedStore = new Store($store->id);
    $observedHours = $updatedStore->hours;

    echo "Observed hours in DB: " . $observedHours . "\n";

    // BUG: If the bug is present, the code checks if $store->hours is an array.
    // If the Store class initializes $hours = [], then is_array is true, 
    // and it executes $store->hours = json_encode($newHours) where $newHours is empty.
    // This overwrites the existing DB hours with "[]".
    
    // If the fix is present, it checks isset($info['hours']), which is false here,
    // so the existing hours in the DB are preserved.
    if ($observedHours === '["Mon: 09:00-18:00", "Tue: 09:00-18:00"]') {
        echo "SUCCESS: Existing hours were preserved because 'hours' was not in the import data.\n";
        exit(0);
    } else {
        echo "FAILURE: Existing hours were overwritten (likely by '[]') despite being absent from import data.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
