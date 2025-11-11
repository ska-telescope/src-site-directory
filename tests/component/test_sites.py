"""
A module for component tests related to sites.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_sites(load_nodes_data):
    """Test to list all sites"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/sites")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify we have at least one site
        if len(data) > 0:
            assert "name" in data[0]
            assert "id" in data[0]
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_sites_only_names(load_nodes_data):
    """Test to list sites with only_names parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/sites?only_names=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return a list of strings (names)
        if len(data) > 0:
            assert isinstance(data[0], str)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_sites_filter_by_node_names(load_nodes_data):
    """Test to list sites filtered by node names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/sites?node_names={node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_sites_filter_by_multiple_node_names(load_nodes_data):
    """Test to list sites filtered by multiple node names (comma-separated)"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        # Use the same node name twice to test comma-separated format
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/sites?node_names={node_name},{node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_sites_include_inactive(load_nodes_data):
    """Test to list sites with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/sites?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_site_by_id(load_nodes_data):
    """Test to get a site by ID"""
    api_url = get_api_url()
    # First, get the list of sites to find a site ID
    sites_response = send_get_request(f"{api_url}/sites")
    if sites_response.status_code == 200:
        sites_data = sites_response.json()
        if len(sites_data) > 0:
            site_id = sites_data[0]["id"]
            response = httpx.get(f"{api_url}/sites/{site_id}")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["id"] == site_id
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_get_site_not_found():
    """Test to get a non-existent site"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.get(f"{api_url}/sites/{fake_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 404
    else:
        assert response.status_code in (403, 404)


@pytest.mark.component
def test_enable_site(load_nodes_data):
    """Test to enable a site and verify state change"""
    api_url = get_api_url()
    # First, get the list of sites to find a site ID
    sites_response = send_get_request(f"{api_url}/sites")
    if sites_response.status_code == 200:
        sites_data = sites_response.json()
        if len(sites_data) > 0:
            site_id = sites_data[0]["id"]
            response = httpx.put(f"{api_url}/sites/{site_id}/enable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "site_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is False  # Enabled means False
                
                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/sites/{site_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is False
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_disable_site(load_nodes_data):
    """Test to disable a site and verify state change"""
    api_url = get_api_url()
    # First, get the list of sites to find a site ID
    sites_response = send_get_request(f"{api_url}/sites")
    if sites_response.status_code == 200:
        sites_data = sites_response.json()
        if len(sites_data) > 0:
            site_id = sites_data[0]["id"]
            response = httpx.put(f"{api_url}/sites/{site_id}/disable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "site_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is True  # Disabled means True
                
                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/sites/{site_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is True
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_enable_disable_site_cycle(load_nodes_data):
    """Test enable/disable cycle for site with state verification"""
    api_url = get_api_url()
    # First, get the list of sites to find a site ID
    sites_response = send_get_request(f"{api_url}/sites")
    if sites_response.status_code == 200:
        sites_data = sites_response.json()
        if len(sites_data) > 0:
            site_id = sites_data[0]["id"]
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                # 1. Disable the site
                disable_response = httpx.put(f"{api_url}/sites/{site_id}/disable")  # noqa: E231
                assert disable_response.status_code == 200
                disable_data = disable_response.json()
                assert disable_data.get("is_force_disabled") is True
                
                # Verify disabled state
                verify_disabled = send_get_request(f"{api_url}/sites/{site_id}")
                if verify_disabled.status_code == 200:
                    assert verify_disabled.json().get("is_force_disabled") is True
                
                # 2. Re-enable the site
                enable_response = httpx.put(f"{api_url}/sites/{site_id}/enable")  # noqa: E231
                assert enable_response.status_code == 200
                enable_data = enable_response.json()
                assert enable_data.get("is_force_disabled") is False
                
                # Verify enabled state
                verify_enabled = send_get_request(f"{api_url}/sites/{site_id}")
                if verify_enabled.status_code == 200:
                    assert verify_enabled.json().get("is_force_disabled") is False


@pytest.mark.component
def test_enable_site_not_found():
    """Test to enable a non-existent site"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/sites/{fake_id}/enable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API returns 404 when site not found (based on server.py line 880)
        assert response.status_code == 404
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_disable_site_not_found():
    """Test to disable a non-existent site"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/sites/{fake_id}/disable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API returns 404 when site not found (based on server.py line 912)
        assert response.status_code == 404
    else:
        assert response.status_code == 403

