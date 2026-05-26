<?php

/**
 * Ensures upload-related directories exist (Windows-safe, no chmod required).
 * Called from public/index.php on every web request and before dev server start.
 */
$basePath = dirname(__DIR__);

$directories = [
    $basePath.'/storage/framework/uploads',
    $basePath.'/storage/app/public/tickets',
    $basePath.'/public/uploads/tickets',
];

foreach ($directories as $directory) {
    if (is_dir($directory)) {
        continue;
    }

    @mkdir($directory, 0777, true);
}

$uploadTmp = $basePath.'/storage/framework/uploads';
$uploadTmpResolved = realpath($uploadTmp) ?: $uploadTmp;

if (! defined('APP_UPLOAD_TMP_DIR')) {
    define('APP_UPLOAD_TMP_DIR', $uploadTmpResolved);
}

// Helps FPM/Apache; built-in server needs -d upload_tmp_dir on the php -S process (see ServeCommand).
if (is_dir($uploadTmpResolved) && is_writable($uploadTmpResolved)) {
    @ini_set('upload_tmp_dir', $uploadTmpResolved);
}
