"""
A module for component tests related to status.
"""

import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_check_ping():
    """Test to check ping API"""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/ping")  # noqa: E231
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "UP"


@pytest.mark.component
def test_check_health():
    """Test to check health API"""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/health")  # noqa: E231
    assert response.status_code == 500  # permissions and auth API will be down
    response_data = response.json()
    assert response_data["uptime"] > 0
