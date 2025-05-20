"""
A module for component tests related to compute.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_compute():
    """Test to list all compute"""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


@pytest.mark.post_deployment
def test_set_compute_enabled():
    """Test to set compute as enabled"""
    compute_id = "db1d3ee3-74e4-48aa-afaf-8d7709a2f57c"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}/enable")  # noqa: E231
    response_data = response.json()
    get_compute = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}")  # noqa: E231
    response_data = get_compute.json()
    print(response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["compute_id"] == compute_id
        assert response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403
    assert 0


@pytest.mark.post_deployment
def test_set_compute_disabled():
    """Test to set compute as disabled"""
    compute_id = "db1d3ee3-74e4-48aa-afaf-8d7709a2f57c"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}/disable")  # noqa: E231
    response_data = response.json()
    get_compute = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/compute/{compute_id}")  # noqa: E231
    response_data = get_compute.json()
    print(response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert response_data["compute_id"] == compute_id
        assert response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
    assert 0
