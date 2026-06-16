<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title ?? 'Система заявок СПК' }}</title>
    <style>
        :root {
            --bg: #f4efe6;
            --panel: rgba(255, 252, 247, 0.92);
            --panel-strong: #fffaf2;
            --line: #dccdb4;
            --text: #2f261a;
            --muted: #72614b;
            --accent: #9c4f2d;
            --accent-dark: #74371d;
            --success-bg: #e6f3e8;
            --success-text: #27573a;
            --danger-bg: #fbe7e3;
            --danger-text: #8f3626;
            --status-open-bg: #fff3d8;
            --status-open-text: #8a5a00;
            --status-progress-bg: #dff1ff;
            --status-progress-text: #0d5885;
            --status-resolved-bg: #e3f7ea;
            --status-resolved-text: #22663a;
            --status-closed-bg: #ece7ff;
            --status-closed-text: #5a4aa8;
            --shadow: 0 24px 60px rgba(72, 49, 23, 0.12);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(201, 143, 94, 0.22), transparent 28%),
                radial-gradient(circle at bottom right, rgba(112, 143, 123, 0.18), transparent 24%),
                linear-gradient(180deg, #f7f2ea 0%, #efe4d3 100%);
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        .page {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
            padding: 32px 0 48px;
        }

        .hero {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            align-items: flex-start;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            padding: 28px 30px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(255, 251, 245, 0.96), rgba(238, 225, 206, 0.9)),
                radial-gradient(circle at top right, rgba(156, 79, 45, 0.12), transparent 30%);
            box-shadow: 0 30px 60px rgba(72, 49, 23, 0.16);
            backdrop-filter: blur(10px);
        }

        .hero::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 10px;
            background: linear-gradient(180deg, #b05f36 0%, #8f4626 100%);
        }

        .hero h1 {
            margin: 0 0 10px;
            font-size: clamp(30px, 4vw, 46px);
            line-height: 1;
            letter-spacing: -0.03em;
        }

        .hero p {
            margin: 0;
            max-width: 720px;
            color: var(--muted);
            line-height: 1.6;
        }

        .hero-badge {
            flex-shrink: 0;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(255, 250, 242, 0.78);
            color: var(--accent);
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 12px;
            border: 1px solid rgba(156, 79, 45, 0.12);
        }

        .panel {
            padding: 24px;
            border: 1px solid rgba(220, 205, 180, 0.9);
            border-radius: 24px;
            background: var(--panel);
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
        }

        .stack {
            display: grid;
            gap: 18px;
        }

        .flash,
        .error-list {
            padding: 14px 16px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.5;
        }

        .flash {
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid rgba(39, 87, 58, 0.14);
        }

        .error-list {
            margin: 0;
            padding-left: 28px;
            background: var(--danger-bg);
            color: var(--danger-text);
            border: 1px solid rgba(143, 54, 38, 0.14);
        }

        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        .toolbar-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }

        .button,
        button {
            appearance: none;
            border: 0;
            border-radius: 14px;
            padding: 12px 18px;
            background: var(--accent);
            color: #fff;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.15s ease, background 0.15s ease;
        }

        .button:hover,
        button:hover {
            background: var(--accent-dark);
            transform: translateY(-1px);
        }

        .button.secondary,
        .button-muted {
            background: rgba(114, 97, 75, 0.12);
            color: var(--text);
        }

        .grid {
            display: grid;
            gap: 18px;
        }

        .filters-grid {
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            align-items: end;
        }

        .tickets-grid {
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        }

        .ticket-card {
            position: relative;
            overflow: hidden;
            padding: 22px;
            border-radius: 16px;
            background:
                linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(248, 241, 232, 0.92));
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 18px 34px rgba(91, 64, 33, 0.08);
            display: grid;
            gap: 14px;
        }

        .ticket-card::after {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 90px;
            height: 90px;
            background: radial-gradient(circle, rgba(176, 95, 54, 0.12) 0%, transparent 70%);
            pointer-events: none;
        }

        .ticket-card header {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: flex-start;
        }

        .ticket-card h3 {
            margin: 0;
            font-size: 22px;
            line-height: 1.15;
        }

        .ticket-card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
        }

        .ticket-title-group {
            display: grid;
            gap: 8px;
            padding-right: 24px;
        }

        .ticket-kicker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--accent);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .ticket-kicker::before {
            content: "";
            width: 18px;
            height: 2px;
            background: var(--accent);
        }

        .meta {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(156, 79, 45, 0.1);
            color: var(--accent-dark);
            font-size: 13px;
            font-weight: 700;
        }

        .pill-muted {
            background: rgba(114, 97, 75, 0.12);
            color: var(--muted);
        }

        .status-open {
            background: var(--status-open-bg);
            color: var(--status-open-text);
        }

        .status-progress {
            background: var(--status-progress-bg);
            color: var(--status-progress-text);
        }

        .status-resolved {
            background: var(--status-resolved-bg);
            color: var(--status-resolved-text);
        }

        .status-closed {
            background: var(--status-closed-bg);
            color: var(--status-closed-text);
        }

        .detail-list {
            display: grid;
            gap: 8px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.5;
            padding-top: 8px;
            border-top: 1px solid rgba(220, 205, 180, 0.8);
        }

        .detail-list strong {
            color: var(--text);
        }

        .detail-card {
            padding: 20px;
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255, 252, 248, 0.98), rgba(245, 237, 226, 0.9));
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 16px 34px rgba(84, 60, 31, 0.08);
        }

        .detail-card h2,
        .detail-card h3 {
            margin: 0 0 12px;
        }

        .detail-columns {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 18px;
        }

        .form-shell {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 18px;
            align-items: start;
        }

        .form-panel {
            display: grid;
            gap: 16px;
        }

        .aside-stack {
            display: grid;
            gap: 16px;
        }

        .info-card {
            position: relative;
            overflow: hidden;
            padding: 20px;
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(246, 237, 224, 0.92));
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 16px 34px rgba(84, 60, 31, 0.08);
        }

        .info-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: linear-gradient(180deg, #b05f36 0%, #8f4626 100%);
        }

        .info-card h3 {
            margin: 0 0 10px;
            font-size: 20px;
        }

        .info-card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
        }

        .ticket-hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 14px;
        }

        .description-card {
            min-height: 100%;
        }

        .description-card p {
            font-size: 16px;
            line-height: 1.7;
        }

        .wide-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .section-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--accent);
            font-size: 12px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 700;
        }

        .section-divider::before,
        .section-divider::after {
            content: "";
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(156, 79, 45, 0.12), rgba(156, 79, 45, 0.5), rgba(156, 79, 45, 0.12));
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
        }

        .stat-card {
            position: relative;
            overflow: hidden;
            padding: 20px 18px 18px 24px;
            border-radius: 10px;
            background: linear-gradient(180deg, rgba(255, 252, 248, 0.98), rgba(248, 239, 226, 0.86));
            border: 1px solid rgba(214, 196, 170, 0.95);
            box-shadow: 0 14px 34px rgba(88, 61, 31, 0.08);
        }

        .stat-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 7px;
            background: var(--accent);
        }

        .stat-card small {
            display: block;
            color: var(--muted);
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
        }

        .stat-card strong {
            display: block;
            margin-top: 10px;
            font-size: 36px;
            line-height: 1;
        }

        .stat-card span {
            display: block;
            margin-top: 8px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.4;
        }

        .stat-card.status-open-card::before {
            background: #d2a02f;
        }

        .stat-card.status-progress-card::before {
            background: #2f7fc4;
        }

        .stat-card.status-resolved-card::before {
            background: #3f8c57;
        }

        .stat-card.status-closed-card::before {
            background: #6955c4;
        }

        .empty {
            padding: 26px;
            border: 1px dashed var(--line);
            border-radius: 22px;
            text-align: center;
            color: var(--muted);
            background: rgba(255, 250, 242, 0.75);
        }

        .form-grid {
            display: grid;
            gap: 16px;
        }

        label {
            display: grid;
            gap: 8px;
            font-weight: 700;
        }

        .hint {
            font-size: 14px;
            font-weight: 400;
            color: var(--muted);
        }

        input,
        textarea,
        select {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid var(--line);
            background: #fffdf9;
            color: var(--text);
            font: inherit;
        }

        textarea {
            min-height: 180px;
            resize: vertical;
        }

        .footer-note {
            margin-top: 18px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.6;
        }

        .auth-shell {
            width: min(520px, calc(100% - 32px));
            margin: 0 auto;
            padding: 60px 0;
        }

        @media (max-width: 720px) {
            .page {
                width: min(100% - 20px, 1120px);
                padding-top: 20px;
            }

            .panel,
            .hero {
                padding: 20px;
                border-radius: 22px;
            }

            .hero {
                flex-direction: column;
            }

            .detail-columns {
                grid-template-columns: 1fr;
            }

            .form-shell {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
@yield('content')
</body>
</html>
