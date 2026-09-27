<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29741, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Ticket BOOM-5382: The configuration data is lost after reloading dashboard page.
 * 
 * The bug is caused by the fact that the Configuration class uses a static cache 
 * that is shared across different configuration tables. 
 * 
 * When Configuration::loadConfiguration() is called (e.g., during page boot), 
 * it populates the cache with values from the default 'ps_configuration' table.
 * 
 * When ConfigurationKPI::get() is called, it switches the table definition to 
 * 'ps_configuration_kpi'. However, if the same key exists in both tables, 
 * Configuration::get() will return the value already present in the cache 
 * (from the 'ps_configuration' table) instead of querying the 'ps_configuration_kpi' table.
 * 
 * The fix ensures that when the KPI definition is set, the cache for the 
 * KPI table is explicitly loaded, overriding any conflicting global values.
 */

$key = 'BOOM_5382_TEST_KEY';
$globalValue = 'GLOBAL_VALUE';
$kpiValue = 'KPI_VALUE';

// 1. Setup: Create the same key in both tables with different values.
// Configuration::updateValue updates ps_configuration
Configuration::updateValue($key, $globalValue);
// ConfigurationKPI::updateValue updates ps_configuration_kpi
ConfigurationKPI::updateValue($key, $kpiValue);

// 2. Simulate a page reload: Clear the static cache.
try {
    $ref = new ReflectionClass('Configuration');
    $cacheProp = $ref->getProperty('_cache');
    $cacheProp->setAccessible(true);
    $cacheProp->setValue(null, []);
} catch (\Throwable $e) {
    echo "Reflection failed: " . $e->getMessage() . "\n";
    exit(1);
}

// 3. Simulate the boot process: loadConfiguration() is called for the default table.
// This fills the cache with the value from ps_configuration.
Configuration::loadConfiguration();

// 4. Attempt to retrieve the KPI value.
// Before the fix: ConfigurationKPI::get() switches the table to 'configuration_kpi',
// but Configuration::get() finds the key in the shared cache and returns the global value.
// After the fix: ConfigurationKPI::setKpiDefinition() calls parent::loadConfiguration(),
// which refreshes the cache with values from 'ps_configuration_kpi'.
$observedValue = ConfigurationKPI::get($key);

echo "Expected (KPI) value: $kpiValue\n";
echo "Observed value: $observedValue\n";

if ($observedValue === $globalValue) {
    echo "BUG DETECTED: The global configuration value was returned instead of the KPI value.\n";
    exit(1);
}

if ($observedValue === $kpiValue) {
    echo "SUCCESS: The KPI configuration value was correctly retrieved.\n";
    exit(0);
}

echo "Unexpected value observed.\n";
exit(1);
