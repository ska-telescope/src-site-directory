"""
A module with integration tests for SKA SRC Site Capabilities Site Delete APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.delete_api
# @pytest.mark.post_deployment
def test_delete_sites():
    """Test to verify delete sites API"""
    check_sites_availability()
    response = httpx.delete(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["successful"] == True
        tear_down()
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]


def check_sites_availability():
    """A method to check whether sites are available to perform other operations"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )

    response_data = response.json()
    assert len(response_data) != 0


def tear_down():
    """Make sites available again"""
    response = httpx.post(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert len(response_data) != 0
        assert 0
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]

