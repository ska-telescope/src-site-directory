"""Integration tests for Site Capabilities API."""
import json
import logging
import random

import pytest
import requests

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        data = response.json()
        logger.info("Response JSON:")
        logger.info(json.dumps(data, indent=2))

        # If the response is empty, treat it as no result
        if not data or not isinstance(data, dict):
            return None

        return data
    except ValueError:
        logger.warning("Response not JSON. Raw text:")
        logger.warning(response.text)
        return None


def send_post_request(url, token, json_body):
    """Send POST request with authorization token and JSON body."""
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json", "Content-Type": "application/json"}
    logger.info("POST %s -> sending payload:", url)
    logger.info(json.dumps(json_body, indent=2))

    response = requests.post(url, headers=headers, json=json_body, timeout=30)

    logger.info("POST %s -> %s", url, response.status_code)
    try:
        logger.info("Response: %s", json.dumps(response.json(), indent=2))
    except (ValueError, requests.exceptions.JSONDecodeError):
        logger.warning("Response not JSON. Raw text:")
        logger.warning(response.text)

    assert response.status_code in [200, 201], f"POST to {url} failed with status {response.status_code}"
    return response


@pytest.mark.integration
def test_post_and_get_node_storm1(site_capabilities_token):
    """Test creating and retrieving STORM1 node via API."""
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)
    # Delete STORM1 node if it exists
    delete_url = "http://scapi-core:8080/v1/nodes/STORM1"
    delete_response = send_post_request(delete_url, site_capabilities_token, {})
    # delete_response = requests.delete(delete_url, headers=headers)
    if delete_response.status_code == 200:
        logger.info("STORM1 node deleted successfully before test.")
    elif delete_response.status_code == 404:
        logger.info("STORM1 node did not exist before test.")
    else:
        logger.warning("Unexpected DELETE status: %s", delete_response.status_code)

    node_payload = {
        "name": "STORM1",
        "description": "Storm 1",
        "comments": "",
        "version": 1,
        "sites": [
            {
                "name": "STORM1",
                "comments": "",
                "id": "to be assigned",
                "description": "Storm 1",
                "country": "SKAO",
                "primary_contact_email": "michele.delliveneri@skao.int",
                "secondary_contact_email": "",
                "storages": [
                    {
                        "id": "to be assigned",
                        "host": "storm1.local",
                        "base_path": "/sa",
                        "srm": "storm",
                        "device_type": "",
                        "size_in_terabytes": 0.01,
                        "name": "STORM1",
                        "supported_protocols": [{"prefix": "https", "port": 443}],
                        "areas": [
                            {
                                "id": "to be assigned",
                                "type": "rse",
                                "relative_path": "/",
                                "name": "STORM1",
                                "downtime": [],
                                "other_attributes": "",
                                "is_force_disabled": False,
                            }
                        ],
                        "downtime": [],
                        "is_force_disabled": False,
                    }
                ],
                "latitude": latitude,
                "longitude": longitude,
                "id": "to be assigned",
                "downtime": [],
                "is_force_disabled": False,
                "other_attributes": "",
            }
        ],
    }

    # Check if the node already exists
    get_url = "http://scapi-core:8080/v1/nodes/STORM1"
    try:
        response = send_get_request(get_url, site_capabilities_token)
        if response and response.get("name") == "STORM1":
            logger.info("STORM1 already exists, skipping creation.")
            return
    except (requests.exceptions.RequestException, ValueError):
        logger.info("STORM1 does not exist or error occurred, proceeding to create.")

    # Send POST to create node
    post_url = "http://scapi-core:8080/v1/nodes"
    post_response = send_post_request(post_url, site_capabilities_token, node_payload)

    if not post_response:
        logger.warning("POST /nodes returned no JSON, assuming creation succeeded.")

    # Validate with GET
    get_result = send_get_request(get_url, site_capabilities_token)
    assert get_result is not None, "Expected non-empty response"
    assert get_result.get("name") == "STORM1", f"Unexpected name: {get_result}"
    assert get_result.get("sites", [{}])[0].get("name") == "STORM1", f"Unexpected sites data: {get_result.get('sites')}"


