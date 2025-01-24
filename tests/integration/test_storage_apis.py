"""
A module with integration tests for SKA SRC Site Capabilities Storage APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_all_storages():
    """Test to list all storages"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages"
    )
    response_data = response.json()
    for item in response_data:
        assert item["storages"][0]["id"] != ""


@pytest.mark.post_deployment
def test_get_storage_from_id():
    """Test to get strorage from storage id"""
    storage_id = "89ee6cac-0977-425e-b766-780a8e14420d"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{storage_id}"
    )
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_fail_to_get_storage_from_id():
    """Test fail to get storage from storage id"""
    storage_id = "19497bf6-0710-4000-8f0b-4d7163ba7801"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{storage_id}"
    )
    response_data = response.json()
    assert (
        f"Compute element with identifier {storage_id} could not be found"
        in response_data["detail"]
    )


@pytest.mark.post_deployment
def test_list_all_storages_for_grafana():
    """Test to list all storages grafana format"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/grafana"
    )
    response_data = response.json()
    for item in response_data:
        storage_format = item.keys()
        assert list(storage_format) == ["key", "latitude", "longitude", "name"]


@pytest.mark.post_deployment
def test_list_storages_in_topojson():
    """Test to list all storages topojson format"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/topojson"
    )
    response_data = response.json()
    assert response_data["type"] == "Topology"
