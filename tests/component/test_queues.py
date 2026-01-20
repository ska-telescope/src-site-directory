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


