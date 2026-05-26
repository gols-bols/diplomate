<?php

declare(strict_types=1);

/**
 * Dev server with upload_tmp_dir on the php -S process (Windows-safe).
 * Used by "composer serve" and serve.ps1.
 */

$basePath = dirname(__DIR__);

require $basePath.'/bootstrap/upload_dirs.php';

$uploadTmp = defined('APP_UPLOAD_TMP_DIR')
    ? APP_UPLOAD_TMP_DIR
    : ($basePath.'/storage/framework/uploads');

$host = getenv('SERVER_HOST') ?: '127.0.0.1';
$port = (int) (getenv('SERVER_PORT') ?: 8000);

$argv = $GLOBALS['argv'] ?? [];
foreach ($argv as $index => $arg) {
    if ($arg === '--host' && isset($argv[$index + 1])) {
        $host = $argv[$index + 1];
    }
    if ($arg === '--port' && isset($argv[$index + 1])) {
        $port = (int) $argv[$index + 1];
    }
}

$server = file_exists($basePath.'/server.php')
    ? $basePath.'/server.php'
    : $basePath.'/vendor/laravel/framework/src/Illuminate/Foundation/resources/server.php';

$publicPath = $basePath.'/public';

$command = [
    PHP_BINARY,
    '-d', 'upload_max_filesize=8M',
    '-d', 'post_max_size=12M',
    '-d', 'upload_tmp_dir='.$uploadTmp,
    '-S', $host.':'.$port,
    $server,
];

fwrite(STDERR, "upload_tmp_dir={$uploadTmp}\n");
fwrite(STDERR, "Server: http://{$host}:{$port}\n");

$descriptors = [
    0 => STDIN,
    1 => STDOUT,
    2 => STDERR,
];

$process = proc_open($command, $descriptors, $pipes, $publicPath);

if (! is_resource($process)) {
    fwrite(STDERR, "Failed to start PHP built-in server.\n");
    exit(1);
}

$exitCode = proc_close($process);
exit($exitCode);
