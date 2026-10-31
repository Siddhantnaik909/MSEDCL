"""Login and logout endpoints."""

import secrets

from flask import flash, redirect, render_template, request, session, url_for

from services.auth_service import authenticate_user, record_login
from services.frontend_service import react_frontend_enabled, serve_react_frontend


def register_auth_routes(app, *, csrf_protect, db_factory, log_audit):
    @app.route("/login", methods=["GET", "POST"])
    @csrf_protect
    def login():
        if request.method == "GET" and react_frontend_enabled():
            return serve_react_frontend()

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = authenticate_user(username, password, db_factory)
            if user:
                session.clear()
                session["_csrf_token"] = secrets.token_hex(24)
                session["user_id"] = user.id
                record_login(db_factory, user.id)
                log_audit("LOGIN_SUCCESS", username, "User logged in")

                if user.role in ("admin", "quality", "manager"):
                    return redirect(url_for("dashboard"))
                return redirect(url_for("my_profile"))

            log_audit("LOGIN_FAILED", username, "Invalid login credentials")
            flash("Invalid username or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        log_audit("LOGOUT", session.get("user_id", ""), "User signed out")
        session.clear()
        return redirect(url_for("login"))
