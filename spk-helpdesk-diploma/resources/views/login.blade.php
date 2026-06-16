@extends('layouts.app')

@section('content')
<main class="auth-shell">
    <section class="hero">
        <div>
            <h1>Система управления заявками</h1>
            <p>
                Внутренний web-интерфейс для регистрации и отслеживания обращений в ГБПОУ МО СПК.
                Текущая версия проекта поддерживает вход в систему и базовый цикл работы с заявками.
            </p>
        </div>
        <div class="hero-badge">Laravel 11</div>
    </section>

    <section class="panel stack">
        @if($errors->any())
            <ul class="error-list">
                @foreach($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        @endif

        <form class="form-grid" method="post" action="{{ route('login') }}">
            @csrf

            <label>
                Email
                <input type="email" name="email" value="{{ old('email') }}" placeholder="user@example.ru" required>
            </label>

            <label>
                Пароль
                <input type="password" name="password" placeholder="Введите пароль" required>
            </label>

            <button type="submit">Войти в систему</button>
        </form>

        <p class="footer-note">
            Для демонстрации проекта после миграций необходимо создать хотя бы одного пользователя в таблице
            <code>users</code> и использовать его учетные данные для входа.
        </p>
    </section>
</main>
@endsection
