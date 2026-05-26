<?php

namespace App\Http\Controllers;

use App\Models\Ticket;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class AdminController extends Controller
{
    public function users(): View
    {
        $this->authorizeAdmin();

        $users = User::query()
            ->withCount([
                'createdTickets',
                'assignedTickets',
                'assignedTickets as active_assigned_tickets_count' => fn ($query) => $query->whereIn('status', ['open', 'in_progress']),
            ])
            ->orderByRaw("FIELD(role, 'admin', 'manager', 'user')")
            ->orderBy('name')
            ->get();

        return view('admin.users', compact('users'));
    }

    public function updateUser(Request $request, User $user): RedirectResponse
    {
        $this->authorizeAdmin();

        abort_if((int) auth()->id() === (int) $user->id && $request->input('role') !== 'admin', 422, 'Нельзя снять роль администратора с текущего пользователя.');

        $data = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'role' => ['required', 'in:admin,manager,user'],
            'campus' => ['nullable', 'in:main,1,2,3'],
        ]);

        if ($data['role'] === 'admin') {
            $data['campus'] = null;
        }

        if (in_array($data['role'], ['manager', 'user'], true) && empty($data['campus'])) {
            return back()
                ->withErrors(['campus' => 'Для пользователя или менеджера нужно выбрать корпус.'])
                ->withInput();
        }

        $user->update($data);

        return redirect()
            ->route('admin.users')
            ->with('success', 'Пользователь обновлен.');
    }

    private function authorizeAdmin(): void
    {
        abort_unless(auth()->user()?->role === 'admin', 403);
    }
}
