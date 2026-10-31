"""JSON API endpoints for the React client."""

import secrets
import os
import smtplib
import ssl
from functools import wraps
from email.message import EmailMessage

from flask import jsonify, request, send_file, session

from services.auth_service import authenticate_user, record_login
from services.dashboard_service import get_dashboard_data
from services.user_management_service import (
    create_managed_user,
    delete_managed_user,
    get_users,
    reset_managed_user_password,
    toggle_managed_user_status,
)


def register_api_routes(app, *, db_factory, csrf_token, log_audit):
    def api_error(message, status):
        return jsonify({"error": {"message": message}}), status

    def authenticated(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                return api_error("Sign in to continue.", 401)

            with db_factory() as connection:
                user = connection.execute(
                    "SELECT * FROM users WHERE id=? AND active=1",
                    (user_id,),
                ).fetchone()
            if not user:
                session.clear()
                return api_error("Your session has expired. Sign in again.", 401)

            request.current_user = dict(user)
            return fn(*args, **kwargs)

        return wrapped

    def require_roles(*allowed):
        def decorator(fn):
            @wraps(fn)
            @authenticated
            def wrapped(*args, **kwargs):
                if request.current_user["role"] not in allowed:
                    return api_error("You do not have permission to access this resource.", 403)
                return fn(*args, **kwargs)

            return wrapped

        return decorator

    def require_csrf():
        expected = session.get("_csrf_token")
        provided = request.headers.get("X-CSRF-Token") or request.headers.get(
            "X-XSRF-TOKEN"
        )
        if not expected or not provided or not secrets.compare_digest(
            expected, str(provided)
        ):
            log_audit(
                "CSRF_VALIDATION_FAILED",
                request.endpoint or "unknown",
                f"Method: {request.method}, Path: {request.path}",
            )
            return api_error("CSRF token validation failed. Refresh and try again.", 403)
        return None

    @app.get("/api/v1/auth/csrf")
    def api_csrf_token():
        return jsonify({"csrf_token": csrf_token()})

    @app.get("/api/v1/auth/me")
    @authenticated
    def api_current_user():
        user = request.current_user
        return jsonify(
            {
                "id": user["id"],
                "username": user["username"],
                "full_name": user.get("full_name") or user["username"],
                "role": user["role"],
                "advisor_id": user.get("advisor_id"),
            }
        )

    @app.post("/api/v1/auth/login")
    def api_login():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error

        payload = request.get_json(silent=False)
        if not isinstance(payload, dict):
            return api_error("A JSON request body is required.", 400)
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "")
        user = authenticate_user(username, password, db_factory)
        if not user:
            log_audit("LOGIN_FAILED", username, "Invalid login credentials")
            return api_error("Invalid username or password.", 401)

        session.clear()
        session["_csrf_token"] = secrets.token_hex(24)
        session["user_id"] = user.id
        record_login(db_factory, user.id)
        log_audit("LOGIN_SUCCESS", username, "User logged in")

        with db_factory() as connection:
            profile = connection.execute(
                "SELECT full_name, advisor_id FROM users WHERE id=?",
                (user.id,),
            ).fetchone()
        return jsonify(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": profile["full_name"] or user.username,
                    "role": user.role,
                    "advisor_id": profile["advisor_id"],
                },
                "next": "/my-profile" if user.role in ("viewer", "advisor") else "/",
            }
        )

    @app.post("/api/v1/auth/logout")
    @authenticated
    def api_logout():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        log_audit(
            "LOGOUT",
            request.current_user["username"],
            "User signed out",
        )
        session.clear()
        return jsonify({"ok": True})

    @app.get("/api/v1/dashboard")
    @authenticated
    def api_dashboard():
        if request.current_user["role"] in ("viewer", "advisor"):
            return api_error("This dashboard is not available for your role.", 403)
        data = get_dashboard_data(
            db_factory,
            {
                "department": request.args.get("department", "All"),
                "start": request.args.get("start", ""),
                "end": request.args.get("end", ""),
                "auditor": request.args.get("auditor", ""),
                "advisor_q": request.args.get("advisor_q", ""),
                "score_bracket": request.args.get("score_bracket", "All"),
                "fatal_status": request.args.get("fatal_status", "All"),
            },
        )
        return jsonify(data)

    @app.get("/api/v1/admin/users")
    @require_roles("admin", "manager")
    def api_admin_users():
        users = get_users(db_factory)
        return jsonify(
            {
                "users": [
                    {
                        key: user[key]
                        for key in (
                            "id",
                            "username",
                            "full_name",
                            "email",
                            "role",
                            "advisor_id",
                            "active",
                            "created_at",
                            "last_login",
                        )
                    }
                    for user in users
                ]
            }
        )

    @app.post("/api/v1/admin/users")
    @require_roles("admin", "manager")
    def api_admin_user_create():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        payload = request.get_json(silent=False)
        if not isinstance(payload, dict):
            return api_error("A JSON request body is required.", 400)
        if request.current_user["role"] != "admin" and payload.get("role") == "admin":
            return api_error("Only administrators can create administrator accounts.", 403)
        category, message = create_managed_user(
            db_factory,
            username=str(payload.get("username") or "").strip(),
            full_name=str(payload.get("full_name") or "").strip(),
            email=str(payload.get("email") or "").strip(),
            role=str(payload.get("role") or "quality"),
            advisor_id=str(payload.get("advisor_id") or "").strip() or None,
            password=str(payload.get("password") or ""),
            actor_role=request.current_user["role"],
            log_audit=log_audit,
        )
        if category != "success":
            return api_error(message, 400)
        return jsonify({"message": message}), 201

    @app.patch("/api/v1/admin/users/<int:user_id>/status")
    @require_roles("admin", "manager")
    def api_admin_user_status(user_id):
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        result = toggle_managed_user_status(
            db_factory,
            user_id=user_id,
            actor_id=request.current_user["id"],
            actor_role=request.current_user["role"],
            log_audit=log_audit,
        )
        if result is None:
            return api_error("User account was not found.", 404)
        category, message = result
        return (
            (jsonify({"message": message}), 200)
            if category == "success"
            else api_error(message, 403)
        )

    @app.post("/api/v1/admin/users/<int:user_id>/password")
    @require_roles("admin")
    def api_admin_user_password(user_id):
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        payload = request.get_json(silent=False)
        password = str(payload.get("password") or "") if isinstance(payload, dict) else ""
        if not password:
            return api_error("A new password is required.", 400)
        if len(password) < 8:
            return api_error("Password must be at least 8 characters long.", 400)
        with db_factory() as connection:
            exists = connection.execute("SELECT id FROM users WHERE id=?", (user_id,)).fetchone()
        if not exists:
            return api_error("User account was not found.", 404)
        _, message = reset_managed_user_password(
            db_factory,
            user_id=user_id,
            new_password=password,
            log_audit=log_audit,
        )
        return jsonify({"message": message})

    @app.delete("/api/v1/admin/users/<int:user_id>")
    @require_roles("admin")
    def api_admin_user_delete(user_id):
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        result = delete_managed_user(
            db_factory,
            user_id=user_id,
            actor_id=request.current_user["id"],
            log_audit=log_audit,
        )
        if result is None:
            return api_error("User account was not found.", 404)
        category, message = result
        return (
            (jsonify({"message": message}), 200)
            if category == "success"
            else api_error(message, 403)
        )

    @app.get("/api/v1/admin/settings")
    @require_roles("admin")
    def api_admin_settings():
        with db_factory() as connection:
            rows = connection.execute(
                "SELECT setting_key, setting_value FROM system_settings"
            ).fetchall()
        values = {row["setting_key"]: row["setting_value"] for row in rows}
        return jsonify(
            {
                "settings": {
                    key: value
                    for key, value in values.items()
                    if key not in ("smtp_password", "ms_client_secret")
                },
                "smtp_password_configured": bool(values.get("smtp_password")),
                "ms_client_secret_configured": bool(values.get("ms_client_secret")),
            }
        )

    @app.put("/api/v1/admin/settings")
    @require_roles("admin")
    def api_admin_settings_update():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        payload = request.get_json(silent=False)
        if not isinstance(payload, dict):
            return api_error("A JSON request body is required.", 400)
        allowed = {
            "company_name",
            "admin_email",
            "default_date_range",
            "enable_excel_import",
            "email_provider",
            "smtp_host",
            "smtp_port",
            "smtp_username",
            "smtp_password",
            "smtp_from",
            "ms_client_id",
            "ms_tenant_id",
            "ms_client_secret",
        }
        updates = {
            key: str(value).strip()
            for key, value in payload.items()
            if key in allowed and value is not None
        }
        if not updates.get("company_name", "configured").strip():
            return api_error("Organization name cannot be empty.", 400)
        if not updates.get("admin_email", "configured").strip():
            return api_error("Administrator email cannot be empty.", 400)
        if updates.get("email_provider", "smtp") not in ("smtp", "ms_graph"):
            return api_error("Select a supported email provider.", 400)
        if updates.get("enable_excel_import", "true") not in ("true", "false"):
            return api_error("Import setting must be enabled or disabled.", 400)
        if "default_date_range" in updates:
            try:
                date_range = int(updates["default_date_range"])
            except ValueError:
                return api_error("Default date range must be a whole number.", 400)
            if not 1 <= date_range <= 3650:
                return api_error("Default date range must be between 1 and 3650 days.", 400)
        if "smtp_port" in updates:
            try:
                smtp_port = int(updates["smtp_port"])
            except ValueError:
                return api_error("SMTP port must be a whole number.", 400)
            if not 1 <= smtp_port <= 65535:
                return api_error("SMTP port must be between 1 and 65535.", 400)
        for secret_key in ("smtp_password", "ms_client_secret"):
            if not updates.get(secret_key):
                updates.pop(secret_key, None)
        with db_factory() as connection:
            for key, value in updates.items():
                connection.execute(
                    """
                    INSERT INTO system_settings (setting_key, setting_value, updated_at, updated_by)
                    VALUES (?, ?, datetime('now'), ?)
                    ON CONFLICT(setting_key) DO UPDATE SET
                    setting_value=excluded.setting_value,
                    updated_at=datetime('now'),
                    updated_by=excluded.updated_by
                    """,
                    (key, value, request.current_user["username"]),
                )
        log_audit("UPDATE_SETTINGS", "System", "Settings updated by administrator")
        return jsonify({"message": "System settings saved."})

    @app.post("/api/v1/admin/settings/test-email")
    @require_roles("admin")
    def api_admin_test_email():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        payload = request.get_json(silent=False)
        recipient = str(payload.get("recipient") or "").strip() if isinstance(payload, dict) else ""
        if not recipient:
            return api_error("Enter a test recipient email.", 400)
        with db_factory() as connection:
            rows = connection.execute(
                "SELECT setting_key, setting_value FROM system_settings"
            ).fetchall()
        configured = {row["setting_key"]: row["setting_value"] for row in rows}
        host = configured.get("smtp_host") or os.environ.get("SMTP_HOST") or ""
        username = configured.get("smtp_username") or os.environ.get("SMTP_USERNAME") or ""
        password = configured.get("smtp_password") or os.environ.get("SMTP_PASSWORD") or ""
        if not all((host, username, password)):
            return api_error("SMTP host, username, or password is missing from settings.", 400)
        try:
            message = EmailMessage()
            message["Subject"] = "MSEDCL Quality Audit System - Diagnostic Test"
            message["From"] = (
                configured.get("smtp_from")
                or os.environ.get("SMTP_FROM")
                or username
            )
            message["To"] = recipient
            message.set_content(
                "This is an automated diagnostic test message confirming SMTP connectivity from the MSEDCL Quality Audit Portal."
            )
            port = int(
                configured.get("smtp_port")
                or os.environ.get("SMTP_PORT", "587")
            )
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(username, password)
                server.send_message(message)
        except (OSError, ValueError, smtplib.SMTPException) as error:
            log_audit("EMAIL_TEST_FAILED", recipient, f"{type(error).__name__}: {error}")
            return api_error("Email connection test failed. Check the SMTP settings and server logs.", 502)
        log_audit("EMAIL_TEST_SUCCESS", recipient, "SMTP diagnostic ping succeeded")
        return jsonify({"message": f"Test email accepted by {host} for {recipient}."})

    @app.get("/api/v1/admin/audit-logs")
    @require_roles("admin")
    def api_admin_audit_logs():
        with db_factory() as connection:
            logs = connection.execute(
                "SELECT * FROM audit_logs ORDER BY id DESC LIMIT 500"
            ).fetchall()
        return jsonify({"logs": [dict(row) for row in logs]})

    @app.post("/api/v1/admin/audits/purge")
    @require_roles("admin")
    def api_admin_purge_audits():
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        payload = request.get_json(silent=False)
        if not isinstance(payload, dict) or payload.get("confirmation") != "PURGE":
            return api_error("Confirm the purge by entering PURGE.", 400)
        with db_factory() as connection:
            deleted_audits = connection.execute("DELETE FROM audits").rowcount
            deleted_batches = connection.execute("DELETE FROM import_batches").rowcount
        log_audit(
            "PURGE_AUDITS",
            "audits",
            f"Purged {deleted_audits} audits and {deleted_batches} batch records. Users preserved.",
        )
        return jsonify(
            {
                "message": f"Removed {deleted_audits} audit records and {deleted_batches} import batches. User accounts and settings were preserved.",
                "deleted_audits": deleted_audits,
                "deleted_batches": deleted_batches,
            }
        )

    @app.get("/api/v1/admin/backup")
    @require_roles("admin")
    def api_admin_backup():
        log_audit("DOWNLOAD_DB_BACKUP", "quality_audit.db", "Database backup downloaded")
        from app import get_db_path

        return send_file(
            get_db_path(),
            as_attachment=True,
            download_name="quality_audit_backup.db",
        )
