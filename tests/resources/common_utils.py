"""This module implement common utils
"""
import json
import os
from os.path import dirname, join

import httpx

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


def get_test_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    file_path = join(
        dirname(__file__),
        "..",
        "test-data",
        f"{slug}.json",
    )
    with open(file_path, "r", encoding="UTF-8") as f:
        json_value = f.read()
    print("json_value:::", json_value)
    print("type of json values:", type(json_value))
    return json.load(json_value)


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
