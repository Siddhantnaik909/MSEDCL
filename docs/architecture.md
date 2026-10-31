# MSEDCL Quality Audit — Architecture

## Current design

The project is a modular Flask monolith with a gradual React + TypeScript
migration. Flask remains the security boundary, owns the SQLite database, and
continues to serve Jinja pages for workflows not yet migrated. React uses
versioned Flask JSON endpoints for sign-in, the dashboard, and admin user,
settings, and audit-log pages.

The Render Docker service builds React and Flask together. In that deployment,
Flask serves the React bundle and API on one origin, preserving session-cookie
and CSRF behavior. Local development runs Vite separately and proxies API
requests to Flask.

See [current architecture](./CURRENT_ARCHITECTURE.md),
[target architecture](./target-architecture.md), and
[refactor plan](./REFACTOR_PLAN.md) for boundaries and migration status.

## Request flow

```text
React browser ──> Flask /api/v1 ──> auth, role and CSRF checks
                                  └─> services/repositories ──> SQLite
React browser ──> Flask static frontend routes (production build)
Browser ────────> Flask/Jinja routes for workflows not yet migrated
```

## Application entry point

`app.py` configures Flask, logging, session settings, database initialization,
security headers, and route registration. `scripts/prestart.py` initializes
and migrates the configured database before Gunicorn starts in the Docker
deployment. Flask's development server is for local use only.

When `SERVE_REACT_FRONTEND=true`, the application serves `frontend/dist` for
the React root, sign-in, and migrated admin pages. It raises a clear error if
the production build is missing. Without that setting, Flask keeps the
existing Jinja pages as the default.

## Responsibilities

| Area | Responsibility |
|---|---|
| `config/` | Environment-backed settings and logging |
| `middleware/security.py` | Session authentication, role checks, CSRF, response headers |
| `routes/` | Auth, admin user-management, and versioned API HTTP handlers |
| `services/` | Shared authentication, dashboard, user, and frontend behavior |
| `repositories/` | SQLite connection and selected user queries |
| `app.py` | Existing legacy route handlers and application composition |
| `init_db.py` / `migrate_db.py` | Create the schema and upgrade existing databases |
| `frontend/src/` | React app, feature screens, shared shell, and API client |
| `templates/`, `static/` | Existing Flask/Jinja workflows and assets |

## Security and data boundaries

- Flask session data is the source of identity; the browser does not store a
  separate authorization token.
- Role checks and advisor record scoping are enforced server-side.
- Mutating requests use session-bound CSRF checks.
- Passwords are stored as hashes; Render account passwords are prompted as
  secrets and are not embedded in the Blueprint or Docker image.
- SQLite is the system of record. The current Render free-tier Blueprint uses
  ephemeral storage and is demo-only; see [Render deployment](./render-deployment.md).

## Migration boundaries

The React UI does not yet replace every workflow. Audit views, imports,
warnings/PIPs, email history, exports, and employee profile flows still rely
on Flask/Jinja routes. Keep those routes and their permission behavior until
an equivalent React/API implementation is tested.

For local commands see [local development](./local-development.md).
