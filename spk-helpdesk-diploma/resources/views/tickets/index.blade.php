@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>Журнал заявок</h1>
            <p>
                В системе реализовано ролевое разграничение: заявитель подает обращения, менеджер ведет заявки только
                своего корпуса, а администратор контролирует всю систему и назначает исполнителей.
            </p>
        </div>
        <div class="hero-badge">{{ auth()->user()->role_label }} · {{ auth()->user()->campus_label }}</div>
    </section>

    <section class="panel stack">
        <div class="section-divider">Оперативная сводка</div>

        <div class="stats-grid">
            <div class="stat-card">
                <small>Общий поток</small>
                <strong>{{ $tickets->count() }}</strong>
                <span>Все обращения, попавшие в текущую выборку.</span>
            </div>
            <div class="stat-card status-open-card">
                <small>Новые</small>
                <strong>{{ $tickets->where('status', 'open')->count() }}</strong>
                <span>Заявки, ожидающие принятия в работу.</span>
            </div>
            <div class="stat-card status-progress-card">
                <small>В работе</small>
                <strong>{{ $tickets->where('status', 'in_progress')->count() }}</strong>
                <span>Обращения, по которым уже ведется обработка.</span>
            </div>
            <div class="stat-card status-resolved-card">
                <small>Решенные</small>
                <strong>{{ $tickets->where('status', 'resolved')->count() }}</strong>
                <span>Заявки, закрытые по факту устранения проблемы.</span>
            </div>
        </div>

        <div class="section-divider">Поиск нужной выборки</div>

        <form class="grid filters-grid" method="get" action="{{ route('tickets.index') }}">
            <label>
                Статус
                <select name="status">
                    <option value="">Все статусы</option>
                    <option value="open" @selected(($filters['status'] ?? '') === 'open')>Открыта</option>
                    <option value="in_progress" @selected(($filters['status'] ?? '') === 'in_progress')>В работе</option>
                    <option value="resolved" @selected(($filters['status'] ?? '') === 'resolved')>Решена</option>
                    <option value="closed" @selected(($filters['status'] ?? '') === 'closed')>Закрыта</option>
                </select>
            </label>

            <label>
                Приоритет
                <select name="priority">
                    <option value="">Все приоритеты</option>
                    <option value="low" @selected(($filters['priority'] ?? '') === 'low')>Низкий</option>
                    <option value="normal" @selected(($filters['priority'] ?? '') === 'normal')>Обычный</option>
                    <option value="high" @selected(($filters['priority'] ?? '') === 'high')>Высокий</option>
                </select>
            </label>

            @if(auth()->user()->role === 'admin')
                <label>
                    Корпус
                    <select name="campus">
                        <option value="">Все корпуса</option>
                        <option value="main" @selected(($filters['campus'] ?? '') === 'main')>Главный корпус</option>
                        <option value="1" @selected(($filters['campus'] ?? '') === '1')>Учебный корпус 1</option>
                        <option value="2" @selected(($filters['campus'] ?? '') === '2')>Учебный корпус 2</option>
                        <option value="3" @selected(($filters['campus'] ?? '') === '3')>Учебный корпус 3</option>
                    </select>
                </label>
            @endif

            <div class="toolbar-actions">
                <button type="submit">Применить фильтры</button>
                <a class="button secondary" href="{{ route('tickets.index') }}">Сбросить</a>
            </div>
        </form>

        <div class="section-divider">Лента обращений</div>

        <div class="toolbar">
            <div>
                <strong>Всего заявок: {{ $tickets->count() }}</strong>
                <div class="footer-note">
                    @if(auth()->user()->role === 'admin')
                        Администратор видит все корпуса и может назначать исполнителей.
                    @elseif(auth()->user()->role === 'manager')
                        Менеджер видит только заявки своего корпуса и меняет их рабочие статусы.
                    @else
                        Заявитель видит только собственные обращения и не редактирует их после отправки.
                    @endif
                </div>
            </div>

            <div class="toolbar-actions">
                @if(auth()->user()->role === 'user')
                    <a class="button secondary" href="{{ route('tickets.create') }}">Создать заявку</a>
                @endif
                <form method="post" action="{{ route('logout') }}">
                    @csrf
                    <button class="button-muted" type="submit">Выйти</button>
                </form>
            </div>
        </div>

        @if(session('success'))
            <div class="flash">{{ session('success') }}</div>
        @endif

        @if($tickets->isEmpty())
            <div class="empty">
                Пока заявок нет. Создайте первую запись, чтобы продемонстрировать работу системы.
            </div>
        @else
            <div class="grid tickets-grid">
                @foreach($tickets as $ticket)
                    <article class="ticket-card">
                        <header>
                            <div class="ticket-title-group">
                                <div class="ticket-kicker">Служба обращений</div>
                                <h3>{{ $ticket->title }}</h3>
                                <div class="footer-note">{{ $ticket->campus_label }} · {{ $ticket->room ?: 'Кабинет не указан' }}</div>
                            </div>
                            <span class="pill {{ $ticket->status_class }}">{{ $ticket->status_label }}</span>
                        </header>

                        <div class="meta">
                            <span class="pill pill-muted">Приоритет: {{ $ticket->priority_label }}</span>
                            @if($ticket->assignee)
                                <span class="pill pill-muted">Исполнитель: {{ $ticket->assignee->name }}</span>
                            @endif
                        </div>

                        <p>{{ $ticket->description }}</p>

                        <div class="detail-list">
                            <div><strong>Заявитель:</strong> {{ $ticket->requester_name ?: ($ticket->creator?->name ?? 'Не указан') }}</div>
                            <div><strong>Подал обращение:</strong> {{ optional($ticket->created_at)->format('d.m.Y H:i') ?? '—' }}</div>
                            <div><strong>Корпус:</strong> {{ $ticket->campus_label }}</div>
                            <div><strong>Кабинет:</strong> {{ $ticket->room ?: 'Не указан' }}</div>
                        </div>

                        @if(in_array(auth()->user()->role, ['admin', 'manager'], true))
                            <div class="toolbar-actions">
                                <a class="button secondary" href="{{ route('tickets.show', $ticket) }}">Открыть</a>
                                <a class="button secondary" href="{{ route('tickets.edit', $ticket) }}">Редактировать</a>
                            </div>
                        @else
                            <div class="toolbar-actions">
                                <a class="button secondary" href="{{ route('tickets.show', $ticket) }}">Открыть</a>
                            </div>
                        @endif
                    </article>
                @endforeach
            </div>
        @endif
    </section>
</main>
@endsection
