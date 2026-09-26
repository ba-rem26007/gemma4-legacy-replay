<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37009, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

/**
 * Dummy module to capture the hook parameters.
 */
class HookTestModule extends Module
{
    public static $capturedParams = [];

    public function __construct()
    {
        $this->name = 'hooktestmodule';
        $this->tab = 'administration';
        $this->version = '1.0';
        $this->author = 'Test';
        parent::__construct();
    }

    public function hookActionEmailSendBefore($params)
    {
        self::$capturedParams = $params;
    }
}

try {
    $moduleName = 'hooktestmodule';
    
    // 1. Ensure the module exists in the ps_module table
    $idModule = (int)Db::getInstance()->getValue('SELECT id_module FROM ' . _DB_PREFIX_ . 'module WHERE name = "' . pSQL($moduleName) . '"');
    if (!$idModule) {
        Db::getInstance()->execute('INSERT INTO ' . _DB_PREFIX_ . 'module (name, active) VALUES ("' . pSQL($moduleName) . '", 1)');
        $idModule = (int)Db::getInstance()->getValue('SELECT id_module FROM ' . _DB_PREFIX_ . 'module WHERE name = "' . pSQL($moduleName) . '"');
    }

    // 2. Register the module to the hook using the PrestaShop API
    // This handles the insertion into ps_hook_module correctly using id_module
    Hook::registerHook('actionEmailSendBefore', $moduleName);

    // 3. Disable actual mail sending to avoid errors/spam during test
    Configuration::updateValue('PS_MAIL_METHOD', Mail::METHOD_DISABLE);

    // 4. Define test data
    $idLang = 1;
    $template = 'contact';
    $subject = 'Test Subject';
    $templateVars = [];
    $to = 'recipient@example.com';
    $toName = 'Recipient Name';
    $from = 'sender@example.com';
    $fromName = 'Sender Name';
    $replyTo = 'reply@example.com';
    $replyToName = 'Reply To Name Special';

    // 5. Trigger Mail::send()
    // Signature: send($idLang, $template, $subject, $templateVars, $to, $toName, $from, $fromName, $fileAttachment, $modeSend, $templatePath, $bcc, $replyTo, $replyToName)
    Mail::send(
        $idLang,
        $template,
        $subject,
        $templateVars,
        $to,
        $toName,
        $from,
        $fromName,
        null,
        Mail::METHOD_DISABLE,
        _PS_MAIL_DIR_,
        null,
        $replyTo,
        $replyToName
    );

    // 6. Verify if replyToName was passed to the hook
    $params = HookTestModule::$capturedParams;
    
    echo "Hook parameters captured:\n";
    echo "replyTo: " . ($params['replyTo'] ?? 'NOT FOUND') . "\n";
    echo "replyToName: " . ($params['replyToName'] ?? 'NOT FOUND') . "\n";

    if (isset($params['replyToName']) && $params['replyToName'] === $replyToName) {
        echo "SUCCESS: replyToName is present and correct.\n";
        exit(0);
    } else {
        echo "FAILURE: replyToName is missing or incorrect.\n";
        exit(1);
    }

} catch (\Throwable $t) {
    echo "ERROR: " . $t->getMessage() . "\n";
    exit(1);
}
