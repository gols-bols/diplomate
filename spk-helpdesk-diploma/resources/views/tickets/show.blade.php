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
                <span class="pill pill-muted">Корпус: {{ $ticket->campus_label }}</span>
            </div>
        </div>
        <div class="hero-badge">{{ $ticket->status_label }}</div>
    </section>

    <section class="panel stack">
        <div class="section-divider">Карточка обращения</div>

        <div class="detail-columns">
            <article class="detail-card description-card">
                <h2>Описание обращения</h2>
                <p>{{ $ticket->description }}</p>
            </article>

            <aside class="detail-card">
                <h3>Служебные сведения</h3>
                <div class="detail-list">
                    <div><strong>Заявитель:</strong> {{ $ticket->requester_name ?: ($ticket->creator?->name ?? 'Не указан') }}</div>
                    <div><strong>Роль заявителя:</strong> {{ $ticket->creator?->role_label ?? 'Не указана' }}</div>
                    <div><strong>Корпус:</strong> {{ $ticket->campus_label }}</div>
                    <div><strong>Кабинет:</strong> {{ $ticket->room ?: 'Не указан' }}</div>
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
            @endif
        </div>
    </section>
</main>
@endsection
