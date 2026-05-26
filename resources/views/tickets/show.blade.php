@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>{{ $ticket->title }}</h1>
            <p>
                Карточка заявки показывает полную информацию по обращению: заявителя, корпус, кабинет, исполнителя,
                статус и приоритет. Такой формат удобен и для работы, и для демонстрации проекта на защите.
            </p>
            <div class="ticket-hero-meta">
                <span class="pill {{ $ticket->status_class }}">{{ $ticket->status_label }}</span>
                <span class="pill pill-muted">Приоритет: {{ $ticket->priority_label }}</span>
                <span class="pill pill-muted">Категория: {{ $ticket->category_label }}</span>
                <span class="pill {{ $ticket->is_overdue ? 'pill-danger' : 'pill-muted' }}">Срок: {{ $ticket->deadline_label }}</span>
                <span class="pill pill-muted">Корпус: {{ $ticket->campus_label }}</span>
            </div>
        </div>
        <div class="hero-badge">{{ $ticket->status_label }}</div>
    </section>

    <section class="panel stack">
        @if(session('success'))
            <div class="flash">{{ session('success') }}</div>
        @endif

        <div class="section-divider">Карточка обращения</div>

        <div class="detail-columns">
            <article class="detail-card description-card">
                <h2>Описание обращения</h2>
                <p>{{ $ticket->description }}</p>
                @if($ticket->attachment_url)
                    <figure class="ticket-attachment">
                        <img src="{{ $ticket->attachment_url }}" alt="Вложение к заявке">
                        <figcaption>Фото, приложенное при создании заявки</figcaption>
                    </figure>
                @endif
            </article>

            <aside class="detail-card">
                <h3>Служебные сведения</h3>
                <div class="detail-list">
                    <div><strong>Заявитель:</strong> {{ $ticket->requester_name ?: ($ticket->creator?->name ?? 'Не указан') }}</div>
                    <div><strong>Роль заявителя:</strong> {{ $ticket->creator?->role_label ?? 'Не указана' }}</div>
                    <div><strong>Корпус:</strong> {{ $ticket->campus_label }}</div>
                    <div><strong>Кабинет:</strong> {{ $ticket->room ?: 'Не указан' }}</div>
                    <div><strong>Категория:</strong> {{ $ticket->category_label }}</div>
                    <div><strong>Срок:</strong> {{ $ticket->deadline_label }}</div>
                    <div><strong>Исполнитель:</strong> {{ $ticket->assignee?->name ?? 'Не назначен' }}</div>
                    <div><strong>Создано:</strong> {{ optional($ticket->created_at)->format('d.m.Y H:i') ?? '—' }}</div>
                    <div><strong>Обновлено:</strong> {{ optional($ticket->updated_at)->format('d.m.Y H:i') ?? '—' }}</div>
                </div>
            </aside>
        </div>

        <div class="wide-actions">
            <a class="button secondary" href="{{ route('tickets.index') }}">Назад к списку</a>
            @if(in_array(auth()->user()->role, ['admin', 'manager'], true))
                <a class="button" href="{{ route('tickets.edit', $ticket) }}">Перейти к обработке</a>
                @if($ticket->status !== 'in_progress')
                    <form method="post" action="{{ route('tickets.transition', $ticket) }}">
                        @csrf
                        @method('patch')
                        <input type="hidden" name="status" value="in_progress">
                        <button class="button-muted" type="submit">Взять в работу</button>
                    </form>
                @endif
                @if($ticket->status !== 'resolved')
                    <form method="post" action="{{ route('tickets.transition', $ticket) }}">
                        @csrf
                        @method('patch')
                        <input type="hidden" name="status" value="resolved">
                        <button class="button-muted" type="submit">Отметить решенной</button>
                    </form>
                @endif
                @if($ticket->status !== 'closed')
                    <form method="post" action="{{ route('tickets.transition', $ticket) }}">
                        @csrf
                        @method('patch')
                        <input type="hidden" name="status" value="closed">
                        <button class="button-muted" type="submit">Закрыть</button>
                    </form>
                @endif
            @endif
        </div>

        <div class="section-divider">История и комментарии</div>

        @if($errors->any())
            <ul class="error-list">
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        @endif

        <form class="comment-form" method="post" action="{{ route('tickets.comments.store', $ticket) }}">
            @csrf
            <label>
                Добавить запись в историю
                <span class="hint">
                    Заявитель может уточнить проблему, а сотрудник сопровождения — зафиксировать ход работ.
                </span>
                <textarea name="body" placeholder="Например: Проверил подключение, требуется замена кабеля." required>{{ old('body') }}</textarea>
            </label>
            <div class="toolbar-actions">
                <button type="submit">Добавить комментарий</button>
            </div>
        </form>

        @if($ticket->comments->isEmpty())
            <div class="empty">По заявке пока нет комментариев. Первая запись появится после уточнения или изменения статуса.</div>
        @else
            <div class="timeline">
                @foreach($ticket->comments as $comment)
                    <article class="timeline-item {{ $comment->type === 'system' ? 'timeline-system' : '' }}">
                        <div class="timeline-marker"></div>
                        <div class="timeline-card">
                            <header>
                                <strong>{{ $comment->author_label }}</strong>
                                <span>{{ optional($comment->created_at)->format('d.m.Y H:i') }}</span>
                            </header>
                            <p>{{ $comment->body }}</p>
                        </div>
                    </article>
                @endforeach
            </div>
        @endif
    </section>
</main>
@endsection
