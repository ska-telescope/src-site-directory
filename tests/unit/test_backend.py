import pytest
from src.ska_src_site_capabilities_api.db.backend import MongoBackend


@pytest.fixture
def backend(mocker):
    # Setup a mock MongoBackend instance
    backend = MongoBackend(
        mongo_username="user",
        mongo_password="pass",
        mongo_host="localhost",
        mongo_port=27017,
        mongo_database="test_db",
    )
    mocker.patch.object(
        backend, "list_site_names_unique", return_value=["CNSRC", "UKSRC"]
    )
    mocker.patch.object(
        backend,
        "get_site_version_latest",
        side_effect=lambda site_name: {
            "CNSRC": {
                "name": "CNSRC",
                "global_services": [],
                "compute": [
                    {
                        "id": "dd875a28-2df8-4f9f-838c-aa4110b4c4b9",
                        "associated_local_services": [
                            {
                                "id": "1f73c95e-301b-4f5e-a2cf-aeb461da2d70",
                                "type": "jupyterhub",
                                "prefix": "https",
                                "host": "canfar.shao.ac.cn",
                                "path": "/hub",
                                "identifier": "CNSRC JupyterHUB service",
                                "enabled": True,
                                "is_proxy": False,
                            },
                            {
                                "id": "52acaf90-2701-4f79-b696-fcc1c559e4ec",
                                "type": "jupyterhub",
                                "prefix": "https",
                                "host": "canfar.shao.ac.cn",
                                "path": "/science-portal",
                                "identifier": "CNSRC CANFAR Science Portal",
                                "enabled": True,
                                "is_proxy": False,
                            },
                        ],
                    }
                ],
            },
            "UKSRC": {
                "name": "UKSRC",
                "global_services": [],
                "compute": [
                    {
                        "id": "e24a1a87-01f2-4a4a-8e3e-4234951c45d0",
                        "associated_local_services": [
                            {
                                "id": "21990532-7231-4ab9-9fa7-3dfe587332ec",
                                "type": "jupyterhub",
                                "prefix": "https",
                                "host": "portal.apps.hpc.cam.ac.uk",
                                "path": "/auth/federated/start/?option=ska-iam_openid",
                                "identifier": "Cambridge HPC Azimuth Instance",
                                "enabled": True,
                                "is_proxy": False,
                            }
                        ],
                    }
                ],
            },
        }[site_name],
    )
    return backend


def test_list_services_with_site_name_filter(backend):
    # Test the list_services function with site_name filter
    services = backend.list_services(site_names="CNSRC")
    assert len(services) == 1
    assert services[0]["site_name"] == "CNSRC"
    assert len(services[0]["services"]) == 2


def test_list_services_with_service_type_filter(backend):
    # Test the list_services function with service_type filter
    services = backend.list_services(service_type="jupyterhub")
    assert len(services) == 2  # Expecting services from both CNSRC and UKSRC
    for service in services:
        assert service["site_name"] in ["CNSRC", "UKSRC"]
        assert all(s["type"] == "jupyterhub" for s in service["services"])


def test_list_services_with_compute_id_filter(backend):
    # Test the list_services function with compute_id filter
    services = backend.list_services(compute_id="dd875a28-2df8-4f9f-838c-aa4110b4c4b9")
    assert len(services) == 1
    assert services[0]["site_name"] == "CNSRC"
    assert len(services[0]["services"]) == 2
    assert all(
        s["associated_compute_id"] == "dd875a28-2df8-4f9f-838c-aa4110b4c4b9"
        for s in services[0]["services"]
    )


def test_add_site(backend, mocker):
    # Setup test data
    site_values = {"name": "TestSite", "description": "A test site"}

    # Mock the MongoClient to avoid actual database operations
    mock_client = mocker.patch(
        "src.ska_src_site_capabilities_api.db.backend.MongoClient"
    )
    mock_db = mock_client.return_value.__getitem__.return_value
    mock_db.sites.insert_one.return_value.inserted_id = "mock_id"
    mock_db.sites.find.return_value = []  # Simulate no existing versions

    # Call the add_site function
    inserted_id = backend.add_site(site_values)

    # Assertions
    assert inserted_id == "mock_id"
    mock_db.sites.insert_one.assert_called_once_with(
        {"name": "TestSite", "description": "A test site", "version": 1}
    )


def test_delete_site_version(backend, mocker):
    # Mock the MongoClient to avoid actual database operations
    mock_client = mocker.patch(
        "src.ska_src_site_capabilities_api.db.backend.MongoClient"
    )
    mock_db = mock_client.return_value.__getitem__.return_value
    mock_db.sites.delete_one.return_value.deleted_count = 1

    # Call the delete_site_version function
    result = backend.delete_site_version("TestSite", 1)

    # Assertions
    assert result.deleted_count == 1
    mock_db.sites.delete_one.assert_called_once_with({"name": "TestSite", "version": 1})


def test_dump_sites(backend, mocker):
    # Mock the MongoClient to avoid actual database operations
    mock_client = mocker.patch(
        "src.ska_src_site_capabilities_api.db.backend.MongoClient"
    )
    mock_db = mock_client.return_value.__getitem__.return_value
    mock_db.sites.find.return_value = [{"name": "TestSite", "_id": "mock_id"}]

    # Call the dump_sites function
    result = backend.dump_sites()

    # Assertions
    assert result == [{"name": "TestSite"}]
    mock_db.sites.find.assert_called_once_with({})


def test_get_compute(backend, mocker):
    # Mock the list_sites_version_latest method
    mocker.patch.object(
        backend,
        "list_sites_version_latest",
        return_value=[{"compute": [{"id": "compute_1", "name": "Compute1"}]}],
    )

    # Call the get_compute function
    result = backend.get_compute("compute_1")

    # Assertions
    assert result == {"id": "compute_1", "name": "Compute1"}


def test_get_service(backend, mocker):
    # Mock the list_services method
    mocker.patch.object(
        backend,
        "list_services",
        return_value=[
            {
                "site_name": "TestSite",
                "services": [{"id": "service_1", "name": "Service1"}],
            }
        ],
    )

    # Call the get_service function
    result = backend.get_service("service_1")

    # Assertions
    assert result == {"site_name": "TestSite", "id": "service_1", "name": "Service1"}


def test_get_site(backend, mocker):
    # Mock the MongoClient to avoid actual database operations
    mock_client = mocker.patch(
        "src.ska_src_site_capabilities_api.db.backend.MongoClient"
    )
    mock_db = mock_client.return_value.__getitem__.return_value
    mock_db.sites.find.return_value = [
        {"name": "TestSite", "version": 1, "_id": "mock_id"}
    ]

    # Call the get_site function
    result = backend.get_site("TestSite")

    # Assertions
    assert result == [{"name": "TestSite", "version": 1, "_id": "mock_id"}]
    mock_db.sites.find.assert_called_once_with({"name": "TestSite"})
