"""
A module with integration tests for SKA SRC Site Capabilities GET APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_check_ping():
    """Test method for ping API"""
    print(KUBE_NAMESPACE)
    print(CLUSTER_DOMAIN)
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/ping"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_check_health():
    """Test method for health API"""
    print(KUBE_NAMESPACE)
    print(CLUSTER_DOMAIN)
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/health"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    assert 0


@pytest.mark.post_deployment
def test_get_sites_api():
    """Test method for get sites API"""
    # response = httpx.get(
    #     "https://site-capabilities.srcdev.skao.int/api/v1/sites"
    # )
    print(KUBE_NAMESPACE)
    print(CLUSTER_DOMAIN)
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    assert 0


# API path
#  http://<service-name>.<namespace>.svc.<cluster-domain>:<port>/<api-name>

#  cluster-domain = cluster.local
#  port = 8080
