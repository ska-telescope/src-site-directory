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

