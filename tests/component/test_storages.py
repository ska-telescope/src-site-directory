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
        assert response.status_code == 401


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
            assert response.status_code == 401


@pytest.mark.component
def test_list_storages_filter_by_multiple_node_names(load_nodes_data):
    """Test to list storages filtered by multiple node names (comma-separated)"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        # Use the same node name twice to test comma-separated format
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/storages?node_names={node_name},{node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 401


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
                    assert response.status_code == 401


@pytest.mark.component
def test_list_storages_filter_by_multiple_site_names(load_nodes_data):
    """Test to list storages filtered by multiple site names (comma-separated)"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) >= 2:
                # Get two site names
                site_name_1 = node_data["sites"][0]["name"]
                site_name_2 = node_data["sites"][1]["name"]
                response = httpx.get(f"{api_url}/storages?site_names={site_name_1},{site_name_2}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 401
            elif "sites" in node_data and len(node_data["sites"]) == 1:
                # If only one site, use it twice to test comma-separated format
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/storages?site_names={site_name},{site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 401


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
        assert response.status_code == 401


@pytest.mark.component
def test_list_storages_grafana(load_nodes_data):
    """Test to list storages in Grafana format

    Note: Sites without latitude/longitude are automatically skipped by the backend.
    """
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/storages/grafana")  # noqa: E231
    # Grafana endpoint doesn't require authentication
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # Verify that all entries have required Grafana fields
    for entry in data:
        assert "key" in entry
        assert "latitude" in entry
        assert "longitude" in entry
        assert "name" in entry
        assert isinstance(entry["latitude"], (int, float))
        assert isinstance(entry["longitude"], (int, float))


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
                assert response.status_code == 401


@pytest.mark.component
def test_get_storage_not_found():
    """Test to get a non-existent storage"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.get(f"{api_url}/storages/{fake_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 404
    else:
        assert response.status_code in (401, 404)


@pytest.mark.component
def test_enable_storage(load_nodes_data):
    """Test to enable a storage and verify state change"""
    api_url = get_api_url()
    # First, get the list of storages to find a storage ID
    storages_response = send_get_request(f"{api_url}/storages")
    if storages_response.status_code == 200:
        storages_data = storages_response.json()
        if len(storages_data) > 0:
            storage_id = storages_data[0]["id"]
            response = httpx.put(f"{api_url}/storages/{storage_id}/enable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "storage_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is False  # Enabled means False

                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/storages/{storage_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is False
            else:
                assert response.status_code == 401


@pytest.mark.component
def test_disable_storage(load_nodes_data):
    """Test to disable a storage and verify state change"""
    api_url = get_api_url()
    # First, get the list of storages to find a storage ID
    storages_response = send_get_request(f"{api_url}/storages")
    if storages_response.status_code == 200:
        storages_data = storages_response.json()
        if len(storages_data) > 0:
            storage_id = storages_data[0]["id"]
            response = httpx.put(f"{api_url}/storages/{storage_id}/disable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "storage_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is True  # Disabled means True

                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/storages/{storage_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is True
            else:
                assert response.status_code == 401


@pytest.mark.component
def test_enable_disable_storage_cycle(load_nodes_data):
    """Test enable/disable cycle for storage with state verification"""
    api_url = get_api_url()
    # First, get the list of storages to find a storage ID
    storages_response = send_get_request(f"{api_url}/storages")
    if storages_response.status_code == 200:
        storages_data = storages_response.json()
        if len(storages_data) > 0:
            storage_id = storages_data[0]["id"]
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                # 1. Disable the storage
                disable_response = httpx.put(f"{api_url}/storages/{storage_id}/disable")  # noqa: E231
                assert disable_response.status_code == 200
                disable_data = disable_response.json()
                assert disable_data.get("is_force_disabled") is True

                # Verify disabled state
                verify_disabled = send_get_request(f"{api_url}/storages/{storage_id}")
                if verify_disabled.status_code == 200:
                    assert verify_disabled.json().get("is_force_disabled") is True

                # 2. Re-enable the storage
                enable_response = httpx.put(f"{api_url}/storages/{storage_id}/enable")  # noqa: E231
                assert enable_response.status_code == 200
                enable_data = enable_response.json()
                assert enable_data.get("is_force_disabled") is False

                # Verify enabled state
                verify_enabled = send_get_request(f"{api_url}/storages/{storage_id}")
                if verify_enabled.status_code == 200:
                    assert verify_enabled.json().get("is_force_disabled") is False


@pytest.mark.component
def test_enable_storage_not_found():
    """Test to enable a non-existent storage"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/storages/{fake_id}/enable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 401


@pytest.mark.component
def test_disable_storage_not_found():
    """Test to disable a non-existent storage"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/storages/{fake_id}/disable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 401
