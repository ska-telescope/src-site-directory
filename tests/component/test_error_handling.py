"""
Component tests for error handling - invalid formats and malformed parameters.

These tests verify that the API properly handles edge cases and invalid input.
"""

import os

import httpx
import pytest

from tests.component.conftest import DISABLE_AUTHENTICATION, get_api_url, send_get_request


@pytest.mark.component
def test_invalid_node_version_format(load_nodes_data):
    """Test that invalid node_version format returns appropriate error"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Test with non-numeric, non-"latest" version
        response = send_get_request(f"{api_url}/nodes/{node_name}?node_version=invalid")

        if DISABLE_AUTHENTICATION:
            # API should return 404 with IncorrectNodeVersionType error
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "version" in data["detail"].lower() or "integer" in data["detail"].lower()
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_invalid_node_version_format_site_endpoint(load_nodes_data):
    """Test that invalid node_version format in site endpoint returns appropriate error"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Get a site name from the node
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if node_data and "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                # Test with non-numeric, non-"latest" version
                response = send_get_request(f"{api_url}/nodes/{node_name}/sites/{site_name}?node_version=not_a_number")

                if DISABLE_AUTHENTICATION:
                    # API should return 404 with IncorrectNodeVersionType error
                    assert response.status_code == 404
                    data = response.json()
                    assert "detail" in data
                    assert "version" in data["detail"].lower() or "integer" in data["detail"].lower()
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_compute():
    """Test that invalid UUID format for compute_id returns appropriate error"""
    api_url = get_api_url()
    # Test with clearly invalid UUID format
    invalid_uuid = "not-a-uuid"
    response = send_get_request(f"{api_url}/compute/{invalid_uuid}")

    if DISABLE_AUTHENTICATION:
        # FastAPI should return 422 (Unprocessable Entity) for invalid UUID format
        # or the API might return 404 if it tries to process it
        assert response.status_code in (404, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_service():
    """Test that invalid UUID format for service_id returns appropriate error"""
    api_url = get_api_url()
    invalid_uuid = "invalid-uuid-format"
    response = send_get_request(f"{api_url}/services/{invalid_uuid}")

    if DISABLE_AUTHENTICATION:
        assert response.status_code in (404, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_site():
    """Test that invalid UUID format for site_id returns appropriate error"""
    api_url = get_api_url()
    invalid_uuid = "not-a-valid-uuid-123"
    response = send_get_request(f"{api_url}/sites/{invalid_uuid}")

    if DISABLE_AUTHENTICATION:
        assert response.status_code in (404, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_storage():
    """Test that invalid UUID format for storage_id returns appropriate error"""
    api_url = get_api_url()
    invalid_uuid = "bad-uuid-format"
    response = send_get_request(f"{api_url}/storages/{invalid_uuid}")

    if DISABLE_AUTHENTICATION:
        assert response.status_code in (404, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_storage_area():
    """Test that invalid UUID format for storage_area_id returns appropriate error"""
    api_url = get_api_url()
    invalid_uuid = "invalid-uuid"
    response = send_get_request(f"{api_url}/storage-areas/{invalid_uuid}")

    if DISABLE_AUTHENTICATION:
        assert response.status_code in (404, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_malformed_query_parameter_include_inactive():
    """Test that malformed include_inactive query parameter is handled gracefully"""
    api_url = get_api_url()
    # Test with invalid boolean value
    response = send_get_request(f"{api_url}/compute?include_inactive=not_a_boolean")

    if DISABLE_AUTHENTICATION:
        # FastAPI should handle this - might return 422 or ignore invalid value
        # The API might default to False or return an error
        assert response.status_code in (200, 422, 400)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_malformed_query_parameter_node_names():
    """Test that malformed node_names query parameter is handled gracefully"""
    api_url = get_api_url()
    # Test with special characters that might cause issues
    response = send_get_request(f"{api_url}/compute?node_names=node%20with%20spaces,another")

    if DISABLE_AUTHENTICATION:
        # Should handle URL-encoded spaces or return appropriate error
        assert response.status_code in (200, 400, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_malformed_query_parameter_empty_values():
    """Test that empty query parameter values are handled gracefully"""
    api_url = get_api_url()
    # Test with empty node_names
    response = send_get_request(f"{api_url}/compute?node_names=")

    if DISABLE_AUTHENTICATION:
        # Should handle empty values gracefully (treat as no filter or return error)
        assert response.status_code in (200, 400, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_malformed_query_parameter_multiple_equals():
    """Test that query parameters with multiple equals signs are handled"""
    api_url = get_api_url()
    # Test with malformed parameter (multiple = signs)
    response = send_get_request(f"{api_url}/compute?node_names=test=value")

    if DISABLE_AUTHENTICATION:
        # Should handle or reject malformed parameters
        assert response.status_code in (200, 400, 422)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_invalid_node_version_numeric_string(load_nodes_data):
    """Test that node_version with numeric string (should be valid) works"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Test with valid numeric string (should work)
        response = send_get_request(f"{api_url}/nodes/{node_name}?node_version=1")

        if DISABLE_AUTHENTICATION:
            # Should accept numeric string as valid version
            assert response.status_code in (
                200,
                404,
            )  # 404 if version doesn't exist, 200 if it does
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_invalid_node_version_negative_number(load_nodes_data):
    """Test that negative node_version is handled"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Test with negative number (technically valid int but unlikely to exist)
        response = send_get_request(f"{api_url}/nodes/{node_name}?node_version=-1")

        if DISABLE_AUTHENTICATION:
            # Should accept as valid int format, but return 404 if version doesn't exist
            assert response.status_code in (200, 404)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_invalid_uuid_format_enable_disable():
    """Test that invalid UUID format in enable/disable endpoints returns appropriate response

    Note: The API may return 200 with empty response when resource is not found,
    or 404/422 depending on validation. Sites endpoint returns 404, but compute
    and other resources may return 200 with empty dict.
    """
    api_url = get_api_url()
    invalid_uuid = "not-a-uuid"

    # Test enable endpoint
    enable_response = httpx.put(f"{api_url}/compute/{invalid_uuid}/enable", timeout=30)
    if DISABLE_AUTHENTICATION:
        # API may return 200 (with empty response) or 404/422
        assert enable_response.status_code in (200, 404, 422)
        if enable_response.status_code == 200:
            # If 200, verify response is empty or indicates not found
            data = enable_response.json()
            assert isinstance(data, dict)
            # Empty dict or missing compute_id indicates resource not found
            assert not data or "compute_id" not in data
    else:
        assert enable_response.status_code == 403

    # Test disable endpoint
    disable_response = httpx.put(f"{api_url}/compute/{invalid_uuid}/disable", timeout=30)
    if DISABLE_AUTHENTICATION:
        # API may return 200 (with empty response) or 404/422
        assert disable_response.status_code in (200, 404, 422)
        if disable_response.status_code == 200:
            # If 200, verify response is empty or indicates not found
            data = disable_response.json()
            assert isinstance(data, dict)
            # Empty dict or missing compute_id indicates resource not found
            assert not data or "compute_id" not in data
    else:
        assert disable_response.status_code == 403
