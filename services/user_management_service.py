"""Business workflows for administrator-managed user accounts."""

import sqlite3

from werkzeug.security import generate_password_hash

from repositories.admin_user_repository import (
    create_user,
    delete_user,
    find_user,
    list_users,
    set_user_active,
    update_user_password,
)

ALLOWED_ROLES = ("admin", "quality", "manager", "viewer", "advisor")


def get_users(db_factory):
    return list_users(db_factory)


def create_managed_user(
    db_factory,
    *,
    username,
    full_name,
    email,
    role,
    advisor_id,
    password,
    actor_role,
    log_audit,
):
    if not username or not password:
        return "error", "Username and password are required."
    if role not in ALLOWED_ROLES:
        return "error", "Invalid role selected."
    if actor_role != "admin" and role == "admin":
        return "error", "Only administrators can create administrator accounts."
    if len(password) < 8:
        return "error", "Password must be at least 8 characters long."

    try:
        created = create_user(
            db_factory,
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            advisor_id=advisor_id,
            full_name=full_name,
            email=email,
        )
    except sqlite3.IntegrityError as error:
        return "error", f"Could not create user: {error}"

    if not created:
        return "error", f"Username '{username}' is already registered."

    log_audit("CREATE_USER", username, f"Role: {role}, AdvisorID: {advisor_id}, Email: {email}")
    return "success", f"User '{username}' created successfully."


def toggle_managed_user_status(db_factory, *, user_id, actor_id, actor_role, log_audit):
    if user_id == actor_id:
        return "error", "You cannot deactivate your own account."

    user = find_user(db_factory, user_id)
    if not user:
        return None

    if actor_role != "admin" and user["role"] == "admin":
        return "error", "Only administrators can deactivate administrator accounts."

    new_status = 0 if user["active"] else 1
    set_user_active(db_factory, user_id, new_status)
    log_audit("TOGGLE_USER_STATUS", user["username"], f"New active status: {new_status}")
    status_text = "Active" if new_status else "Inactive"
    return "success", f"User '{user['username']}' status updated to {status_text}."


def reset_managed_user_password(db_factory, *, user_id, new_password, log_audit):
    username = update_user_password(
        db_factory,
        user_id,
        generate_password_hash(new_password),
    )
    log_audit(
        "RESET_PASSWORD",
        username if username else user_id,
        "Administrator reset password",
    )
    return "success", "Password reset successfully for user."


def delete_managed_user(db_factory, *, user_id, actor_id, log_audit):
    if user_id == actor_id:
        return "error", "You cannot delete your own account."

    username = delete_user(db_factory, user_id)
    if not username:
        return None

    log_audit("DELETE_USER", username, "User account deleted")
    return "success", f"User '{username}' deleted."
