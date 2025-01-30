"""
A module with integration tests for SKA SRC Site Capabilities Site Delete APIs.
"""
import json
import os

import httpx
import pytest

# from tests.resources.common_utils import get_test_json
from tests.resources.site_versions import TEST_SITE_VER_1, TEST_SITE_VER_2

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
        data=json.dumps(TEST_SITE_VER_1),
    )
    print(response)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        check_site_is_present(site="TestSite")
    else:
        assert response.status_code == 403


@pytest.mark.delete_api
def test_delete_all_versions_site():
    """Test to verify delete all site versions API"""
    load_multiple_sites([TEST_SITE_VER_1, TEST_SITE_VER_2])

    site_to_delete = "TestSite"
    response = httpx.delete(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site_to_delete}"
    )
    print(response)
    response_data = response.json()
    print(response)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["successful"] is True
        check_site_not_present(site=site_to_delete)
    else:
        assert response.status_code == 403


@pytest.mark.delete_api
def test_delete_given_versions_site():
    """Test to verify delete all site versions API"""
    load_multiple_sites([TEST_SITE_VER_1, TEST_SITE_VER_2])

    site = "TestSite"
    version = ["1", "2"]
    for ver in version:
        response = httpx.delete(
            f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites/{site}/{ver}"
        )
    print(response)
    response_data = response.json()
    print(response)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["successful"] is True
        check_version_not_present(site)
    else:
        assert response.status_code == 403


def check_site_is_present(site: str):
    """Method to verify sites"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    assert response.status_code == 200
    assert site in response_data


def check_site_not_present(site: str):
    """Method to verify deleted sites"""

    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    assert response.status_code == 200
    assert site not in response_data


def check_version_not_present(site_name: str):
    """Method to verify given site version are removed"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    print(response)
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        print(response_data)
        assert site_name not in response_data
        assert 0
    else:
        assert len(response_data) != 0


def load_multiple_sites(site_list):
    """Method to post Sites one by one"""

    for site in site_list:
        response = httpx.post(
            f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites",
            data=json.dumps(site),
        )
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


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
