@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>Редактирование заявки</h1>
            <p>
                Здесь действует строгое разграничение ролей: администратор управляет всеми полями и назначением исполнителя,
                менеджер корпуса меняет только рабочие параметры заявок своего корпуса.
            </p>
        </div>
        <a class="hero-badge" href="{{ route('tickets.index') }}">К списку</a>
    </section>

    <section class="panel stack">
        @if($errors->any())
            <ul class="error-list">
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        @endif

        <div class="form-shell">
            <form class="form-panel" method="post" action="{{ route('tickets.update', $ticket) }}">
                @csrf
                @method('put')

                @if(auth()->user()->role === 'admin')
                    <label>
                        Заголовок заявки
                        <input name="title" value="{{ old('title', $ticket->title) }}" required>
                    </label>

                    <label>
                        Подробное описание
                        <textarea name="description" required>{{ old('description', $ticket->description) }}</textarea>
                    </label>

                    <label>
                        Корпус
                        <select name="campus">
                            <option value="main" @selected(old('campus', $ticket->campus) === 'main')>Главный корпус</option>
                            <option value="1" @selected(old('campus', $ticket->campus) === '1')>Учебный корпус 1</option>
                            <option value="2" @selected(old('campus', $ticket->campus) === '2')>Учебный корпус 2</option>
                            <option value="3" @selected(old('campus', $ticket->campus) === '3')>Учебный корпус 3</option>
                        </select>
                    </label>

                    <label>
                        Кабинет
                        <input name="room" value="{{ old('room', $ticket->room) }}" required>
                    </label>

                    <label>
                        Исполнитель
                        <select name="assignee_id">
                            <option value="">Не назначен</option>
                            @foreach($managers as $manager)
                                <option value="{{ $manager->id }}" @selected((string) old('assignee_id', $ticket->assignee_id) === (string) $manager->id)>
                                    {{ $manager->name }} · {{ $manager->campus_label }}
                                </option>
                            @endforeach
                        </select>
                    </label>
                @else
                    <section class="info-card">
                        <h3>Карточка обращения</h3>
                        <div class="detail-list">
                            <div><strong>Заявитель:</strong> {{ $ticket->requester_name ?: ($ticket->creator?->name ?? 'Не указан') }}</div>
                            <div><strong>Корпус:</strong> {{ $ticket->campus_label }}</div>
                            <div><strong>Кабинет:</strong> {{ $ticket->room ?: 'Не указан' }}</div>
                            <div><strong>Тема:</strong> {{ $ticket->title }}</div>
                            <div><strong>Описание:</strong> {{ $ticket->description }}</div>
                        </div>
                    </section>
                @endif

                <label>
                    Приоритет
                    <select name="priority">
                        <option value="low" @selected(old('priority', $ticket->priority) === 'low')>Низкий</option>
                        <option value="normal" @selected(old('priority', $ticket->priority) === 'normal')>Обычный</option>
                        <option value="high" @selected(old('priority', $ticket->priority) === 'high')>Высокий</option>
                    </select>
                </label>

                <label>
                    Статус
                    <select name="status">
                        <option value="open" @selected(old('status', $ticket->status) === 'open')>Открыта</option>
                        <option value="in_progress" @selected(old('status', $ticket->status) === 'in_progress')>В работе</option>
                        <option value="resolved" @selected(old('status', $ticket->status) === 'resolved')>Решена</option>
                        <option value="closed" @selected(old('status', $ticket->status) === 'closed')>Закрыта</option>
                    </select>
                </label>

                <div class="toolbar-actions">
                    <button type="submit">Сохранить изменения</button>
                    <a class="button secondary" href="{{ route('tickets.index') }}">Отмена</a>
                </div>
            </form>

            <aside class="aside-stack">
                <section class="info-card">
                    <h3>Текущий маршрут</h3>
                    <p>
                        @if(auth()->user()->role === 'admin')
                            Администратор может менять все поля заявки, переносить ее между корпусами и назначать ответственного менеджера.
                        @else
                            Менеджер корпуса управляет только рабочими параметрами и двигает заявку по этапам обработки внутри своей зоны ответственности.
                        @endif
                    </p>
                </section>

                <section class="info-card">
                    <h3>Оперативная памятка</h3>
                    <p>
                        Держите статус и приоритет в актуальном состоянии: именно по этим полям строится сводка и оперативная картина по обращениям.
                    </p>
                </section>
            </aside>
        </div>
    </section>
</main>
@endsection
