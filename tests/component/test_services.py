"""
A module for component tests related to services.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_services():
    """Test to list all services"""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_services_enabled():
    """Test to set service as enabled"""
    service_id = "4f57724b-aa73-4c6c-bf0c-3fb95677cc91"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}/enable")  # noqa: E231
    response_data = response.json()
    get_response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}")  # noqa: E231
    response_data = get_response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["service_id"] == service_id
        assert response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403
    assert 0


@pytest.mark.post_deployment
def test_set_services_disabled():
    """Test to set service as disabled"""
    service_id = "4f57724b-aa73-4c6c-bf0c-3fb95677cc91"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}/disable")  # noqa: E231
    response_data = response.json()
    get_response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}")  # noqa: E231
    response_data = get_response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["service_id"] == service_id
        assert response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
