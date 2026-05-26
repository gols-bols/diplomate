<?php

declare(strict_types=1);

require dirname(__DIR__) . '/vendor/autoload.php';

$app = require dirname(__DIR__) . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Http\Controllers\TicketController;
use App\Models\Ticket;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Auth;

$user = User::query()->where('email', 'user@spk.local')->first();
if (! $user) {
    fwrite(STDERR, "user@spk.local not found — run migrate --seed\n");
    exit(1);
}

Auth::login($user);

$controller = app(TicketController::class);
$reflection = new ReflectionClass($controller);

$maxKb = $reflection->getMethod('attachmentMaxKilobytes');
$maxKb->setAccessible(true);
echo 'attachmentMaxKilobytes=' . $maxKb->invoke($controller) . PHP_EOL;

$uploadError = $reflection->getMethod('attachmentUploadError');
$uploadError->setAccessible(true);

// Minimal valid 1x1 PNG
$png = base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
$tmp = tempnam(sys_get_temp_dir(), 'ticket_test_');
$path = $tmp . '.png';
rename($tmp, $path);
file_put_contents($path, $png);

$_FILES['attachment'] = [
    'name' => 'test.png',
    'type' => 'image/png',
    'tmp_name' => $path,
    'error' => UPLOAD_ERR_OK,
    'size' => filesize($path),
];

$request = Request::create('/tickets', 'POST', [
    'title' => 'Тест вложения ' . uniqid(),
    'description' => 'Проверка загрузки фото',
    'priority' => 'normal',
    'category' => 'other',
    'campus' => '1',
    'room' => 'Тест 1',
], [], ['attachment' => new UploadedFile($path, 'test.png', 'image/png', UPLOAD_ERR_OK, true)]);

$request->setUserResolver(fn () => $user);

$store = $reflection->getMethod('store');
$store->setAccessible(true);

/** @var Illuminate\Http\RedirectResponse $response */
$response = $store->invoke($controller, $request);

$ticket = Ticket::query()->where('title', $request->input('title'))->first();
@unlink($path);

if (! $ticket) {
    echo "FAIL: ticket not created\n";
    exit(1);
}

if (! $ticket->attachment_path || ! is_file(public_path($ticket->attachment_path))) {
    echo "FAIL: attachment_path={$ticket->attachment_path}\n";
    exit(1);
}

echo "OK: saved {$ticket->attachment_path} url={$ticket->attachment_url}\n";
$ticket->delete();
@unlink(public_path($ticket->attachment_path));
