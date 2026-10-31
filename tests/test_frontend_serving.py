import pytest

import init_db
from services import frontend_service


def _create_frontend_build(build_dir):
    assets = build_dir / "assets"
    styles = build_dir / "css"
    assets.mkdir(parents=True)
    styles.mkdir()
    (build_dir / "index.html").write_text(
        "<!doctype html><div id='root'>react-build</div>", encoding="utf-8"
    )
    (assets / "app.js").write_text("window.reactBuild = true", encoding="utf-8")
    (styles / "legacy-theme.css").write_text("body { color: navy; }", encoding="utf-8")
    (build_dir / "favicon.svg").write_text("<svg></svg>", encoding="utf-8")


def test_react_frontend_serves_production_pages_and_assets(
    test_app, tmp_path, monkeypatch
):
    build_dir = tmp_path / "dist"
    _create_frontend_build(build_dir)
    monkeypatch.setattr(frontend_service, "FRONTEND_DIST", build_dir)
    monkeypatch.setenv("SERVE_REACT_FRONTEND", "true")

    with test_app.session_transaction() as session:
        session["user_id"] = 1

    assert b"react-build" in test_app.get("/").data
    assert b"react-build" in test_app.get("/login").data
    assert b"react-build" in test_app.get("/admin/users").data
    assert b"react-build" in test_app.get("/admin/settings").data
    assert b"react-build" in test_app.get("/admin/audit-logs").data
    assert test_app.get("/assets/app.js").data == b"window.reactBuild = true"
    assert b"color: navy" in test_app.get("/css/legacy-theme.css").data
    assert test_app.get("/favicon.svg").status_code == 200
    assert test_app.get("/healthz").json == {"status": "ok"}


def test_react_frontend_is_disabled_by_default(test_app, monkeypatch):
    monkeypatch.delenv("SERVE_REACT_FRONTEND", raising=False)

    response = test_app.get("/login")

    assert response.status_code == 200
    assert b"react-build" not in response.data


def test_healthcheck_fails_when_enabled_frontend_build_is_missing(
    test_app, tmp_path, monkeypatch
):
    monkeypatch.setattr(frontend_service, "FRONTEND_DIST", tmp_path / "missing")
    monkeypatch.setenv("SERVE_REACT_FRONTEND", "true")

    with pytest.raises(RuntimeError, match="frontend/dist/index.html is missing"):
        test_app.get("/healthz")


def test_production_database_requires_configured_account_passwords(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("SERVE_REACT_FRONTEND", "true")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("QUALITY_PASSWORD", raising=False)
    monkeypatch.delenv("MANAGER_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="ADMIN_PASSWORD"):
        init_db.init_db(str(tmp_path / "production.db"))


def test_production_database_rejects_local_demo_passwords(tmp_path, monkeypatch):
    monkeypatch.setenv("SERVE_REACT_FRONTEND", "true")
    monkeypatch.setenv("ADMIN_PASSWORD", "Msedcl@123")
    monkeypatch.setenv("QUALITY_PASSWORD", "Msedcl@1234")
    monkeypatch.setenv("MANAGER_PASSWORD", "Msedcl@1235")

    with pytest.raises(RuntimeError, match="local demo passwords are not allowed"):
        init_db.init_db(str(tmp_path / "production.db"))
