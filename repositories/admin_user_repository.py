"""Persistence queries for administrator-managed user accounts."""


def list_users(db_factory):
    with db_factory() as connection:
        return connection.execute("SELECT * FROM users ORDER BY id ASC").fetchall()


def create_user(db_factory, *, username, password_hash, role, advisor_id, full_name, email):
    with db_factory() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE username=?",
            (username,),
        ).fetchone()
        if existing:
            return False

        connection.execute(
            """
            INSERT INTO users (username, password_hash, role, advisor_id, active, full_name, email, created_at)
            VALUES (?, ?, ?, ?, 1, ?, ?, datetime('now'))
            """,
            (username, password_hash, role, advisor_id, full_name, email),
        )
    return True


def find_user(db_factory, user_id):
    with db_factory() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
    return dict(user) if user else None


def set_user_active(db_factory, user_id, active):
    with db_factory() as connection:
        connection.execute(
            "UPDATE users SET active=? WHERE id=?",
            (active, user_id),
        )


def update_user_password(db_factory, user_id, password_hash):
    with db_factory() as connection:
        connection.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (password_hash, user_id),
        )
        user = connection.execute(
            "SELECT username FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
    return user["username"] if user else None


def delete_user(db_factory, user_id):
    with db_factory() as connection:
        user = connection.execute(
            "SELECT username FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
        if user:
            connection.execute("DELETE FROM users WHERE id=?", (user_id,))
    return user["username"] if user else None
