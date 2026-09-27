<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29619, validé pre/post automatiquement
require 'config/config.inc.php';

/**
 * Test for Ticket: Hook actionObjectUpdateAfter - Infinite loop that leads to memory limit in FO
 * 
 * The loop chain:
 * 1. Hook::exec('actionObjectUpdateAfter')
 * 2. -> getHookModuleExecList()
 * 3. -> getAllHookRegistrations()
 * 4. -> Customer::isLogged() (or similar check)
 * 5. -> Cookie::isSessionAlive()
 * 6. -> Cookie::getSession()
 * 7. -> CustomerSession::save()
 * 8. -> ObjectModel::update()
 * 9. -> Hook::exec('actionObjectUpdateAfter') -> LOOP
 */

// 1. Setup Context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);
$cookie = Context::getContext()->cookie;

// 2. Setup Customer
$customer = new Customer(1);
if (!Validate::isLoadedObject($customer)) {
    $customer = new Customer();
    $customer->firstname = 'Test';
    $customer->lastname = 'User';
    $customer->email = 'test@example.com';
    $customer->passwd = 'password';
    $customer->add();
}
Context::getContext()->customer = $customer;

// 3. Setup CustomerSession
// We need a session that is already in the DB so that getSession() loads it and save() calls update().
$session = new CustomerSession();
$session->id_customer = (int)$customer->id;
$session->save();
$id_session_pk = (int)$session->id;

// 4. Simulate logged-in state in the cookie
// Cookie::getSession($sessionId) uses the ID passed to the constructor, which is the primary key.
$cookie->id_customer = (int)$customer->id;
$cookie->session_id = $id_session_pk;

// 5. Setup Hook and Module to close the loop
$hookName = 'actionObjectUpdateAfter';
$id_hook = (int)Db::getInstance()->getValue('SELECT id_hook FROM '._DB_PREFIX_.'hook WHERE name = "'.pSQL($hookName).'"');
if (!$id_hook) {
    Db::getInstance()->execute('INSERT INTO '._DB_PREFIX_.'hook (name) VALUES ("'.pSQL($hookName).'")');
    $id_hook = (int)Db::getInstance()->getValue('SELECT id_hook FROM '._DB_PREFIX_.'hook WHERE name = "'.pSQL($hookName).'"');
}

$moduleName = 'loop_test_module';
$id_module = (int)Db::getInstance()->getValue('SELECT id_module FROM '._DB_PREFIX_.'module WHERE name = "'.pSQL($moduleName).'"');
if (!$id_module) {
    Db::getInstance()->execute('INSERT INTO '._DB_PREFIX_.'module (name, active) VALUES ("'.pSQL($moduleName).'", 1)');
    $id_module = (int)Db::getInstance()->getValue('SELECT id_module FROM '._DB_PREFIX_.'module WHERE name = "'.pSQL($moduleName).'"');
}

Db::getInstance()->execute('DELETE FROM '._DB_PREFIX_.'hook_module WHERE id_hook = '.$id_hook);
Db::getInstance()->execute('INSERT INTO '._DB_PREFIX_.'hook_module (id_module, id_hook) VALUES ('.$id_module.', '.$id_hook.')');

echo "Setup complete. Customer ID: {$customer->id}, Session PK: {$id_session_pk}\n";

// 6. Trigger the loop
// We set a memory limit that is slightly above current usage but low enough to crash during recursion.
// Since the environment uses ~25MB, we set it to 64MB.
ini_set('memory_limit', '64M');

try {
    echo "Triggering Hook::exec('actionObjectUpdateAfter') to detect infinite loop...\n";
    
    /**
     * This call should trigger the recursive chain.
     * If the fix is NOT present, Cookie::getSession() will instantiate a new CustomerSession 
     * and call save() every time, leading to an infinite loop of Hook::exec calls.
     * If the fix IS present, the session is cached in Cookie::$session, and save() is only called once.
     */
    Hook::exec($hookName, ['object' => $session]);
    
    echo "Success: No infinite loop detected.\n";
    exit(0);
} catch (\Throwable $t) {
    echo "Caught expected crash or exception: " . $t->getMessage() . "\n";
    // If it's a memory limit or recursion error, it's the bug.
    exit(1);
}
