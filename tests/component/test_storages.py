"""
A module for  component tests related to storages.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_storages():
    """Test to list storages."""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_storages_enabled():
    """Test to set storage as enabled/disabled"""
    storage_id = "180f2f39-4548-4f11-80b1-7471564e5c05"
    response = httpx.put(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/{storage_id}/enabled"  # noqa: E231
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["storageID"] == storage_id
    else:
        assert response.status_code == 403
