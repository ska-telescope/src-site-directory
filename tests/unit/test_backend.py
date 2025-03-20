import json
from pathlib import Path

import mongomock
import pytest

from ska_src_site_capabilities_api.db.backend import MongoBackend


@pytest.fixture(scope="module")
def dummy_nodes():
    """Fixture to return nodes json."""
    with Path("etc/init/nodes.json").open("r") as nodes_file:
        return json.load(nodes_file)


@pytest.fixture(scope="module")
def dummy_nodes_archived():
    """Fixture to return nodes_archived json."""
    with Path("etc/init/nodes.json").open("r") as nodes_file:
        return json.load(nodes_file)


@pytest.fixture(scope="module")
def mock_backend(mock_client, mock_db, dummy_nodes, dummy_nodes_archived):
    """Fixture that returns a mocked backend with prepopulated data."""
    if mock_db["nodes"].count_documents({}) == 0:
        mock_db["nodes"].insert_many(dummy_nodes)
    if mock_db["nodes_archived"].count_documents({}) == 0:
        mock_db["nodes_archived"].insert_many(dummy_nodes_archived)
    return MongoBackend(client=mock_client, mongo_database="test")


@pytest.fixture(scope="module")
def mock_client():
    return mongomock.MongoClient()


@pytest.fixture(scope="module")
def mock_db(mock_client):
    return mock_client["test"]


@pytest.mark.parametrize("id,expected_exists", [("db1d3ee3-74e4-48aa-afaf-8d7709a2f57c", True), ("0", False)])
def test_get_compute(id, expected_exists, mock_backend):
    # Call the get_compute function
    result = mock_backend.get_compute(compute_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.parametrize("name,expected_exists", [("SKAOSRC", True), ("A", False)])
def test_get_node(name, expected_exists, mock_backend):
    # Call the get_node function
    result = mock_backend.get_node(node_name=name, node_version="latest")
    if expected_exists:
        assert result.get("name") == name
    else:
        assert not result


@pytest.mark.parametrize("id,expected_exists", [("cd200c23-60f4-49c0-a987-3e11f06a4c8c", True), ("0", False)])
def test_get_service(id, expected_exists, mock_backend):
    # Call the get_service function
    result = mock_backend.get_service(service_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.parametrize("id,expected_exists", [("8b008348-0d8d-4505-a625-1e6e8df56e8a", True), ("0", False)])
def test_get_site(id, expected_exists, mock_backend):
    # Call the get_site function
    result = mock_backend.get_site(site_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.parametrize(
    "node_name,site_name,expected_exists", [("SKAOSRC", "SKAOSRC_A", True), ("SKAOSRC", "SKAOSRC_C", False)]
)
def test_get_site_by_names(node_name, site_name, expected_exists, mock_backend):
    # Call the get_site_by_names function
    result = mock_backend.get_site_from_names(node_name=node_name, site_name=site_name, node_version="latest")
    if expected_exists:
        assert result.get("parent_node_name") == node_name
        assert result.get("name") == site_name
    else:
        assert not result


@pytest.mark.parametrize("id,expected_exists", [("180f2f39-4548-4f11-80b1-7471564e5c05", True), ("0", False)])
def test_get_storage(id, expected_exists, mock_backend):
    # Call the get_storage function
    result = mock_backend.get_storage(storage_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.parametrize("id,expected_exists", [("f62199c3-62ad-44ee-a6e0-dd34e891d423", True), ("0", False)])
def test_get_storage_area(id, expected_exists, mock_backend):
    # Call the get_storage_area function
    result = mock_backend.get_storage_area(storage_area_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


def test_list_compute_with_node_name_filter(mock_backend):
    # Test the list_compute function with node_name filter
    compute = mock_backend.list_compute(only_node_names="SKAOSRC")
    assert len(compute) == 2


@pytest.mark.unit_test
def test_list_compute_with_site_name_filter(mock_backend):
    # Test the list_compute function with site_name filter
    compute = mock_backend.list_compute(only_site_names="SKAOSRC_B")
    assert len(compute) == 1


def test_list_nodes(mock_backend):
    # Test the list_nodes function
    sites = mock_backend.list_nodes()
    assert len(sites) == 1


def test_list_services_with_node_name_filter(mock_backend):
    # Test the list_services function with node_name filter
    services = mock_backend.list_services(only_node_names="SKAOSRC")
    assert len(services) == 7


@pytest.mark.unit_test
def test_list_services_with_site_name_filter(mock_backend):
    # Test the list_services function with site_name filter
    services = mock_backend.list_services(only_site_names="SKAOSRC_B")
    assert len(services) == 6


def test_list_services_with_service_types_filter(mock_backend):
    # Test the list_services function with service_types filter
    services = mock_backend.list_services(only_service_types="jupyterhub")
    assert len(services) == 3
    assert all(s.get("type") == "jupyterhub" for s in services)


def test_list_sites(mock_backend):
    # Test the list_sites function
    sites = mock_backend.list_sites()
    assert len(sites) == 2


def test_list_storages_with_node_name_filter(mock_backend):
    # Test the list_storages function with node_name filter
    storages = mock_backend.list_storages(only_node_names="SKAOSRC")
    assert len(storages) == 2


def test_list_storages_with_site_name_filter(mock_backend):
    # Test the list_storages function with site_name filter
    storages = mock_backend.list_storages(only_site_names="SKAOSRC_B")
    assert len(storages) == 1


def test_list_storage_areas_with_node_name_filter(mock_backend):
    # Test the list_storage_areas function with node_name filter
    storage_areas = mock_backend.list_storage_areas(only_node_names="SKAOSRC")
    assert len(storage_areas) == 3


def test_list_storage_areas_with_site_name_filter(mock_backend):
    # Test the list_storage_areas function with site_name filter
    storage_areas = mock_backend.list_storage_areas(only_site_names="SKAOSRC_B")
    assert len(storage_areas) == 1
