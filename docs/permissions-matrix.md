# MSEDCL Quality Audit — Permissions Matrix

## Roles

| Role | Abbreviation | Purpose |
|---|---|---|
| **Admin** | admin | Full system control: user management, settings, purges, restarts, all data access |
| **Quality** | quality | Audit ingestion, warnings creation, all audit data access |
| **Manager** | manager | Audit viewing, reports, approvals, user management (non-admin roles) |
| **Viewer** | viewer | Read-only access to own advisor records |
| **Advisor** | advisor | Own records only, feedback submission on warnings |

## Route × Role Access Matrix

| Route | Admin | Quality | Manager | Viewer | Advisor | Notes |
|---|---|---|---|---|---|---|
| `/login` | ✅ | ✅ | ✅ | ✅ | ✅ | Public (POST with CSRF) |
| `/` (dashboard) | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/audits/<dept>` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/fatal-calls` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/score-reports` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/auditors` | ✅ | ✅ | ✅ | ❌ | ❌ | Team/individual performance stats |
| `/advisor-search` | ✅ | ✅ | ✅ | ❌ | ❌ | Advisor 360° drilldown |
| `/export-center` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor restricted to own advisor_id |
| `/export/zip` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor restricted to own advisor_id |
| `/export/advisor/<emp_id>` | ✅ | ✅ | ✅ | ✅* | ✅* | *Viewer/advisor only own advisor_id |
| `/warnings` (GET) | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/warnings` (POST) | ✅ | ✅ | ✅ | ❌ | ❌ | 403 for viewer/advisor |
| `/warnings/<id>/send` | ✅ | ✅ | ✅ | ❌ | ❌ | Email dispatch |
| `/warnings/<id>/close` | ✅ | ✅ | ✅ | ❌ | ❌ | Close/resolve warnings |
| `/warnings/<id>/delete` | ✅ | ❌ | ❌ | ❌ | ❌ | Admin only |
| `/warnings/<id>/feedback` | ✅ | ✅ | ✅ | ✅ | ✅ | Ownership verified for viewer/advisor |
| `/email-history` | ✅ | ✅ | ✅ | ✅ | ✅ | Viewer/advisor scoped to own advisor_id |
| `/upload` | ✅ | ✅ | ❌ | ❌ | ❌ | File ingestion |
| `/upload/batch/<id>/delete` | ✅ | ✅ | ❌ | ❌ | ❌ | Delete import batches |
| `/admin/users` | ✅ | ✅ | ✅ | ❌ | ❌ | User management |
| `/admin/users/create` | ✅ | ✅ | ✅* | ❌ | ❌ | *Manager cannot create admin accounts |
| `/admin/users/<id>/toggle` | ✅ | ✅ | ✅* | ❌ | ❌ | *Manager cannot deactivate admins |
| `/admin/users/reset-password` | ✅ | ❌ | ❌ | ❌ | ❌ | Admin only |
| `/admin/users/<id>/delete` | ✅ | ❌ | ❌ | ❌ | ❌ | Admin only |
| `/admin/settings` | ✅ | ❌ | ❌ | ❌ | ❌ | System configuration |
| `/admin/settings/test-email` | ✅ | ❌ | ❌ | ❌ | ❌ | SMTP testing |
| `/admin/audit-logs` | ✅ | ❌ | ❌ | ❌ | ❌ | Security audit trail |
| `/admin/audits/purge` | ✅ | ❌ | ❌ | ❌ | ❌ | Purge audit records (users preserved) |
| `/admin/restart` | ✅ | ❌ | ❌ | ❌ | ❌ | System restart (password verified) |
| `/api/advisor/lookup` | ✅ | ✅ | ✅ | ✅* | ✅* | *Viewer/advisor restricted to own advisor_id |

## Record-Level Isolation Rules

### Viewer / Advisor Roles
- **Dashboard**: Filtered by `advisor_id` (own records only)
- **Audits views**: Filtered by `advisor_id`
- **Fatal calls**: Filtered by `advisor_id`
- **Score reports**: Filtered by `advisor_id`
- **Export center/zip**: Restricted to own `advisor_id`; blocked if no `advisor_id` configured
- **Export advisor**: Blocked if requesting different advisor's data
- **Warnings (GET)**: Filtered by `advisor_id`
- **Warnings (POST)**: Blocked (403) for viewer/advisor
- **Email history**: Filtered by `advisor_id`
- **API advisor lookup**: Restricted to own advisor record

### Admin / Quality / Manager Roles
- Full access to all audit data
- No advisor_id filtering applied
- Can create warnings, uploads, manage users
- Cannot access another user's private data without explicit permission (fail-closed by default)

## Privilege Escalation Prevention

| Scenario | Protection |
|---|---|
| Manager creates admin account | Blocked (only admin can grant `admin` role) |
| Manager deactivates admin account | Blocked (only admin can deactivate admin) |
| Self-deactivation | Blocked (cannot deactivate own account) |
| Self-deletion | Blocked (cannot delete own account) |
| Client-supplied role field | Ignored; role set server-side |
| Client-supplied advisor_id | Ignored for auth; derived from session |
| IDOR via URL parameter | Blocked (`/export/advisor/<emp_id>` checks ownership) |
| Session fixation | Session cleared on login; new session created |

## CSRF Protection Scope

All POST routes protected:
- `/login`, `/upload`, `/warnings`, `/warnings/<id>/send|close|delete|feedback`
- `/admin/users/create|toggle|reset-password|delete`
- `/admin/settings`, `/admin/settings/test-email`
- `/admin/audits/purge`, `/admin/restart`
- `/upload/batch/<id>/delete`, `/api/advisor/lookup`

## Unsafe Practices Removed / Never Introduced

- ❌ No client-supplied `role`, `owner_id`, `tenant_id` trusted as authorization
- ❌ No frontend-only permission checks without server enforcement
- ❌ No plain-text password storage
- ❌ No SQL string interpolation
- ❌ No exposed secrets in templates, logs, or error messages