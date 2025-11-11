"""
A module for component tests related to nodes.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request, send_post_request, send_delete_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_nodes(load_nodes_data):
    """Test to list all nodes"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify we have at least one node
        assert len(data) > 0
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_nodes_only_names(load_nodes_data):
    """Test to list nodes with only_names parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes?only_names=true")  # noqa: E231
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
def test_list_nodes_include_inactive(load_nodes_data):
    """Test to list nodes with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_node_by_name(load_nodes_data):
    """Test to get a node by name"""
    api_url = get_api_url()
    # Get the first node name from the loaded data
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/nodes/{node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            # API returns empty dict {} if node not found, or node data if found
            if data:  # If node exists
                assert "name" in data
                assert data["name"] == node_name
            # If empty dict, node doesn't exist (but API still returns 200)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_get_node_by_name_latest_version(load_nodes_data):
    """Test to get a node by name with latest version"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/nodes/{node_name}?node_version=latest")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            # API returns empty dict {} if node not found, or node data if found
            if data:  # If node exists
                assert "name" in data
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_get_node_not_found():
    """Test to get a non-existent node"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes/NONEXISTENT_NODE")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API returns 200 with empty dict {} when node not found
        assert response.status_code == 200
        data = response.json()
        assert data == {}  # Empty dict indicates node not found
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_dump_nodes(load_nodes_data):
    """Test to dump all versions of all nodes"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes/dump")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_site_from_node_and_site_name(load_nodes_data):
    """Test to get a site from node and site names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Try to get the first site from the node
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/nodes/{node_name}/sites/{site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert "name" in data
                    assert data["name"] == site_name
                else:
                    assert response.status_code == 403

