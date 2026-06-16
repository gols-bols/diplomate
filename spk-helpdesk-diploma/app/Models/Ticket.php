<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Model;

class Ticket extends Model
{
    public const CAMPUS_LABELS = [
        'main' => 'Главный корпус',
        '1' => 'Учебный корпус 1',
        '2' => 'Учебный корпус 2',
        '3' => 'Учебный корпус 3',
    ];

    public const STATUS_LABELS = [
        'open' => 'Открыта',
        'in_progress' => 'В работе',
        'resolved' => 'Решена',
        'closed' => 'Закрыта',
    ];

    public const STATUS_COLORS = [
        'open' => 'status-open',
        'in_progress' => 'status-progress',
        'resolved' => 'status-resolved',
        'closed' => 'status-closed',
    ];

    protected $fillable = [
        'title',
        'description',
        'priority',
        'status',
        'requester_name',
        'campus',
        'room',
        'created_by',
        'assignee_id',
    ];

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function assignee(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assignee_id');
    }

    public function getCampusLabelAttribute(): string
    {
        return self::CAMPUS_LABELS[$this->campus] ?? 'Не указан';
    }

    public function getStatusLabelAttribute(): string
    {
        return self::STATUS_LABELS[$this->status] ?? $this->status;
    }

    public function getStatusClassAttribute(): string
    {
        return self::STATUS_COLORS[$this->status] ?? 'status-open';
    }

    public function getPriorityLabelAttribute(): string
    {
        return match ($this->priority) {
            'high' => 'Высокий',
            'low' => 'Низкий',
            default => 'Обычный',
        };
    }
}
