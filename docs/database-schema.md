# MSEDCL Quality Audit — Database Schema

## Tables

### `audits` — Call Quality Audit Records

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER | NO | Primary key, autoincrement |
| `department` | TEXT | NO | Inbound / Outbound |
| `call_id` | TEXT | YES | Call identifier |
| `call_date` | TEXT | YES | Call date (ISO format) |
| `evaluation_date` | TEXT | YES | Evaluation date |
| `advisor_id` | TEXT | YES | Employee/advisor ID |
| `advisor_name` | TEXT | NO | Advisor full name |
| `team_leader` | TEXT | YES | Team leader name |
| `auditor_name` | TEXT | YES | Quality auditor name |
| `quality_score` | REAL | YES | Quality score (0-100) |
| `is_fatal` | INTEGER | NO | 0 = non-fatal, 1 = fatal |
| `fatal_category` | TEXT | YES | Fatal reason category |
| `error_categories` | TEXT | YES | Error categories |
| `observation` | TEXT | YES | Auditor remarks |
| `location` | TEXT | YES | Location/center/site |
| `audio_url` | TEXT | YES | Call recording URL |
| `source_file` | TEXT | YES | Uploaded filename |
| `import_batch` | TEXT | YES | Import batch ID |
| `row_hash` | TEXT | YES | Unique hash (deduplication) |
| `imported_at` | TEXT | NO | Import timestamp |

### `warnings` — Disciplinary Warnings & PIPs

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | NO | — | Primary key, autoincrement |
| `advisor_id` | TEXT | YES | — | Advisor ID |
| `advisor_name` | TEXT | NO | — | Advisor name |
| `warning_type` | TEXT | NO | — | Warning type |
| `issue_date` | TEXT | NO | — | Issue date |
| `status` | TEXT | YES | 'Open' | Open/In Progress/Closed |
| `created_by` | TEXT | YES | — | Username who created |
| `created_at` | TEXT | NO | — | Creation timestamp |
| `advisor_feedback` | TEXT | YES | — | Advisor feedback |

### `import_batches` — File Upload Tracking

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | TEXT | NO | Primary key (batch ID) |
| `department` | TEXT | NO | Inbound / Outbound |
| `source_file` | TEXT | NO | Uploaded filename |
| `uploaded_by` | TEXT | NO | Username |
| `uploaded_at` | TEXT | NO | Upload timestamp |
| `rows_seen` | INTEGER | NO | Total rows in file |
| `rows_inserted` | INTEGER | NO | Successfully inserted rows |
| `duplicates` | INTEGER | NO | Duplicate rows skipped |
| `rejected` | INTEGER | NO | Rejected rows |
| `report_json` | TEXT | YES | Error details JSON |

### `users` — RBAC User Accounts

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | NO | — | Primary key, autoincrement |
| `username` | TEXT | NO | — | Unique username |
| `password_hash` | TEXT | NO | — | PBKDF2-SHA256 hash |
| `role` | TEXT | NO | — | admin/quality/manager/viewer/advisor |
| `active` | INTEGER | NO | 1 | 1 = active, 0 = inactive |
| `created_at` | TEXT | YES | datetime('now') | Creation timestamp |
| `last_login` | TEXT | YES | — | Last login timestamp |
| `email` | TEXT | YES | — | Email address |
| `full_name` | TEXT | YES | — | Full name |
| `advisor_id` | TEXT | YES | — | Linked advisor code |

**CHECK constraint:** `role IN ('admin','quality','manager','viewer','advisor')`

### `email_history` — Email Dispatch Audit Trail

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | NO | — | Primary key |
| `warning_id` | INTEGER | YES | — | References warnings.id |
| `created_at` | TEXT | NO | — | Creation timestamp |
| `employee_id` | TEXT | YES | — | Employee ID |
| `advisor_name` | TEXT | NO | — | Advisor name |
| `department` | TEXT | YES | — | Department |
| `recipient_email` | TEXT | NO | — | Recipient email |
| `email_type` | TEXT | NO | — | Email type |
| `subject` | TEXT | NO | — | Email subject |
| `body` | TEXT | NO | — | Email body |
| `related_audit_ids` | TEXT | YES | — | Related audit IDs |
| `created_by` | TEXT | NO | — | Creator username |
| `sent_status` | TEXT | NO | 'Draft' | Draft/Sent/Failed |
| `sent_at` | TEXT | YES | — | Sent timestamp |
| `delivery_status` | TEXT | YES | 'Pending Confirmation' | Delivery status |
| `acknowledgement_at` | TEXT | YES | — | Acknowledgement timestamp |
| `error_details` | TEXT | YES | — | Error details if failed |

### `audit_logs` — Security Audit Trail

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | INTEGER | NO | — | Primary key |
| `timestamp` | TEXT | NO | — | Action timestamp |
| `actor_username` | TEXT | NO | — | User who performed action |
| `actor_role` | TEXT | NO | — | Role of actor |
| `action` | TEXT | NO | — | Action type |
| `target_entity` | TEXT | YES | — | Entity affected |
| `details` | TEXT | YES | — | Additional details |
| `ip_address` | TEXT | YES | — | Source IP address |

### `system_settings` — Configurable System Settings

| Column | Type | Nullable | Description |
|---|---|---|---|
| `setting_key` | TEXT | NO | Primary key |
| `setting_value` | TEXT | NO | Setting value |
| `updated_at` | TEXT | NO | Last update timestamp |
| `updated_by` | TEXT | NO | Username who updated |

## Default System Settings

| Key | Default Value |
|---|---|
| `company_name` | Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL) |
| `admin_email` | admin.qa@msedcl.in |
| `enable_excel_import` | true |
| `default_date_range` | 30 |
| `email_provider` | smtp |
| `smtp_host` | (empty) |
| `smtp_port` | 587 |
| `smtp_username` | (empty) |
| `smtp_password` | (empty) |
| `smtp_from` | quality.audit@msedcl.in |
| `ms_client_id` | (empty) |
| `ms_tenant_id` | (empty) |
| `ms_client_secret` | (empty) |
| `ms_sender_email` | (empty) |
| `notify_on_fatal` | false |
| `notify_on_import` | false |

## Default Seed Users (created only if `users` table is empty)

| Username | Role | Password Source (local demo only) |
|---|---|---|
| `qaadmin` | admin | `ADMIN_PASSWORD` env var or the local demo fallback |
| `quality1` | quality | `QUALITY_PASSWORD` env var or the local demo fallback |
| `manager1` | manager | `MANAGER_PASSWORD` env var or the local demo fallback |

## Data Safety

- No data reset, truncation, or destructive migrations performed
- All existing records preserved
- Primary keys and foreign key relationships intact
- Row hash deduplication prevents duplicate audit imports
- Audit logs immutable (only INSERT, no UPDATE/DELETE)