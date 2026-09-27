<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30309, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * The bug occurs in WebserviceOutputBuilder::renderFlatAssociation.
 * When $fields_assoc is a numerically indexed array (e.g. [0 => ['id' => 123]]),
 * the old code checks if the key ($field_name) is equal to 'id'.
 * Since 0 != 'id', it falls into the elseif and sets $field['sqlId'] = 0.
 * This results in an XML tag <0>, which is invalid.
 * 
 * The fix changes the check to see if the field array itself contains an 'id' key.
 */

class TestWebserviceOutputBuilder extends WebserviceOutputBuilder
{
    public function publicRenderFlatAssociation($object, $depth, $assoc_name, $resource_name, $fields_assoc, $object_assoc, $parent_details)
    {
        return $this->renderFlatAssociation($object, $depth, $assoc_name, $resource_name, $fields_assoc, $object_assoc, $parent_details);
    }
}

try {
    // Setup Context
    Context::getContext()->shop = new Shop(1);
    Context::getContext()->language = new Language(1);

    // Instantiate the builder and the renderer
    $builder = new TestWebserviceOutputBuilder('/api');
    $builder->setObjectRender(new WebserviceOutputCore());

    // Mock data that triggers the bug
    // This structure is exactly what happens in renderAssociations when $fields_assoc is empty
    // and the association value has an 'id'.
    $fields_assoc = [
        0 => ['id' => 123] 
    ];
    $object_assoc = ['id' => 123];
    $product = new Product(1);

    // Execute the method
    $output = $builder->publicRenderFlatAssociation(
        $product, 
        0, 
        'test_assoc', 
        'test_resource', 
        $fields_assoc, 
        $object_assoc, 
        ''
    );

    echo "Output generated: " . $output . "\n";

    // The bug is the presence of a tag starting with a number (specifically <0>)
    // The fix ensures the tag is <id>
    if (strpos($output, '<0>') !== false) {
        echo "Bug reproduced: XML tag starts with a number (<0>).\n";
        exit(1);
    }

    if (strpos($output, '<id>') !== false) {
        echo "Success: XML tag is correctly named <id>.\n";
        exit(0);
    }

    echo "Unexpected output format.\n";
    exit(1);

} catch (\Throwable $t) {
    echo "Error: " . $t->getMessage() . "\n";
    exit(1);
}
