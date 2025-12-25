"""
Configuration and fixtures for component tests.
"""

import json
import logging
import os
from pathlib import Path

import httpx
import pytest

logger = logging.getLogger(__name__)

# Determine API URL - support both local and Kubernetes environments
KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")

if KUBE_NAMESPACE and CLUSTER_DOMAIN:
    BASE_API_URL = "http://core.{}.svc.{}:8080/v1".format(KUBE_NAMESPACE, CLUSTER_DOMAIN)
else:
    # Default to localhost for local development
    BASE_API_URL = os.getenv("API_URL", "http://localhost:8080/v1")

DISABLE_AUTHENTICATION = os.getenv("DISABLE_AUTHENTICATION") == "yes"


def get_api_url() -> str:
    """Get the base API URL for component tests."""
    return BASE_API_URL


def send_post_request(url: str, json_body: dict, headers: dict = None) -> httpx.Response:
    """Send POST request with JSON body."""
    if headers is None:
        headers = {"Content-Type": "application/json"}
    if DISABLE_AUTHENTICATION:
        # No auth header needed
        pass
    else:
        # For authenticated requests, you would add Bearer token here
        # token = os.getenv("SITE_CAPABILITIES_TOKEN")
        # if token:
        #     headers["Authorization"] = f"Bearer {token}"
        pass

    response = httpx.post(url, json=json_body, headers=headers, timeout=30)
    logger.info("POST %s -> %s", url, response.status_code)
    return response


def send_get_request(url: str, headers: dict = None) -> httpx.Response:
    """Send GET request."""
    if headers is None:
        headers = {}
    if not DISABLE_AUTHENTICATION:
        # For authenticated requests, you would add Bearer token here
        # token = os.getenv("SITE_CAPABILITIES_TOKEN")
        # if token:
        #     headers["Authorization"] = f"Bearer {token}"
        pass

    response = httpx.get(url, headers=headers, timeout=30)
    logger.info("GET %s -> %s", url, response.status_code)
    return response


def send_delete_request(url: str, headers: dict = None) -> httpx.Response:
    """Send DELETE request."""
    if headers is None:
        headers = {}
    if not DISABLE_AUTHENTICATION:
        # For authenticated requests, you would add Bearer token here
        # token = os.getenv("SITE_CAPABILITIES_TOKEN")
        # if token:
        #     headers["Authorization"] = f"Bearer {token}"
        pass

    response = httpx.delete(url, headers=headers, timeout=30)
    logger.info("DELETE %s -> %s", url, response.status_code)
    return response


@pytest.fixture(scope="module")
def nodes_data():
    """Load nodes data from JSON file."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "component"
    nodes_file = assets_dir / "nodes.json"
    with nodes_file.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def load_nodes_data(nodes_data):
    """Load nodes data into the API before running component tests."""
    api_url = get_api_url()
    nodes_url = f"{api_url}/nodes"

    logger.info("Loading nodes data into API at %s", nodes_url)

    # First, try to delete existing nodes to start fresh
    for node in nodes_data:
        node_name = node.get("name")
        if node_name:
            delete_url = f"{nodes_url}/{node_name}"
            try:
                send_delete_request(delete_url)
                logger.info("Deleted existing node: %s", node_name)
            except Exception as e:
                logger.debug("Could not delete node %s (may not exist): %s", node_name, e)

    # Load each node
    loaded_nodes = []
    for node in nodes_data:
        node_name = node.get("name")
        if not node_name:
            logger.warning("Skipping node without name: %s", node)
            continue

        try:
            # Check if node already exists
            get_url = f"{nodes_url}/{node_name}"
            get_response = send_get_request(get_url)
            if get_response.status_code == 200:
                logger.info("Node %s already exists, skipping creation", node_name)
                loaded_nodes.append(node_name)
                continue

            # Create the node
            post_response = send_post_request(nodes_url, node)
            if post_response.status_code in (200, 201):
                logger.info("Successfully loaded node: %s", node_name)
                loaded_nodes.append(node_name)
            else:
                logger.error(
                    "Failed to load node %s: %s - %s",
                    node_name,
                    post_response.status_code,
                    post_response.text,
                )
        except Exception as e:
            logger.error("Error loading node %s: %s", node_name, e)

    logger.info("Loaded %d nodes: %s", len(loaded_nodes), loaded_nodes)
    yield loaded_nodes

    # Optional: Cleanup after tests (commented out to preserve data for debugging)
    # for node_name in loaded_nodes:
    #     try:
    #         delete_url = f"{nodes_url}/{node_name}"
    #         send_delete_request(delete_url)
    #         logger.info("Cleaned up node: %s", node_name)
    #     except Exception as e:
    #         logger.warning("Could not cleanup node %s: %s", node_name, e)
