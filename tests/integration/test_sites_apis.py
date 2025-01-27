"""
A module with integration tests for SKA SRC Site Capabilities Site APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_get_sites():
    """Test method for get sites API"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )

    response_data = response.json()
    assert len(response_data) != 0


@pytest.mark.parametrize(
    "site_name",
    [
        "SWESRC",
        "CHSRC",
        "CNSRC",
        "UKSRC",
        "SKAOSRC",
        "AUSSRC",
        "KRSRC",
        "NLSRC",
        "ESPSRC",
        "JPSRC",
        "CANSRC",
    ],
)
@pytest.mark.post_deployment
def test_get_all_versions_sites(site_name):
    """Test method to get all versions for sites"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_name}"
    )

    response_data = response.json()
    print(response_data)
    print(response.status_code)
    print(os.getenv("DISABLE_AUTH"))
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response_data[0]["version"] is not None
    else:
        assert "Not authenticated" in response_data["detail"]


# authentication is required
@pytest.mark.post_deployment
def test_get_latest_version_sites():
    """Test method to get all versions for sites"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/latest"
    )

    response_data = response.json()
    print(response_data)
    print(response.status_code)
    print(os.getenv("DISABLE_AUTH"))
    if os.getenv("DISABLE_AUTH") == "yes":
        assert len(response_data) > 0