@pytest.mark.integration
def test_post_and_get_node_storm2(site_capabilities_token):
    """Test creating and retrieving STORM2 node with compute services via API."""
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)
    # Delete STORM2 node if it exists
    delete_url = "http://scapi-core:8080/v1/nodes/STORM2"
    delete_response = send_post_request(delete_url, site_capabilities_token, {})
    if delete_response.status_code == 200:
        logger.info("STORM2 node deleted successfully before test.")
    elif delete_response.status_code == 404:
        logger.info("STORM2 node did not exist before test.")
    else:
        logger.warning("Unexpected DELETE status: %s", delete_response.status_code)

    node_payload = {
        "name": "STORM2",
        "description": "Storm 2",
        "comments": "",
        "version": 1,
        "sites": [
            {
                "name": "STORM2",
                "comments": "",
                "id": "to be assigned",
                "description": "Storm 2",
                "country": "SKAO",
                "primary_contact_email": "michele.delliveneri@skao.int",
                "secondary_contact_email": "",
                "storages": [
                    {
                        "id": "to be assigned",
                        "host": "storm2.local",
                        "base_path": "/sa",
                        "srm": "storm",
                        "device_type": "",
                        "size_in_terabytes": 0.01,
                        "name": "STORM2",
                        "supported_protocols": [{"prefix": "https", "port": 443}],
                        "areas": [
                            {
                                "id": "to be assigned",
                                "type": "rse",
                                "relative_path": "/",
                                "name": "STORM2",
                                "downtime": [],
                                "other_attributes": "",
                                "is_force_disabled": False,
                            },
                            {
                                "id": "to be assigned",
                                "type": "ingest",
                                "relative_path": "/tmp/ingest/staging",
                                "other_attributes": {},
                                "downtime": [],
                                "is_force_disabled": False,
                            },
                        ],
                        "downtime": [],
                        "is_force_disabled": False,
                    }
                ],
                "latitude": latitude,
                "longitude": longitude,
                "id": "to be assigned",
                "downtime": [],
                "is_force_disabled": False,
                "other_attributes": "",
            }
        ],
    }

    # Check if the node already exists
    get_url = "http://scapi-core:8080/v1/nodes/STORM2"
    try:
        response = send_get_request(get_url, site_capabilities_token)
        if response and response.get("name") == "STORM2":
            logger.info("STORM2 already exists, skipping creation.")
            return
    except (requests.exceptions.RequestException, ValueError):
        logger.info("STORM2 does not exist or error occurred, proceeding to create.")

    # Send POST to create node
    post_url = "http://scapi-core:8080/v1/nodes"
    post_response = send_post_request(post_url, site_capabilities_token, node_payload)

    if not post_response:
        logger.warning("POST /nodes returned no JSON, assuming creation succeeded.")

    # Get the storage area id
    get_url = "http://scapi-core:8080/v1/nodes/STORM2"
    response = send_get_request(get_url, site_capabilities_token)

    assert response is not None, "Failed to fetch existing node"
    storage_area_id = response.get("sites", [{}])[0].get("storages", [{}])[0].get("areas", [{}])[0].get("id")
    ingest_area_id = response.get("sites", [{}])[0].get("storages", [{}])[0].get("areas", [{}])[1].get("id")
    response["sites"][0]["compute"] = [
        {
            "id": "to be assigned",
            "hardware_type": "container",
            "description": "",
            "associated_local_services": [
                {
                    "id": "to be assigned",
                    "type": "prepare_data",
                    "prefix": "http",
                    "host": "dp-core",
                    "port": 8000,
                    "path": "/",
                    "other_attributes": {},
                    "is_mandatory": False,
                    "downtime": [],
                    "is_force_disabled": False,
                    "associated_storage_area_id": storage_area_id,
                },
                {
                    "id": "to be assigned",
                    "type": "ingest",
                    "version": "1.0.0",
                    "associated_storage_area_id": ingest_area_id,
                    "other_attributes": {},
                    "is_mandatory": False,
                    "is_force_disabled": False,
                },
            ],
            "hardware_capabilities": [],
            "downtime": [],
            "is_force_disabled": False,
        }
    ]
    # Send POST to create compute
    post_url = "http://scapi-core:8080/v1/nodes/STORM2"
    post_response = send_post_request(post_url, site_capabilities_token, response)

    if not post_response:
        logger.warning("POST /nodes/STORM2/compute returned no JSON, assuming creation succeeded.")

    # Validate with GET
    get_result = send_get_request(get_url, site_capabilities_token)
    assert get_result is not None, "Expected non-empty response"
    assert get_result.get("name") == "STORM2", f"Unexpected name: {get_result}"
    assert get_result.get("sites", [{}])[0].get("name") == "STORM2", f"Unexpected sites data: {get_result.get('sites')}"
