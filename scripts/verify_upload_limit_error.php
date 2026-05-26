<?php

declare(strict_types=1);

require dirname(__DIR__) . '/vendor/autoload.php';

$app = require dirname(__DIR__) . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Http\Controllers\TicketController;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;

$controller = app(TicketController::class);
$reflection = new ReflectionClass($controller);
$method = $reflection->getMethod('attachmentUploadError');
$method->setAccessible(true);

$_FILES['attachment'] = [
    'name' => 'big.jpg',
    'type' => 'image/jpeg',
    'tmp_name' => '',
    'error' => UPLOAD_ERR_INI_SIZE,
    'size' => 0,
];

$request = Request::create('/tickets', 'POST');
$message = $method->invoke($controller, $request);

echo $message ? "OK error detected: {$message}\n" : "FAIL: no error for UPLOAD_ERR_INI_SIZE\n";
exit($message ? 0 : 1);
