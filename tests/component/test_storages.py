"""
A module for  component tests related to storages.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_storages():
    """Test to list storages."""
    response = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/storages")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403
