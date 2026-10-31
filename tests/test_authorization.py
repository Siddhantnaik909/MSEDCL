"""Authorization tests for MSEDCL Quality Audit.

Tests role-based access control, record-level isolation, IDOR prevention,
and privilege escalation prevention.
"""

import pytest


class TestRoleBasedAccess:
    """Test that routes enforce correct role requirements."""

    def test_admin_can_access_all_routes(self, test_app):
        """Admin user should have access to all routes."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'admin', 1, 'admin@msedcl.in', 'Admin User')",
                ("admin", generate_password_hash("adminpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "admin", "password": "adminpass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/")
        assert response.status_code == 200

        response = test_app.get("/auditors")
        assert response.status_code == 200

        response = test_app.get("/admin/users")
        assert response.status_code == 200

        response = test_app.get("/admin/settings")
        assert response.status_code == 200

    def test_quality_can_access_quality_routes(self, test_app):
        """Quality user should access quality routes but not admin-only settings."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'quality', 1, 'quality@msedcl.in', 'Quality User')",
                ("quality", generate_password_hash("qualitypass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "quality", "password": "qualitypass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/")
        assert response.status_code == 200

        response = test_app.get("/upload")
        assert response.status_code == 200

        response = test_app.get("/warnings")
        assert response.status_code == 200

        response = test_app.get("/admin/settings", follow_redirects=False)
        assert response.status_code == 403

class TestRecordLevelIsolation:
    """Test that viewers/advisors see only their own records."""

    def test_viewer_sees_only_own_audits(self, test_app):
        """Viewer with advisor_id should only see their own audit records."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'viewer', 1, 'viewer@msedcl.in', 'Viewer User', 'ADV-001')",
                ("viewer1", generate_password_hash("viewerpass123")),
            )
            con.execute(
                "INSERT INTO audits (department, advisor_id, advisor_name, quality_score, is_fatal, imported_at) "
                "VALUES ('Inbound', 'ADV-001', 'Viewer User', 85, 0, datetime('now'))",
            )
            con.execute(
                "INSERT INTO audits (department, advisor_id, advisor_name, quality_score, is_fatal, imported_at) "
                "VALUES ('Inbound', 'ADV-002', 'Other User', 90, 0, datetime('now'))",
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "viewer1", "password": "viewerpass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/my-profile")

        response = test_app.get("/my-profile")
        assert response.status_code == 200
        assert b"Viewer User" in response.data
        assert b"Other User" not in response.data

    def test_advisor_cannot_access_other_advisors_export(self, test_app):
        """Advisor should not be able to export another advisor's data."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'advisor', 1, 'advisor1@msedcl.in', 'Advisor One', 'ADV-001')",
                ("advisor1", generate_password_hash("advisorpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "advisor1", "password": "advisorpass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/export/advisor/ADV-002", follow_redirects=False)
        assert response.status_code == 403

    def test_advisor_can_access_own_export(self, test_app):
        """Advisor should be able to export their own advisor data."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os


class TestPrivilegeEscalation:
    """Test that privilege escalation is prevented."""

    def test_manager_cannot_create_admin_account(self, test_app, csrf_token):
        """Manager user should not be able to create admin accounts."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'manager', 1, 'manager@msedcl.in', 'Manager User')",
                ("manager", generate_password_hash("managerpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "manager", "password": "managerpass123", "csrf_token": "test-token"},
        )

        response = test_app.post(
            "/admin/users/create",
            data={
                "username": "newadmin",
                "password": "newadminpass123",
                "role": "admin",
                "csrf_token": csrf_token(),
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

        with sqlite3.connect(db_path) as con:
            user = con.execute(
                "SELECT id FROM users WHERE username = 'newadmin'"
            ).fetchone()
            assert user is None

    def test_manager_cannot_deactivate_admin(self, test_app, csrf_token):
        """Manager user should not be able to deactivate admin accounts."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'manager', 1, 'manager@msedcl.in', 'Manager User')",
                ("manager", generate_password_hash("managerpass123")),
            )
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'admin', 1, 'admin@msedcl.in', 'Admin User')",
                ("admin", generate_password_hash("adminpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "manager", "password": "managerpass123", "csrf_token": "test-token"},
        )

        response = test_app.post(
            "/admin/users/2/toggle",
            data={"csrf_token": csrf_token()},
            follow_redirects=False,
        )
        assert response.status_code == 302

        with sqlite3.connect(db_path) as con:
            user = con.execute(
                "SELECT active FROM users WHERE username = 'admin'"
            ).fetchone()
            assert user[0] == 1

    def test_csrf_protection_blocks_missing_token(self, test_app):
        """POST requests without valid CSRF token should be rejected."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'admin', 1, 'admin@msedcl.in', 'Admin User')",
                ("admin", generate_password_hash("adminpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "admin", "password": "adminpass123", "csrf_token": "test-token"},
        )

        response = test_app.post(
            "/admin/settings",
            data={"company_name": "Test"},
            follow_redirects=False,
        )
        assert response.status_code == 403
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'advisor', 1, 'advisor1@msedcl.in', 'Advisor One', 'ADV-001')",
                ("advisor1", generate_password_hash("advisorpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "advisor1", "password": "advisorpass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/export/advisor/ADV-001", follow_redirects=False)
        assert response.status_code in (200, 302)

    def test_manager_can_access_manager_routes(self, test_app):
        """Manager user should access manager routes but not admin-only routes."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'manager', 1, 'manager@msedcl.in', 'Manager User')",
                ("manager", generate_password_hash("managerpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "manager", "password": "managerpass123", "csrf_token": "test-token"},
        )

        response = test_app.get("/")
        assert response.status_code == 200

        response = test_app.get("/auditors")
        assert response.status_code == 200

        response = test_app.get("/admin/settings", follow_redirects=False)
        assert response.status_code == 403