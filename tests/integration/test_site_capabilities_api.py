"""Integration tests for Site Capabilities API."""

import json
import logging
import random
from pathlib import Path

import pytest
import requests

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


BASE_API_URL = "http://scapi-core:8080/v1"
#BASE_API_URL = "http://localhost:8080/v1"


@pytest.fixture(scope="module")
def compute_storm2():
    """Fixture to return storm2 compute json."""
    with Path("tests/assets/integration/compute_storm2.json").open("r") as compute_file:
        return json.load(compute_file)


@pytest.fixture(scope="module")
def node_storm1():
    """Fixture to return storm1 node json."""
    with Path("tests/assets/integration/node_storm1.json").open("r") as node_file:
        return json.load(node_file)


@pytest.fixture(scope="module")
def node_storm2():
    """Fixture to return storm2 node json."""
    with Path("tests/assets/integration/node_storm2.json").open("r") as node_file:
        return json.load(node_file)


@pytest.fixture(scope="module")
def site_capabilities_token():
    """Read and return the site capabilities token from file."""
    with open("/tmp/site_capabilities_token.txt", encoding="utf-8") as f:
        token = f.read().strip()
    return token


def send_get_request(url, token):
    """Send GET request with authorization token and return JSON response."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=30)
    logger.info("Status Code: %s", response.status_code)
    try:
        response.json()
        return response
    except ValueError:
        logger.warning("Response not JSON. Raw text:")
        logger.warning(response.text)
        return None


def send_post_request(url, token, json_body):
    """Send POST request with authorization token and JSON body."""
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json", "Content-Type": "application/json"}
    logger.info("POST %s -> sending payload:", url)
    response = requests.post(url, headers=headers, json=json_body, timeout=30)
    logger.info("POST %s -> %s", url, response.status_code)
    try:
        logger.info("Response: %s", json.dumps(response.json(), indent=2))
    except (ValueError, json.JSONDecodeError):
        logger.warning("Response not JSON. Raw text:")
        logger.warning(response.text)
    return response


class TestNode:
    @staticmethod
    def get_compute_url(node_name: str) -> str:
        return f"{BASE_API_URL}/compute?node_names={node_name}"

    @staticmethod
    def get_nodes_url() -> str:
        return f"{BASE_API_URL}/nodes"

    @staticmethod
    def get_node_url(node_name: str) -> str:
        return f"{TestNode.get_nodes_url()}/{node_name}"

    @staticmethod
    def get_storage_areas_url(node_name: str) -> str:
        return f"{BASE_API_URL}/storage-areas?node_names={node_name}"

    def _create_node(self, node_name: str, site_capabilities_token: str, node_payload: dict) -> dict:
        """Check existence of node & create if needed."""
        try:
            existing = send_get_request(self.get_node_url(node_name), token=site_capabilities_token).json()
            if existing and existing.get("name") == node_name:
                logger.info("%s already exists, skipping creation.", node_name)
                return existing
        except (requests.exceptions.RequestException, ValueError):
            logger.info("%s does not exist or error occurred, proceeding to create.", node_name)

        post_response = send_post_request(self.get_nodes_url(), token=site_capabilities_token, json_body=node_payload)
        if not post_response:
            logger.warning("POST /nodes returned no JSON, assuming creation succeeded.")
        return post_response

    def _delete_node(self, node_name: str, site_capabilities_token: str):
        """Delete existing node."""
        return send_post_request(self.get_node_url(node_name), token=site_capabilities_token, json_body={})

    def _edit_node(self, node_name: str, site_capabilities_token: str, node_payload: dict) -> dict:
        """Edit a node."""
        post_response = send_post_request(self.get_node_url(node_name), token=site_capabilities_token, json_body=node_payload)
        if not post_response:
            logger.warning(f"POST /nodes/{node_name} returned no JSON, assuming edit succeeded.")
        return post_response

    def _get_compute(self, node_name: str, site_capabilities_token: str):
        """Get a compute."""
        return send_get_request(self.get_compute_url(node_name), token=site_capabilities_token)

    def _get_node(self, node_name: str, site_capabilities_token: str):
        """Get a node."""
        return send_get_request(self.get_node_url(node_name), token=site_capabilities_token)

    def _get_storage_areas(self, node_name: str, site_capabilities_token: str):
        """Get a storage area."""
        return send_get_request(self.get_storage_areas_url(node_name), token=site_capabilities_token)

    @staticmethod
    def _strip_keys_for_comparison(obj, keys=["id", "created_at", "created_by_username", "version"]):
        """Recursively remove specified keys from a dictionary or list for comparison."""
        if isinstance(obj, dict):
            return {k: TestNode._strip_keys_for_comparison(v, keys) for k, v in obj.items() if k not in keys}
        elif isinstance(obj, list):
            return [TestNode._strip_keys_for_comparison(item, keys) for item in obj]
        return obj


@pytest.mark.integration
class TestNodeAdd(TestNode):
    @pytest.mark.order(1)
    def test_delete_node_STORM1(self, site_capabilities_token):
        response = self._delete_node(node_name="STORM1", site_capabilities_token=site_capabilities_token)
        assert response.status_code == 200

    @pytest.mark.order(2)
    def test_delete_node_STORM2(self, site_capabilities_token):
        response = self._delete_node(node_name="STORM2", site_capabilities_token=site_capabilities_token)
        assert response.status_code == 200

    @pytest.mark.order(3)
    def test_create_node_STORM1(self, site_capabilities_token, node_storm1):
        create_response = self._create_node(node_name="STORM1", site_capabilities_token=site_capabilities_token, node_payload=node_storm1)
        assert create_response.status_code == 200

        # Verify
        get_response = self._get_node(node_name="STORM1", site_capabilities_token=site_capabilities_token)
        assert get_response.status_code == 200
        assert self._strip_keys_for_comparison(get_response.json()) == self._strip_keys_for_comparison(node_storm1)  ## in == out

    @pytest.mark.order(4)
    def test_create_node_STORM2(self, site_capabilities_token, node_storm2):
        create_response = self._create_node(node_name="STORM2", site_capabilities_token=site_capabilities_token, node_payload=node_storm2)
        assert create_response.status_code == 200

        # Verify
        get_response = self._get_node(node_name="STORM2", site_capabilities_token=site_capabilities_token)
        assert get_response.status_code == 200
        assert self._strip_keys_for_comparison(get_response.json()) == self._strip_keys_for_comparison(node_storm2)  ## in == out


@pytest.mark.integration
class TestNodeEdit(TestNode):
    @pytest.mark.order(5)
    def test_create_new_compute_STORM2(self, site_capabilities_token, compute_storm2):
        # Get the current storage areas json for STORM2
        get_storage_areas_response = self._get_storage_areas(node_name="STORM2", site_capabilities_token=site_capabilities_token)
        assert get_storage_areas_response.status_code == 200
        storage_areas_storm2 = get_storage_areas_response.json()

        # Populate compute_storm2 asset with associated_storage_area_ids
        rse_storage_area_id = next((area for area in storage_areas_storm2 if area.get("type") == "rse"), {}).get("id", None)
        ingest_area_id = next((area for area in storage_areas_storm2 if area.get("type") == "ingest"), {}).get("id", None)
        next((svc for svc in compute_storm2["associated_local_services"] if svc["type"] == "prepare_data"), {})["associated_storage_area_id"] = rse_storage_area_id
        next((svc for svc in compute_storm2["associated_local_services"] if svc["type"] == "ingest"), {})["associated_storage_area_id"] = ingest_area_id

        # Get the full storm2 node json
        get_node_response = self._get_node(node_name="STORM2", site_capabilities_token=site_capabilities_token)
        assert get_node_response.status_code == 200
        node_storm2 = get_node_response.json()

        # Attach this compute block to the existing STORM2 node json
        next(site for site in node_storm2["sites"] if site["name"] == "STORM2")["compute"] = [compute_storm2]
        response = self._edit_node(node_name="STORM2", site_capabilities_token=site_capabilities_token, node_payload=node_storm2)
        assert response.status_code == 200

        # Verify
        get_node_response = self._get_node(node_name="STORM2", site_capabilities_token=site_capabilities_token)
        assert get_node_response.status_code == 200
        node_storm2 = get_node_response.json()
        first_compute_element_storm2 = next(
            (site.get("compute", [])[0] for site in node_storm2.get("sites", []) if site.get("name") == "STORM2" and site.get("compute")),
            {}
        )
        assert self._strip_keys_for_comparison(first_compute_element_storm2) == self._strip_keys_for_comparison(compute_storm2)    # in == out 
