"""Integration tests for Site Capabilities API."""

import json
import logging
from pathlib import Path

import pytest
from ska_test_utils.scapi import create_node, delete_node, edit_node, get_node, get_storage_areas

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="module")
def compute_storm2():
    """Fixture to return storm2 compute json."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "integration"
    with (assets_dir / "compute_storm2.json").open("r", encoding="utf-8") as compute_file:
        return json.load(compute_file)


@pytest.fixture(scope="module")
def node_storm1():
    """Fixture to return storm1 node json."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "integration"
    with (assets_dir / "node_storm1.json").open("r", encoding="utf-8") as node_file:
        return json.load(node_file)


@pytest.fixture(scope="module")
def node_storm2():
    """Fixture to return storm2 node json."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "integration"
    with (assets_dir / "node_storm2.json").open("r", encoding="utf-8") as node_file:
        return json.load(node_file)



def _strip_keys_for_comparison(obj, keys=None):
    """Recursively remove specified keys from a dictionary or list for comparison."""
    if keys is None:
        keys = ["id", "created_at", "created_by_username", "version"]
    if isinstance(obj, dict):
        return {k: _strip_keys_for_comparison(v, keys) for k, v in obj.items() if k not in keys}
    if isinstance(obj, list):
        return [_strip_keys_for_comparison(item, keys) for item in obj]
    return obj


@pytest.mark.integration
class TestNodeAdd:
    @pytest.mark.order(1)
    def test_delete_node_storm1(self, scapi_base_url, site_capabilities_token):
        response = delete_node(scapi_base_url, site_capabilities_token, "STORM1")
        assert response.status_code == 200

    @pytest.mark.order(2)
    def test_delete_node_storm2(self, scapi_base_url, site_capabilities_token):
        response = delete_node(scapi_base_url, site_capabilities_token, "STORM2")
        assert response.status_code == 200

    @pytest.mark.order(3)
    def test_create_node_storm1(self, scapi_base_url, site_capabilities_token, node_storm1):
        create_response = create_node(scapi_base_url, site_capabilities_token, node_storm1)
        assert create_response.status_code == 200

        get_response = get_node(scapi_base_url, site_capabilities_token, "STORM1")
        assert get_response.status_code == 200
        assert _strip_keys_for_comparison(get_response.json()) == _strip_keys_for_comparison(node_storm1)

    @pytest.mark.order(4)
    def test_create_node_storm2(self, scapi_base_url, site_capabilities_token, node_storm2):
        create_response = create_node(scapi_base_url, site_capabilities_token, node_storm2)
        assert create_response.status_code == 200

        get_response = get_node(scapi_base_url, site_capabilities_token, "STORM2")
        assert get_response.status_code == 200
        assert _strip_keys_for_comparison(get_response.json()) == _strip_keys_for_comparison(node_storm2)


@pytest.mark.integration
class TestNodeEdit:
    @pytest.mark.order(5)
    def test_create_new_compute_storm2(self, scapi_base_url, site_capabilities_token, compute_storm2):
        # Get the current storage areas for STORM2
        get_storage_areas_response = get_storage_areas(scapi_base_url, site_capabilities_token, "STORM2")
        assert get_storage_areas_response.status_code == 200
        storage_areas_storm2 = get_storage_areas_response.json()

        # Populate compute_storm2 asset with associated_storage_area_ids
        rse_storage_area_id = next((area for area in storage_areas_storm2 if area.get("type") == "rse"), {}).get("id", None)
        ingest_area_id = next((area for area in storage_areas_storm2 if area.get("type") == "ingest"), {}).get("id", None)
        next((svc for svc in compute_storm2["associated_local_services"] if svc["type"] == "prepare_data"), {})[
            "associated_storage_area_id"
        ] = rse_storage_area_id
        next((svc for svc in compute_storm2["associated_local_services"] if svc["type"] == "ingest"), {})[
            "associated_storage_area_id"
        ] = ingest_area_id

        # Get the full STORM2 node and attach the compute block
        get_node_response = get_node(scapi_base_url, site_capabilities_token, "STORM2")
        assert get_node_response.status_code == 200
        node_storm2 = get_node_response.json()

        next(site for site in node_storm2["sites"] if site["name"] == "STORM2")["compute"] = [compute_storm2]
        response = edit_node(scapi_base_url, site_capabilities_token, "STORM2", node_storm2)
        assert response.status_code == 200

        # Verify
        get_node_response = get_node(scapi_base_url, site_capabilities_token, "STORM2")
        assert get_node_response.status_code == 200
        node_storm2 = get_node_response.json()
        first_compute_element_storm2 = next(
            (site.get("compute", [])[0] for site in node_storm2.get("sites", []) if site.get("name") == "STORM2" and site.get("compute")), {}
        )
        assert _strip_keys_for_comparison(first_compute_element_storm2) == _strip_keys_for_comparison(compute_storm2)
