"""Workflow tests for MSEDCL Quality Audit.

These tests validate core business flows without depending on fragile fixture data.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash


class TestWarningLifecycle:
    """Test warning/PIP creation, status transitions, and feedback."""

    def test_quality_can_create_warning(self, test_app, csrf_token):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'quality', 1, 'quality1@msedcl.in', 'Quality User')",
                ("quality_warning", generate_password_hash("qualitypass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "quality_warning", "password": "qualitypass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.post(
            "/warnings",
            data={
                "advisor_name": "Test Advisor",
                "advisor_id": "ADV-001",
                "department": "Inbound",
                "warning_type": "First Warning",
                "issue_date": "2024-01-15",
                "recipient_email": "advisor@msedcl.in",
                "subject": "Test Warning",
                "body": "Test body content",
                "status": "Open",
                "csrf_token": csrf_token(),
            },
            follow_redirects=False,
        )
        assert response.status_code == 302

        with sqlite3.connect(db_path) as con:
            warning = con.execute(
                "SELECT COUNT(*) FROM warnings WHERE advisor_name = ?",
                ("Test Advisor",),
            ).fetchone()
            assert warning[0] >= 1

    def test_viewer_cannot_create_warning(self, test_app, csrf_token):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'viewer', 1, 'viewer_workflow@msedcl.in', 'Viewer User', 'ADV-003')",
                ("viewer_workflow", generate_password_hash("viewerpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "viewer_workflow", "password": "viewerpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.post(
            "/warnings",
            data={
                "advisor_name": "Test Advisor",
                "advisor_id": "ADV-001",
                "department": "Inbound",
                "warning_type": "First Warning",
                "issue_date": "2024-01-15",
                "recipient_email": "advisor@msedcl.in",
                "subject": "Test Warning",
                "body": "Test body content",
                "csrf_token": csrf_token(),
            },
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_warning_status_lifecycle(self, test_app, csrf_token):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'admin', 1, 'admin_workflow@msedcl.in', 'Admin User')",
                ("admin_warning", generate_password_hash("adminpass123")),
            )
            con.execute(
                "INSERT INTO warnings (advisor_id, advisor_name, warning_type, issue_date, recipient_email, subject, body, email_status, status, created_by, created_at) "
                "VALUES ('ADV-001', 'Test Advisor', 'First Warning', '2024-01-15', 'advisor@msedcl.in', 'Test Subject', 'Test Body', 'Draft', 'Open', 'admin_warning', datetime('now'))"
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "admin_warning", "password": "adminpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.post(
            "/warnings/1/close",
            data={"closure_remarks": "Resolved successfully", "csrf_token": csrf_token()},
            follow_redirects=False,
        )
        assert response.status_code == 302

        with sqlite3.connect(db_path) as con:
            warning = con.execute("SELECT status FROM warnings WHERE id = 1").fetchone()
            assert warning[0] == "Closed"

    def test_advisor_can_submit_feedback(self, test_app, csrf_token):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'advisor', 1, 'advisor_workflow@msedcl.in', 'Advisor User', 'ADV-004')",
                ("advisor_feedback", generate_password_hash("advisorpass123")),
            )
            con.execute(
                "INSERT INTO warnings (advisor_id, advisor_name, warning_type, issue_date, recipient_email, subject, body, email_status, status, created_by, created_at) "
                "VALUES ('ADV-004', 'Advisor User', 'First Warning', '2024-01-15', 'advisor@msedcl.in', 'Test Subject', 'Test Body', 'Draft', 'Open', 'admin_warning', datetime('now'))"
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "advisor_feedback", "password": "advisorpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.post(
            "/warnings/1/feedback",
            data={"feedback": "I have taken corrective action.", "csrf_token": csrf_token()},
            follow_redirects=False,
        )
        assert response.status_code == 302

        with sqlite3.connect(db_path) as con:
            warning = con.execute("SELECT advisor_feedback FROM warnings WHERE id = 1").fetchone()
            assert warning[0] == "I have taken corrective action."

    def test_advisor_cannot_submit_feedback_for_others_warning(self, test_app, csrf_token):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name, advisor_id) "
                "VALUES (?, ?, 'advisor', 1, 'advisor_other@msedcl.in', 'Advisor Other', 'ADV-005')",
                ("advisor_other", generate_password_hash("advisorpass123")),
            )
            con.execute(
                "INSERT INTO warnings (advisor_id, advisor_name, warning_type, issue_date, recipient_email, subject, body, email_status, status, created_by, created_at) "
                "VALUES ('ADV-006', 'Advisor One', 'First Warning', '2024-01-15', 'advisor@msedcl.in', 'Test Subject', 'Test Body', 'Draft', 'Open', 'admin_warning', datetime('now'))"
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "advisor_other", "password": "advisorpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.post(
            "/warnings/1/feedback",
            data={"feedback": "Unauthorized feedback", "csrf_token": csrf_token()},
            follow_redirects=False,
        )
        assert response.status_code == 403


class TestExportFunctionality:
    """Test export routes enforce data isolation."""

    def test_admin_can_export_all(self, test_app):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'admin', 1, 'admin_export@msedcl.in', 'Admin User')",
                ("admin_export", generate_password_hash("adminpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "admin_export", "password": "adminpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.get("/export-center", follow_redirects=False)
        assert response.status_code == 200

    def test_viewer_without_advisor_id_cannot_export(self, test_app):
        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'viewer', 1, 'viewer_export@msedcl.in', 'Viewer User')",
                ("viewer_export", generate_password_hash("viewerpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "viewer_export", "password": "viewerpass123", "csrf_token": "test-token"},
            follow_redirects=False,
        )

        response = test_app.get("/export-center", follow_redirects=False)
        assert response.status_code == 302
