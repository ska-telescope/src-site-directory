"""
A module for component tests related to storages.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_storages(load_nodes_data):
    """Test to list storages."""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/storages")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got storages data
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_storages_filter_by_node_names(load_nodes_data):
    """Test to list storages filtered by node names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/storages?node_names={node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_storages_filter_by_site_names(load_nodes_data):
    """Test to list storages filtered by site names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/storages?site_names={site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_list_storages_include_inactive(load_nodes_data):
    """Test to list storages with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/storages?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_storages_grafana(load_nodes_data):
    """Test to list storages in Grafana format"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/storages/grafana")  # noqa: E231
    # Grafana endpoint doesn't require authentication
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.component
def test_list_storages_topojson(load_nodes_data):
    """Test to list storages in topojson format"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/storages/topojson")  # noqa: E231
    # Topojson endpoint doesn't require authentication
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Topojson format should have specific structure
    assert "type" in data or "objects" in data


@pytest.mark.component
def test_get_storage_by_id(load_nodes_data):
    """Test to get a storage by ID"""
    api_url = get_api_url()
    # First, get the list of storages to find a storage ID
    storages_response = send_get_request(f"{api_url}/storages")
    if storages_response.status_code == 200:
        storages_data = storages_response.json()
        if len(storages_data) > 0:
            storage_id = storages_data[0]["id"]
            response = httpx.get(f"{api_url}/storages/{storage_id}")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["id"] == storage_id
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_get_storage_not_found():
    """Test to get a non-existent storage"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.get(f"{api_url}/storages/{fake_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 404
    else:
        assert response.status_code in (403, 404)
