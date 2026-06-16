<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use Notifiable;

    public const CAMPUS_LABELS = [
        'main' => 'Главный корпус',
        '1' => 'Учебный корпус 1',
        '2' => 'Учебный корпус 2',
        '3' => 'Учебный корпус 3',
    ];

    protected $fillable = [
        'name',
        'email',
        'password',
        'role',
        'campus',
    ];

    protected $hidden = [
        'api_token',
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'password' => 'hashed',
        ];
    }

    public function getRoleLabelAttribute(): string
    {
        return match ($this->role) {
            'admin' => 'Администратор',
            'manager' => 'Менеджер корпуса',
            default => 'Заявитель',
        };
    }

    public function getCampusLabelAttribute(): string
    {
        if ($this->role === 'admin') {
            return 'Все корпуса';
        }

        return self::CAMPUS_LABELS[$this->campus ?? 'main'] ?? 'Не указан';
    }
}
