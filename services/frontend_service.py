"""Serve the built React client from the Flask application in production."""

import os
from pathlib import Path

from flask import abort, jsonify, send_from_directory


FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"


def react_frontend_enabled():
    enabled = os.environ.get("SERVE_REACT_FRONTEND", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if enabled and not (FRONTEND_DIST / "index.html").is_file():
        raise RuntimeError(
            "SERVE_REACT_FRONTEND is enabled, but frontend/dist/index.html is missing. "
            "Build the React client before starting Flask."
        )
    return enabled


def serve_react_frontend():
    if not react_frontend_enabled():
        abort(404)
    return send_from_directory(FRONTEND_DIST, "index.html")


def register_frontend_routes(app):
    @app.get("/assets/<path:filename>")
    def react_asset(filename):
        if not react_frontend_enabled():
            abort(404)
        return send_from_directory(FRONTEND_DIST / "assets", filename)

    @app.get("/css/<path:filename>")
    def react_public_css(filename):
        if not react_frontend_enabled():
            abort(404)
        return send_from_directory(FRONTEND_DIST / "css", filename)

    @app.get("/favicon.svg")
    def react_favicon():
        if not react_frontend_enabled():
            abort(404)
        return send_from_directory(FRONTEND_DIST, "favicon.svg")

    @app.get("/healthz")
    def healthcheck():
        react_frontend_enabled()
        return jsonify({"status": "ok"})
