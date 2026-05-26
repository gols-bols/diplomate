<?php

declare(strict_types=1);

require dirname(__DIR__) . '/bootstrap/upload_dirs.php';

$dirs = [
    dirname(__DIR__) . '/storage/framework/uploads',
    dirname(__DIR__) . '/public/uploads/tickets',
    dirname(__DIR__) . '/storage/app/public/tickets',
];

$failed = false;

foreach ($dirs as $dir) {
    $probe = $dir . DIRECTORY_SEPARATOR . '_verify_' . getmypid() . '.txt';
    $ok = is_dir($dir) && file_put_contents($probe, 'ok') !== false;
    if ($ok) {
        @unlink($probe);
        echo "OK writable: $dir\n";
    } else {
        echo "FAIL: $dir\n";
        $failed = true;
    }
}

exit($failed ? 1 : 0);
