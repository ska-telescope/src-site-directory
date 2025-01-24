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
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_get_storage_from_id():
    """Test to get strorage from strorage id"""
    storage_id = "19497bf6-0710-4000-8f0b-4d7163ba7801"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{storage_id}"
    )
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_list_all_grafana_storages():
    """Test to list all grafana format storages"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/grafana"
    )
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_list_storages_in_topojson():
    """Test to list all topojson format storages"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages/topojson"
    )
    response_data = response.json()
    print(response_data)
    assert 0
