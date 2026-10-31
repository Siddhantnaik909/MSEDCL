# MSEDCL Quality Audit — Current Architecture

## System context

```text
Browser
  ├─ HTML forms and pages ──> Flask routes in app.py / routes/ ──> SQLite
  ├─ CSS/JavaScript ────────> static/
  └─ React UI ──────────────> /api/v1 auth/dashboard/admin ──> shared SQLite
       └─ unmigrated workflows ──> existing Flask/Jinja routes

Flask app.py ──> routes/ ──> services/ ──> repositories/ ──> SQLite
           ├──> export_service.py ──> pandas / openpyxl
           ├──> init_db.py
           └──> migrate_db.py
```

The application is a Flask modular monolith with server-rendered Jinja pages
and a feature-by-feature React + TypeScript migration in `frontend/`. React
currently provides sign-in, the operations dashboard, and admin user,
settings, and audit-log pages. Other workflows continue to use Flask/Jinja.
In Render's Docker configuration, Flask serves the built React client from the
same origin as the API; local development uses Vite's API proxy instead.

## Existing boundaries

| Component | Responsibility | Current limitation |
|---|---|---|
| `app.py` | Startup, most feature routes, RBAC, workflows, integrations | Most feature handlers remain coupled |
| `export_service.py` | Export dataset preparation and file generation | The rest of the business logic is still in routes |
| `init_db.py` | Create the SQLite schema and seed initial settings/users | Called at import time by the app |
| `migrate_db.py` | Upgrade existing schema | Migration ownership is separate from route logic |
| `config/` | Environment-backed settings and logging configuration | Newly introduced |
| `middleware/security.py` | Login, role, CSRF, and response-header policies | Newly introduced and used by `app.py` |
| `routes/auth_routes.py` | Login/logout HTTP handlers | Newly introduced; existing endpoint names retained |
| `routes/admin_routes.py` | Administrator user-management HTTP handlers | Newly introduced; endpoint names and access rules retained |
| `routes/api_routes.py` | React session, dashboard, and admin JSON endpoints | CSRF/session checks and role boundaries |
| `services/auth_service.py` | Credential validation and login timestamp use case | Newly introduced |
| `services/dashboard_service.py` | Filtered dashboard metrics, charts, and advisor summary | Shared JSON API data source |
| `services/user_management_service.py` | User-management workflows and validation | Used by legacy and API routes |
| `services/frontend_service.py` | Serves the built React client and health check in production | Enabled by `SERVE_REACT_FRONTEND` |
| `repositories/` | SQLite connection and auth/admin-user queries | Newly introduced |
| `models/user.py` | Authenticated user model | Newly introduced |
| `templates/` | Server-rendered page UI | Not reusable as a React view layer |
| `static/` | CSS and JavaScript | Assets are not organized by feature |
| `tests/` | Auth, authorization, and workflow behavior | More service/API boundary tests are needed |

## Runtime request flow

1. Flask resolves a route declared in `app.py` or a registered route module.
2. React routes return the Vite build when production serving is enabled;
   unmigrated routes render their existing Jinja templates.
3. API and page authentication resolve the active user from the Flask session.
4. Role checks and any record-level filters are applied on the server.
5. Services/repositories or the shared SQLite connection perform data access.
6. Flask returns React/Jinja HTML, JSON, or a generated file.

## Data and trust boundaries

- SQLite is the system of record.
- The server-side session is the authority for identity and role.
- Viewer/advisor access must be scoped using the advisor ID from the loaded
  user record, never a client-provided identity.
- CSRF checks protect state-changing requests.
- Exports and file uploads are server-side operations and must retain existing
  validation and authorization.

## Transition constraints

- Keep the current Jinja application available while the React client is
  introduced.
- Do not move authorization into React or trust client-side role checks.
- Do not replace or recreate the database as part of modularization.
- Both interfaces must call the same application services during transition;
  business rules must not be duplicated between API and HTML routes.
- Retire a legacy route only after equivalent behavior and authorization are
  covered by tests.

## Status

The authentication/configuration and administrator user-management slices
are modularized. React sign-in, dashboard, user management, system settings,
and audit activity use the versioned API. Other feature routes remain in
`app.py`; the
proposed structure and migration stages are in
[`target-architecture.md`](./target-architecture.md) and
[`REFACTOR_PLAN.md`](./REFACTOR_PLAN.md).

For local commands see [`local-development.md`](./local-development.md). The
Render Blueprint builds and serves both clients in one Docker web service;
its current free-tier SQLite storage is ephemeral, as detailed in
[`render-deployment.md`](./render-deployment.md).
