"""
A module for component tests related to downtime metrics.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_get_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_downtime_metrics(load_nodes_data):
    """Test to get downtime metrics"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/downtime-metrics")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # Verify we got downtime metrics data
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_downtime_metrics_filter_by_node_names(load_nodes_data):
    """Test to get downtime metrics filtered by node names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/downtime-metrics?node_names={node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code == 403
