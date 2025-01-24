"""
A module with integration tests for SKA SRC Site Capabilities Schema APIs.
"""
import os

import httpx
import pytest

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.post_deployment
def test_list_schemas():
    """Test API to list all schemas"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/schemas"
    )

    response_data = response.json()
    print(response_data)
    assert 0


# @pytest.mark.post_deployment
# def test_get_schema():
#     """Test API to get particular schema"""
#     schema_str = "xyz"
#     response = httpx.get(
#         f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/schemas/{schema_str}"
#     )

#     response_data = response.json()
#     print(response_data)
#     assert 0
