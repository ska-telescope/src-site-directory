"""Integration tests for Site Capabilities API."""

import logging
import os

import pytest
import requests

from ska_src_auth_api.client.integration import AuthenticationIntegrationClient
from ska_src_site_capabilities_api.client.integration import SiteCapabilitiesIntegrationClient

logger = logging.getLogger(__name__)

AAPI_URL = os.getenv("AAPI_URL", "http://aapi.test")
AAPI_SERVICE_VERSION = os.getenv("AAPI_SERVICE_VERSION", "v1")
IAM_TEST_ADMIN_USERNAME = os.getenv("IAM_TEST_ADMIN_USERNAME", "admin")
IAM_TEST_ADMIN_PASSWORD = os.getenv("IAM_TEST_ADMIN_PASSWORD", "adminpassword")
SCAPI_URL = os.getenv("SCAPI_URL", "http://scapi-core:8080")
SCAPI_SERVICE_VERSION = os.getenv("SCAPI_SERVICE_VERSION", "v1")

AAPI_SERVICE_URL = f"{AAPI_URL}/{AAPI_SERVICE_VERSION}"
SCAPI_SERVICE_URL = f"{SCAPI_URL}/{SCAPI_SERVICE_VERSION}"
NODE1_SITE1_STORAGE_ID = "test-ephemeral-node1-site1-storage"
NODE1_SITE1_STORAGE_AREA_DET_ID = "test-ephemeral-node1-site1-storage-area-det"
NODE1_SITE1_STORAGE_AREA_NONDET_ID = "test-ephemeral-node1-site1-storage-area-nondet"
NODE2_SITE2_STORAGE_ID = "test-ephemeral-node2-site2-storage"
NODE2_SITE2_STORAGE_AREA_DET_ID = "test-ephemeral-node2-site2-storage-area-det"
NODE2_SITE2_STORAGE_AREA_NONDET_ID = "test-ephemeral-node2-site2-storage-area-nondet"
NODE2_SITE2_STORAGE_AREA_INGEST_ID = "test-ephemeral-node2-site2-storage-area-ingest"
NODE2_SITE2_COMPUTE_ID = "test-ephemeral-node2-site2-compute"
NODE2_SITE2_SERVICE_PREPARE_DATA_ID = "test-ephemeral-node2-site2-service-prepare-data"
NODE2_SITE2_SERVICE_INGEST_ID = "test-ephemeral-node2-site2-service-ingest"
NODE2_SITE2_SERVICE_PRODUCT_STREAMER_ID = "test-ephemeral-node2-site2-service-product-streamer"


@pytest.fixture(scope="session")
def site_capabilities_token() -> str:
    """Obtain a SCAPI-scoped token via the AAPI device flow."""
    with AuthenticationIntegrationClient(AAPI_SERVICE_URL, IAM_TEST_ADMIN_USERNAME, IAM_TEST_ADMIN_PASSWORD) as flow:
        flow.authorize()
        access_token = flow.fetch_token()["token"]["access_token"]
        response = flow.exchange_token(service="site-capabilities-api", version="latest", try_use_cache=True, access_token=access_token)
        return response.json()["access_token"]


