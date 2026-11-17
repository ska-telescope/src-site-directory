"""Integration tests: a user's token must never come back in an error response."""

import base64
import json
import logging
import uuid

import pytest
import requests
from conftest import SCAPI_SERVICE_URL

logger = logging.getLogger(__name__)


def _b64url_json(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


def _canary_token() -> tuple[str, str]:
    """Return a made-up, JWT-shaped token and the unique marker it contains.

    The marker is the signature segment, so it appears verbatim wherever the token does. Its length is a multiple of 4
    so it decodes as base64: PAPI then rejects the token the normal way (no public key for its "kid", 400) rather than
    crashing on a malformed signature.
    """
    marker = "canary" + uuid.uuid4().hex[:26]
    header = _b64url_json({"alg": "RS256", "typ": "JWT", "kid": "canary"})
    payload = _b64url_json({"sub": "canary"})
    return f"{header}.{payload}.{marker}", marker


@pytest.mark.integration
def test_rejected_token_is_not_echoed_in_the_error_response():
    """SCAPI asks PAPI to authorise the request; PAPI rejects the canary token; the token must not come back."""
    token, marker = _canary_token()

    response = requests.get(f"{SCAPI_SERVICE_URL}/nodes", headers={"Authorization": f"Bearer {token}"}, timeout=30)

    # A rejection, not a crash or a success: otherwise this test isn't checking the error path it's meant to.
    assert 400 <= response.status_code < 500, f"Expected PAPI's rejection to come back as a 4xx, got {response.status_code}"
    assert marker not in response.text, "The rejected token was echoed back in SCAPI's error response"
