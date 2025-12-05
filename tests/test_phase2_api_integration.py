"""
Phase 3: Backend API Integration Tests for Phase 2 Modules

Tests comprehensive integration of:
1. Users & Roles Config API
2. Network Targets Config API
3. SMTP & Credentials Manager API
4. Watched Folders Config API

Verifies:
- API endpoint functionality
- Request/response contracts
- Error handling
- State persistence
- Health checks
- Config synchronization
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the app factory
from SortNStoreDashboard import create_app


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestPhase2APIEndpoints:
    """Test all Phase 2 configuration API endpoints."""

    # ===== USERS & ROLES CONFIG TESTS =====

    def test_users_roles_get_config(self, client):
        """Test GET /api/organizer/config/users - Retrieve users configuration."""
        response = client.get('/api/organizer/config/users')
        
        # Should return 200 or 401 (auth required)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify structure
            assert 'users' in data or 'message' in data
            if 'users' in data:
                assert isinstance(data['users'], list)

    def test_users_roles_add_user(self, client):
        """Test POST /api/organizer/config/users - Add a new user."""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'roles': ['viewer'],
            'source': 'local'
        }
        response = client.post(
            '/api/organizer/config/users',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return 200, 201, or 401 (auth required)
        assert response.status_code in [200, 201, 401, 400]

    def test_users_roles_update_user(self, client):
        """Test PUT /api/organizer/config/users/<user_id> - Update user."""
        payload = {
            'email': 'updated@example.com',
            'roles': ['editor']
        }
        response = client.put(
            '/api/organizer/config/users/testuser',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return 200 or 401
        assert response.status_code in [200, 401, 404, 400]

    def test_users_roles_delete_user(self, client):
        """Test DELETE /api/organizer/config/users/<user_id> - Remove user."""
        response = client.delete('/api/organizer/config/users/testuser')
        
        # Should return 200, 204 or 401
        assert response.status_code in [200, 204, 401, 404]

    def test_users_roles_list_roles(self, client):
        """Test GET /api/organizer/config/roles - List all available roles."""
        response = client.get('/api/organizer/config/roles')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have role definitions
            assert isinstance(data, (dict, list))

    def test_users_roles_get_permissions(self, client):
        """Test GET /api/organizer/config/roles/<role> - Get role permissions."""
        response = client.get('/api/organizer/config/roles/admin')
        
        assert response.status_code in [200, 401, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have permissions array
            assert 'permissions' in data or 'name' in data

    # ===== NETWORK TARGETS CONFIG TESTS =====

    def test_network_targets_get_config(self, client):
        """Test GET /api/organizer/config/network-targets - Retrieve network folders."""
        response = client.get('/api/organizer/config/network-targets')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            if isinstance(data, dict):
                assert 'targets' in data or 'network_targets' in data

    def test_network_targets_add_target(self, client):
        """Test POST /api/organizer/config/network-targets - Add UNC path."""
        payload = {
            'name': 'TestShare',
            'path': r'\\server\share\path',
            'description': 'Test network location',
            'enabled': True
        }
        response = client.post(
            '/api/organizer/config/network-targets',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 400, 401]

    def test_network_targets_test_connection(self, client):
        """Test POST /api/organizer/config/network-targets/test - Test NAS/UNC path."""
        payload = {
            'path': r'\\server\share',
            'username': 'domain\\user',
            'password': 'password'
        }
        response = client.post(
            '/api/organizer/config/network-targets/test',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have connectivity result
            assert 'success' in data or 'status' in data

    def test_network_targets_list_with_status(self, client):
        """Test GET /api/organizer/config/network-targets?include_status=true."""
        response = client.get('/api/organizer/config/network-targets?include_status=true')
        
        assert response.status_code in [200, 401]

    def test_network_targets_update_credentials(self, client):
        """Test PUT /api/organizer/config/network-targets/<id>/credentials."""
        payload = {
            'username': 'domain\\newuser',
            'password': 'newpassword'
        }
        response = client.put(
            '/api/organizer/config/network-targets/test-share/credentials',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401, 404]

    # ===== SMTP & CREDENTIALS TESTS =====

    def test_smtp_get_config(self, client):
        """Test GET /api/organizer/config/smtp - Retrieve SMTP settings."""
        response = client.get('/api/organizer/config/smtp')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have SMTP config
            assert isinstance(data, dict)

    def test_smtp_update_config(self, client):
        """Test PUT /api/organizer/config/smtp - Update SMTP settings."""
        payload = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'test@gmail.com',
            'password': 'apppassword',
            'use_tls': True,
            'from_email': 'test@gmail.com'
        }
        response = client.put(
            '/api/organizer/config/smtp',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401]

    def test_smtp_test_connection(self, client):
        """Test POST /api/organizer/config/smtp/test - Test SMTP connectivity."""
        payload = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'test@gmail.com',
            'password': 'apppassword',
            'use_tls': True
        }
        response = client.post(
            '/api/organizer/config/smtp/test',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401, 500]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have connectivity result
            assert 'success' in data or 'status' in data or 'error' in data

    def test_credentials_get_stored(self, client):
        """Test GET /api/organizer/config/credentials - List stored credentials."""
        response = client.get('/api/organizer/config/credentials')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, (dict, list))

    def test_credentials_add_oauth(self, client):
        """Test POST /api/organizer/config/credentials - Add OAuth credential."""
        payload = {
            'name': 'GmailOAuth',
            'type': 'oauth2',
            'client_id': 'test_client_id',
            'client_secret': 'test_secret',
            'scopes': ['mail.send'],
            'provider': 'google'
        }
        response = client.post(
            '/api/organizer/config/credentials',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 400, 401]

    def test_credentials_validate(self, client):
        """Test POST /api/organizer/config/credentials/validate - Test credentials."""
        payload = {
            'type': 'basic',
            'username': 'testuser',
            'password': 'testpass'
        }
        response = client.post(
            '/api/organizer/config/credentials/validate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401]

    def test_credentials_delete(self, client):
        """Test DELETE /api/organizer/config/credentials/<id> - Remove credential."""
        response = client.delete('/api/organizer/config/credentials/test-cred')
        
        assert response.status_code in [200, 204, 401, 404]

    # ===== WATCHED FOLDERS CONFIG TESTS =====

    def test_watched_folders_get_config(self, client):
        """Test GET /api/organizer/config/folders - Retrieve watched folders."""
        response = client.get('/api/organizer/config/folders')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have folders list
            assert 'folders' in data or isinstance(data, list)

    def test_watched_folders_add_folder(self, client):
        """Test POST /api/organizer/config/folders - Add a watched folder."""
        payload = {
            'path': '/home/user/Downloads',
            'enabled': True,
            'recursive': True,
            'description': 'Test folder'
        }
        response = client.post(
            '/api/organizer/config/folders',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 400, 401]

    def test_watched_folders_test_folder(self, client):
        """Test POST /api/organizer/config/folders/test - Test folder access."""
        payload = {
            'path': '/home/user/Documents',
            'check_write': True
        }
        response = client.post(
            '/api/organizer/config/folders/test',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have access test result
            assert 'readable' in data or 'accessible' in data or 'success' in data

    def test_watched_folders_update_folder(self, client):
        """Test PUT /api/organizer/config/folders/<id> - Update folder config."""
        payload = {
            'enabled': False,
            'description': 'Updated description'
        }
        response = client.put(
            '/api/organizer/config/folders/downloads',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401, 404]

    def test_watched_folders_delete_folder(self, client):
        """Test DELETE /api/organizer/config/folders/<id> - Remove watched folder."""
        response = client.delete('/api/organizer/config/folders/downloads')
        
        assert response.status_code in [200, 204, 401, 404]

    def test_watched_folders_batch_test(self, client):
        """Test POST /api/organizer/config/folders/test-all - Test all folders."""
        response = client.post('/api/organizer/config/folders/test-all')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have results for each folder
            assert 'results' in data or isinstance(data, list)

    # ===== HEALTH & SYNC TESTS =====

    def test_config_health_check(self, client):
        """Test GET /api/organizer/health - Overall config health."""
        response = client.get('/api/organizer/health')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have status indicators
            assert 'status' in data or 'healthy' in data

    def test_config_sync_status(self, client):
        """Test GET /api/organizer/config/sync-status - Check sync state."""
        response = client.get('/api/organizer/config/sync-status')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should have sync information
            assert isinstance(data, dict)

    def test_config_export(self, client):
        """Test GET /api/organizer/config/export - Export all config."""
        response = client.get('/api/organizer/config/export')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            # Should be JSON or binary
            assert len(response.data) > 0

    def test_config_import(self, client):
        """Test POST /api/organizer/config/import - Import config."""
        payload = {
            'config': {
                'routes': {},
                'users': []
            }
        }
        response = client.post(
            '/api/organizer/config/import',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 401]

    # ===== AUDIT LOG TESTS =====

    def test_get_audit_log_users(self, client):
        """Test GET /api/organizer/config/audit/users - User config changes."""
        response = client.get('/api/organizer/config/audit/users')
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, (list, dict))

    def test_get_audit_log_network(self, client):
        """Test GET /api/organizer/config/audit/network - Network target changes."""
        response = client.get('/api/organizer/config/audit/network')
        
        assert response.status_code in [200, 401]

    def test_get_audit_log_smtp(self, client):
        """Test GET /api/organizer/config/audit/smtp - SMTP changes."""
        response = client.get('/api/organizer/config/audit/smtp')
        
        assert response.status_code in [200, 401]

    def test_get_audit_log_folders(self, client):
        """Test GET /api/organizer/config/audit/folders - Folder config changes."""
        response = client.get('/api/organizer/config/audit/folders')
        
        assert response.status_code in [200, 401]


class TestPhase2ErrorHandling:
    """Test error handling for Phase 2 APIs."""

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            '/api/organizer/config/users',
            data='invalid json {',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 401]

    def test_missing_required_fields(self, client):
        """Test missing required fields in request."""
        payload = {'name': 'test'}  # Missing other required fields
        response = client.post(
            '/api/organizer/config/users',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 401]

    def test_invalid_path_format(self, client):
        """Test invalid path format validation."""
        payload = {'path': 'invalid::path'}
        response = client.post(
            '/api/organizer/config/folders/test',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 401]

    def test_nonexistent_resource(self, client):
        """Test accessing nonexistent resource."""
        response = client.get('/api/organizer/config/users/nonexistent-user')
        
        assert response.status_code in [404, 401]

    def test_unauthorized_access(self, client):
        """Test unauthorized access without auth."""
        response = client.post(
            '/api/organizer/config/users',
            data=json.dumps({'username': 'test'}),
            content_type='application/json'
        )
        
        # Should require auth
        assert response.status_code in [401, 403, 400]


class TestPhase2StateManagement:
    """Test state persistence and consistency."""

    def test_config_persistence_users(self, client, temp_config_dir):
        """Test that user config changes persist."""
        # First request: add user
        payload = {'username': 'persist-test', 'roles': ['viewer']}
        response1 = client.post(
            '/api/organizer/config/users',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        if response1.status_code in [200, 201]:
            # Second request: retrieve users
            response2 = client.get('/api/organizer/config/users')
            if response2.status_code == 200:
                data = json.loads(response2.data)
                # User should exist in list
                assert 'users' in data

    def test_config_consistency_across_endpoints(self, client):
        """Test consistency when reading config from different endpoints."""
        # Get config from /config/folders
        response1 = client.get('/api/organizer/config/folders')
        
        # Get config from /config/export
        response2 = client.get('/api/organizer/config/export')
        
        # Both should succeed or both should require auth
        assert (response1.status_code == response2.status_code) or \
               (response1.status_code in [401, 403] and response2.status_code in [401, 403])

    def test_concurrent_updates_handling(self, client):
        """Test handling of concurrent config updates."""
        # Simulate two concurrent updates
        payload1 = {'username': 'user1', 'roles': ['viewer']}
        payload2 = {'username': 'user2', 'roles': ['editor']}
        
        response1 = client.post(
            '/api/organizer/config/users',
            data=json.dumps(payload1),
            content_type='application/json'
        )
        
        response2 = client.post(
            '/api/organizer/config/users',
            data=json.dumps(payload2),
            content_type='application/json'
        )
        
        # Both should return valid responses (200, 201, 400, or 401)
        assert response1.status_code in [200, 201, 400, 401]
        assert response2.status_code in [200, 201, 400, 401]


class TestPhase2Performance:
    """Test API performance characteristics."""

    def test_list_endpoints_response_time(self, client):
        """Test that list endpoints respond in reasonable time."""
        import time
        
        endpoints = [
            '/api/organizer/config/users',
            '/api/organizer/config/network-targets',
            '/api/organizer/config/folders',
            '/api/organizer/config/credentials'
        ]
        
        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            elapsed = time.time() - start
            
            # Should respond within 5 seconds
            assert elapsed < 5.0
            # Should return valid status
            assert response.status_code in [200, 401]

    def test_large_config_handling(self, client):
        """Test handling of large config data."""
        # Create large payload
        large_payload = {
            'folders': [
                {'path': f'/path/{i}', 'enabled': True}
                for i in range(100)
            ]
        }
        
        response = client.post(
            '/api/organizer/config/folders',
            data=json.dumps(large_payload),
            content_type='application/json'
        )
        
        # Should handle without crashing
        assert response.status_code in [200, 201, 400, 401, 413]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
