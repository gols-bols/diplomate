<?php

declare(strict_types=1);

$basePath = dirname(__DIR__);
require $basePath.'/bootstrap/upload_dirs.php';

$uploadTmp = defined('APP_UPLOAD_TMP_DIR') ? APP_UPLOAD_TMP_DIR : ($basePath.'/storage/framework/uploads');

$command = [
    PHP_BINARY,
    '-d', 'upload_max_filesize=8M',
    '-d', 'post_max_size=12M',
    '-d', 'upload_tmp_dir='.$uploadTmp,
    '-r', 'echo ini_get("upload_tmp_dir");',
];

$descriptors = [['pipe', 'r'], ['pipe', 'w'], ['pipe', 'w']];
$process = proc_open($command, $descriptors, $pipes, $basePath.'/public');

if (! is_resource($process)) {
    echo "FAIL: proc_open\n";
    exit(1);
}

$out = stream_get_contents($pipes[1]);
proc_close($process);

$read = trim((string) $out);

if ($read === $uploadTmp) {
    echo "OK php -d upload_tmp_dir={$read}\n";
    exit(0);
}

echo "FAIL: expected [{$uploadTmp}], got [{$read}]\n";
exit(1);
