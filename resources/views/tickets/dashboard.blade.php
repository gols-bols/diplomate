@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>Аналитический дашборд</h1>
            <p>
                Сводка показывает состояние заявок с учетом роли пользователя: администратор видит всю систему,
                менеджер — только свой корпус, заявитель — только собственные обращения.
            </p>
        </div>
        <div class="hero-badge">{{ auth()->user()->role_label }} · {{ auth()->user()->campus_label }}</div>
    </section>

    <section class="panel stack">
        <div class="section-divider">Ключевые показатели</div>

        <div class="stats-grid">
            <div class="stat-card">
                <small>Всего заявок</small>
                <strong>{{ $tickets->count() }}</strong>
                <span>Количество обращений в доступной области.</span>
            </div>
            <div class="stat-card status-open-card">
                <small>Ожидают реакции</small>
                <strong>{{ $tickets->where('status', 'open')->count() }}</strong>
                <span>Новые обращения без начала обработки.</span>
            </div>
            <div class="stat-card status-progress-card">
                <small>Активные</small>
                <strong>{{ $tickets->whereIn('status', ['open', 'in_progress'])->count() }}</strong>
                <span>Заявки, которые еще требуют действий.</span>
            </div>
            <div class="stat-card status-resolved-card">
                <small>Завершенные</small>
                <strong>{{ $tickets->whereIn('status', ['resolved', 'closed'])->count() }}</strong>
                <span>Решенные и закрытые обращения.</span>
            </div>
        </div>

        <div class="section-divider">Распределение нагрузки</div>

        <div class="analytics-grid">
            <article class="chart-card">
                <h3>Статусы заявок</h3>
                <div class="bar-list">
                    @foreach($statusStats as $item)
                        <div class="bar-row">
                            <header>
                                <span>{{ $item['label'] }}</span>
                                <span>{{ $item['count'] }} · {{ $item['percent'] }}%</span>
                            </header>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: {{ max($item['percent'], $item['count'] ? 8 : 0) }}%"></div>
                            </div>
                        </div>
                    @endforeach
                </div>
            </article>

            <article class="chart-card">
                <h3>Приоритеты</h3>
                <div class="bar-list">
                    @foreach($priorityStats as $item)
                        <div class="bar-row">
                            <header>
                                <span>{{ $item['label'] }}</span>
                                <span>{{ $item['count'] }} · {{ $item['percent'] }}%</span>
                            </header>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: {{ max($item['percent'], $item['count'] ? 8 : 0) }}%"></div>
                            </div>
                        </div>
                    @endforeach
                </div>
            </article>
        </div>

        <div class="analytics-grid">
            <article class="chart-card">
                <h3>Корпуса</h3>
                <div class="bar-list">
                    @foreach($campusStats as $item)
                        <div class="bar-row">
                            <header>
                                <span>{{ $item['label'] }}</span>
                                <span>{{ $item['count'] }} · {{ $item['percent'] }}%</span>
                            </header>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: {{ max($item['percent'], $item['count'] ? 8 : 0) }}%"></div>
                            </div>
                        </div>
                    @endforeach
                </div>
            </article>

            <article class="chart-card">
                <h3>Категории</h3>
                @if($categoryStats->isEmpty())
                    <div class="empty">Пока нет данных по категориям.</div>
                @else
                    <div class="bar-list">
                        @foreach($categoryStats as $item)
                            <div class="bar-row">
                                <header>
                                    <span>{{ $item['label'] }}</span>
                                    <span>{{ $item['count'] }} · {{ $item['percent'] }}%</span>
                                </header>
                                <div class="bar-track">
                                    <div class="bar-fill" style="width: {{ max($item['percent'], $item['count'] ? 8 : 0) }}%"></div>
                                </div>
                            </div>
                        @endforeach
                    </div>
                @endif
            </article>
        </div>

        <div class="analytics-grid">
            <article class="chart-card">
                <h3>Исполнители</h3>
                @if($assigneeStats->isEmpty())
                    <div class="empty">Пока нет данных по исполнителям.</div>
                @else
                    <div class="dashboard-list">
                        @foreach($assigneeStats as $item)
                            <div class="dashboard-row">
                                <div>
                                    <strong>{{ $item['name'] }}</strong>
                                    <small>Активных заявок: {{ $item['active'] }}</small>
                                </div>
                                <span class="pill pill-muted">{{ $item['count'] }}</span>
                            </div>
                        @endforeach
                    </div>
                @endif
            </article>
        </div>

        <div class="section-divider">Последние обращения</div>

        @if($latest->isEmpty())
            <div class="empty">В доступной области пока нет заявок.</div>
        @else
            <div class="dashboard-list">
                @foreach($latest as $ticket)
                    <a class="dashboard-row" href="{{ route('tickets.show', $ticket) }}">
                        <div>
                            <strong>{{ $ticket->title }}</strong>
                            <small>{{ $ticket->campus_label }} · {{ $ticket->room ?: 'Кабинет не указан' }}</small>
                        </div>
                        <span class="pill {{ $ticket->status_class }}">{{ $ticket->status_label }}</span>
                    </a>
                @endforeach
            </div>
        @endif
    </section>
</main>
@endsection
