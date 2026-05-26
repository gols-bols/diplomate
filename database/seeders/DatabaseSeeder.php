<?php

namespace Database\Seeders;

use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $admin = User::query()->updateOrCreate(
            ['email' => 'admin@spk.local'],
            [
                'name' => 'Администратор СПК',
                'password' => 'password',
                'role' => 'admin',
                'campus' => null,
            ]
        );

        $mainManager = User::query()->updateOrCreate(
            ['email' => 'manager-main@spk.local'],
            [
                'name' => 'Менеджер главного корпуса',
                'password' => 'password',
                'role' => 'manager',
                'campus' => 'main',
            ]
        );

        $secondManager = User::query()->updateOrCreate(
            ['email' => 'manager-k2@spk.local'],
            [
                'name' => 'Менеджер корпуса 2',
                'password' => 'password',
                'role' => 'manager',
                'campus' => '2',
            ]
        );

        $user = User::query()->updateOrCreate(
            ['email' => 'user@spk.local'],
            [
                'name' => 'Пользователь СПК',
                'password' => 'password',
                'role' => 'user',
                'campus' => '1',
            ]
        );

        $printerTicket = Ticket::query()->firstOrCreate(
            [
                'title' => 'Не работает принтер в кабинете 21',
                'created_by' => $user->id,
            ],
            [
                'description' => 'Принтер включается, но документы остаются в очереди печати и не выводятся на устройство.',
                'priority' => 'high',
                'category' => 'printing',
                'status' => 'open',
                'requester_name' => $user->name,
                'campus' => '1',
                'room' => 'Кабинет 21',
                'deadline' => now()->addDays(1)->toDateString(),
                'assignee_id' => null,
            ]
        );

        $projectorTicket = Ticket::query()->firstOrCreate(
            [
                'title' => 'Требуется настройка проектора',
                'created_by' => $user->id,
            ],
            [
                'description' => 'В аудитории нет изображения на проекторе, требуется проверить кабель и источник сигнала.',
                'priority' => 'normal',
                'category' => 'equipment',
                'status' => 'in_progress',
                'requester_name' => $user->name,
                'campus' => '2',
                'room' => 'Аудитория 204',
                'deadline' => now()->addDays(3)->toDateString(),
                'assignee_id' => $secondManager->id,
            ]
        );

        $networkTicket = Ticket::query()->firstOrCreate(
            [
                'title' => 'Нет доступа к локальной сети в приемной',
                'created_by' => $admin->id,
            ],
            [
                'description' => 'Компьютер в методическом кабинете не получает сетевой адрес и не открывает внутренние ресурсы колледжа.',
                'priority' => 'high',
                'category' => 'network',
                'status' => 'resolved',
                'requester_name' => 'Секретарь приемной комиссии',
                'campus' => 'main',
                'room' => 'Приемная',
                'deadline' => now()->subDays(1)->toDateString(),
                'assignee_id' => $mainManager->id,
            ]
        );

        $libraryTicket = Ticket::query()->firstOrCreate(
            [
                'title' => 'Не работает интернет в библиотеке',
                'created_by' => $user->id,
            ],
            [
                'description' => 'В библиотеке отсутствует доступ к интернету на двух рабочих местах.',
                'priority' => 'high',
                'category' => 'network',
                'status' => 'closed',
                'requester_name' => $user->name,
                'campus' => '3',
                'room' => 'Библиотека, зал 1',
                'deadline' => now()->subDays(2)->toDateString(),
                'assignee_id' => $admin->id,
            ]
        );

        $printerTicket->comments()->firstOrCreate(
            ['body' => 'Заявка принята в журнал. Требуется проверить очередь печати и подключение устройства.'],
            ['user_id' => $admin->id, 'type' => 'system']
        );

        $projectorTicket->comments()->firstOrCreate(
            ['body' => 'Проверка назначена менеджеру корпуса 2. Нужно уточнить источник сигнала и состояние HDMI-кабеля.'],
            ['user_id' => $secondManager->id, 'type' => 'comment']
        );

        $networkTicket->comments()->firstOrCreate(
            ['body' => 'Проблема устранена после замены патч-корда и перезапуска сетевого оборудования.'],
            ['user_id' => $mainManager->id, 'type' => 'comment']
        );

        $libraryTicket->comments()->firstOrCreate(
            ['body' => 'Заявка закрыта после восстановления доступа к сети на рабочих местах библиотеки.'],
            ['user_id' => $admin->id, 'type' => 'system']
        );
    }
}
