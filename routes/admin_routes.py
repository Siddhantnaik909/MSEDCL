"""Administrator user-management endpoints."""

from flask import flash, redirect, render_template, request, url_for

from services.user_management_service import (
    create_managed_user,
    delete_managed_user,
    get_users,
    reset_managed_user_password,
    toggle_managed_user_status,
)
from services.frontend_service import react_frontend_enabled, serve_react_frontend


def register_admin_routes(app, *, roles, csrf_protect, db_factory, log_audit):
    @app.route("/admin/users")
    @roles("admin", "manager")
    def user_management():
        if react_frontend_enabled():
            return serve_react_frontend()
        users = get_users(db_factory)
        return render_template("user_management.html", page="users", users=users)

    @app.route("/admin/users/create", methods=["POST"])
    @roles("admin", "manager")
    @csrf_protect
    def user_create():
        category, message = create_managed_user(
            db_factory,
            username=request.form.get("username", "").strip(),
            full_name=request.form.get("full_name", "").strip(),
            email=request.form.get("email", "").strip(),
            role=request.form.get("role", "quality"),
            advisor_id=request.form.get("advisor_id", "").strip() or None,
            password=request.form.get("password", ""),
            actor_role=request.current_user["role"],
            log_audit=log_audit,
        )
        flash(message, category)
        return redirect(url_for("user_management"))

    @app.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
    @roles("admin", "manager")
    @csrf_protect
    def user_toggle_status(user_id):
        result = toggle_managed_user_status(
            db_factory,
            user_id=user_id,
            actor_id=request.current_user["id"],
            actor_role=request.current_user["role"],
            log_audit=log_audit,
        )
        if result:
            category, message = result
            flash(message, category)
        return redirect(url_for("user_management"))

    @app.route("/admin/users/reset-password", methods=["POST"])
    @roles("admin")
    @csrf_protect
    def user_reset_password():
        user_id = request.form.get("user_id")
        new_password = request.form.get("new_password")
        if not user_id or not new_password:
            flash("Missing user ID or password.", "error")
            return redirect(url_for("user_management"))

        category, message = reset_managed_user_password(
            db_factory,
            user_id=user_id,
            new_password=new_password,
            log_audit=log_audit,
        )
        flash(message, category)
        return redirect(url_for("user_management"))

    @app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
    @roles("admin")
    @csrf_protect
    def user_delete(user_id):
        result = delete_managed_user(
            db_factory,
            user_id=user_id,
            actor_id=request.current_user["id"],
            log_audit=log_audit,
        )
        if result:
            category, message = result
            flash(message, category)
        return redirect(url_for("user_management"))
