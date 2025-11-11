"""
A module for component tests related to compute.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_compute(load_nodes_data):
    """Test to list all compute"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/compute")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got compute data
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_compute_filter_by_node_names(load_nodes_data):
    """Test to list compute filtered by node names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/compute?node_names={node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_compute_filter_by_site_names(load_nodes_data):
    """Test to list compute filtered by site names"""
    api_url = get_api_url()
    # Get a site name from the loaded nodes
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/compute?site_names={site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_list_compute_include_inactive(load_nodes_data):
    """Test to list compute with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/compute?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_compute_by_id(load_nodes_data):
    """Test to get a compute by ID"""
    api_url = get_api_url()
    # First, get the list of compute to find a compute ID
    compute_response = send_get_request(f"{api_url}/compute")
    if compute_response.status_code == 200:
        compute_data = compute_response.json()
        if len(compute_data) > 0:
            compute_id = compute_data[0]["id"]
            response = httpx.get(f"{api_url}/compute/{compute_id}")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["id"] == compute_id
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_get_compute_not_found():
    """Test to get a non-existent compute"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.get(f"{api_url}/compute/{fake_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 404
    else:
        assert response.status_code in (403, 404)


@pytest.mark.component
def test_enable_compute(load_nodes_data):
    """Test to enable a compute resource"""
    api_url = get_api_url()
    # First, get the list of compute to find a compute ID
    compute_response = send_get_request(f"{api_url}/compute")
    if compute_response.status_code == 200:
        compute_data = compute_response.json()
        if len(compute_data) > 0:
            compute_id = compute_data[0]["id"]
            response = httpx.put(f"{api_url}/compute/{compute_id}/enable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure
                assert isinstance(data, dict)
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_disable_compute(load_nodes_data):
    """Test to disable a compute resource"""
    api_url = get_api_url()
    # First, get the list of compute to find a compute ID
    compute_response = send_get_request(f"{api_url}/compute")
    if compute_response.status_code == 200:
        compute_data = compute_response.json()
        if len(compute_data) > 0:
            compute_id = compute_data[0]["id"]
            response = httpx.put(f"{api_url}/compute/{compute_id}/disable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure
                assert isinstance(data, dict)
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_enable_disable_compute_cycle(load_nodes_data):
    """Test enable/disable cycle for compute resource"""
    api_url = get_api_url()
    # First, get the list of compute to find a compute ID
    compute_response = send_get_request(f"{api_url}/compute")
    if compute_response.status_code == 200:
        compute_data = compute_response.json()
        if len(compute_data) > 0:
            compute_id = compute_data[0]["id"]
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                # Disable the compute
                disable_response = httpx.put(f"{api_url}/compute/{compute_id}/disable")  # noqa: E231
                assert disable_response.status_code == 200
                
                # Re-enable the compute
                enable_response = httpx.put(f"{api_url}/compute/{compute_id}/enable")  # noqa: E231
                assert enable_response.status_code == 200


@pytest.mark.component
def test_enable_compute_not_found():
    """Test to enable a non-existent compute"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/compute/{fake_id}/enable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_disable_compute_not_found():
    """Test to disable a non-existent compute"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/compute/{fake_id}/disable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 403
