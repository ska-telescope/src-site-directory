"""
A module with integration tests for SKA SRC Site Capabilities GET APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_check_ping():
    """Test to check ping API"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/ping"
    )
    response_data = response.json()
    assert response_data["status"] == "UP"


@pytest.mark.post_deployment
def test_check_health():
    """Test to check health API"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/health"
    )
    response_data = response.json()
    assert response_data["uptime"] > 0
    assert (
        response_data["dependent_services"]["permissions-api"]["status"]
        == "UP"
    )


@pytest.mark.post_deployment
def test_get_sites_api():
    """Test method for get sites API"""
    print(KUBE_NAMESPACE)
    print(CLUSTER_DOMAIN)
    response_a = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/www/sites/add"
    )
    print(response_a)
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    response_data = response.json()
    print(response_data)
    assert 0
