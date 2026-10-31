"""Regression tests for the React client JSON API."""

import os
import sqlite3

from werkzeug.security import generate_password_hash


def _create_user(db_path, username, role="quality", advisor_id=None):
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash("testpass123"),
                role,
                f"{username}@msedcl.in",
                "Test User",
                advisor_id,
            ),
        )


def _api_login(client, username):
    with client.session_transaction() as session:
        token = session["_csrf_token"]
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "testpass123"},
        headers={"X-CSRF-Token": token},
    )
    return response


def test_api_login_rotates_csrf_and_returns_session_user(test_app, csrf_token):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "react-user")
    anonymous_token = csrf_token()

    response = test_app.post(
        "/api/v1/auth/login",
        json={"username": "react-user", "password": "testpass123"},
        headers={"X-CSRF-Token": anonymous_token},
    )

    assert response.status_code == 200
    assert response.json["user"]["username"] == "react-user"
    assert response.json["next"] == "/"
    assert csrf_token() != anonymous_token
    assert test_app.get("/api/v1/auth/me").json["role"] == "quality"


def test_api_login_requires_csrf(test_app):
    response = test_app.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 403
    assert "CSRF" in response.json["error"]["message"]


def test_api_logout_requires_csrf_and_clears_session(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "logout-user")
    assert _api_login(test_app, "logout-user").status_code == 200
    with test_app.session_transaction() as session:
        token = session["_csrf_token"]

    response = test_app.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 200
    assert response.json["ok"] is True
    assert test_app.get("/api/v1/auth/me").status_code == 401


def test_api_dashboard_requires_authentication(test_app):
    response = test_app.get("/api/v1/dashboard")
    assert response.status_code == 401
    assert response.json["error"]["message"] == "Sign in to continue."


def test_api_dashboard_returns_real_empty_state_and_filters(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "dashboard-user")
    _api_login(test_app, "dashboard-user")

    response = test_app.get("/api/v1/dashboard?department=Inbound")

    assert response.status_code == 200
    assert response.json["filters"]["department"] == "Inbound"
    assert response.json["metrics"]["total_audits"] == 0
    assert response.json["advisor_summary"] == []


def test_api_dashboard_denies_employee_roles(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "profile-user", role="viewer", advisor_id="ADV-001")
    assert _api_login(test_app, "profile-user").status_code == 200

    response = test_app.get("/api/v1/dashboard")

    assert response.status_code == 403
    assert "not available" in response.json["error"]["message"]


