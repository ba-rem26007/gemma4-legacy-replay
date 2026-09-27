<?php
// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #29638, validé pre/post automatiquement
require 'config/config.inc.php';

use WebserviceRequest;
use WebserviceSpecificManagementAttachments;
use Attachment;

try {
    // 1. Setup: Create an existing attachment to update
    $attachment = new Attachment();
    $attachment->file = 'old_file.txt';
    $attachment->file_name = 'old_file.txt';
    $attachment->mime = 'text/plain';
    $attachment->add();
    $id = $attachment->id;

    // Set an initial name to test the name-preservation fix
    $defaultLangId = (int)Configuration::get('PS_LANG_DEFAULT');
    $attachment->name[$defaultLangId] = 'Original Name';
    $attachment->update();

    echo "Attachment created with ID: $id, File: {$attachment->file}, Name: {$attachment->name[$defaultLangId]}\n";

    // 2. Simulate a PATCH request to update the file
    // We simulate the environment that the Webservice would have
    $_SERVER['REQUEST_METHOD'] = 'PATCH';
    $_POST['name'] = 'New Name (should not overwrite)';
    
    $tmpFile = tempnam(sys_get_temp_dir(), 'ps_test');
    file_put_contents($tmpFile, 'new content for the file');
    
    $_FILES['file'] = [
        'name' => 'new_file.txt',
        'type' => 'text/plain',
        'tmp_name' => $tmpFile,
        'error' => 0,
        'size' => strlen('new content for the file'),
    ];

    // Instantiate the request object
    $request = new WebserviceRequest();
    $request->method = 'PATCH';
    // urlSegment[0] = 'file' triggers executeFileAddAndEdit()
    $request->urlSegment = ['file', $id];

    // Instantiate the manager
    $manager = new WebserviceSpecificManagementAttachments();
    $manager->setWsObject($request);

    // Execute the logic
    $manager->manage();

    // 3. Verification
    $updatedAttachment = new Attachment($id);
    
    echo "Updated File: " . $updatedAttachment->file . "\n";
    echo "Updated Name: " . $updatedAttachment->name[$defaultLangId] . "\n";

    $fileUpdated = ($updatedAttachment->file !== 'old_file.txt');
    $namePreserved = ($updatedAttachment->name[$defaultLangId] === 'Original Name');

    if (!$fileUpdated) {
        echo "FAIL: The file was not updated. PATCH method is likely not handled in manageAttachments().\n";
        exit(1);
    }

    if (!$namePreserved) {
        echo "FAIL: The attachment name was overwritten, but it should have been preserved if already set.\n";
        exit(1);
    }

    echo "SUCCESS: File updated and name preserved via PATCH.\n";
    exit(0);

} catch (\Throwable $t) {
    echo "EXCEPTION: " . $t->getMessage() . "\n";
    echo $t->getTraceAsString() . "\n";
    exit(1);
}
