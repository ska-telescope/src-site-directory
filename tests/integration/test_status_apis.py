"""
A module with integration tests for SKA SRC Site Capabilities Site APIs.
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
