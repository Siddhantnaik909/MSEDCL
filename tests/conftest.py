"""Test configuration and fixtures for MSEDCL Quality Audit test suite.

Creates a disposable SQLite test database for each test, ensuring
no production data is touched and no state leaks between tests.
"""

import os
import sys
import tempfile
import sqlite3

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module
import init_db
import migrate_db


def _create_test_db():
    """Create a temporary SQLite database and return its path."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return path


@pytest.fixture
def test_db_path():
    """Fixture providing a path to a fresh test database."""
    path = _create_test_db()
    yield path
    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def test_app(test_db_path):
    """Create a Flask app configured with the test database."""
    os.environ["DATABASE_PATH"] = test_db_path
    os.environ["APP_SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
    os.environ["SESSION_COOKIE_SECURE"] = "false"
    os.environ["PORT"] = "5000"

    # Initialize schema
    init_db.init_db(test_db_path)
    migrate_db.run_migrations(test_db_path)

    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False  # CSRF handled manually in tests

    with app_module.app.test_client() as client:
        with client.session_transaction() as session:
            session["_csrf_token"] = "test-token"
        with app_module.app.app_context():
            yield client

    # Cleanup env
    os.environ.pop("DATABASE_PATH", None)
    os.environ.pop("APP_SECRET_KEY", None)


@pytest.fixture
def csrf_token(test_app):
    """Return the CSRF token currently associated with the test client's session."""
    def get_token():
        with test_app.session_transaction() as session:
            return session["_csrf_token"]

    return get_token