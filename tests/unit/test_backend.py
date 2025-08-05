import json
from pathlib import Path

import mongomock
import pytest

from ska_src_site_capabilities_api.backend.mongo import MongoBackend


@pytest.fixture(scope="module")
def dummy_nodes():
    """Fixture to return nodes json."""
    with Path("tests/assets/unit/nodes.json").open("r") as nodes_file:
        return json.load(nodes_file)


@pytest.fixture(scope="module")
def dummy_nodes_archived():
    """Fixture to return nodes_archived json."""
    with Path("tests/assets/unit/nodes.json").open("r") as nodes_file:
        return json.load(nodes_file)


@pytest.fixture(scope="function")
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


@pytest.mark.unit
def test_add_edit_node(mock_db, mock_backend):
    count_nodes = mock_db["nodes"].count_documents({})
    count_nodes_archived = mock_db["nodes_archived"].count_documents({})

    mock_backend.add_edit_node(mock_backend.get_node("TEST", "latest"), node_name="TEST")
    assert mock_db["nodes"].count_documents({}) == count_nodes
    assert mock_db["nodes_archived"].count_documents({}) == count_nodes_archived + 1


@pytest.mark.unit
def test_delete_all_nodes(mock_db, mock_backend):
    mock_backend.delete_all_nodes()
    assert mock_db["nodes"].count_documents({}) == 0
    assert mock_db["nodes_archived"].count_documents({}) == 0


@pytest.mark.unit
@pytest.mark.parametrize("name", [("TEST")])
def test_delete_node_by_name(name, mock_db, mock_backend):
    nodes_documents_before_count = mock_db["nodes"].count_documents({})
    nodes_archived_documents_before_count = mock_db["nodes_archived"].count_documents({})
    mock_backend.delete_node_by_name(node_name=name)
    assert mock_db["nodes"].count_documents({}) == nodes_documents_before_count - 1
    assert mock_db["nodes_archived"].count_documents({}) == nodes_archived_documents_before_count - 1


