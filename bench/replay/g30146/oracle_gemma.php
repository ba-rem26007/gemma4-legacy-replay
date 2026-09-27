<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #30146, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test for Ticket: The override directory is deleted when overrides are uninstalled
 * The bug is in Module::removeOverrideDirectory where the loop condition 
 * uses getPathname() instead of getRealPath(), causing it to potentially 
 * bypass the stop condition and delete the root /override directory.
 */

// Module is abstract, we need a concrete implementation to instantiate it
class TestModule extends Module {
    public function __construct() {
        parent::__construct('testmodule', 'Test Module');
    }
}

// 1. Setup environment
$dirOverride = _PS_ROOT_DIR_ . DIRECTORY_SEPARATOR . 'override';
$dirClasses = $dirOverride . DIRECTORY_SEPARATOR . 'classes';

// Ensure we have a clean state for the test
if (!is_dir($dirOverride)) {
    mkdir($dirOverride, 0777, true);
}
if (!is_dir($dirClasses)) {
    mkdir($dirClasses, 0777, true);
}

// Create the files that should be handled
// /override/index.php should be PRESERVED
$indexOverride = $dirOverride . DIRECTORY_SEPARATOR . 'index.php';
file_put_contents($indexOverride, '<?php');

// /override/classes/index.php should be DELETED
$indexClasses = $dirClasses . DIRECTORY_SEPARATOR . 'index.php';
file_put_contents($indexClasses, '<?php');

// To trigger the bug, the directory must contain ONLY index.php 
// (or be empty) so that the Finder doesn't find other files and break the loop.
$files = glob($dirClasses . DIRECTORY_SEPARATOR . '*');
foreach ($files as $file) {
    if (basename($file) !== 'index.php') {
        unlink($file);
    }
}

echo "Setup: /override/index.php exists: " . (file_exists($indexOverride) ? 'Yes' : 'No') . "\n";
echo "Setup: /override/classes/index.php exists: " . (file_exists($indexClasses) ? 'Yes' : 'No') . "\n";

try {
    // 2. Call the private method removeOverrideDirectory via Reflection
    $module = new TestModule();
    $reflection = new ReflectionClass($module);
    $method = $reflection->getMethod('removeOverrideDirectory');
    $method->setAccessible(true);

    echo "Executing removeOverrideDirectory...\n";
    // We simulate the call: remove the 'classes' subtree but stop at 'override'
    // We use realpath to ensure the comparison in the loop is tested against a resolved path
    $method->invoke($module, realpath($dirOverride), realpath($dirClasses));

} catch (\Throwable $e) {
    echo "Error during execution: " . $e->getMessage() . "\n";
    exit(1);
}

// 3. Verification
$indexExists = file_exists($indexOverride);
$classesExists = is_dir($dirClasses);

echo "Result - /override/index.php exists: " . ($indexExists ? 'Yes' : 'No') . "\n";
echo "Result - /override/classes directory exists: " . ($classesExists ? 'Yes' : 'No') . "\n";

// The bug is that /override/index.php is deleted because getPathname() 
// does not match the realpath of $directoryOverride.
if ($indexExists) {
    echo "SUCCESS: /override/index.php was preserved.\n";
    exit(0);
} else {
    echo "FAILURE: /override/index.php was deleted.\n";
    exit(1);
}
