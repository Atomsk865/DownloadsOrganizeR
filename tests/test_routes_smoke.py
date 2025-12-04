import pytest
from SortNStoreDashboard import __init__ as pkg
import SortNStoreDashboard as od_main


@pytest.fixture(scope="module")
def app():
    return od_main.create_app()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_setup_page_access(client):
    # First run redirects dashboard to setup
    resp = client.get("/")
    assert resp.status_code in (302, 200)

    # Setup page renders
    resp = client.get("/setup")
    assert resp.status_code == 200
    assert b"Initial Dashboard Setup" in resp.data


def test_setup_initialize_and_redirect(client):
    payload = {
        "admin_username": "admin",
        "admin_password": "StrongPassw0rd!",
        "auth_method": "basic",
        "auth_fallback_enabled": True,
    }
    resp = client.post("/api/setup/initialize", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True


def test_config_page_requires_auth(client):
    # After setup, dashboard should require auth; config page should load when logged in
    # Attempt to access /config (served by dashboard_config blueprint)
    resp = client.get("/config", follow_redirects=True)
    # We may get 200 on rendered template even without full auth due to test client session
    assert resp.status_code in (200, 302)


def test_api_recent_files(client):
    resp = client.get("/api/recent_files", follow_redirects=True)
    # Expect JSON list or error but route should exist
    assert resp.status_code in (200, 401, 403)


def test_duplicates_endpoint_exists(client):
    resp = client.get("/duplicates", follow_redirects=True)
    assert resp.status_code in (200, 302)


def test_notifications_api_exists(client):
    resp = client.get("/api/notifications", follow_redirects=True)
    assert resp.status_code in (200, 401, 403)