def test_api_dashboard_aggregates_audits_without_synthetic_chart_values(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "real-dashboard-user")
    _api_login(test_app, "real-dashboard-user")
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO audits (
                department, advisor_id, advisor_name, auditor_name,
                call_date, quality_score, is_fatal, imported_at
            ) VALUES ('Inbound', 'ADV-101', 'Advisor One', 'Auditor One',
                      '2026-10-29', 75, 1, datetime('now'))
            """
        )
        connection.execute(
            """
            INSERT INTO audits (
                department, advisor_id, advisor_name, auditor_name,
                call_date, quality_score, is_fatal, imported_at
            ) VALUES ('Outbound', 'ADV-102', 'Advisor Two', 'Auditor One',
                      '2026-10-29', 95, 0, datetime('now'))
            """
        )

    response = test_app.get("/api/v1/dashboard")
    data = response.json

    assert response.status_code == 200
    assert data["metrics"]["total_audits"] == 2
    assert data["metrics"]["inbound_count"] == 1
    assert data["metrics"]["outbound_count"] == 1
    assert data["metrics"]["fatal_count"] == 1
    assert data["chart_data"]["dates"] == ["2026-10-29"]
    assert data["chart_data"]["inbound_by_date"] == [1]
    assert data["chart_data"]["outbound_by_date"] == [1]
    assert len(data["advisor_summary"]) == 2


def _admin_csrf_token(client):
    with client.session_transaction() as session:
        return session["_csrf_token"]


def test_admin_user_api_is_role_protected_and_never_returns_password_hash(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "api-admin", role="admin")
    assert _api_login(test_app, "api-admin").status_code == 200

    users_response = test_app.get("/api/v1/admin/users")

    assert users_response.status_code == 200
    admin_entry = next(
        user for user in users_response.json["users"] if user["username"] == "api-admin"
    )
    assert "password_hash" not in admin_entry

    created = test_app.post(
        "/api/v1/admin/users",
        json={
            "username": "new-operator",
            "full_name": "New Operator",
            "email": "operator@msedcl.in",
            "role": "quality",
            "password": "securepass123",
        },
        headers={"X-CSRF-Token": _admin_csrf_token(test_app)},
    )

    assert created.status_code == 201
    assert any(
        user["username"] == "new-operator"
        for user in test_app.get("/api/v1/admin/users").json["users"]
    )


def test_admin_settings_api_redacts_secrets_and_keeps_blank_secret_unchanged(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "settings-admin", role="admin")
    assert _api_login(test_app, "settings-admin").status_code == 200
    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO system_settings (setting_key, setting_value, updated_at, updated_by)
            VALUES (?, ?, datetime('now'), 'test')
            ON CONFLICT(setting_key) DO UPDATE SET
                setting_value=excluded.setting_value,
                updated_at=datetime('now'),
                updated_by='test'
            """,
            [
                ("smtp_password", "smtp-private-value"),
                ("ms_client_secret", "graph-private-value"),
                ("company_name", "MSEDCL"),
                ("admin_email", "admin@msedcl.in"),
            ],
        )

    response = test_app.get("/api/v1/admin/settings")
    assert response.status_code == 200
    assert "smtp_password" not in response.json["settings"]
    assert "ms_client_secret" not in response.json["settings"]
    assert response.json["smtp_password_configured"] is True
    assert response.json["ms_client_secret_configured"] is True

    saved = test_app.put(
        "/api/v1/admin/settings",
        json={
            "company_name": "MSEDCL QA",
            "admin_email": "admin@msedcl.in",
            "smtp_password": "",
            "ms_client_secret": "",
        },
        headers={"X-CSRF-Token": _admin_csrf_token(test_app)},
    )
    assert saved.status_code == 200
    with sqlite3.connect(db_path) as connection:
        values = dict(connection.execute(
            "SELECT setting_key, setting_value FROM system_settings WHERE setting_key IN ('smtp_password', 'ms_client_secret')"
        ))
    assert values == {
        "smtp_password": "smtp-private-value",
        "ms_client_secret": "graph-private-value",
    }


def test_admin_endpoints_enforce_roles_and_csrf(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "api-manager", role="manager")
    assert _api_login(test_app, "api-manager").status_code == 200

    assert test_app.get("/api/v1/admin/users").status_code == 200
    assert test_app.get("/api/v1/admin/settings").status_code == 403
    assert test_app.get("/api/v1/admin/audit-logs").status_code == 403

    response = test_app.post(
        "/api/v1/admin/users",
        json={
            "username": "not-an-admin",
            "role": "admin",
            "password": "securepass123",
        },
        headers={"X-CSRF-Token": _admin_csrf_token(test_app)},
    )
    assert response.status_code == 403


def test_admin_purge_requires_explicit_confirmation_and_preserves_accounts(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "purge-admin", role="admin")
    assert _api_login(test_app, "purge-admin").status_code == 200
    with sqlite3.connect(db_path) as connection:
        users_before_purge = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        connection.execute(
            """
            INSERT INTO audits (department, advisor_name, imported_at)
            VALUES ('Inbound', 'Advisor', datetime('now'))
            """
        )
        connection.execute(
            """
            INSERT INTO import_batches (
                id, department, source_file, uploaded_by, uploaded_at,
                rows_seen, rows_inserted, duplicates, rejected
            ) VALUES ('purge-test', 'Inbound', 'audit.csv', 'purge-admin',
                      datetime('now'), 1, 1, 0, 0)
            """
        )
    headers = {"X-CSRF-Token": _admin_csrf_token(test_app)}

    denied = test_app.post("/api/v1/admin/audits/purge", json={}, headers=headers)
    assert denied.status_code == 400
    assert "PURGE" in denied.json["error"]["message"]

    purged = test_app.post(
        "/api/v1/admin/audits/purge",
        json={"confirmation": "PURGE"},
        headers=headers,
    )
    assert purged.status_code == 200
    assert purged.json["deleted_audits"] == 1
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == users_before_purge
        assert connection.execute("SELECT COUNT(*) FROM audits").fetchone()[0] == 0


def test_admin_backup_download_is_admin_only_and_uses_active_database(test_app):
    db_path = os.environ["DATABASE_PATH"]
    _create_user(db_path, "backup-admin", role="admin")
    assert _api_login(test_app, "backup-admin").status_code == 200

    response = test_app.get("/api/v1/admin/backup")

    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment;")
    assert response.data.startswith(b"SQLite format 3\x00")
