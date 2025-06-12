"""
A module for component tests related to sites.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_set_site_enabled():
    """Test to set site as enabled"""
    site_id = "8b008348-0d8d-4505-a625-1e6e8df56e8a"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}/enable")  # noqa: E231
    get_site = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}")  # noqa: E231
    get_site_response_data = get_site.json()
    print(get_site_response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert get_site_response_data["id"] == site_id
        assert get_site_response_data["is_force_disabled"] is False
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_set_site_disabled():
    """Test to set site as disabled"""
    site_id = "8b008348-0d8d-4505-a625-1e6e8df56e8a"
    response = httpx.put(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}/disable")  # noqa: E231
    get_site = httpx.get(f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_id}")  # noqa: E231
    get_site_response_data = get_site.json()
    print(get_site_response_data)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        assert get_site_response_data["id"] == site_id
        assert get_site_response_data["is_force_disabled"] is True
    else:
        assert response.status_code == 403
