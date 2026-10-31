"""HTTP route registration."""

from routes.auth_routes import register_auth_routes
from routes.admin_routes import register_admin_routes
from routes.api_routes import register_api_routes


def register_routes(app, *, roles, csrf_protect, db_factory, csrf_token, log_audit):
    register_auth_routes(
        app,
        csrf_protect=csrf_protect,
        db_factory=db_factory,
        log_audit=log_audit,
    )
    register_admin_routes(
        app,
        roles=roles,
        csrf_protect=csrf_protect,
        db_factory=db_factory,
        log_audit=log_audit,
    )
    register_api_routes(
        app,
        db_factory=db_factory,
        csrf_token=csrf_token,
        log_audit=log_audit,
    )
