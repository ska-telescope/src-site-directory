"""
A module with integration tests for SKA SRC Site Capabilities Services APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_services():
    """Test API to list all services"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services?include_associated_with_compute=true&include_disabled=false"
    )

    response_data = response.json()
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        for item in response_data:
            assert item["services"] is not None
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]


@pytest.mark.post_deployment
def test_list_services_using_id():
    """Test API to get services with id"""
    service_id = "1f73c95e-301b-4f5e-a2cf-aeb461da2d70"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}"
    )

    response_data = response.json()
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["id"] == service_id
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]


@pytest.mark.post_deployment
def test_list_services_types():
    """Test API to list services types"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/types"
    )

    response_data = response.json()
    assert response.status_code == 200
    assert "echo" in response_data["local"]
    assert "jupyterhub" in response_data["local"]
    assert "binderhub" in response_data["local"]
    assert "dask" in response_data["local"]
    assert "ingest" in response_data["local"]
    assert "rucio" in response_data["global"]
    assert "iam" in response_data["global"]
    assert "data-management-api" in response_data["global"]
    assert "site-capabilities-api" in response_data["global"]
    assert "permissions-api" in response_data["global"]
