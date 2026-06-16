<?php

declare(strict_types=1);

session_start();

date_default_timezone_set('Europe/Moscow');

$dbPath = __DIR__ . '/../data/app.sqlite';
$firstRun = !file_exists($dbPath);

$pdo = new PDO('sqlite:' . $dbPath);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$pdo->exec('PRAGMA foreign_keys = ON');

if ($firstRun) {
    $schema = file_get_contents(__DIR__ . '/../src/schema.sql');
    $pdo->exec($schema);

    $stmt = $pdo->prepare('INSERT INTO users (full_name, email, password_hash, role, department) VALUES (?, ?, ?, ?, ?)');
    $stmt->execute([
        'Администратор СПК',
        'admin@spk.local',
        password_hash('admin123', PASSWORD_DEFAULT),
        'admin',
        'ИТ-отдел',
    ]);
}

function db(): PDO
{
    global $pdo;
    return $pdo;
}

function current_user(): ?array
{
    if (!isset($_SESSION['user_id'])) {
        return null;
    }

    $stmt = db()->prepare('SELECT id, full_name, email, role, department FROM users WHERE id = ?');
    $stmt->execute([$_SESSION['user_id']]);
    $user = $stmt->fetch();

    if (!$user) {
        unset($_SESSION['user_id']);
        return null;
    }

    return $user;
}

function is_admin(): bool
{
    $user = current_user();
    return $user && in_array($user['role'], ['admin', 'manager'], true);
}

function redirect(string $url): void
{
    header('Location: ' . $url);
    exit;
}

function flash(string $type, string $message): void
{
    $_SESSION['flash'][] = ['type' => $type, 'message' => $message];
}

function flashes(): array
{
    $messages = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $messages;
}