@pytest.fixture(scope="session")
def scapi_client(site_capabilities_token) -> SiteCapabilitiesIntegrationClient:
    """A SiteCapabilitiesIntegrationClient authenticated with a SCAPI-scoped token."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {site_capabilities_token}"})
    return SiteCapabilitiesIntegrationClient(api_url=SCAPI_SERVICE_URL, session=session)


@pytest.mark.integration
class TestNodeAdd:
    @pytest.mark.order(1)
    @pytest.mark.parametrize("node", ["STORM1", "STORM2"])
    def test_delete_node(self, scapi_client, node):
        scapi_client.deregister_node(node)

    @pytest.mark.order(2)
    @pytest.mark.parametrize(
        ("node", "description", "storage_id", "host", "areas"),
        [
            (
                "STORM1",
                "Storm 1",
                NODE1_SITE1_STORAGE_ID,
                "storm1.test",
                [
                    (NODE1_SITE1_STORAGE_AREA_DET_ID, "STORM1", "/deterministic", "rse"),
                    (NODE1_SITE1_STORAGE_AREA_NONDET_ID, "STORM1_NONDET", "/nondeterministic", "rse"),
                ],
            ),
            (
                "STORM2",
                "Storm 2",
                NODE2_SITE2_STORAGE_ID,
                "storm2.test",
                [
                    (NODE2_SITE2_STORAGE_AREA_DET_ID, "STORM2", "/deterministic", "rse"),
                    (NODE2_SITE2_STORAGE_AREA_NONDET_ID, "STORM2_NONDET", "/nondeterministic", "rse"),
                    (NODE2_SITE2_STORAGE_AREA_INGEST_ID, "STORM2_INGEST", "/ingest/staging", "ingest"),
                ],
            ),
        ],
        ids=["storm1", "storm2"],
    )
    def test_create_node(self, scapi_client, node, description, storage_id, host, areas):
        # Step 1: register node, site, storage, and its storage areas
        scapi_client.register_node(node, description=description)
        scapi_client.register_site(node, node, description=description, contact="dms@skao.int")
        scapi_client.register_storage(node, node, storage_id, name=node, host=host)
        for area_id, area_name, relative_path, area_type in areas:
            scapi_client.register_storage_area(node, storage_id, area_id, name=area_name, relative_path=relative_path, area_type=area_type)

        # Step 2: verify the registration round-trips correctly
        node_json = scapi_client.get_node_version(node).json()
        site = next(s for s in node_json["sites"] if s["name"] == node)
        storage = next(s for s in site["storages"] if s["id"] == storage_id)
        assert storage["host"] == host
        assert {a["id"] for a in storage["areas"]} == {area_id for area_id, *_ in areas}


@pytest.mark.integration
class TestNodeEdit:
    @pytest.mark.order(5)
    def test_create_new_compute_storm2(self, scapi_client):
        # Step 1: look up the storage areas created in TestNodeAdd, to associate with the new services
        get_storage_areas_response = scapi_client.list_storage_areas(node_names=["STORM2"])
        assert get_storage_areas_response.status_code == 200
        storage_areas_storm2 = get_storage_areas_response.json()
        rse_area_id = next(area["id"] for area in storage_areas_storm2 if area["type"] == "rse" and area["name"] == "STORM2")
        ingest_area_id = next(area["id"] for area in storage_areas_storm2 if area["type"] == "ingest")

        # Step 2: register compute and its associated services
        scapi_client.register_compute("STORM2", "STORM2", NODE2_SITE2_COMPUTE_ID, hardware_type="container")
        scapi_client.register_service(
            "STORM2",
            NODE2_SITE2_COMPUTE_ID,
            NODE2_SITE2_SERVICE_PREPARE_DATA_ID,
            service_type="prepare_data",
            host="gatekeeper.test",
            port=443,
            prefix="https",
            path="dpapi/v1/stage",
            other_attributes={"supported_approaches": ["copy", "symlink", "cavern"], "default_approach": "copy"},
            storage_area_id=rse_area_id,
        )
        scapi_client.register_service(
            "STORM2",
            NODE2_SITE2_COMPUTE_ID,
            NODE2_SITE2_SERVICE_INGEST_ID,
            service_type="ingest",
            version="1.0.0",
            storage_area_id=ingest_area_id,
        )
        scapi_client.register_service(
            "STORM2",
            NODE2_SITE2_COMPUTE_ID,
            NODE2_SITE2_SERVICE_PRODUCT_STREAMER_ID,
            service_type="product_streamer",
            host="psapi.test",
            port=443,
            prefix="https",
            path="v1/data/product",
        )

        # Step 3: verify the registration round-trips correctly
        node = scapi_client.get_node_version("STORM2").json()
        site = next(s for s in node["sites"] if s["name"] == "STORM2")
        compute = next(c for c in site["compute"] if c["id"] == NODE2_SITE2_COMPUTE_ID)
        services_by_type = {s["type"]: s for s in compute["associated_local_services"]}
        assert services_by_type["prepare_data"]["host"] == "gatekeeper.test"
        assert services_by_type["prepare_data"]["associated_storage_area_id"] == rse_area_id
        assert services_by_type["ingest"]["associated_storage_area_id"] == ingest_area_id
        assert services_by_type["product_streamer"]["host"] == "psapi.test"


@pytest.mark.integration
class TestNodeCleanup:
    @pytest.mark.order(6)
    @pytest.mark.parametrize("node", ["STORM1", "STORM2"])
    def test_delete_node(self, scapi_client, node):
        scapi_client.deregister_node(node)
