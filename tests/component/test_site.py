"""
A module for  component tests related to compute.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_set_site_enabled():
    """Test to set site as enabled"""
    site_id = "5b8251b6-12ea-499e-8699-edcd8a55d9b8"
    response = httpx.put(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}/enabled"  # noqa: E231
    )
    response_data = response.json()
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["site_id"] == site_id
        assert response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_site_disabled():
    """Test to set site as disabled"""
    site_id = "5b8251b6-12ea-499e-8699-edcd8a55d9b8"
    response = httpx.put(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}/disabled"  # noqa: E231
    )
    response_data = response.json()
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["site_id"] == site_id
        assert response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
