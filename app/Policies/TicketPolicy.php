<?php

namespace App\Policies;

use App\Models\Ticket;
use App\Models\User;

class TicketPolicy
{
    public function view(?User $user, Ticket $ticket): bool
    {
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

    public function update(?User $user, Ticket $ticket): bool
    {
        if (! $user) {
            return false;
        }

        if ($user->role === 'admin') {
            return true;
        }

        return $user->role === 'manager' && $user->campus === $ticket->campus;
    }

    public function create(?User $user): bool
    {
        return $user !== null && $user->role === 'user';
    }
}
