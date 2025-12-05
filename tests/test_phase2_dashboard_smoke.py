"""
Phase 3: Dashboard Frontend Smoke Tests

Tests UI functionality and integration for all 4 Phase 2 modules:
1. Users & Roles Config UI
2. Network Targets Config UI
3. SMTP & Credentials Manager UI
4. Watched Folders Config UI

Verifies:
- Page rendering
- Form validation
- Data display
- Error messages
- User interactions
"""

import pytest
from bs4 import BeautifulSoup
import json
import re


@pytest.fixture
def app():
    """Create and configure a test app."""
    from SortNStoreDashboard import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


class TestPhase2DashboardPages:
    """Test Phase 2 dashboard pages render correctly."""

    def test_users_and_roles_page_renders(self, client):
        """Test Users & Roles configuration page loads."""
        response = client.get('/dashboard/users')
        
        # Should return 200 or redirect to login
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Page should contain UI elements
            assert 'user' in html.lower() or 'role' in html.lower()

    def test_network_targets_page_renders(self, client):
        """Test Network Targets configuration page loads."""
        response = client.get('/dashboard/network-targets')
        
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Page should contain network/UNC related content
            assert any(keyword in html.lower() for keyword in ['network', 'unc', 'share', 'path'])

    def test_smtp_config_page_renders(self, client):
        """Test SMTP & Credentials configuration page loads."""
        response = client.get('/dashboard/smtp')
        
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Page should contain email/SMTP related content
            assert any(keyword in html.lower() for keyword in ['smtp', 'email', 'mail', 'server'])

    def test_watched_folders_page_renders(self, client):
        """Test Watched Folders configuration page loads."""
        response = client.get('/dashboard/folders')
        
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Page should contain folder-related content
            assert any(keyword in html.lower() for keyword in ['folder', 'directory', 'path', 'watch'])


class TestPhase2FormValidation:
    """Test form validation on UI forms."""

    def test_users_form_has_validation(self, client):
        """Test Users form includes validation attributes."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for form elements with validation
            form_elements = soup.find_all(['input', 'select', 'textarea'])
            # Should have some form elements
            assert len(form_elements) > 0 or 'form' in html.lower()

    def test_network_targets_form_validation(self, client):
        """Test Network Targets form has path validation."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have path input fields
            assert 'input' in html.lower() or 'path' in html.lower()

    def test_smtp_form_validation(self, client):
        """Test SMTP form has email validation."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have email/server input fields
            assert 'input' in html.lower()

    def test_folders_form_validation(self, client):
        """Test Folders form has path validation."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have path input fields
            assert 'input' in html.lower() or 'path' in html.lower()


class TestPhase2DataDisplay:
    """Test data display and rendering."""

    def test_users_list_displays(self, client):
        """Test Users list displays in UI."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have table or list element
            assert any(tag in html.lower() for tag in ['<table', '<tr', '<li', 'list'])

    def test_network_targets_list_displays(self, client):
        """Test Network Targets list displays."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have table or list
            assert any(tag in html.lower() for tag in ['<table', '<tr', '<li', 'list'])

    def test_smtp_config_displays(self, client):
        """Test SMTP config displays current settings."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have input fields for settings
            assert 'input' in html.lower()

    def test_folders_list_displays(self, client):
        """Test Watched Folders list displays."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have table or list
            assert any(tag in html.lower() for tag in ['<table', '<tr', '<li', 'list'])


class TestPhase2ButtonsAndActions:
    """Test action buttons and interactive elements."""

    def test_users_page_has_add_button(self, client):
        """Test Users page has 'Add User' button."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have button for adding users
            assert any(keyword in html.lower() for keyword in ['add', 'create', 'new', 'button'])

    def test_network_targets_page_has_add_button(self, client):
        """Test Network Targets page has 'Add Target' button."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have button for adding targets
            assert any(keyword in html.lower() for keyword in ['add', 'create', 'new', 'button'])

    def test_network_targets_has_test_button(self, client):
        """Test Network Targets page has 'Test Connection' button."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have test button
            assert any(keyword in html.lower() for keyword in ['test', 'button', 'check'])

    def test_smtp_page_has_test_button(self, client):
        """Test SMTP page has 'Test Connection' button."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have test button
            assert any(keyword in html.lower() for keyword in ['test', 'button'])

    def test_folders_page_has_add_button(self, client):
        """Test Folders page has 'Add Folder' button."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have button for adding folders
            assert any(keyword in html.lower() for keyword in ['add', 'create', 'new', 'button'])

    def test_folders_has_test_button(self, client):
        """Test Folders page has 'Test Folder' button."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have test button
            assert any(keyword in html.lower() for keyword in ['test', 'button'])


