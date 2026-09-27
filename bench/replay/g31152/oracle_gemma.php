<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #31152, validé pre/post automatiquement
require 'config/config.inc.php';

try {
    // 1. Setup: Create two countries with different zip code formats
    // France: 5 digits (NNNNN)
    $countryFR = new Country();
    $countryFR->iso_code = 'FR';
    $countryFR->zip_code_format = 'NNNNN';
    $countryFR->active = 1;
    $countryFR->contains_states = 0;
    $countryFR->need_identification_number = 0;
    $countryFR->display_tax_label = 1;
    $countryFR->name = array(1 => 'France');
    $countryFR->add();

    // Switzerland: 4 digits (NNNN)
    $countryCH = new Country();
    $countryCH->iso_code = 'CH';
    $countryCH->zip_code_format = 'NNNN';
    $countryCH->active = 1;
    $countryCH->contains_states = 0;
    $countryCH->need_identification_number = 0;
    $countryCH->display_tax_label = 1;
    $countryCH->name = array(1 => 'Switzerland');
    $countryCH->add();

    // 2. Configure the environment to trigger the bug
    // Set global default country to France
    Configuration::updateValue('PS_COUNTRY_DEFAULT', (int)$countryFR->id);

    $language = new Language(1);
    $translator = new Translator();
    
    // The formatter is initialized. We simulate the "Shop A" context where 
    // the default country is Switzerland.
    $formatter = new CustomerAddressFormatter($language);
    $formatter->setCountry($countryCH);

    // Instantiate the form. 
    // Based on PrestaShop 1.7/8 structure, the constructor typically takes:
    // (Translator, Smarty, Formatter, Language, Persister)
    $form = new CustomerAddressForm(
        $translator, 
        null, 
        $formatter, 
        $language, 
        null
    );

    // 3. Trigger the bug:
    // The user is adding an address for Switzerland.
    // The 'id_country' in params matches the current formatter country (Switzerland).
    // BEFORE FIX: The code skips the first 'if', goes to 'else', and resets the 
    // formatter country to PS_COUNTRY_DEFAULT (France).
    // AFTER FIX: The code enters the 'if' and keeps Switzerland.
    $params = [
        'id_country' => (int)$countryCH->id,
        'postcode' => '1234', // Valid Swiss postcode (4 digits), invalid French (5 digits)
        'city' => 'Zurich',
        'address1' => 'Street 1',
        'firstname' => 'John',
        'lastname' => 'Doe',
    ];

    $form->fillWith($params);

    echo "Selected Country ID: " . $params['id_country'] . "\n";
    echo "Formatter Country ID after fillWith: " . $formatter->getCountry()->id . "\n";
    echo "Formatter Country Format: " . $formatter->getCountry()->zip_code_format . "\n";
    echo "Postcode value: " . $params['postcode'] . "\n";

    $isValid = $form->validate();
    echo "Form is valid: " . ($isValid ? 'YES' : 'NO') . "\n";

    // If the bug is present, the formatter was reset to France (NNNNN), 
    // so '1234' is invalid. If fixed, it stays Switzerland (NNNN), so '1234' is valid.
    exit($isValid ? 0 : 1);

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
}
