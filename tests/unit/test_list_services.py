import pytest
from src.ska_src_site_capabilities_api.db.backend import MongoBackend

@pytest.fixture
def backend(mocker):
    # Setup a mock MongoBackend instance
    backend = MongoBackend(
        mongo_username='user',
        mongo_password='pass',
        mongo_host='localhost',
        mongo_port=27017,
        mongo_database='test_db'
    )
    mocker.patch.object(backend, 'list_site_names_unique', return_value=['CNSRC', 'UKSRC'])
    mocker.patch.object(backend, 'get_site_version_latest', side_effect=lambda site_name: {
        'CNSRC': {
            'name': 'CNSRC',
            'global_services': [],
            'compute': [{
                'id': 'dd875a28-2df8-4f9f-838c-aa4110b4c4b9',
                'associated_local_services': [
                    {
                        'id': '1f73c95e-301b-4f5e-a2cf-aeb461da2d70',
                        'type': 'jupyterhub',
                        'prefix': 'https',
                        'host': 'canfar.shao.ac.cn',
                        'path': '/hub',
                        'identifier': 'CNSRC JupyterHUB service',
                        'enabled': True,
                        'is_proxy': False
                    },
                    {
                        'id': '52acaf90-2701-4f79-b696-fcc1c559e4ec',
                        'type': 'jupyterhub',
                        'prefix': 'https',
                        'host': 'canfar.shao.ac.cn',
                        'path': '/science-portal',
                        'identifier': 'CNSRC CANFAR Science Portal',
                        'enabled': True,
                        'is_proxy': False
                    }
                ]
            }]
        },
        'UKSRC': {
            'name': 'UKSRC',
            'global_services': [],
            'compute': [{
                'id': 'e24a1a87-01f2-4a4a-8e3e-4234951c45d0',
                'associated_local_services': [
                    {
                        'id': '21990532-7231-4ab9-9fa7-3dfe587332ec',
                        'type': 'jupyterhub',
                        'prefix': 'https',
                        'host': 'portal.apps.hpc.cam.ac.uk',
                        'path': '/auth/federated/start/?option=ska-iam_openid',
                        'identifier': 'Cambridge HPC Azimuth Instance',
                        'enabled': True,
                        'is_proxy': False
                    }
                ]
            }]
        }
    }[site_name])
    return backend

def test_list_services_with_site_name_filter(backend):
    # Test the list_services function with site_name filter
    services = backend.list_services(site_names='CNSRC')
    assert len(services) == 1
    assert services[0]['site_name'] == 'CNSRC'
    assert len(services[0]['services']) == 2

def test_list_services_with_service_type_filter(backend):
    # Test the list_services function with service_type filter
    services = backend.list_services(service_type='jupyterhub')
    assert len(services) == 2  # Expecting services from both CNSRC and UKSRC
    for service in services:
        assert service['site_name'] in ['CNSRC', 'UKSRC']
        assert all(s['type'] == 'jupyterhub' for s in service['services'])

def test_list_services_with_compute_id_filter(backend):
    # Test the list_services function with compute_id filter
    services = backend.list_services(compute_id='dd875a28-2df8-4f9f-838c-aa4110b4c4b9')
    assert len(services) == 1
    assert services[0]['site_name'] == 'CNSRC'
    assert len(services[0]['services']) == 2
    assert all(s['associated_compute_id'] == 'dd875a28-2df8-4f9f-838c-aa4110b4c4b9' for s in services[0]['services']) 