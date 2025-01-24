"""
A module with integration tests for SKA SRC Site Capabilities Storage APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.parametrize(
    "api_name",
    ["storages", "storage-areas"],
)
@pytest.mark.post_deployment
def test_get_list(api_name):
    """Test API to list all storages and storage areas"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/{api_name}"
    )
    response_data = response.json()
    if api_name == "storage-areas":
        api_name = api_name.replace("-", "_")
    for item in response_data:
        assert item[api_name] is not None


@pytest.mark.post_deployment
def test_get_list_from_id():
    """Test API to get storage areas using id"""
    id = "b183cfeb-03e7-4c38-a9cf-1f4307dad45a"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storage-areas/{id}"
    )
    response_data = response.json()
    assert response_data["id"] == id


@pytest.mark.parametrize(
    "api_name",
    ["storages", "storage-areas"],
)
@pytest.mark.post_deployment
def test_get_list_failure(api_name):
    """Test API failure to get storage and storage areas using id"""
    id = "19497bf6-0710-4000-8f0b-4d7163ba7801"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/{api_name}/{id}"
    )
    response_data = response.json()
    if api_name == "storage-areas":
        assert (
            f"Storage area with identifier '{id}' could not be found"
            in response_data["detail"]
        )
    else:
        assert (
            f"Storage with identifier '{id}' could not be found"
            in response_data["detail"]
        )


@pytest.mark.parametrize(
    "api_name",
    ["storages", "storage-areas"],
)
@pytest.mark.post_deployment
def test_get_list_in_grafana_format(api_name):
    """Test API to list all storages and storage areas in grafana format"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/{api_name}/grafana"
    )
    response_data = response.json()
    for item in response_data:
        storage_format = item.keys()
        assert list(storage_format) == ["key", "latitude", "longitude", "name"]


@pytest.mark.parametrize(
    "api_name",
    ["storages", "storage-areas"],
)
@pytest.mark.post_deployment
def test_get_list_in_topojson_format(api_name):
    """Test API to list all storages and storage areas in grafana format"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/{api_name}/topojson"
    )
    response_data = response.json()
    assert response_data["type"] == "Topology"
