"""
A module with integration tests for SKA SRC Site Capabilities Compute APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_all_computes():
    """Test to list all computes"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute"
    )
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_get_compute_from_id():
    """Test to get compute from compute_id"""
    compute_id = "19497bf6-0710-4000-8f0b-4d7163ba7801"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}"
    )
    response_data = response.json()
    print(response_data)
    assert 0
