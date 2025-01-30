"""
A module with integration tests for SKA SRC Site Capabilities Site Delete APIs.
"""
import json
import os

import httpx
import pytest

# from tests.resources.common_utils import get_test_json
from tests.resources.site_versions import TEST_SITE_VER_1

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.delete_api
# @pytest.mark.post_deployment
def test_post_sites():
    """Test to verify post sites API"""
    # sites_json = get_test_json("test_site_version_1")
    # json_data = json.loads(sites_json)

    # headers = {"Content-Type": "application/json"}
    response = httpx.post(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites",
        data=TEST_SITE_VER_1,
        # headers=headers,
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert len(response_data) != 0
        assert 0
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]


# def check_sites_availability():
#     """A method to check whether sites are available to perform other operations"""
#     response = httpx.get(
#         f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
#     )

#     response_data = response.json()
#     assert len(response_data) != 0


# def tear_down():
#     """Make sites available again"""
#     sites_json = get_test_json("test_site_version_1")
#     # json_data = json.loads(sites_json)

#     headers = {'Content-Type': 'application/json'}
#     response = httpx.post(
#         f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites", data=sites_json, headers=headers
#     )
#     response_data = response.json()
#     print(response_data)
#     if os.getenv("DISABLE_AUTH") == "yes":
#         assert response.status_code == 200
#         assert len(response_data) != 0
#     else:
#         assert response.status_code == 403
#         assert "Not authenticated" in response_data["detail"]
#     json_str = get_test_json("sites")
#     print("json_str::::", json_str)
