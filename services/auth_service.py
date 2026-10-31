"""Authentication use cases."""

from werkzeug.security import check_password_hash

from models.user import AuthenticatedUser
from repositories.user_repository import find_active_user


def authenticate_user(username, password, db_factory):
    """Return an active user matching the supplied credentials, or None."""
    user = find_active_user(username, db_factory)

    if user and check_password_hash(user["password_hash"], password):
        return AuthenticatedUser.from_row(user)
    return None


def record_login(db_factory, user_id):
    """Update the last successful login timestamp."""
    with db_factory() as connection:
        connection.execute(
            "UPDATE users SET last_login=datetime('now') WHERE id=?",
            (user_id,),
        )
