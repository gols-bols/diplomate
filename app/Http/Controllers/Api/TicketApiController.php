<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Ticket;
use App\Models\TicketComment;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class TicketApiController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $user = $request->user();

        $validator = Validator::make($request->query(), [
            'status' => ['nullable', 'in:open,in_progress,resolved,closed'],
            'priority' => ['nullable', 'in:low,normal,high'],
            'campus' => ['nullable', 'in:main,1,2,3'],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Ошибка в параметрах фильтрации.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $filters = $validator->validated();

        $query = Ticket::query()
            ->with(['creator', 'assignee'])
            ->withCount('comments')
            ->latest();

        if ($user?->role === 'manager') {
            $query->where('campus', $user->campus);
        }

        if ($user?->role === 'user') {
            $query->where('created_by', $user->id);
        }

        if (! empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (! empty($filters['priority'])) {
            $query->where('priority', $filters['priority']);
        }

        if (! empty($filters['campus']) && $user?->role === 'admin') {
            $query->where('campus', $filters['campus']);
        }

        return response()->json([
            'message' => 'Список заявок получен.',
            'data' => $query->get()->map(fn (Ticket $ticket) => $this->serializeTicket($ticket)),
        ]);
    }

    public function show(Request $request, Ticket $ticket): JsonResponse
    {
        $this->authorize('view', $ticket);

        $ticket->load(['creator', 'assignee', 'comments.user']);

        return response()->json([
            'message' => 'Карточка заявки получена.',
            'data' => $this->serializeTicket($ticket, includeComments: true),
        ]);
    }

    public function comment(Request $request, Ticket $ticket): JsonResponse
    {
        $this->authorize('view', $ticket);

        $validator = Validator::make($request->all(), [
            'body' => ['required', 'string', 'max:2000'],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Ошибка валидации комментария.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $comment = $ticket->comments()->create([
            'user_id' => (int) $request->user()->id,
            'type' => 'comment',
            'body' => $validator->validated()['body'],
        ]);

        $comment->load('user');

        return response()->json([
            'message' => 'Комментарий добавлен в историю заявки.',
            'data' => $this->serializeComment($comment),
        ], 201);
    }

    public function store(Request $request): JsonResponse
    {
        $user = $request->user();

        if (! $user || $user->role !== 'user') {
            return response()->json([
                'message' => 'Создавать заявки через API может только пользователь-заявитель.',
            ], 403);
        }

        $validator = Validator::make($request->all(), [
            'title' => ['required', 'string', 'max:255'],
            'description' => ['required', 'string'],
            'priority' => ['required', 'in:low,normal,high'],
            'campus' => ['required', 'in:main,1,2,3'],
            'room' => ['required', 'string', 'max:50'],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Ошибка валидации при создании заявки.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $ticket = Ticket::query()->create([
            ...$validator->validated(),
            'status' => 'open',
            'requester_name' => $user->name,
            'created_by' => $user->id,
        ]);

        $ticket->load(['creator', 'assignee']);

        return response()->json([
            'message' => 'Заявка успешно создана.',
            'data' => $this->serializeTicket($ticket),
        ], 201);
    }

    public function update(Request $request, Ticket $ticket): JsonResponse
    {
        $this->authorize('update', $ticket);

        $user = $request->user();

        if ($user?->role === 'admin') {
            $validator = Validator::make($request->all(), [
                'title' => ['required', 'string', 'max:255'],
                'description' => ['required', 'string'],
                'priority' => ['required', 'in:low,normal,high'],
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
                'campus' => ['required', 'in:main,1,2,3'],
                'room' => ['required', 'string', 'max:50'],
                'assignee_id' => ['nullable', 'integer', 'exists:users,id'],
            ]);
        } else {
            $validator = Validator::make($request->all(), [
                'priority' => ['required', 'in:low,normal,high'],
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
            ]);
        }

        if ($validator->fails()) {
            return response()->json([
                'message' => 'Ошибка валидации при обновлении заявки.',
                'errors' => $validator->errors(),
            ], 422);
        }

        $before = $ticket->only(['priority', 'status', 'assignee_id']);

        $ticket->update($validator->validated());
        $this->writeUpdateHistory($ticket, $before, (int) $request->user()->id);

        $ticket->load(['creator', 'assignee']);

        return response()->json([
            'message' => 'Заявка успешно обновлена.',
            'data' => $this->serializeTicket($ticket),
        ]);
    }


    private function writeUpdateHistory(Ticket $ticket, array $before, int $userId): void
    {
        $ticket->refresh();

        $changes = [];

        if (($before['status'] ?? null) !== $ticket->status) {
            $changes[] = 'статус: ' . $ticket->status_label;
        }

        if (($before['priority'] ?? null) !== $ticket->priority) {
            $changes[] = 'приоритет: ' . $ticket->priority_label;
        }

        if ((int) ($before['assignee_id'] ?? 0) !== (int) ($ticket->assignee_id ?? 0)) {
            $ticket->load('assignee');
            $changes[] = 'исполнитель: ' . ($ticket->assignee?->name ?? 'не назначен');
        }

        if ($changes === []) {
            return;
        }

        $ticket->comments()->create([
            'user_id' => $userId,
            'type' => 'system',
            'body' => 'Обновлены рабочие параметры заявки: ' . implode(', ', $changes) . '.',
        ]);
    }

    private function serializeComment(TicketComment $comment): array
    {
        return [
            'id' => $comment->id,
            'type' => $comment->type,
            'author_label' => $comment->author_label,
            'body' => $comment->body,
            'user' => $comment->user ? [
                'id' => $comment->user->id,
                'name' => $comment->user->name,
            ] : null,
            'created_at' => optional($comment->created_at)?->toDateTimeString(),
        ];
    }

    private function serializeTicket(Ticket $ticket, bool $includeComments = false): array
    {
        $payload = [
            'id' => $ticket->id,
            'title' => $ticket->title,
            'description' => $ticket->description,
            'priority' => $ticket->priority,
            'priority_label' => $ticket->priority_label,
            'status' => $ticket->status,
            'status_label' => $ticket->status_label,
            'campus' => $ticket->campus,
            'campus_label' => $ticket->campus_label,
            'room' => $ticket->room,
            'requester_name' => $ticket->requester_name,
            'created_by' => $ticket->created_by,
            'assignee_id' => $ticket->assignee_id,
            'creator' => $ticket->creator ? [
                'id' => $ticket->creator->id,
                'name' => $ticket->creator->name,
                'email' => $ticket->creator->email,
            ] : null,
            'assignee' => $ticket->assignee ? [
                'id' => $ticket->assignee->id,
                'name' => $ticket->assignee->name,
                'email' => $ticket->assignee->email,
            ] : null,
            'comments_count' => $ticket->comments_count ?? $ticket->comments()->count(),
            'created_at' => optional($ticket->created_at)?->toDateTimeString(),
            'updated_at' => optional($ticket->updated_at)?->toDateTimeString(),
        ];

        if ($includeComments) {
            $payload['comments'] = $ticket->comments
                ->map(fn (TicketComment $comment) => $this->serializeComment($comment))
                ->values()
                ->all();
        }

        return $payload;
    }
}
