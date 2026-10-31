# MSEDCL Quality Audit — Refactor Plan

## Guardrails

- Preserve the existing SQLite database and user workflows.
- Do not remove Jinja routes before React parity and authorization tests exist.
- Keep the Flask server as the sole authority for identity, roles, CSRF, and
  record-level access.
- Extract behavior in small slices; keep a runnable application at every stage.
- Run the existing tests at each stage and add focused tests before moving a
  workflow.

## Phases

### 1. Establish baseline and contracts

- Keep the existing auth, authorization, and workflow suite green.
- Correct route and permission documentation against implementation.
- Define versioned API response/error conventions and OpenAPI contract.
- Capture representative behavior for dashboard, warnings, imports, exports,
  and own-profile scoping.

**Exit:** route inventory and permission policy reviewed; API contract checked
into `contracts/openapi.yaml`.

### 2. Create application package without behavior changes

- Introduce `create_app(config=None)` and explicit configuration.
- Keep root `app.py` as a compatibility entry point importing the app factory.
- Move startup/blueprint wiring first; do not move every handler in one change.
- Make database initialization/migrations an explicit CLI/deployment step, not
  a side effect of importing the application.

**Exit:** legacy routes still render and current tests pass using the factory.

### 3. Extract shared backend capabilities

Move related code in this order:

1. Authentication, CSRF, and authorization policy helpers.
2. SQLite connection and repositories for users/audits.
3. Dashboard and audit query services.
4. Warning lifecycle and email dispatch services.
5. Import and export services.
6. Administration and system settings.

Legacy routes should become thin adapters to the extracted services. Each
slice receives service and route tests before proceeding.

**Exit:** route handlers contain request/response orchestration, not SQL or
business workflows.

### 4. Add the versioned JSON API

- Implement `/api/v1/auth/csrf`, login, logout, and current-user endpoints.
- Use the existing session model; add API-compatible CSRF headers.
- Add API endpoints feature-by-feature, starting with dashboard, audits, and
  profile, then warnings, imports, exports, and admin.
- Apply role and record policies on the server and test both allowed and denied
  paths.
- Use consistent JSON errors and a versioned API contract.

**Exit:** API integration tests cover status codes, CSRF, RBAC, and data
isolation for each migrated feature.

### 5. Add React + TypeScript client

- Set up Vite, TypeScript, router, shared layout, typed API client, and test
  runner.
- Implement login/current-user handling first, then dashboard and profile.
- Migrate audits, warnings, exports/imports, and admin features in that order.
- Add loading, empty, validation, permission-denied, and server-error states.
- Keep the UI accessible and responsive; do not rely on role-hidden controls
  for security.

**Exit:** end-to-end coverage demonstrates the existing core workflows through
React and the JSON API.

### 6. Cut over and retire legacy UI selectively

- Compare route behavior and permissions for each migrated feature.
- Keep old routes available during a defined transition period.
- Remove a Jinja page only after users have a React equivalent and tests cover
  the replaced flow.
- Retain file-generation and operational endpoints in Flask.

**Exit:** the React app is the default UI, with documented rollback and no
unintended route or data loss.

### 7. Operational hardening

- Review deployment, session cookie, CSRF, rate limiting, backup, logging, and
  upload limits in the target environment.
- Measure database write concurrency before deciding whether to migrate from
  SQLite.
- Add browser-level smoke tests and database restore verification.

**Exit:** deployment and rollback are tested in a non-production environment.

## First implementation slice

The first code change should only introduce the Flask application factory and
test configuration while retaining the existing route module. This reduces
startup coupling and creates a stable place to register future API and legacy
blueprints. It must not move all routes or create a placeholder React UI in the
same change.

## Out of scope until evidence supports it

- Microservices, message brokers, and distributed caching
- Replacing SQLite before concurrency or operations require it
- Moving authorization decisions to the browser
- Rewriting all server-rendered screens at once
- Replacing the warning/email workflows without parity tests
