"""
A module for component tests related to status.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_check_ping():
    """Test to check ping API"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/ping")  # noqa: E231
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "UP"


@pytest.mark.component
def test_check_health():
    """Test to check health API"""
    from tests.component.conftest import DISABLE_AUTHENTICATION

    api_url = get_api_url()
    response = httpx.get(f"{api_url}/health")  # noqa: E231

    # When authentication is disabled, health check should pass (200)
    # When authentication is enabled but dependencies are down, expect 500
    if DISABLE_AUTHENTICATION:
        assert response.status_code == 200
    else:
        assert response.status_code == 500  # permissions and auth API will be down

    response_data = response.json()
    assert response_data["uptime"] > 0
