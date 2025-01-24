"""
A module with integration tests for SKA SRC Site Capabilities Services APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_services():
    """Test API to list all services"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services?include_associated_with_compute=true&include_disabled=false"
    )

    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_list_services_using_id():
    """Test API to get services with id"""
    service_id = "19498554-8b10-4000-8ee5-a9ae31910401"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/{service_id}"
    )

    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_list_services_types():
    """Test API to list services types"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/services/types"
    )

    response_data = response.json()
    print(response_data)
    assert 0
