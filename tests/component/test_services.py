"""
A module for component tests related to services.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_services(load_nodes_data):
    """Test to list all services"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got services data
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_node_names(load_nodes_data):
    """Test to list services filtered by node names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/services?node_names={node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_site_names(load_nodes_data):
    """Test to list services filtered by site names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/services?site_names={site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_service_types(load_nodes_data):
    """Test to list services filtered by service types"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?service_types=ingest")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_service_scope(load_nodes_data):
    """Test to list services filtered by service scope"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?service_scope=local")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_service_scope_global(load_nodes_data):
    """Test to list services filtered by global service scope"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?service_scope=global")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_associated_storage_area_id(load_nodes_data):
    """Test to list services filtered by associated storage area ID"""
    api_url = get_api_url()
    # First, get a storage area ID from the storage areas
    storage_areas_response = send_get_request(f"{api_url}/storage-areas")
    if storage_areas_response.status_code == 200:
        storage_areas_data = storage_areas_response.json()
        if len(storage_areas_data) > 0:
            storage_area_id = storage_areas_data[0]["id"]
            response = httpx.get(f"{api_url}/services?associated_storage_area_id={storage_area_id}")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_multiple_node_names(load_nodes_data):
    """Test to list services filtered by multiple node names (comma-separated)"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        # Use the same node name twice to test comma-separated format
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/services?node_names={node_name},{node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_multiple_site_names(load_nodes_data):
    """Test to list services filtered by multiple site names (comma-separated)"""
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
                response = httpx.get(f"{api_url}/services?site_names={site_name_1},{site_name_2}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 403
            elif "sites" in node_data and len(node_data["sites"]) == 1:
                # If only one site, use it twice to test comma-separated format
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/services?site_names={site_name},{site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, list)
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_list_services_filter_by_multiple_service_types(load_nodes_data):
    """Test to list services filtered by multiple service types (comma-separated)"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?service_types=ingest,echo")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_include_inactive(load_nodes_data):
    """Test to list services with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_services_prometheus_output(load_nodes_data):
    """Test to list services with Prometheus output format"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services?output=prometheus")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        # Prometheus format should be a list
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_service_types():
    """Test to list service types"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/services/types")  # noqa: E231
    # Service types endpoint doesn't require authentication
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Should have local and global service types
    assert "local" in data
    assert "global" in data
    assert isinstance(data["local"], list)
    assert isinstance(data["global"], list)


@pytest.mark.component
def test_get_service_by_id(load_nodes_data):
    """Test to get a service by ID"""
    api_url = get_api_url()
    # First, get the list of services to find a service ID
    services_response = send_get_request(f"{api_url}/services")
    if services_response.status_code == 200:
        services_data = services_response.json()
        if len(services_data) > 0:
            service_id = services_data[0]["id"]
            response = httpx.get(f"{api_url}/services/{service_id}")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["id"] == service_id
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_get_service_not_found():
    """Test to get a non-existent service"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.get(f"{api_url}/services/{fake_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 404
    else:
        assert response.status_code in (403, 404)


@pytest.mark.component
def test_enable_service(load_nodes_data):
    """Test to enable a service and verify state change"""
    api_url = get_api_url()
    # First, get the list of services to find a service ID
    services_response = send_get_request(f"{api_url}/services")
    if services_response.status_code == 200:
        services_data = services_response.json()
        if len(services_data) > 0:
            service_id = services_data[0]["id"]
            response = httpx.put(f"{api_url}/services/{service_id}/enable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "service_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is False  # Enabled means False
                
                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/services/{service_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is False
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_disable_service(load_nodes_data):
    """Test to disable a service and verify state change"""
    api_url = get_api_url()
    # First, get the list of services to find a service ID
    services_response = send_get_request(f"{api_url}/services")
    if services_response.status_code == 200:
        services_data = services_response.json()
        if len(services_data) > 0:
            service_id = services_data[0]["id"]
            response = httpx.put(f"{api_url}/services/{service_id}/disable")  # noqa: E231
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                assert response.status_code == 200
                data = response.json()
                # Verify response structure and state change
                assert isinstance(data, dict)
                assert "service_id" in data
                assert "is_force_disabled" in data
                assert data["is_force_disabled"] is True  # Disabled means True
                
                # Verify state persisted by getting the resource again
                verify_response = send_get_request(f"{api_url}/services/{service_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data.get("is_force_disabled") is True
            else:
                assert response.status_code == 403


@pytest.mark.component
def test_enable_disable_service_cycle(load_nodes_data):
    """Test enable/disable cycle for service with state verification"""
    api_url = get_api_url()
    # First, get the list of services to find a service ID
    services_response = send_get_request(f"{api_url}/services")
    if services_response.status_code == 200:
        services_data = services_response.json()
        if len(services_data) > 0:
            service_id = services_data[0]["id"]
            if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                # 1. Disable the service
                disable_response = httpx.put(f"{api_url}/services/{service_id}/disable")  # noqa: E231
                assert disable_response.status_code == 200
                disable_data = disable_response.json()
                assert disable_data.get("is_force_disabled") is True
                
                # Verify disabled state
                verify_disabled = send_get_request(f"{api_url}/services/{service_id}")
                if verify_disabled.status_code == 200:
                    assert verify_disabled.json().get("is_force_disabled") is True
                
                # 2. Re-enable the service
                enable_response = httpx.put(f"{api_url}/services/{service_id}/enable")  # noqa: E231
                assert enable_response.status_code == 200
                enable_data = enable_response.json()
                assert enable_data.get("is_force_disabled") is False
                
                # Verify enabled state
                verify_enabled = send_get_request(f"{api_url}/services/{service_id}")
                if verify_enabled.status_code == 200:
                    assert verify_enabled.json().get("is_force_disabled") is False


@pytest.mark.component
def test_enable_service_not_found():
    """Test to enable a non-existent service"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/services/{fake_id}/enable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_disable_service_not_found():
    """Test to disable a non-existent service"""
    api_url = get_api_url()
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = httpx.put(f"{api_url}/services/{fake_id}/disable")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 with empty response or 404
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 403
