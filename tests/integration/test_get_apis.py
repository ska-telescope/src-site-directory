"""
A module with integration tests for SKA SRC Site Capabilities GET APIs.
"""
import httpx
import pytest


@pytest.mark.post_deployment
def test_get_sites_api():
    """Test method for get sites API"""
    response = httpx.get(
        "https://site-capabilities.srcdev.skao.int/api/v1/sites"
    )
    response_data = response.json()
    print(response_data)
