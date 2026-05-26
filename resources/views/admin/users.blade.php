@extends('layouts.app')

@section('content')
<main class="page">
    <section class="hero">
        <div>
            <h1>Админка пользователей</h1>
            <p>
                Здесь администратор управляет ролями и корпусами пользователей без прямого доступа к базе данных.
                Это отдельный служебный интерфейс для сопровождения системы.
            </p>
        </div>
        <div class="hero-badge">Только администратор</div>
    </section>

    <section class="panel stack">
        @if(session('success'))
            <div class="flash">{{ session('success') }}</div>
        @endif

        @if($errors->any())
            <ul class="error-list">
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        @endif

        <div class="section-divider">Пользователи и зоны ответственности</div>

        <div class="admin-grid">
            @foreach($users as $user)
                <article class="admin-card">
                    <header>
                        <div>
                            <h3>{{ $user->name }}</h3>
                            <p>{{ $user->email }}</p>
                        </div>
                        <span class="pill pill-muted">{{ $user->role_label }}</span>
                    </header>

                    <div class="admin-metrics">
                        <div>
                            <strong>{{ $user->created_tickets_count }}</strong>
                            <span>создано</span>
                        </div>
                        <div>
                            <strong>{{ $user->assigned_tickets_count }}</strong>
                            <span>назначено</span>
                        </div>
                        <div>
                            <strong>{{ $user->active_assigned_tickets_count }}</strong>
                            <span>активно</span>
                        </div>
                    </div>

                    <form class="admin-form" method="post" action="{{ route('admin.users.update', $user) }}">
                        @csrf
                        @method('put')

                        <label>
                            ФИО / название
                            <input name="name" value="{{ old('name', $user->name) }}" required>
                        </label>

                        <label>
                            Роль
                            <select name="role">
                                <option value="user" @selected(old('role', $user->role) === 'user')>Заявитель</option>
                                <option value="manager" @selected(old('role', $user->role) === 'manager')>Менеджер корпуса</option>
                                <option value="admin" @selected(old('role', $user->role) === 'admin')>Администратор</option>
                            </select>
                        </label>

                        <label>
                            Корпус
                            <select name="campus">
                                <option value="">Все корпуса / не указан</option>
                                @foreach(\App\Models\User::CAMPUS_LABELS as $value => $label)
                                    <option value="{{ $value }}" @selected(old('campus', $user->campus) === $value)>{{ $label }}</option>
                                @endforeach
                            </select>
                        </label>

                        <button type="submit">Сохранить пользователя</button>
                    </form>
                </article>
            @endforeach
        </div>
    </section>
</main>
@endsection
