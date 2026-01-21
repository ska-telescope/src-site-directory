"""
A module for component tests related to queues.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_queues(load_nodes_data):
    """Test to list all queues"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/queues")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got services data
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 401


@pytest.mark.component
@pytest.mark.parametrize(
    "node_names,site_names,include_inactive,result_count",
    [(None, None, False, 3), (None, None, True, 6), ("TEST", "TEST_A", True, 5), ("TEST", "TEST_A", False, 2), ("TEST", "TEST_B", True, 1)],
)
def test_get_queues(node_names, site_names, include_inactive, result_count):
    """Test to get queues with various filters"""
    api_url = get_api_url()
    base_url = f"{api_url}/queues?"
    if node_names:
        base_url += f"node_names={node_names}&"
    if site_names:
        base_url += f"site_names={site_names}&"
    base_url += f"include_inactive={str(include_inactive).lower()}"

    response = httpx.get(base_url)  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got services data
        queues = response.json()
        assert len(queues) == result_count
    else:
        assert response.status_code == 401


@pytest.mark.component
@pytest.mark.parametrize("queue_id,expected_exists", [("a1b2c3d4-e5f6-4789-abcd-1234567890ab", True), ("INVALID_QUEUE_ID", False)])
def test_get_queue_by_id(queue_id, expected_exists):
    """Test to get a queue by its ID"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/queues/{queue_id}")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got services data
        data = response.json()
        if expected_exists:
            assert response.status_code == 200
            assert data.get("id") == queue_id
        else:
            assert response.status_code == 404
    else:
        assert response.status_code == 401
