"""
A module for  component tests related to storage areas.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_storage_areas():
    """Test to list storage areas."""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storage-areas")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_storages_areas_enabled():
    """Test to set storage areas as enabled"""
    storage_area_id = "448e27fe-b695-4f91-90c3-0a8f2561ccdf"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storage-areas/{storage_area_id}/enabled")  # noqa: E231
    response_data = response.json()
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["storage_area_id"] == storage_area_id
        assert response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_storages_areas_disabled():
    """Test to set storage areas as disabled"""
    storage_area_id = "448e27fe-b695-4f91-90c3-0a8f2561ccdf"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storage-areas/{storage_area_id}/disabled")  # noqa: E231
    response_data = response.json()
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["storage_area_id"] == storage_area_id
        assert response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
