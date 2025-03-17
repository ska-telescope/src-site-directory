import pytest
from ska_src_site_capabilities_api.db.backend import MongoBackend

@pytest.fixture
def mock_backend():
    storages_data = {
        "KRSRC": {
            "name": "KRSRC",
            "storages": [
                {
                    "id": "b5900a8e-c5f2-429a-9343-9e7087d94974",
                    "host": "skadtn1.kreonet.net",
                    "base_path": "/storm/sa",
                    "latitude": 36.321329,
                    "longitude": 127.42001,
                    "srm": "xrd",
                    "device_type": "",
                    "size_in_terabytes": 0.1,
                    "identifier": "KRSRC",
                    "supported_protocols": [
                        {
                            "prefix": "https",
                            "port": 8443
                        }
                    ],
                    "areas": [
                        {
                            "id": "1298a618-38f1-43bf-ac66-4e4c2bf20606",
                            "type": "rse",
                            "relative_path": "/test_rse/dev/deterministic",
                            "identifier": "KRSRC_STORM"
                        }
                    ]
                }
            ],
        },
        "AUSSRC": {
            "name": "AUSSRC",
            "storages": [
                {
                    "id": "d46c5c0f-96f0-4a9f-9fe6-02f541b6938e",
                    "host": "storm-storage-01.aussrc.org",
                    "base_path": "/storm/sa",
                    "latitude": -31.9529,
                    "longitude": 115.8613,
                    "srm": "storm",
                    "device_type": "",
                    "size_in_terabytes": 0.04,
                    "identifier": "AUSSRC",
                    "supported_protocols": [
                        {
                            "prefix": "https",
                            "port": 443
                        }
                    ],
                    "areas": [
                        {
                            "id": "f1902d12-9c48-4673-a55a-7e7d05b6c57b",
                            "type": "rse",
                            "relative_path": "/test_rse/dev/deterministic",
                            "identifier": "AUSSRC_STORM"
                        }
                    ]
                }
            ],
        }
    }

    backend = MongoBackend("user", "password", "localhost", 27017, "database")
    
    backend.get_site_version_latest = storages_data.get

    return backend

def test_krsrc_site_name(mock_backend):
    response = mock_backend.list_storage_areas(site_name="KRSRC")
    assert len(response) == 1
    assert response[0]["site_name"] == "KRSRC"

def test_aussrc_site_name(mock_backend):
    response = mock_backend.list_storage_areas(site_name="AUSSRC")
    assert len(response) == 1
    assert response[0]["site_name"] == "AUSSRC"

def test_wrong_site_name(mock_backend):
    response = mock_backend.list_storage_areas(site_name="KRSRC")
    assert len(response) == 1
    assert response[0]["site_name"] != "UKSRC"

def test_krsrc_associated_storage_id(mock_backend):
    response = mock_backend.list_storage_areas(site_name="KRSRC")
    assert len(response) == 1
    assert response[0]["storage_areas"][0]["associated_storage_id"] == "b5900a8e-c5f2-429a-9343-9e7087d94974"

def test_aussrc_associated_storage_id(mock_backend):
    response = mock_backend.list_storage_areas(site_name="AUSSRC")
    assert len(response) == 1
    assert response[0]["storage_areas"][0]["associated_storage_id"] == "d46c5c0f-96f0-4a9f-9fe6-02f541b6938e"

def test_krsrc_storage_areas_identifier(mock_backend):
    response = mock_backend.list_storage_areas(site_name="KRSRC")
    assert len(response) == 1
    assert response[0]["storage_areas"][0]["identifier"] == "KRSRC_STORM"

def test_aussrc_storage_areas_identifier(mock_backend):
    response = mock_backend.list_storage_areas(site_name="AUSSRC")
    assert len(response) == 1
    assert response[0]["storage_areas"][0]["identifier"] == "AUSSRC_STORM"

def test_wrong_storage_areas(mock_backend):
    response = mock_backend.list_storage_areas(site_name="KRSRC")
    assert len(response) == 1
    assert response[0]["storage_areas"][0]["identifier"] != "XXSRC_STORM"
