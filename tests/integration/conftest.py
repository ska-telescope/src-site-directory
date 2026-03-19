"""Integration test configuration for Site Capabilities API."""

import logging
import os
import sys
from pathlib import Path

import pytest
from ska_test_utils.auth import get_scapi_token

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)

try:
    project_path = Path(__file__).resolve().parents[3]
    src_path = project_path / "src"
    if src_path.is_dir():
        sys.path.insert(0, str(src_path))
except IndexError:
    pass


@pytest.fixture(scope="session")
def scapi_base_url() -> str:
    return os.environ.get("SCAPI_URL", "http://scapi-core:8080") + "/v1"


@pytest.fixture(scope="session")
def site_capabilities_token(scapi_base_url) -> str:
    """Obtain a SCAPI-scoped token via AAPI device flow."""
    return get_scapi_token()
