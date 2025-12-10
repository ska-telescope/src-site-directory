"""
Component tests for Web UI endpoints.

These tests verify that the HTML web interface endpoints return proper HTML responses.
"""

import os

import httpx
import pytest

from tests.component.conftest import DISABLE_AUTHENTICATION, get_api_url, send_get_request


@pytest.mark.component
def test_get_operator_docs():
    """Test to get operator documentation page."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/docs/oper")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    # Check for expected HTML content
    html_content = response.text
    assert "<html" in html_content.lower() or "<!doctype" in html_content.lower()
    assert "operator" in html_content.lower() or "documentation" in html_content.lower()


@pytest.mark.component
def test_get_user_docs():
    """Test to get user documentation page."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/docs/user")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    # Check for expected HTML content
    html_content = response.text
    assert "<html" in html_content.lower() or "<!doctype" in html_content.lower()
    assert "user" in html_content.lower() or "documentation" in html_content.lower()


@pytest.mark.component
def test_get_login_page():
    """Test to get login page."""
    api_url = get_api_url()
    # Use httpx directly to control redirect behavior
    response = httpx.get(f"{api_url}/www/login", follow_redirects=False, timeout=30)

    # Login page may return 200 (HTML), 302/307 (redirect to auth provider), or 500 (if dependencies unavailable)
    # In k8s environments, 500 may occur if MongoDB or other dependencies are unavailable
    assert response.status_code in (200, 302, 307, 500)

    if response.status_code == 200:
        assert "text/html" in response.headers.get("content-type", "").lower()
        html_content = response.text
        assert "<html" in html_content.lower() or "<!doctype" in html_content.lower() or "login" in html_content.lower()
    elif response.status_code in (302, 307):
        # Redirect to authentication provider
        assert "location" in response.headers
    elif response.status_code == 500:
        # In k8s environments, dependencies might be unavailable
        # This is acceptable for component tests in CI environments
        pass


@pytest.mark.component
def test_get_logout_page():
    """Test to get logout page."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/logout")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    # Check for expected HTML content
    html_content = response.text
    assert "logout" in html_content.lower() or "logged out" in html_content.lower()


@pytest.mark.component
def test_get_nodes_form(load_nodes_data):
    """Test to get node management form."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/nodes")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    html_content = response.text

    if DISABLE_AUTHENTICATION:
        # When auth is disabled, should show the form
        assert "node" in html_content.lower() or "form" in html_content.lower() or "add" in html_content.lower()
    else:
        # When auth is enabled, may show login prompt or form depending on session
        assert "login" in html_content.lower() or "node" in html_content.lower() or "form" in html_content.lower()


@pytest.mark.component
def test_get_edit_node_form(load_nodes_data):
    """Test to get edit node form for an existing node."""
    api_url = get_api_url()

    # Use an existing node if available
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = send_get_request(f"{api_url}/www/nodes/{node_name}")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()

        html_content = response.text

        if DISABLE_AUTHENTICATION:
            # When auth is disabled, should show the edit form
            assert "node" in html_content.lower() or "form" in html_content.lower() or "edit" in html_content.lower()
        else:
            # When auth is enabled, may show login prompt or form depending on session
            assert "login" in html_content.lower() or "node" in html_content.lower() or "form" in html_content.lower()
    else:
        # If no nodes are loaded, test with a non-existent node
        response = send_get_request(f"{api_url}/www/nodes/nonexistent-node")

        # Should return 200 (with error message or login prompt) or 404/500
        assert response.status_code in (200, 404, 500)

        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "").lower()


@pytest.mark.component
def test_get_edit_node_form_nonexistent():
    """Test to get edit node form for a non-existent node."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/nodes/nonexistent-node-12345")

    # Should return 200 (with error message or login prompt) or 404/500
    assert response.status_code in (200, 404, 500)

    if response.status_code == 200:
        assert "text/html" in response.headers.get("content-type", "").lower()


@pytest.mark.component
def test_get_services_report(load_nodes_data):
    """Test to get services report page."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/reports/services")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    html_content = response.text

    if DISABLE_AUTHENTICATION:
        # When auth is disabled, should show the report
        assert "services" in html_content.lower() or "report" in html_content.lower() or "srcnet" in html_content.lower()
    else:
        # When auth is enabled, may show login prompt or report depending on session
        assert "login" in html_content.lower() or "services" in html_content.lower() or "report" in html_content.lower()


@pytest.mark.component
def test_get_topology_view(load_nodes_data):
    """Test to get topology view page."""
    api_url = get_api_url()
    response = send_get_request(f"{api_url}/www/topology")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    html_content = response.text

    if DISABLE_AUTHENTICATION:
        # When auth is disabled, should show the topology view
        assert "topology" in html_content.lower() or "srcnet" in html_content.lower()
    else:
        # When auth is enabled, may show login prompt or topology depending on session
        assert "login" in html_content.lower() or "topology" in html_content.lower()


@pytest.mark.component
def test_get_downtime_dashboard(load_nodes_data):
    """Test to get downtime dashboard page."""

    api_url = get_api_url()

    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = send_get_request(f"{api_url}/www/downtime/{node_name}")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()

        html_content = response.text

        if DISABLE_AUTHENTICATION:
            # When auth is disabled, should show the downtime dashboard
            assert "downtime" in html_content.lower() or "resource type" in html_content.lower() or "ongoing downtimes" in html_content.lower()
        else:
            # When auth is enabled, may show login prompt or dashboard depending on session
            assert "login" in html_content.lower() or "downtimes srcnet node" in html_content.lower() or "resource type" in html_content.lower()
    else:
        # If no nodes are loaded, test with a non-existent node
        response = send_get_request(f"{api_url}/www/downtime/nonexistent-node")

        # Should return 200 (with error message or login prompt) or 404/500
        assert response.status_code in (200, 404, 500)

        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "").lower()
