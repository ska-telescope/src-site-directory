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
    for item in response_data:
        assert item["site_name"] in [
            "CNSRC",
            "UKSRC",
            "SKAOSRC",
            "ESPSRC",
            "CANSRC",
        ]
        assert item["compute"][0]["id"] != ""


@pytest.mark.post_deployment
def test_get_compute_from_id():
    """Test to get compute from compute_id"""
    compute_id = "dd875a28-2df8-4f9f-838c-aa4110b4c4b9"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}"
    )
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_fail_to_get_compute_from_id():
    """Test fail to get compute from compute_id"""
    compute_id = "19497bf6-0710-4000-8f0b-4d7163ba7801"
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}"
    )
    response_data = response.json()
    assert (
        f"Compute element with identifier {compute_id} could not be found"
        in response_data["detail"]
    )
