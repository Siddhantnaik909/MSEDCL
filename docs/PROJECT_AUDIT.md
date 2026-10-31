# MSEDCL Quality Audit — Project audit

## Summary

This repository contains a Flask/SQLite quality-audit portal and a Vite React
and TypeScript client being migrated feature by feature. Flask remains the
backend and security authority. The React client uses a versioned API for
sign-in, the operations dashboard, administrator user management, system
settings, and audit activity. The remaining workflows continue to use
Flask/Jinja.

## Current implementation

| Area | Current implementation |
|---|---|
| Backend | Flask entry point in `app.py`; auth, admin-user, and API routes are modularized |
| UI | React + TypeScript in `frontend/`; existing Jinja templates remain active |
| API | `/api/v1` session/CSRF, dashboard, and administrator endpoints |
| Data | SQLite schema in `init_db.py`, updates in `migrate_db.py`, shared by both UIs |
| Services | Authentication, dashboard, user management, and frontend delivery helpers |
| Tests | Pytest auth, authorization, workflow, API, and deployment-serving coverage |
| Deployment | Multi-stage Docker build and Render Blueprint; free-tier database is ephemeral |

## Features retained

- Session login/logout and role-based access.
- Audit dashboards, filtering, scoring, and advisor analytics.
- Warnings/PIPs, feedback, email history, imports, and exports.
- User management, system settings, audit logs, database backup, and maintenance.
- Password hashing, CSRF protection, security headers, and server-side data
  scoping.

## Known boundaries and risks

1. `app.py` still contains most unmigrated feature handlers, SQL, and
   integrations; continue extracting them in small, tested slices.
2. The JSON API covers the React features listed above, not every Jinja
   workflow.
3. Database initialization still occurs during Flask import for compatibility;
   the production container also runs the explicit prestart initialization
   and migrations before Gunicorn.
4. The Render Blueprint is intentionally a demo setup. Free-tier SQLite data
   can be erased on restart or deployment. Do not enter production or
   irreplaceable data.
5. SQLite is intended for a single application instance. Production use needs
   durable storage, verified backups, and a tested restore procedure before
   relying on it; multi-instance writes require a different database design.

## Validation

From the project root, run `python -m pytest -q`. From `frontend/`, run
`npm run lint` and `npm run build`. The Render Docker build additionally
compiles the React app and starts Flask with `SERVE_REACT_FRONTEND=true`.

For setup and deployment steps, see [local development](./local-development.md)
and [Render deployment](./render-deployment.md).
