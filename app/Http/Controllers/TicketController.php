<?php

namespace App\Http\Controllers;

use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Illuminate\View\View;

class TicketController extends Controller
{
    public function index(): View
    {
        $user = auth()->user();

        $filters = request()->validate([
            'status' => ['nullable', 'in:open,in_progress,resolved,closed'],
            'priority' => ['nullable', 'in:low,normal,high'],
            'category' => ['nullable', 'in:equipment,network,software,access,printing,other'],
            'campus' => ['nullable', 'in:main,1,2,3'],
            'q' => ['nullable', 'string', 'max:120'],
        ]);

        $query = $this->visibleTicketsQuery()
            ->with(['creator', 'assignee'])
            ->withCount('comments')
            ->latest();

        if (! empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (! empty($filters['priority'])) {
            $query->where('priority', $filters['priority']);
        }

        if (! empty($filters['category'])) {
            $query->where('category', $filters['category']);
        }

        if (! empty($filters['campus']) && $user?->role === 'admin') {
            $query->where('campus', $filters['campus']);
        }

        if (! empty($filters['q'])) {
            $this->applySearch($query, $filters['q']);
        }

        $tickets = $query->get();

        return view('tickets.index', compact('tickets', 'filters'));
    }

    public function export(Request $request): StreamedResponse
    {
        $filters = $request->validate([
            'status' => ['nullable', 'in:open,in_progress,resolved,closed'],
            'priority' => ['nullable', 'in:low,normal,high'],
            'category' => ['nullable', 'in:equipment,network,software,access,printing,other'],
            'campus' => ['nullable', 'in:main,1,2,3'],
            'q' => ['nullable', 'string', 'max:120'],
        ]);

        $query = $this->visibleTicketsQuery()
            ->with(['creator', 'assignee'])
            ->latest();

        if (! empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (! empty($filters['priority'])) {
            $query->where('priority', $filters['priority']);
        }

        if (! empty($filters['category'])) {
            $query->where('category', $filters['category']);
        }

        if (! empty($filters['campus']) && auth()->user()?->role === 'admin') {
            $query->where('campus', $filters['campus']);
        }

        if (! empty($filters['q'])) {
            $this->applySearch($query, $filters['q']);
        }

        $filename = 'tickets_export_' . now()->format('Y_m_d_H_i') . '.csv';

        return response()->streamDownload(function () use ($query): void {
            $output = fopen('php://output', 'w');
            fputcsv($output, ['ID', 'Тема', 'Категория', 'Статус', 'Приоритет', 'Срок', 'Корпус', 'Кабинет', 'Заявитель', 'Исполнитель', 'Создано'], ';');

            $query->chunk(100, function ($tickets) use ($output): void {
                foreach ($tickets as $ticket) {
                    fputcsv($output, [
                        $ticket->id,
                        $ticket->title,
                        $ticket->category_label,
                        $ticket->status_label,
                        $ticket->priority_label,
                        $ticket->deadline_label,
                        $ticket->campus_label,
                        $ticket->room,
                        $ticket->requester_name ?: ($ticket->creator?->name ?? 'Не указан'),
                        $ticket->assignee?->name ?? 'Не назначен',
                        optional($ticket->created_at)->format('d.m.Y H:i'),
                    ], ';');
                }
            });

            fclose($output);
        }, $filename, [
            'Content-Type' => 'text/csv; charset=UTF-8',
        ]);
    }

    public function dashboard(): View
    {
        $tickets = $this->visibleTicketsQuery()
            ->with(['assignee'])
            ->latest()
            ->get();

        $total = max($tickets->count(), 1);

        $statusStats = collect(Ticket::STATUS_LABELS)
            ->map(fn (string $label, string $status): array => [
                'label' => $label,
                'count' => $tickets->where('status', $status)->count(),
                'percent' => round($tickets->where('status', $status)->count() / $total * 100),
                'class' => Ticket::STATUS_COLORS[$status] ?? 'status-open',
            ]);

        $campusStats = collect(Ticket::CAMPUS_LABELS)
            ->map(fn (string $label, string $campus): array => [
                'label' => $label,
                'count' => $tickets->where('campus', $campus)->count(),
                'percent' => round($tickets->where('campus', $campus)->count() / $total * 100),
            ])
            ->filter(fn (array $item): bool => $item['count'] > 0 || auth()->user()?->role === 'admin');

        $priorityStats = collect([
            'high' => 'Высокий',
            'normal' => 'Обычный',
            'low' => 'Низкий',
        ])->map(fn (string $label, string $priority): array => [
            'label' => $label,
            'count' => $tickets->where('priority', $priority)->count(),
            'percent' => round($tickets->where('priority', $priority)->count() / $total * 100),
        ]);

        $categoryStats = collect(Ticket::CATEGORY_LABELS)
            ->map(fn (string $label, string $category): array => [
                'label' => $label,
                'count' => $tickets->where('category', $category)->count(),
                'percent' => round($tickets->where('category', $category)->count() / $total * 100),
            ])
            ->filter(fn (array $item): bool => $item['count'] > 0);

        $assigneeStats = $tickets
            ->groupBy(fn (Ticket $ticket): string => $ticket->assignee?->name ?? 'Не назначен')
            ->map(fn ($items, string $name): array => [
                'name' => $name,
                'count' => $items->count(),
                'active' => $items->whereIn('status', ['open', 'in_progress'])->count(),
            ])
            ->sortByDesc('count')
            ->values();

        $latest = $tickets->take(5);

        return view('tickets.dashboard', compact(
            'tickets',
            'statusStats',
            'campusStats',
            'priorityStats',
            'categoryStats',
            'assigneeStats',
            'latest'
        ));
    }

    public function show(Ticket $ticket): View
    {
        abort_unless($this->canView($ticket), 403);

        $ticket->load(['creator', 'assignee', 'comments.user']);

        return view('tickets.show', compact('ticket'));
    }

    public function create(): View
    {
        abort_unless($this->canCreate(), 403);

        return view('tickets.create');
    }

    public function store(Request $request): RedirectResponse
    {
        abort_unless($this->canCreate(), 403);

        $user = auth()->user();

        if ($uploadError = $this->attachmentUploadError($request)) {
            return back()
                ->withErrors(['attachment' => $uploadError])
                ->withInput();
        }

        $maxAttachmentKb = $this->attachmentMaxKilobytes();

        $data = $request->validate([
            'title' => ['required', 'string', 'max:255'],
            'description' => ['required', 'string'],
            'attachment' => ['nullable', 'file', 'image', 'mimes:jpeg,jpg,png,webp,gif', 'max:' . $maxAttachmentKb],
            'priority' => ['required', 'in:low,normal,high'],
            'category' => ['required', 'in:equipment,network,software,access,printing,other'],
            'campus' => ['required', 'in:main,1,2,3'],
            'room' => ['required', 'string', 'max:50'],
            'deadline' => ['nullable', 'date', 'after_or_equal:today'],
        ], [
            'attachment.image' => 'Фото должно быть изображением (JPG, PNG, WebP или GIF).',
            'attachment.mimes' => 'Фото должно быть в формате JPG, PNG, WebP или GIF.',
            'attachment.max' => 'Размер фото не должен превышать ' . $this->formatMegabytes($maxAttachmentKb) . '.',
        ]);

        $data = $this->normalizeDeadline($data);

        $attachmentPath = null;
        if ($request->hasFile('attachment') && $request->file('attachment')->isValid()) {
            try {
                $attachmentPath = $this->storeAttachment($request->file('attachment'));
            } catch (\RuntimeException $exception) {
                return back()
                    ->withErrors(['attachment' => $exception->getMessage()])
                    ->withInput();
            }
        }

        Ticket::query()->create([
            ...collect($data)->except('attachment')->all(),
            'attachment_path' => $attachmentPath,
            'status' => 'open',
            'requester_name' => $user?->name,
            'created_by' => (int) auth()->id(),
        ]);

        return redirect()->route('tickets.index')->with('success', 'Заявка создана.');
    }

    public function edit(Ticket $ticket): View
    {
        abort_unless($this->canEdit($ticket), 403);

        $managers = User::query()
            ->where('role', 'manager')
            ->orderBy('name')
            ->get();

        return view('tickets.edit', compact('ticket', 'managers'));
    }

    public function update(Request $request, Ticket $ticket): RedirectResponse
    {
        abort_unless($this->canEdit($ticket), 403);

        $user = auth()->user();

        if ($user?->role === 'admin') {
            $data = $request->validate([
                'title' => ['required', 'string', 'max:255'],
                'description' => ['required', 'string'],
                'priority' => ['required', 'in:low,normal,high'],
                'category' => ['required', 'in:equipment,network,software,access,printing,other'],
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
                'campus' => ['required', 'in:main,1,2,3'],
                'room' => ['required', 'string', 'max:50'],
                'deadline' => ['nullable', 'date'],
                'assignee_id' => ['nullable', 'integer', 'exists:users,id'],
            ]);
        } else {
            $data = $request->validate([
                'priority' => ['required', 'in:low,normal,high'],
                'deadline' => ['nullable', 'date'],
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
            ]);
        }

        $data = $this->normalizeDeadline($data);

        $before = $ticket->only(['priority', 'status', 'assignee_id', 'deadline']);

        $ticket->update($data);

        $this->writeUpdateHistory($ticket, $before);

        return redirect()
            ->route('tickets.show', $ticket)
            ->with('success', 'Заявка обновлена.');
    }

    public function comment(Request $request, Ticket $ticket): RedirectResponse
    {
        abort_unless($this->canView($ticket), 403);

        $data = $request->validate([
            'body' => ['required', 'string', 'max:2000'],
        ]);

        $ticket->comments()->create([
            'user_id' => (int) auth()->id(),
            'type' => 'comment',
            'body' => $data['body'],
        ]);

        return redirect()
            ->route('tickets.show', $ticket)
            ->with('success', 'Комментарий добавлен в историю заявки.');
    }

    public function transition(Request $request, Ticket $ticket): RedirectResponse
    {
        abort_unless($this->canEdit($ticket), 403);

        $data = $request->validate([
            'status' => ['required', 'in:open,in_progress,resolved,closed'],
        ]);

        $before = $ticket->only(['priority', 'status', 'assignee_id']);
        $ticket->update(['status' => $data['status']]);

        $this->writeUpdateHistory($ticket, $before);

        return redirect()
            ->route('tickets.show', $ticket)
            ->with('success', 'Статус заявки быстро обновлен.');
    }

    private function canEdit(Ticket $ticket): bool
    {
        $user = auth()->user();

        if (! $user) {
            return false;
        }

        if ($user->role === 'admin') {
            return true;
        }

        return $user->role === 'manager' && $user->campus === $ticket->campus;
    }

    private function canView(Ticket $ticket): bool
    {
        $user = auth()->user();

        if (! $user) {
            return false;
        }

        if ($user->role === 'admin') {
            return true;
        }

        if ($user->role === 'manager') {
            return $user->campus === $ticket->campus;
        }

        return (int) $ticket->created_by === (int) $user->id;
    }

    private function canCreate(): bool
    {
        $user = auth()->user();

        return $user !== null && $user->role === 'user';
    }

    private function visibleTicketsQuery(): Builder
    {
        $user = auth()->user();

        $query = Ticket::query();

        if ($user?->role === 'manager') {
            $query->where('campus', $user->campus);
        }

        if ($user?->role === 'user') {
            $query->where('created_by', $user->id);
        }

        return $query;
    }

    private function applySearch(Builder $query, string $search): void
    {
        $query->where(function (Builder $query) use ($search): void {
            $query
                ->where('title', 'like', "%{$search}%")
                ->orWhere('description', 'like', "%{$search}%")
                ->orWhere('requester_name', 'like', "%{$search}%")
                ->orWhere('room', 'like', "%{$search}%")
                ->orWhere('category', 'like', "%{$search}%");
        });
    }

    private function normalizeDeadline(array $data): array
    {
        if (array_key_exists('deadline', $data) && blank($data['deadline'])) {
            $data['deadline'] = null;
        }

        return $data;
    }

    private function storeAttachment(UploadedFile $file): string
    {
        $extension = strtolower($file->getClientOriginalExtension() ?: $file->extension() ?: 'jpg');
        $allowed = ['jpeg', 'jpg', 'png', 'webp', 'gif'];

        if (! in_array($extension, $allowed, true)) {
            $extension = 'jpg';
        }

        $filename = uniqid('ticket_', true) . '.' . $extension;

        foreach ($this->attachmentStorageTargets() as $target) {
            $directory = $target['directory'];

            if (! $this->ensureWritableDirectory($directory)) {
                continue;
            }

            $fullPath = $directory . DIRECTORY_SEPARATOR . $filename;

            if ($this->persistUploadedFile($file, $fullPath)) {
                return $target['path_prefix'] . $filename;
            }
        }

        throw new \RuntimeException(
            'Не удалось сохранить вложение. Запустите сервер через composer serve или serve.ps1 и проверьте каталоги public/uploads/tickets и storage/app/public/tickets.'
        );
    }

    /**
     * @return list<array{directory: string, path_prefix: string}>
     */
    private function attachmentStorageTargets(): array
    {
        return [
            [
                'directory' => public_path('uploads/tickets'),
                'path_prefix' => 'uploads/tickets/',
            ],
            [
                'directory' => storage_path('app/public/tickets'),
                'path_prefix' => 'tickets/',
            ],
        ];
    }

    private function ensureWritableDirectory(string $directory): bool
    {
        if (! is_dir($directory) && ! @mkdir($directory, 0777, true) && ! is_dir($directory)) {
            return false;
        }

        $probe = $directory . DIRECTORY_SEPARATOR . '.write_probe_' . getmypid();

        if (@file_put_contents($probe, '1') === false) {
            return false;
        }

        @unlink($probe);

        return true;
    }

    private function persistUploadedFile(UploadedFile $file, string $fullPath): bool
    {
        if ($file->getRealPath() && @copy($file->getRealPath(), $fullPath)) {
            return is_file($fullPath);
        }

        try {
            $saved = $file->move(dirname($fullPath), basename($fullPath));

            return is_file($saved->getPathname());
        } catch (\Throwable) {
            return false;
        }
    }

    private function attachmentUploadError(Request $request): ?string
    {
        $raw = $_FILES['attachment'] ?? null;

        if (! is_array($raw)) {
            return null;
        }

        $error = (int) ($raw['error'] ?? UPLOAD_ERR_NO_FILE);

        if ($error === UPLOAD_ERR_NO_FILE) {
            return null;
        }

        if (in_array($error, [UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE], true)) {
            return sprintf(
                'Файл слишком большой. Допустимо до %s (текущий лимит PHP: %s). Уменьшите фото или запустите composer serve.',
                $this->formatMegabytes($this->attachmentMaxKilobytes()),
                ini_get('upload_max_filesize') ?: 'неизвестен'
            );
        }

        if ($error === UPLOAD_ERR_CANT_WRITE && empty($raw['tmp_name']) && (int) ($raw['size'] ?? 0) === 0) {
            return sprintf(
                'Файл не принят сервером (часто из‑за лимита post_max_size=%s). Запустите composer serve и уменьшите размер фото.',
                ini_get('post_max_size') ?: 'неизвестен'
            );
        }

        $tmpDir = ini_get('upload_tmp_dir') ?: sys_get_temp_dir();
        $projectTmp = defined('APP_UPLOAD_TMP_DIR')
            ? APP_UPLOAD_TMP_DIR
            : storage_path('framework/uploads');

        return match ($error) {
            UPLOAD_ERR_PARTIAL => 'Файл загружен не полностью. Повторите отправку формы.',
            UPLOAD_ERR_NO_TMP_DIR => sprintf(
                'PHP не находит временный каталог для загрузки (сейчас: %s). Остановите сервер и из папки проекта запустите: composer serve или .\\serve.ps1 (нужен каталог %s). Команда php artisan serve без этих скриптов на Windows часто не задаёт upload_tmp_dir для встроенного сервера.',
                $tmpDir ?: 'не задан',
                $projectTmp
            ),
            UPLOAD_ERR_CANT_WRITE => sprintf(
                'PHP не смог записать файл во временный каталог (%s). Остановите сервер и запустите: composer serve или .\\serve.ps1 (каталог %s).',
                $tmpDir,
                $projectTmp
            ),
            UPLOAD_ERR_EXTENSION => 'Загрузка остановлена настройками PHP (UPLOAD_ERR_EXTENSION). Используйте JPG/PNG/WebP/GIF или запустите composer serve.',
            default => ($file = $request->file('attachment')) && ! $file->isValid()
                ? 'Не удалось загрузить файл. Используйте JPG, PNG, WebP или GIF.'
                : null,
        };
    }

    private function attachmentMaxKilobytes(): int
    {
        return min(5120, $this->iniSizeToKilobytes(ini_get('upload_max_filesize') ?: '2M'));
    }

    private function iniSizeToKilobytes(string $value): int
    {
        $value = trim($value);

        if ($value === '' || $value === '-1') {
            return 5120;
        }

        if (preg_match('/^(\d+(?:\.\d+)?)\s*([kmg])?$/i', $value, $matches) !== 1) {
            return (int) max(1, round(((int) $value) / 1024));
        }

        $number = (float) $matches[1];
        $unit = strtolower($matches[2] ?? '');

        return (int) max(1, match ($unit) {
            'g' => round($number * 1024 * 1024),
            'm' => round($number * 1024),
            'k' => round($number),
            default => round($number / 1024),
        });
    }

    private function formatMegabytes(int $kilobytes): string
    {
        if ($kilobytes >= 1024) {
            $megabytes = $kilobytes / 1024;

            return (fmod($megabytes, 1.0) === 0.0 ? (string) (int) $megabytes : number_format($megabytes, 1, '.', '')) . ' МБ';
        }

        return $kilobytes . ' КБ';
    }

    private function writeUpdateHistory(Ticket $ticket, array $before): void
    {
        $ticket->refresh();

        $changes = [];

        if (($before['status'] ?? null) !== $ticket->status) {
            $changes[] = 'статус: ' . $ticket->status_label;
        }

        if (($before['priority'] ?? null) !== $ticket->priority) {
            $changes[] = 'приоритет: ' . $ticket->priority_label;
        }

        if (($before['deadline'] ?? null) != $ticket->deadline) {
            $changes[] = 'срок: ' . $ticket->deadline_label;
        }

        if ((int) ($before['assignee_id'] ?? 0) !== (int) ($ticket->assignee_id ?? 0)) {
            $ticket->load('assignee');
            $changes[] = 'исполнитель: ' . ($ticket->assignee?->name ?? 'не назначен');
        }

        if ($changes === []) {
            return;
        }

        $ticket->comments()->create([
            'user_id' => (int) auth()->id(),
            'type' => 'system',
            'body' => 'Обновлены рабочие параметры заявки: ' . implode(', ', $changes) . '.',
        ]);
    }
}
