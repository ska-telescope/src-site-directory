"""
A module for component tests related to storages.
"""

import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_storages():
    """Test to list storages."""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_set_storages_enabled():
    """Test to set storage as enabled"""
    storage_id = "180f2f39-4548-4f11-80b1-7471564e5c05"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/{storage_id}/enable")  # noqa: E231
    get_storages = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/{storage_id}")  # noqa: E231
    get_storage_response_data = get_storages.json()
    print(get_storage_response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert get_storage_response_data["id"] == storage_id
        assert get_storage_response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_set_storages_disabled():
    """Test to set storage as disabled"""
    storage_id = "180f2f39-4548-4f11-80b1-7471564e5c05"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/{storage_id}/disable")  # noqa: E231
    get_storage = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/{storage_id}")  # noqa: E231
    get_storage_response_data = get_storage.json()
    print(get_storage_response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert get_storage_response_data["id"] == storage_id
        assert get_storage_response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