@pytest.mark.unit
@pytest.mark.parametrize("id,expected_exists", [("db1d3ee3-74e4-48aa-afaf-8d7709a2f57c", True), ("0", False)])
def test_get_compute(id, expected_exists, mock_backend):
    result = mock_backend.get_compute(compute_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("name,expected_exists", [("TEST", True), ("A", False)])
def test_get_node(name, expected_exists, mock_backend):
    result = mock_backend.get_node(node_name=name, node_version="latest")
    if expected_exists:
        assert result.get("name") == name
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("id,expected_exists", [("cd200c23-60f4-49c0-a987-3e11f06a4c8c", True), ("0", False)])
def test_get_service(id, expected_exists, mock_backend):
    result = mock_backend.get_service(service_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("id,expected_exists", [("8b008348-0d8d-4505-a625-1e6e8df56e8a", True), ("0", False)])
def test_get_site(id, expected_exists, mock_backend):
    result = mock_backend.get_site(site_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("node_name,site_name,expected_exists", [("TEST", "TEST_A", True), ("TEST", "TEST_C", False)])
def test_get_site_by_names(node_name, site_name, expected_exists, mock_backend):
    result = mock_backend.get_site_from_names(node_name=node_name, site_name=site_name, node_version="latest")
    if expected_exists:
        assert result.get("parent_node_name") == node_name
        assert result.get("name") == site_name
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("id,expected_exists", [("180f2f39-4548-4f11-80b1-7471564e5c05", True), ("0", False)])
def test_get_storage(id, expected_exists, mock_backend):
    result = mock_backend.get_storage(storage_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.unit
@pytest.mark.parametrize("id,expected_exists", [("f62199c3-62ad-44ee-a6e0-dd34e891d423", True), ("0", False)])
def test_get_storage_area(id, expected_exists, mock_backend):
    result = mock_backend.get_storage_area(storage_area_id=id)
    if expected_exists:
        assert result.get("id") == id
    else:
        assert not result


@pytest.mark.unit
def test_list_compute_with_node_name_filter(mock_backend):
    compute = mock_backend.list_compute(node_names="TEST")
    assert len(compute) == 2


@pytest.mark.unit
def test_list_compute_with_site_name_filter(mock_backend):
    compute = mock_backend.list_compute(site_names="TEST_B")
    assert len(compute) == 1


@pytest.mark.unit
def test_list_nodes(mock_backend):
    sites = mock_backend.list_nodes()
    assert len(sites) == 1


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment, number_of_services",
    [
        ("Production", 3),
        ("Development", 2),
        ("Integration", 4)
    ],
)
def test_list_services_with_environment_filter(mock_backend, environment, number_of_services):
    services = mock_backend.list_services(environments=[environment])
    assert len(services) == number_of_services


@pytest.mark.unit
def test_list_services_with_node_name_filter(mock_backend):
    services = mock_backend.list_services(node_names="TEST")
    assert len(services) == 7


@pytest.mark.unit
def test_list_services_with_output_prometheus(mock_backend):
    services = mock_backend.list_services(for_prometheus=True)
    for service in services:
        assert "targets" in service
        assert "labels" in service
        assert service["targets"]


@pytest.mark.unit
def test_list_services_with_service_types_filter(mock_backend):
    services = mock_backend.list_services(service_types="jupyterhub")
    assert len(services) == 1
    assert all(s.get("type") == "jupyterhub" for s in services)


@pytest.mark.unit
def test_list_services_with_site_name_filter(mock_backend):
    services = mock_backend.list_services(site_names="TEST_B")
    assert len(services) == 5


@pytest.mark.unit
def test_list_sites(mock_backend):
    sites = mock_backend.list_sites()
    assert len(sites) == 2


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment, number_of_storage_areas",
    [
        ("Production", 1),
        ("Development", 2),
        ("Integration", 1)
    ],
)
def test_list_storage_areas_with_environment_filter(mock_backend, environment, number_of_storage_areas):
    services = mock_backend.list_storage_areas(environments=[environment])
    assert len(services) == number_of_storage_areas


@pytest.mark.unit
def test_list_storages_with_node_name_filter(mock_backend):
    storages = mock_backend.list_storages(node_names="TEST")
    assert len(storages) == 2


@pytest.mark.unit
def test_list_storages_with_site_name_filter(mock_backend):
    storages = mock_backend.list_storages(site_names="TEST_B")
    assert len(storages) == 1


@pytest.mark.unit
def test_list_storage_areas_with_node_name_filter(mock_backend):
    storage_areas = mock_backend.list_storage_areas(node_names="TEST")
    assert len(storage_areas) == 3


@pytest.mark.unit
def test_list_storage_areas_with_site_name_filter(mock_backend):
    storage_areas = mock_backend.list_storage_areas(site_names="TEST_B")
    assert len(storage_areas) == 1


@pytest.mark.unit
@pytest.mark.parametrize("is_force_disabled_flag", [False, True])
def test_set_compute_enabled_disabled(is_force_disabled_flag, mock_backend, id="db1d3ee3-74e4-48aa-afaf-8d7709a2f57c"):
    result = mock_backend.set_compute_force_disabled_flag(id, is_force_disabled_flag)
    # test return body
    assert result.get("compute_id") == id
    assert result.get("is_force_disabled") is is_force_disabled_flag
    # test document update
    assert mock_backend.get_compute(compute_id=id).get("is_force_disabled") is is_force_disabled_flag


@pytest.mark.unit
@pytest.mark.parametrize(
    "is_force_disabled_flag, id",
    [
        (False, "4f57724b-aa73-4c6c-bf0c-3fb95677cc91"),
        (True, "4f57724b-aa73-4c6c-bf0c-3fb95677cc91"),
        (False, "dd200c23-60f4-49c0-a987-3e11f06a4c8d"),
        (True, "dd200c23-60f4-49c0-a987-3e11f06a4c8d"),
    ],
)
def test_set_service_enabled_disabled(mock_backend, is_force_disabled_flag, id):
    result = mock_backend.set_service_force_disabled_flag(id, is_force_disabled_flag)
    # test return body
    assert result.get("service_id") == id
    assert result.get("is_force_disabled") is is_force_disabled_flag
    # test document update
    assert mock_backend.get_service(service_id=id).get("is_force_disabled") is is_force_disabled_flag


@pytest.mark.unit
@pytest.mark.parametrize("is_force_disabled_flag", [False, True])
def test_set_site_enabled_disabled(is_force_disabled_flag, mock_backend, id="8b008348-0d8d-4505-a625-1e6e8df56e8a"):
    result = mock_backend.set_site_force_disabled_flag(id, is_force_disabled_flag)
    # test return body
    assert result.get("site_id") == id
    assert result.get("is_force_disabled") is is_force_disabled_flag
    # test document update
    assert mock_backend.get_site(site_id=id).get("is_force_disabled") is is_force_disabled_flag


@pytest.mark.unit
@pytest.mark.parametrize("is_force_disabled_flag", [False, True])
def test_set_storage_enabled_disabled(is_force_disabled_flag, mock_backend, id="180f2f39-4548-4f11-80b1-7471564e5c05"):
    result = mock_backend.set_storage_force_disabled_flag(id, is_force_disabled_flag)
    # test return body
    assert result.get("storage_id") == id
    assert result.get("is_force_disabled") is is_force_disabled_flag
    # test document update
    assert mock_backend.get_storage(storage_id=id).get("is_force_disabled") is is_force_disabled_flag


@pytest.mark.unit
@pytest.mark.parametrize("is_force_disabled_flag", [False, True])
def test_set_storage_area_enabled_disabled(is_force_disabled_flag, mock_backend, id="f62199c3-62ad-44ee-a6e0-dd34e891d423"):
    result = mock_backend.set_storage_area_force_disabled_flag(id, is_force_disabled_flag)
    # test return body
    assert result.get("storage_area_id") == id
    assert result.get("is_force_disabled") is is_force_disabled_flag
    # test document update
    assert mock_backend.get_storage_area(storage_area_id=id).get("is_force_disabled") is is_force_disabled_flag
