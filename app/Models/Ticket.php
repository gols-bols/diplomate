<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
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

    public const CATEGORY_LABELS = [
        'equipment' => 'Оборудование',
        'network' => 'Сеть и интернет',
        'software' => 'Программное обеспечение',
        'access' => 'Доступы',
        'printing' => 'Печать',
        'other' => 'Другое',
    ];

    protected $fillable = [
        'title',
        'description',
        'attachment_path',
        'priority',
        'category',
        'status',
        'requester_name',
        'campus',
        'room',
        'deadline',
        'created_by',
        'assignee_id',
    ];

    protected function casts(): array
    {
        return [
            'deadline' => 'date:Y-m-d',
        ];
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function assignee(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assignee_id');
    }

    public function comments(): HasMany
    {
        return $this->hasMany(TicketComment::class)->latest();
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

    public function getCategoryLabelAttribute(): string
    {
        return self::CATEGORY_LABELS[$this->category] ?? 'Другое';
    }

    public function getDeadlineLabelAttribute(): string
    {
        return $this->deadline?->format('d.m.Y') ?? 'Без срока';
    }

    public function getIsOverdueAttribute(): bool
    {
        if (! $this->deadline || in_array($this->status, ['resolved', 'closed'], true)) {
            return false;
        }

        return $this->deadline->isPast() && ! $this->deadline->isToday();
    }

    public function getAttachmentUrlAttribute(): ?string
    {
        if (! $this->attachment_path) {
            return null;
        }

        if (str_starts_with($this->attachment_path, 'uploads/')) {
            return asset($this->attachment_path);
        }

        return asset('storage/' . $this->attachment_path);
    }
}
