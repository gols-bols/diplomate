<?php

namespace App\Http\Controllers;

use App\Models\Ticket;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class TicketController extends Controller
{
    public function index(): View
    {
        $user = auth()->user();

        $filters = request()->validate([
            'status' => ['nullable', 'in:open,in_progress,resolved,closed'],
            'priority' => ['nullable', 'in:low,normal,high'],
            'campus' => ['nullable', 'in:main,1,2,3'],
        ]);

        $query = Ticket::query()
            ->with(['creator', 'assignee'])
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

        $tickets = $query->get();

        return view('tickets.index', compact('tickets', 'filters'));
    }

    public function show(Ticket $ticket): View
    {
        abort_unless($this->canView($ticket), 403);

        $ticket->load(['creator', 'assignee']);

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

        $data = $request->validate([
            'title' => ['required', 'string', 'max:255'],
            'description' => ['required', 'string'],
            'priority' => ['required', 'in:low,normal,high'],
            'campus' => ['required', 'in:main,1,2,3'],
            'room' => ['required', 'string', 'max:50'],
        ]);

        Ticket::query()->create([
            ...$data,
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
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
                'campus' => ['required', 'in:main,1,2,3'],
                'room' => ['required', 'string', 'max:50'],
                'assignee_id' => ['nullable', 'integer', 'exists:users,id'],
            ]);
        } else {
            $data = $request->validate([
                'priority' => ['required', 'in:low,normal,high'],
                'status' => ['required', 'in:open,in_progress,resolved,closed'],
            ]);
        }

        $ticket->update($data);

        return redirect()->route('tickets.index')->with('success', 'Заявка обновлена.');
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
}
