# MSEDCL Quality Audit — File Inventory

## Root Directory

| File | Purpose |
|---|---|
| `app.py` | Main Flask application (~68KB). Contains all routes, authentication, authorization, business logic, database helpers, and request handlers. |
| `export_service.py` | Excel/CSV/ZIP report generation service. Styling, dataset building, and export logic for all 12 dataset types. |
| `init_db.py` | Database initialization. Creates all tables and seeds default settings and users. |
| `migrate_db.py` | Schema migrations. Adds columns/tables to existing databases without data loss. |
| `render.yaml` | Render.com cloud deployment configuration (build/start commands, env vars). |
| `run.bat` | Windows batch launcher. Creates venv, installs deps, runs migrations, launches app. |
| `.env.example` | Environment variable template (secrets, DB path, SMTP config). |
| `.gitignore` | Git ignore rules. |
| `requirements.txt` | Python package dependencies (Flask, pandas, openpyxl, gunicorn). |

### `static/` — Frontend Assets

| File | Purpose |
|---|---|
| `static/css/style.css` | Main application stylesheet (theme variables, layout, components). |
| `static/js/chart.umd.min.js` | Chart.js library for dashboard visualizations. |

### `templates/` — Jinja2 HTML Templates

| File | Purpose |
|---|---|
| `templates/layout.html` | Base layout with sidebar navigation, theme toggle, notifications, and global scripts. |
| `templates/login.html` | Sign-in page with CSRF-protected login form. |
| `templates/dashboard.html` | Main dashboard with filters, metrics, charts, and advisor summary table. |
| `templates/audits_view.html` | Audit listing page for Inbound/Outbound calls with filtering. |
| `templates/fatal_calls.html` | Fatal call listing page. |
| `templates/score_reports.html` | Quality score bracket breakdown page. |
| `templates/advisors.html` | Auditor performance summary page. |
| `templates/advisor_search.html` | Advisor 360° drilldown page (audits + warnings per advisor). |
| `templates/export_center.html` | Export center with format options and filters. |
| `templates/warnings.html` | Warnings & PIP management with create/send/close/delete/feedback actions. |
| `templates/email_history.html` | Email dispatch history view. |
| `templates/upload.html` | Excel/CSV file upload for audit ingestion. |
| `templates/user_management.html` | User account creation, role assignment, status toggle, password reset. |
| `templates/settings.html` | System settings (SMTP, email provider, backup, purge, restart). |
| `templates/restarting.html` | System restart in-progress page. |

## Route-to-Template Mapping

| Route | Template | Roles Required |
|---|---|---|
| `/login` | `login.html` | None (public) |
| `/` | `dashboard.html` | Any authenticated |
| `/audits/<dept>` | `audits_view.html` | Any authenticated |
| `/fatal-calls` | `fatal_calls.html` | Any authenticated |
| `/score-reports` | `audits_view.html` | Any authenticated |
| `/auditors` | `auditors.html` | admin, quality, manager |
| `/advisor-search` | `advisor_search.html` | admin, quality, manager |
| `/export-center` | `export_center.html` | Any authenticated |
| `/warnings` | `warnings.html` | admin, quality, manager, viewer, advisor |
| `/email-history` | `email_history.html` | admin, quality, manager |
| `/upload` | `upload.html` | admin, quality |
| `/admin/users` | `user_management.html` | admin, manager |
| `/admin/settings` | `settings.html` | admin |

## Key Dependencies

- `app.py` → `init_db.init_db()` (auto-init DB on startup)
- `app.py` → `export_service` module (report generation)
- All templates → `layout.html` (extends base layout)
- All templates → `static/css/style.css`, `static/js/chart.umd.min.js`
- `app.py` → SQLite database at `DATABASE_PATH` env var (default: `quality_audit.db`)
- `app.py` → `.env` file (loaded at startup if present)