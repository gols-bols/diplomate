@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>Создание новой заявки</h1>
            <p>
                Заявка создается от имени текущего пользователя и сразу фиксируется с указанием корпуса и кабинета.
                Статус назначается системой автоматически и меняется уже сотрудниками сопровождения.
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
            <form class="form-panel" method="post" action="{{ route('tickets.store') }}">
                @csrf

                <label>
                    Заголовок заявки
                    <span class="hint">Коротко опишите проблему, чтобы ее можно было быстро идентифицировать.</span>
                    <input name="title" value="{{ old('title') }}" placeholder="Например: Не работает принтер в кабинете 21" required>
                </label>

                <label>
                    Корпус
                    <span class="hint">Укажите корпус, из которого поступает заявка.</span>
                    <select name="campus">
                        <option value="main" @selected(old('campus') === 'main')>Главный корпус</option>
                        <option value="1" @selected(old('campus', auth()->user()->campus) === '1')>Учебный корпус 1</option>
                        <option value="2" @selected(old('campus') === '2')>Учебный корпус 2</option>
                        <option value="3" @selected(old('campus') === '3')>Учебный корпус 3</option>
                    </select>
                </label>

                <label>
                    Кабинет
                    <span class="hint">Например: кабинет 21, аудитория 204, приемная.</span>
                    <input name="room" value="{{ old('room') }}" placeholder="Укажите кабинет или помещение" required>
                </label>

                <label>
                    Подробное описание
                    <span class="hint">Укажите обстоятельства возникновения проблемы, оборудование и желаемый результат.</span>
                    <textarea name="description" placeholder="Опишите ситуацию подробнее" required>{{ old('description') }}</textarea>
                </label>

                <label>
                    Приоритет
                    <span class="hint">Приоритет влияет на очередность обработки заявки.</span>
                    <select name="priority">
                        <option value="low" @selected(old('priority') === 'low')>Низкий</option>
                        <option value="normal" @selected(old('priority', 'normal') === 'normal')>Обычный</option>
                        <option value="high" @selected(old('priority') === 'high')>Высокий</option>
                    </select>
                </label>

                <div class="toolbar-actions">
                    <button type="submit">Сохранить заявку</button>
                    <a class="button secondary" href="{{ route('tickets.index') }}">Отмена</a>
                </div>
            </form>

            <aside class="aside-stack">
                <section class="info-card">
                    <h3>Кто подает обращение</h3>
                    <p>
                        Заявитель: {{ auth()->user()->name }}<br>
                        Корпус по профилю: {{ auth()->user()->campus_label }}
                    </p>
                </section>

                <section class="info-card">
                    <h3>Как работает маршрут</h3>
                    <p>
                        После отправки заявка автоматически получает статус «Открыта». Дальше ее видят сотрудники сопровождения,
                        а менять статус и назначение могут только менеджеры корпуса и администратор.
                    </p>
                </section>

                <section class="info-card">
                    <h3>Подсказка по оформлению</h3>
                    <p>
                        Лучше сразу указать точный кабинет и конкретно описать проблему: оборудование, симптомы и что именно не работает.
                    </p>
                </section>
            </aside>
        </div>
    </section>
</main>
@endsection
