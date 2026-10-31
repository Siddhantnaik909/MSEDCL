# MSEDCL Quality Audit — Route Inventory

This inventory records the existing Flask surface and the planned React API
surface. Existing paths are registered by `app.py` and route modules;
proposed `/api/v1` paths are not yet implemented.

## Existing routes

| Existing route | Methods | Feature | Access boundary |
|---|---|---|---|
| `/login` | GET, POST | Authentication | Public; POST requires CSRF |
| `/logout` | GET | Authentication | Clears session |
| `/` | GET | Dashboard | Authenticated; viewer/advisor redirected to own profile |
| `/audits` | GET | Audit landing | Authenticated |
| `/audits/<dept>` | GET | Department audits | Authenticated; own-record scope for viewer/advisor |
| `/fatal-calls` | GET | Fatal calls | Authenticated; own-record scope for viewer/advisor |
| `/score-reports` | GET | Score reports | Authenticated; own-record scope for viewer/advisor |
| `/auditors` | GET | Auditor analytics | Admin, quality, manager |
| `/advisor-search` | GET | Advisor search | Admin, quality, manager |
| `/export-center` | GET | Export center | Authenticated; viewer/advisor require assigned advisor ID |
| `/export/single/<key>` | GET | Single report download | Authenticated; row scope required |
| `/export/combined` | GET | Combined workbook | Authenticated; row scope required |
| `/export/zip` | GET | Report archive | Authenticated; row scope required |
| `/export/advisor/<emp_id>` | GET | Advisor workbook | Authenticated; viewer/advisor limited to self |
| `/warnings` | GET, POST | Warnings/PIPs | Authenticated; POST limited to admin, quality, manager |
| `/warnings/<warning_id>/send` | POST | Warning dispatch | Admin, quality, manager |
| `/warnings/<warning_id>/close` | POST | Warning closure | Admin, quality, manager |
| `/warnings/<warning_id>/delete` | POST | Warning deletion | Admin |
| `/warnings/<warning_id>/feedback` | POST | Advisor feedback | Authenticated; ownership enforced for viewer/advisor |
| `/email-history` | GET | Email history | Authenticated; viewer/advisor scoped |
| `/upload` | GET, POST | Workbook/CSV import | Admin, quality |
| `/upload/batch/<batch_id>/delete` | POST | Import batch deletion | Admin, quality |
| `/api/advisor/lookup` | GET | Advisor lookup | Authenticated; scoped for viewer/advisor |
| `/admin/users` | GET | User administration | Admin, manager |
| `/admin/users/create` | POST | User creation | Admin, manager; manager cannot grant admin |
| `/admin/users/<user_id>/toggle` | POST | Account activation | Admin, manager; manager cannot deactivate admin |
| `/admin/users/reset-password` | POST | Password reset | Admin |
| `/admin/users/<user_id>/delete` | POST | Account deletion | Admin |
| `/admin/settings` | GET, POST | System settings | Admin |
| `/admin/settings/test-email` | POST | SMTP test | Admin |
| `/admin/backup/download` | GET | Database backup | Admin |
| `/admin/audit-logs` | GET | Security audit logs | Admin |
| `/admin/audits/purge` | POST | Audit data purge | Admin |
| `/admin/restart` | POST | Application restart | Admin; password confirmation |
| `/my-profile` | GET | Own profile and records | Authenticated; own data only |
| `/profile` | GET | Profile compatibility route | Authenticated |

Every mutating route must retain CSRF protection. Exact behavior remains owned
by the implementation and its tests; this inventory is not a replacement for
those checks.

The authentication endpoints are registered from `routes/auth_routes.py`.
Administrator user-management endpoints are registered from
`routes/admin_routes.py`; their workflows and SQL are in
`services/user_management_service.py` and
`repositories/admin_user_repository.py`. Other feature handlers remain in
`app.py`.

## React API

| Existing capability | Implemented API |
|---|---|
| Login/logout/current user | `/api/v1/auth/csrf`, `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me` |
| Dashboard and score metrics | `/api/v1/dashboard` |

## Planned React API mapping

| Existing capability | Planned API |
|---|---|
| Audit views/fatal calls/score reports | `/api/v1/audits`, `/api/v1/audits/fatal`, `/api/v1/audits/score-reports` |
| Auditor and advisor views | `/api/v1/advisors`, `/api/v1/advisors/{advisor_id}` |
| Warning/PIP lifecycle | `/api/v1/warnings`, `/api/v1/warnings/{id}/send`, `/close`, `/feedback` |
| Email history | `/api/v1/email-history` |
| Upload and import batches | `/api/v1/imports/audits`, `/api/v1/imports/batches` |
| Downloads | `/api/v1/exports`, `/api/v1/exports/{key}`, `/combined`, `/archive` |
| User administration | `/api/v1/admin/users` and scoped subresources |
| Settings and audit logs | `/api/v1/admin/settings`, `/api/v1/admin/audit-logs` |
| Own profile | `/api/v1/me/profile` |

The API will be introduced incrementally. Existing HTML routes and new JSON
routes must call the same services so role rules and business logic remain
consistent.
