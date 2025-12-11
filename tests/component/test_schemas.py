"""
A module for component tests related to schemas.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_schemas():
    """Test to list all schemas"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/schemas")  # noqa: E231
    # Schemas endpoint doesn't require authentication
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verify we have some schemas
    assert len(data) > 0
    # Should be a list of strings (schema names)
    assert isinstance(data[0], str)


@pytest.mark.component
def test_get_schema():
    """Test to get a schema by name"""
    api_url = get_api_url()
    # First, get the list of schemas
    schemas_response = httpx.get(f"{api_url}/schemas")  # noqa: E231
    if schemas_response.status_code == 200:
        schemas_data = schemas_response.json()
        if len(schemas_data) > 0:
            schema_name = schemas_data[0]
            response = httpx.get(f"{api_url}/schemas/{schema_name}")  # noqa: E231
            # Schema endpoint doesn't require authentication
            assert response.status_code == 200
            data = response.json()
            # Should be a JSON schema object
            assert isinstance(data, dict)
            # JSON schemas typically have these properties
            assert "$schema" in data or "properties" in data or "type" in data


@pytest.mark.component
def test_get_schema_not_found():
    """Test to get a non-existent schema"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/schemas/nonexistent_schema")  # noqa: E231
    # Schema endpoint doesn't require authentication
    # API returns 500 (Internal Server Error) when schema file not found
    assert response.status_code == 500
