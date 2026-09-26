<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37009, validé pre/post automatiquement
require 'config/config.inc.php';

// Setup context
Context::getContext()->shop = new Shop(1);
Context::getContext()->language = new Language(1);

/**
 * Dummy module to capture the hook parameters.
 * PrestaShop's Hook::exec will instantiate this class if it's defined and registered.
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
    // 1. Prepare the dummy module in the database
    $moduleName = 'hooktestmodule';
    Db::getInstance()->execute('DELETE FROM ' . _DB_PREFIX_ . 'module WHERE name = "' . $moduleName . '"');
    Db::getInstance()->execute('INSERT INTO ' . _DB_PREFIX_ . 'module (name, active) VALUES ("' . $moduleName . '", 1)');
    
    // 2. Register the module to the specific hook
    Db::getInstance()->execute('DELETE FROM ' . _DB_PREFIX_ . 'hook_module WHERE module = "' . $moduleName . '"');
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
