"""
A module with integration tests for SKA SRC Site Capabilities Site Delete all sites.
"""
import os

import httpx
import pytest

from tests.resources.common_utils import CLUSTER_DOMAIN, KUBE_NAMESPACE


@pytest.mark.delete_api
# @pytest.mark.post_deployment
def test_delete_sites():
    """Test to verify delete sites API"""
    response = httpx.delete(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["successful"] is True
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]