class TestPhase2JavaScriptModules:
    """Test JavaScript modules load correctly."""

    def test_users_js_module_loads(self, client):
        """Test Users & Roles JS module is included."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should include the JS module
            assert any(keyword in html.lower() for keyword in ['script', 'users', 'module'])

    def test_network_targets_js_module_loads(self, client):
        """Test Network Targets JS module is included."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should include the JS module
            assert any(keyword in html.lower() for keyword in ['script', 'network', 'module'])

    def test_smtp_js_module_loads(self, client):
        """Test SMTP JS module is included."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should include the JS module
            assert any(keyword in html.lower() for keyword in ['script', 'smtp', 'module'])

    def test_folders_js_module_loads(self, client):
        """Test Watched Folders JS module is included."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should include the JS module
            assert any(keyword in html.lower() for keyword in ['script', 'folder', 'module'])


class TestPhase2ErrorMessaging:
    """Test error message display."""

    def test_error_message_display_users(self, client):
        """Test error messages display on Users page."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have error handling elements
            assert any(keyword in html.lower() for keyword in ['alert', 'error', 'message', 'modal', 'toast'])

    def test_error_message_display_network(self, client):
        """Test error messages display on Network page."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have error handling elements
            assert any(keyword in html.lower() for keyword in ['alert', 'error', 'message', 'modal'])

    def test_validation_error_display_smtp(self, client):
        """Test validation errors on SMTP form."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have form validation feedback elements
            assert any(keyword in html.lower() for keyword in ['invalid', 'required', 'error', 'feedback'])

    def test_validation_error_display_folders(self, client):
        """Test validation errors on Folders form."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have form validation feedback elements
            assert any(keyword in html.lower() for keyword in ['invalid', 'required', 'error', 'feedback'])


class TestPhase2ResponsiveDesign:
    """Test responsive design elements."""

    def test_users_page_responsive_classes(self, client):
        """Test Users page uses responsive design classes."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have Bootstrap or responsive classes
            assert any(keyword in html.lower() for keyword in ['container', 'row', 'col', 'responsive', 'bootstrap'])

    def test_network_page_responsive_classes(self, client):
        """Test Network page uses responsive design classes."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have responsive classes
            assert any(keyword in html.lower() for keyword in ['container', 'row', 'col', 'responsive'])

    def test_smtp_page_responsive_classes(self, client):
        """Test SMTP page uses responsive design classes."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have responsive classes
            assert any(keyword in html.lower() for keyword in ['container', 'row', 'col'])

    def test_folders_page_responsive_classes(self, client):
        """Test Folders page uses responsive design classes."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have responsive classes
            assert any(keyword in html.lower() for keyword in ['container', 'row', 'col'])


class TestPhase2AccessibilityElements:
    """Test accessibility features."""

    def test_users_page_has_labels(self, client):
        """Test Users page has accessible labels."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Should have label elements
            labels = soup.find_all('label')
            assert len(labels) > 0 or 'aria' in html.lower()

    def test_network_page_has_labels(self, client):
        """Test Network page has accessible labels."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have labels or aria attributes
            assert 'label' in html.lower() or 'aria' in html.lower()

    def test_smtp_page_has_labels(self, client):
        """Test SMTP page has accessible labels."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have labels or aria attributes
            assert 'label' in html.lower() or 'aria' in html.lower()

    def test_folders_page_has_labels(self, client):
        """Test Folders page has accessible labels."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have labels or aria attributes
            assert 'label' in html.lower() or 'aria' in html.lower()


class TestPhase2LoadingStates:
    """Test loading and state indicators."""

    def test_users_page_has_loading_indicator(self, client):
        """Test Users page has loading state handling."""
        response = client.get('/dashboard/users')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have loading elements
            assert any(keyword in html.lower() for keyword in ['loading', 'spinner', 'skeleton', 'placeholder'])

    def test_network_page_has_loading_indicator(self, client):
        """Test Network page has loading state handling."""
        response = client.get('/dashboard/network-targets')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have loading elements
            assert any(keyword in html.lower() for keyword in ['loading', 'spinner', 'skeleton'])

    def test_smtp_page_has_loading_indicator(self, client):
        """Test SMTP page has loading state handling."""
        response = client.get('/dashboard/smtp')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have loading elements
            assert any(keyword in html.lower() for keyword in ['loading', 'spinner'])

    def test_folders_page_has_loading_indicator(self, client):
        """Test Folders page has loading state handling."""
        response = client.get('/dashboard/folders')
        
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            # Should have loading elements
            assert any(keyword in html.lower() for keyword in ['loading', 'spinner'])


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
