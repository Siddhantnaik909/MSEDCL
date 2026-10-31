"""User persistence queries used by authentication workflows."""


def find_active_user(username, db_factory):
    with db_factory() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE username=? AND active=1",
            (username,),
        ).fetchone()
