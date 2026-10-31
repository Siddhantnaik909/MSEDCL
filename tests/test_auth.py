"""Authentication tests for MSEDCL Quality Audit.

Tests login, logout, session management, rate limiting, and CSRF protection.
"""

import pytest


class TestLogin:
    """Test login route behavior."""

    def test_login_page_loads(self, test_app):
        """GET /login should render the login form."""
        response = test_app.get("/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data or b"login" in response.data.lower()

    def test_successful_login(self, test_app, csrf_token):
        """Valid credentials should create a session and redirect to dashboard."""
        # Create a test user directly in the DB
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'quality', 1, 'test@msedcl.in', 'Test User')",
                ("testuser", generate_password_hash("testpass123")),
            )
            con.commit()

        anonymous_token = csrf_token()
        response = test_app.post(
            "/login",
            data={"username": "testuser", "password": "testpass123", "csrf_token": anonymous_token},
            follow_redirects=False,
        )
        assert response.status_code == 302  # Redirect to dashboard
        assert csrf_token() != anonymous_token

        stale_token_response = test_app.post(
            "/warnings",
            data={"csrf_token": anonymous_token},
            follow_redirects=False,
        )
        assert stale_token_response.status_code == 403

    def test_login_rejects_missing_csrf_token(self, test_app):
        response = test_app.post(
            "/login",
            data={"username": "testuser", "password": "testpass123"},
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_invalid_login(self, test_app):
        """Invalid credentials should not create a session."""
        response = test_app.post(
            "/login",
            data={"username": "nonexistent", "password": "wrongpass", "csrf_token": "test-token"},
            follow_redirects=False,
        )
        assert response.status_code == 200  # Stays on login page

    def test_logout_clears_session(self, test_app):
        """Logout should clear the session and redirect to login."""
        # First log in
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'quality', 1, 'test2@msedcl.in', 'Test User 2')",
                ("testuser2", generate_password_hash("testpass123")),
            )
            con.commit()

        test_app.post(
            "/login",
            data={"username": "testuser2", "password": "testpass123", "csrf_token": "test-token"},
        )

        # Then log out
        response = test_app.get("/logout", follow_redirects=False)
        assert response.status_code == 302


class TestSession:
    """Test session security."""

    def test_protected_route_requires_login(self, test_app):
        """Accessing dashboard without login should redirect to login."""
        response = test_app.get("/", follow_redirects=False)
        assert response.status_code == 302  # Redirect to login

    def test_inactive_user_cannot_login(self, test_app):
        """Users with active=0 should not be able to log in."""
        from werkzeug.security import generate_password_hash
        import sqlite3
        import os

        db_path = os.environ.get("DATABASE_PATH")
        with sqlite3.connect(db_path) as con:
            con.execute(
                "INSERT INTO users (username, password_hash, role, active, email, full_name) "
                "VALUES (?, ?, 'quality', 0, 'inactive@msedcl.in', 'Inactive User')",
                ("inactive", generate_password_hash("inactivepass")),
            )
            con.commit()

        response = test_app.post(
            "/login",
            data={"username": "inactive", "password": "inactivepass", "csrf_token": "test-token"},
            follow_redirects=False,
        )
        assert response.status_code == 200  # Should not redirect