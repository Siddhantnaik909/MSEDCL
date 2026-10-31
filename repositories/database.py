"""SQLite connection management."""

import os
import sqlite3


def get_db_path(default_path):
    """Resolve the database path at call time so tests can override it."""
    return os.environ.get("DATABASE_PATH", default_path)


def open_database(default_path):
    connection = sqlite3.connect(get_db_path(default_path))
    connection.row_factory = sqlite3.Row
    return connection
