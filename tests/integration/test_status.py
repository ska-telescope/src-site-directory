import logging

import pytest
import requests

from conftest import SCAPI_SERVICE_URL

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_health():
    """Test the /v1/health endpoint."""
    response = requests.get(f"{SCAPI_SERVICE_URL}/health", timeout=10)
    # Health endpoint may return 200 or 500 depending on dependent services
    assert response.status_code in (200, 500), f"Health endpoint returned unexpected status: {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        assert data["uptime"] > 0
    logger.info("SCAPI health status: %d", response.status_code)


@pytest.mark.integration
def test_ping():
    """Test the /v1/ping endpoint."""
    response = requests.get(f"{SCAPI_SERVICE_URL}/ping", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
