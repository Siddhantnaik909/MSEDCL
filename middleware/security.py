"""Authentication, authorization, CSRF, and response security policies."""

import secrets
from functools import wraps

from flask import abort, request, session


def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def create_security_middleware(db_factory, log_audit):
    def login_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                from flask import redirect, url_for

                return redirect(url_for("login"))
            with db_factory() as connection:
                user = connection.execute(
                    "SELECT * FROM users WHERE id=? AND active=1",
                    (session["user_id"],),
                ).fetchone()
            if not user:
                session.clear()
                from flask import redirect, url_for

                return redirect(url_for("login"))
            request.current_user = dict(user)
            return fn(*args, **kwargs)

        return wrapped

    def roles(*allowed):
        def decorator(fn):
            @wraps(fn)
            @login_required
            def wrapped(*args, **kwargs):
                if request.current_user["role"] not in allowed:
                    abort(403)
                return fn(*args, **kwargs)

            return wrapped

        return decorator

    def csrf_token():
        token = session.get("_csrf_token")
        if not token:
            token = secrets.token_hex(24)
            session["_csrf_token"] = token
        return token

    def csrf_protect(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if request.method in ("GET", "HEAD", "OPTIONS"):
                return fn(*args, **kwargs)
            token = session.get("_csrf_token")
            provided = (
                request.form.get("csrf_token")
                or request.headers.get("X-CSRF-Token")
                or request.headers.get("X-XSRF-TOKEN")
            )
            if not token or not provided or not secrets.compare_digest(
                token, str(provided)
            ):
                log_audit(
                    "CSRF_VALIDATION_FAILED",
                    request.endpoint or "unknown",
                    f"Method: {request.method}, Path: {request.path}",
                )
                abort(
                    403,
                    description=(
                        "CSRF token validation failed. Please refresh the page "
                        "and try again."
                    ),
                )
            return fn(*args, **kwargs)

        return wrapped

    return login_required, roles, csrf_token, csrf_protect
