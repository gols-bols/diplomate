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
    fwrite(STDERR, "user@spk.local not found\n");
    exit(1);
}

Auth::login($user);

$png = base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
$path = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'deadline_test.png';
file_put_contents($path, $png);

$title = 'Тест deadline ' . uniqid();

$request = Request::create('/tickets', 'POST', [
    'title' => $title,
    'description' => 'Пустой срок',
    'priority' => 'normal',
    'category' => 'other',
    'campus' => '1',
    'room' => '101',
    'deadline' => '',
], [], ['attachment' => new UploadedFile($path, 'test.png', 'image/png', UPLOAD_ERR_OK, true)]);

$request->setUserResolver(fn () => $user);

app(TicketController::class)->store($request);

$ticket = Ticket::query()->where('title', $title)->first();
@unlink($path);

if (! $ticket) {
    echo "FAIL: ticket not created\n";
    exit(1);
}

if ($ticket->deadline !== null) {
    echo 'FAIL: deadline=' . var_export($ticket->getRawOriginal('deadline'), true) . "\n";
    $ticket->delete();
    exit(1);
}

$hasAttachment = $ticket->attachment_path && is_file(public_path($ticket->attachment_path));
echo 'OK: deadline is NULL, attachment=' . ($hasAttachment ? 'yes' : 'no') . "\n";

if ($ticket->attachment_path) {
    @unlink(public_path($ticket->attachment_path));
}
$ticket->delete();
