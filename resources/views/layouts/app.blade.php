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

        .topbar {
            width: min(1120px, calc(100% - 32px));
            margin: 20px auto 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            padding: 12px 14px;
            border-radius: 20px;
            background: rgba(255, 252, 247, 0.74);
            border: 1px solid rgba(220, 205, 180, 0.78);
            box-shadow: 0 16px 34px rgba(72, 49, 23, 0.08);
            backdrop-filter: blur(10px);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .brand-mark {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--accent), #d28a4d);
            color: #fff;
            box-shadow: 0 10px 22px rgba(156, 79, 45, 0.22);
        }

        .nav-links {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
            margin-left: auto;
        }

        .nav-user {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .nav-user-name {
            color: var(--muted);
            font-size: 14px;
            font-weight: 700;
        }

        .logout-form {
            margin: 0;
        }

        .logout-form button {
            padding: 9px 14px;
            border-radius: 999px;
            font-size: 14px;
        }

        .nav-link {
            padding: 9px 12px;
            border-radius: 999px;
            color: var(--muted);
            font-size: 14px;
            font-weight: 700;
        }

        .nav-link.active,
        .nav-link:hover {
            background: rgba(156, 79, 45, 0.1);
            color: var(--accent-dark);
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
            overflow-wrap: anywhere;
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

        .button:focus-visible,
        button:focus-visible,
        input:focus-visible,
        textarea:focus-visible,
        select:focus-visible,
        a:focus-visible {
            outline: 3px solid rgba(156, 79, 45, 0.22);
            outline-offset: 2px;
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

        .filters-row {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: flex-end;
        }

        .filters-row label {
            flex: 1 1 170px;
            min-width: 150px;
            margin: 0;
        }

        .filters-row--inline {
            flex-wrap: wrap;
            overflow-x: visible;
            gap: 16px;
        }

        .filters-row--inline label {
            flex: 1 1 220px;
            min-width: 180px;
            width: clamp(220px, 24%, 260px);
            margin-bottom: 0;
        }

        .filters-row .toolbar-actions {
            flex: 1 1 280px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-start;
            gap: 8px;
            margin-left: 0;
        }

        .filters-row--inline input,
        .filters-row--inline select {
            width: 100%;
            min-width: 0;
        }

        @media (max-width: 1100px) {
            .filters-row--inline {
                flex-wrap: wrap;
            }

            .filters-row--inline label,
            .filters-row .toolbar-actions {
                width: 100%;
            }

            .filters-row .toolbar-actions {
                justify-content: stretch;
            }
        }

        @media (max-width: 1100px) {
            .filters-row--inline {
                flex-wrap: wrap;
            }
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
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .ticket-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 22px 40px rgba(91, 64, 33, 0.12);
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
            overflow-wrap: anywhere;
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
            white-space: nowrap;
        }

        .pill,
        .filters-row label,
        .toolbar-actions button,
        .toolbar-actions a {
            min-width: 0;
        }

        .pill-muted {
            background: rgba(114, 97, 75, 0.12);
            color: var(--muted);
        }

        .pill-danger {
            background: var(--danger-bg);
            color: var(--danger-text);
        }

        .status-open {
            background: var(--status-open-bg);
            color: var(--status-open-text);
            border: 1px solid rgba(138, 90, 0, 0.16);
            box-shadow: inset 0 0 0 1px rgba(138, 90, 0, 0.08);
        }

        .status-progress {
            background: var(--status-progress-bg);
            color: var(--status-progress-text);
            border: 1px solid rgba(13, 88, 133, 0.16);
            box-shadow: inset 0 0 0 1px rgba(13, 88, 133, 0.08);
        }

        .status-resolved {
            background: var(--status-resolved-bg);
            color: var(--status-resolved-text);
            border: 1px solid rgba(34, 102, 58, 0.16);
            box-shadow: inset 0 0 0 1px rgba(34, 102, 58, 0.08);
        }

        .status-closed {
            background: var(--status-closed-bg);
            color: var(--status-closed-text);
            border: 1px solid rgba(90, 74, 168, 0.16);
            box-shadow: inset 0 0 0 1px rgba(90, 74, 168, 0.08);
        }

        .ticket-overdue {
            border-color: rgba(143, 54, 38, 0.34);
            box-shadow: 0 18px 34px rgba(143, 54, 38, 0.12);
        }

        .ticket-overdue::before {
            content: "Просрочено";
            position: absolute;
            right: 16px;
            bottom: 16px;
            padding: 6px 10px;
            border-radius: 999px;
            background: var(--danger-bg);
            color: var(--danger-text);
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .detail-list {
            display: grid;
            gap: 8px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.5;
            padding-top: 8px;
            border-top: 1px solid rgba(220, 205, 180, 0.8);
            overflow-wrap: anywhere;
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

        .ticket-attachment {
            margin: 18px 0 0;
        }

        .ticket-attachment img {
            display: block;
            width: 100%;
            max-height: 360px;
            object-fit: contain;
            border-radius: 14px;
            border: 1px solid rgba(214, 197, 171, 0.9);
            background: #fffdf9;
        }

        .ticket-attachment figcaption {
            margin-top: 8px;
            color: var(--muted);
            font-size: 13px;
        }

        .file-preview {
            display: block;
            margin-top: 8px;
            padding: 10px 12px;
            border-radius: 12px;
            background: var(--success-bg);
            color: var(--success-text);
            font-size: 14px;
        }

        input[type="file"] {
            margin-top: 6px;
            max-width: 100%;
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
            min-height: 148px;
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

        .analytics-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
            gap: 18px;
        }

        .chart-card {
            padding: 20px;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(246, 237, 224, 0.92));
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 16px 34px rgba(84, 60, 31, 0.08);
        }

        .chart-card h3 {
            margin: 0 0 14px;
        }

        .bar-list {
            display: grid;
            gap: 14px;
        }

        .bar-row {
            display: grid;
            gap: 7px;
        }

        .bar-row header {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--muted);
            font-size: 14px;
            font-weight: 700;
        }

        .bar-track {
            overflow: hidden;
            height: 12px;
            border-radius: 999px;
            background: rgba(114, 97, 75, 0.12);
        }

        .bar-fill {
            min-width: 6px;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--accent), #d28a4d);
        }

        .dashboard-list {
            display: grid;
            gap: 12px;
        }

        .dashboard-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
            padding: 13px 14px;
            border-radius: 14px;
            background: rgba(255, 250, 242, 0.76);
            border: 1px solid rgba(220, 205, 180, 0.72);
        }

        .dashboard-row strong {
            display: block;
        }

        .dashboard-row small {
            color: var(--muted);
        }

        .admin-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
        }

        .admin-card {
            display: grid;
            gap: 16px;
            padding: 20px;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(246, 237, 224, 0.92));
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 16px 34px rgba(84, 60, 31, 0.08);
        }

        .admin-card header {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: flex-start;
        }

        .admin-card h3 {
            margin: 0 0 6px;
            font-size: 22px;
        }

        .admin-card p {
            margin: 0;
            color: var(--muted);
            overflow-wrap: anywhere;
        }

        .admin-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        .admin-metrics div {
            padding: 12px;
            border-radius: 14px;
            background: rgba(255, 250, 242, 0.76);
            border: 1px solid rgba(220, 205, 180, 0.72);
        }

        .admin-metrics strong {
            display: block;
            font-size: 24px;
        }

        .admin-metrics span {
            display: block;
            color: var(--muted);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .admin-form {
            display: grid;
            gap: 12px;
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
            transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
        }

        input:focus,
        textarea:focus,
        select:focus {
            border-color: rgba(156, 79, 45, 0.55);
            box-shadow: 0 0 0 4px rgba(156, 79, 45, 0.08);
            background: #fff;
        }

        textarea {
            min-height: 180px;
            resize: vertical;
        }

        .comment-form {
            display: grid;
            gap: 14px;
            padding: 18px;
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(239, 226, 207, 0.74));
            border: 1px solid rgba(214, 197, 171, 0.9);
        }

        .comment-form textarea {
            min-height: 120px;
        }

        .timeline {
            position: relative;
            display: grid;
            gap: 14px;
            padding-left: 20px;
        }

        .timeline::before {
            content: "";
            position: absolute;
            top: 6px;
            bottom: 6px;
            left: 7px;
            width: 2px;
            background: linear-gradient(180deg, rgba(156, 79, 45, 0.62), rgba(156, 79, 45, 0.1));
        }

        .timeline-item {
            position: relative;
            display: grid;
            gap: 10px;
        }

        .timeline-marker {
            position: absolute;
            top: 18px;
            left: -18px;
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 0 5px rgba(156, 79, 45, 0.12);
        }

        .timeline-card {
            padding: 16px 18px;
            border-radius: 16px;
            background: rgba(255, 253, 249, 0.95);
            border: 1px solid rgba(214, 197, 171, 0.9);
            box-shadow: 0 12px 28px rgba(84, 60, 31, 0.07);
        }

        .timeline-system .timeline-card {
            background: rgba(238, 247, 240, 0.96);
            border-color: rgba(63, 140, 87, 0.22);
        }

        .timeline-card header {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .timeline-card header span {
            color: var(--muted);
            font-size: 13px;
        }

        .timeline-card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
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

            .topbar,
            .analytics-grid {
                grid-template-columns: 1fr;
            }

            .topbar {
                align-items: flex-start;
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
@auth
    <nav class="topbar">
        <a class="brand" href="{{ route('tickets.index') }}">
            <span class="brand-mark">СП</span>
            <span>СПК Helpdesk</span>
        </a>
        <div class="nav-links">
            <a class="nav-link {{ request()->routeIs('tickets.dashboard') ? 'active' : '' }}" href="{{ route('tickets.dashboard') }}">Дашборд</a>
            <a class="nav-link {{ request()->routeIs('tickets.index') ? 'active' : '' }}" href="{{ route('tickets.index') }}">Журнал</a>
            @if(auth()->user()->role === 'admin')
                <a class="nav-link {{ request()->routeIs('admin.users') ? 'active' : '' }}" href="{{ route('admin.users') }}">Админка</a>
            @endif
            @if(auth()->user()->role === 'user')
                <a class="nav-link {{ request()->routeIs('tickets.create') ? 'active' : '' }}" href="{{ route('tickets.create') }}">Новая заявка</a>
            @endif
            <div class="nav-user">
                <span class="nav-user-name">{{ auth()->user()->name }}</span>
                <form class="logout-form" method="post" action="{{ route('logout') }}">
                    @csrf
                    <button class="button-muted" type="submit">Выйти</button>
                </form>
            </div>
        </div>
    </nav>
@endauth
@yield('content')
</body>
</html>
