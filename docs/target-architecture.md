# MSEDCL Quality Audit — Target Architecture

## Design decision

Use one repository with two clients and one backend:

- **React + TypeScript** is the new primary interactive client.
- **Flask** remains the application and security boundary and exposes a
  versioned JSON API.
- **SQLite** remains the database during the initial refactor. Repositories
  isolate SQL so another database can be considered later without changing
  route or UI code.
- The current Jinja pages remain available during migration and reuse the same
  application services as the JSON API.

This is a modular monolith, not a microservice system. The application's
current size and operational needs do not justify splitting deployments or
duplicating authentication and authorization across services.

## Migration status

The existing project root now contains `config/`, `middleware/`, `models/`,
`repositories/`, `services/`, and `routes/`. Settings, security policies,
database/user queries, the authentication service, and login/logout routes have
been moved into modules. Other feature routes remain in `app.py`. React sign-in,
dashboard, and admin user/settings/audit pages use `/api/v1`; unmigrated
workflows remain in Flask/Jinja. Render's Docker deployment serves both clients
from the same Flask origin. The free-tier Blueprint uses ephemeral SQLite and
must not be treated as production storage.

## Target repository layout

```text
MSEDCL-clone/
├── app.py
├── config/
│   ├── settings.py
│   └── logging_config.py
├── routes/
│   ├── auth_routes.py
│   ├── home_routes.py
│   ├── admin_routes.py
│   ├── user_routes.py
│   ├── advisor_routes.py
│   ├── manager_routes.py
│   ├── audit_routes.py
│   ├── warning_routes.py
│   ├── import_routes.py
│   └── export_routes.py
├── services/
│   ├── auth_service.py
│   ├── audit_service.py
│   ├── warning_service.py
│   ├── import_service.py
│   └── export_service.py
├── models/
├── repositories/
├── middleware/
├── templates/
│   ├── components/
│   └── pages/
├── static/
│   ├── css/shared/
│   ├── css/pages/
│   └── js/
├── migrations/
├── tests/
├── frontend/                       # React + TypeScript client
│   ├── package.json
│   └── src/
│       ├── app/
│       ├── features/
│       ├── components/
│       └── lib/api/
├── docs/
├── requirements.txt
└── README.md
```

Directories that are not present yet are future migration targets. Files should
move in small, tested slices; do not make a large all-at-once rewrite.

## Backend responsibilities

### Application composition

`create_app(config=None)` builds the Flask app, loads explicit configuration,
registers API and legacy blueprints, installs error handlers/security headers,
and exposes health checks. Importing the package must not initialize a
production database or start a server.

### API layer

API endpoints under `/api/v1` should:

- Parse and validate input.
- Call one application service per use case.
- Return documented JSON or a generated file.
- Use a consistent success/error response and HTTP status.
- Avoid SQL and non-trivial business rules in route functions.

Suggested error shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request could not be processed.",
    "details": {},
    "request_id": "..."
  }
}
```

### Services and repositories

- **Services** own workflows: importing a workbook, creating or closing a
  warning, submitting feedback, computing dashboard metrics, and generating
  exports.
- **Repositories** own SQL and database transactions. They return domain data,
  not Flask responses or templates.
- **Domain rules** define role-independent business invariants.
- **Authorization policies** determine what an authenticated user may do and
  which records they may access.
- **Infrastructure adapters** handle SQLite, SMTP, uploaded files, and report
  rendering.

The existing export code should become an export service with database
selection passed in through a repository or service interface.

## React responsibilities

- Render pages and forms; handle navigation and accessible UI state.
- Call only the versioned API through one typed client.
- Keep server state in a query/cache layer; keep transient form state local.
- Treat authorization hints as display logic only. Flask remains authoritative.
- Use feature modules so workflows, API calls, and tests are colocated.
- Do not store session identifiers, access tokens, roles, or advisor identity
  in `localStorage`.

The API client should centralize credentials, CSRF headers, JSON parsing,
timeouts, and typed error conversion. API request/response types should be
generated from or checked against `contracts/openapi.yaml`.

## API outline

All routes below are proposed endpoints; they are not yet implemented.

| Resource | Example endpoints | Notes |
|---|---|---|
| Authentication | `GET /auth/csrf`, `POST /auth/login`, `POST /auth/logout`, `GET /me` | Session-cookie based; login and logout are CSRF protected |
| Dashboard | `GET /dashboard` | Server calculates data using the authenticated user's scope |
| Audits | `GET /audits`, `GET /audits/fatal`, `GET /audits/score-reports` | Filters validated server-side |
| Advisors | `GET /advisors`, `GET /advisors/{advisor_id}` | Admin/quality/manager searches; self-only for viewer/advisor |
| Warnings | `GET/POST /warnings`, `POST /warnings/{id}/send`, `POST /warnings/{id}/close`, `POST /warnings/{id}/feedback` | Role and ownership rules preserved |
| Imports | `POST /imports/audits`, `GET /imports/batches`, `DELETE /imports/batches/{id}` | Multipart upload and batch-specific permissions |
| Exports | `GET /exports`, `GET /exports/{key}`, `GET /exports/combined`, `GET /exports/archive` | Return streamed files; enforce row scope |
| Users | `GET/POST /admin/users`, `PATCH /admin/users/{id}`, `POST /admin/users/{id}/reset-password` | Admin/manager constraints enforced by backend |
| Settings | `GET/PATCH /admin/settings`, `GET /admin/audit-logs` | Admin-only |

Use plural resources and stable identifiers. Prefer `PATCH` for partial updates;
avoid exposing internal database schema as the public API.

## Authentication and security

- Use the existing server-side Flask session in an HttpOnly, SameSite cookie.
- Serve React and the API from the same origin in production where possible.
- Add `GET /api/v1/auth/csrf` to issue the anonymous/session token needed by
  the client. Send it in `X-CSRF-Token` for every unsafe HTTP method, including
  login and logout.
- Rotate the CSRF token after successful login and clear the session at logout.
- Keep cookies `Secure` in HTTPS production environments.
- Resolve the active user and role on the server for each request.
- Apply explicit role policies and record-level scoping in the API/service
  boundary. Never trust a client-supplied role or advisor ID for authorization.
- Keep parameterized queries, upload validation, audit logging, and current
  security headers.
- Return generic authentication failures; do not reveal whether a username
  exists.

## Data and migrations

- Keep SQLite initially and preserve `quality_audit.db` data.
- Route all database access through repositories and use explicit transaction
  boundaries for multi-step changes.
- Maintain forward-only, non-destructive schema migrations.
- Avoid initializing or seeding production users merely by importing a module.
- Evaluate PostgreSQL only if concurrent writes, multiple app instances, or
  operational backup requirements outgrow SQLite.

## Quality strategy

- **Backend unit tests:** service rules, validation, permission policies.
- **Backend integration tests:** repository SQL and transactions against a
  temporary database.
- **API tests:** status codes, response contracts, CSRF, RBAC, record isolation,
  and file downloads.
- **Frontend tests:** feature behavior, forms, error/empty/loading states,
  keyboard interaction, and role-aware navigation.
- **End-to-end tests:** login, audit browsing, warning lifecycle, import,
  export, and advisor isolation through the browser.
- Retain legacy route tests until their routes are retired.

## Deployment

Start with one deployable Flask service and a built React bundle served by the
same origin (static files or a reverse proxy). This keeps session cookies and
CSRF behavior straightforward. Keep local development proxying `/api` from the
Vite dev server to Flask. Do not introduce separate frontend/backend domains
unless deployment requirements call for them.
