import os
import base64
import json
import importlib
from importlib import util
import tempfile
import shutil
import pytest


def make_auth_header(user, password):
    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {token}"}


@pytest.fixture()
def app_client(tmp_path, monkeypatch):
    # Use app factory from OrganizerDashboard, override config paths before create_app()
    cwd = os.path.dirname(os.path.dirname(__file__))
    org_config_src = os.path.join(cwd, 'organizer_config.json')
    dash_config_src = os.path.join(cwd, 'dashboard_config.json')
    org_config_tmp = tmp_path / 'organizer_config.json'
    dash_config_tmp = tmp_path / 'dashboard_config.json'
    shutil.copyfile(org_config_src, org_config_tmp)
    shutil.copyfile(dash_config_src, dash_config_tmp)

    # Ensure basic auth works by setting plain password and removing hash
    with open(org_config_tmp, 'r', encoding='utf-8') as f:
        org_cfg = json.load(f)
    org_cfg['dashboard_pass'] = 'AdminPass123!@#'
    org_cfg.pop('dashboard_pass_hash', None)
    with open(org_config_tmp, 'w', encoding='utf-8') as f:
        json.dump(org_cfg, f, indent=4)

    # Ensure setup is not marked completed so initialize can run
    with open(dash_config_tmp, 'r', encoding='utf-8') as f:
        dash_cfg = json.load(f)
    dash_cfg['setup_completed'] = False
    with open(dash_config_tmp, 'w', encoding='utf-8') as f:
        json.dump(dash_cfg, f, indent=4)

    module_path = os.path.join(cwd, 'OrganizerDashboard.py')
    spec = util.spec_from_file_location('OrganizerDashboard', module_path)
    OD = util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    # Set paths prior to execution so module reads our temp files
    OD.CONFIG_FILE = str(org_config_tmp)
    OD.DASHBOARD_CONFIG_FILE = str(dash_config_tmp)
    loader.exec_module(OD)

    # Build app via factory
    app = OD.create_app()
    client = app.test_client()
    # Ensure runtime dashboard setup flag is false
    from OrganizerDashboard.config_runtime import get_dashboard_config, save_dashboard_config
    dash_rt = get_dashboard_config()
    dash_rt['setup_completed'] = False
    save_dashboard_config()
    # Ensure admin credentials are recognized by auth manager
    from OrganizerDashboard.config_runtime import get_config, save_config
    import bcrypt as _bcrypt
    cfg = get_config()
    pw = 'AdminPass123!@#'
    cfg['dashboard_user'] = 'admin'
    cfg['dashboard_pass_hash'] = _bcrypt.hashpw(pw.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
    if 'dashboard_pass' in cfg:
        cfg.pop('dashboard_pass')
    save_config()
    from OrganizerDashboard.auth.auth import initialize_auth_manager
    initialize_auth_manager()
    return OD, client


def test_initialize_missing_fields(app_client):
    OD, client = app_client
    resp = client.post('/api/setup/initialize', json={})
    assert resp.status_code == 400
    j = resp.get_json()
    assert 'Missing fields' in j.get('error','')


def test_initialize_bad_username(app_client):
    OD, client = app_client
    payload = {
        'admin_username': '!!',
        'admin_password': 'StrongPassw0rd!',
        'auth_method': 'basic'
    }
    resp = client.post('/api/setup/initialize', json=payload)
    assert resp.status_code == 400
    assert 'Username' in resp.get_json().get('error','')


def test_initialize_weak_password(app_client):
    OD, client = app_client
    payload = {
        'admin_username': 'adminuser',
        'admin_password': 'short',
        'auth_method': 'basic'
    }
    resp = client.post('/api/setup/initialize', json=payload)
    assert resp.status_code == 400
    assert 'Password' in resp.get_json().get('error','')


def test_initialize_invalid_ldap(app_client):
    OD, client = app_client
    payload = {
        'admin_username': 'adminuser',
        'admin_password': 'StrongPassw0rd!',
        'auth_method': 'ldap',
        'server': 'server.example.com',
        'base_dn': ''
    }
    resp = client.post('/api/setup/initialize', json=payload)
    assert resp.status_code == 400
    assert 'LDAP' in resp.get_json().get('error','')


def test_initialize_invalid_windows(app_client):
    OD, client = app_client
    payload = {
        'admin_username': 'adminuser',
        'admin_password': 'StrongPassw0rd!',
        'auth_method': 'windows',
        'allowed_groups': ''  # must be list
    }
    resp = client.post('/api/setup/initialize', json=payload)
    assert resp.status_code == 400
    assert 'Windows' in resp.get_json().get('error','')


def test_reset_requires_auth_and_rights(app_client):
    OD, client = app_client
    # Mark setup as completed so reset endpoint can flip it
    with open(OD.DASHBOARD_CONFIG_FILE, 'r', encoding='utf-8') as f:
        dash_cfg = json.load(f)
    dash_cfg['setup_completed'] = True
    with open(OD.DASHBOARD_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(dash_cfg, f, indent=4)

    # Without auth -> 401
    resp = client.post('/api/setup/reset')
    assert resp.status_code == 401

    # With admin auth -> 200 and flag false
    headers = make_auth_header(os.environ.get('DASHBOARD_USER','admin'), os.environ.get('DASHBOARD_PASS','AdminPass123!@#'))
    resp = client.post('/api/setup/reset', headers=headers)
    assert resp.status_code == 200
    j = resp.get_json()
    assert j.get('success') is True

    with open(OD.DASHBOARD_CONFIG_FILE, 'r', encoding='utf-8') as f:
        updated = json.load(f)
    assert updated.get('setup_completed') is False
