"""Unit tests for the PAPI permission dependencies.

The PAPI client owns the canonical tests for how it sends the token. These check the client version SCAPI installs,
as SCAPI uses it, so a client regression or packaging mismatch can't put the token back in the URL unnoticed.
"""

import asyncio
from types import SimpleNamespace
from unittest import mock

import pytest
import requests
from fastapi import HTTPException
from ska_src_permissions_api.client.permissions import PermissionsClient

from ska_src_site_capabilities_api.rest.dependencies import Permissions

pytestmark = pytest.mark.unit

TOKEN = "test-access-token"
PAPI_URL = "https://permissions.example/v1"


def _request():
    return SimpleNamespace(
        scope={"route": SimpleNamespace(path="/v1/nodes/{node_name}")},
        path_params={"node_name": "SKAOSRC"},
        method="GET",
    )


def _papi_response(status_code, payload):
    """A real requests.Response, so raise_for_status() builds the same HTTPError the client raises in production."""
    resp = requests.Response()
    resp.status_code = status_code
    resp.reason = {401: "Unauthorized", 403: "Forbidden"}.get(status_code, "OK")
    resp._content = payload.encode()  # pylint: disable=protected-access
    resp.url = f"{PAPI_URL}/authorise/route/site-capabilities-api?version=1&route=%2Fnodes%2F%7Bnode_name%7D&method=GET"
    return resp


def _permissions(session):
    client = PermissionsClient(PAPI_URL, session=session, calling_service="SCAPI")
    return Permissions(client, "site-capabilities-api", "1")


def _verify_with_bearer_header(session):
    authorization = SimpleNamespace(credentials=TOKEN)
    return asyncio.run(_permissions(session).verify_permission_for_service_route(_request(), authorization))


def _verify_with_query_token(session):
    return asyncio.run(_permissions(session).verify_permission_for_service_route_query_params(_request(), TOKEN))


VERIFIERS = pytest.mark.parametrize(
    "verify",
    [_verify_with_bearer_header, _verify_with_query_token],
    ids=["bearer-header", "query-token"],
)


@VERIFIERS
def test_token_is_sent_to_papi_in_the_authorization_header(verify):
    """The token must not be in the query string, where it ends up in access logs and error messages."""
    session = mock.Mock()
    session.post.return_value = _papi_response(200, '{"is_authorised": true}')

    verify(session)

    args, kwargs = session.post.call_args
    assert TOKEN not in args[0]
    assert TOKEN not in str(kwargs["params"])
    assert kwargs["params"]["route"] == "/nodes/{node_name}"
    assert kwargs["headers"]["Authorization"] == f"Bearer {TOKEN}"


@VERIFIERS
def test_not_authorised_raises_permission_denied(verify):
    session = mock.Mock()
    session.post.return_value = _papi_response(200, '{"is_authorised": false}')

    with pytest.raises(HTTPException) as exc_info:
        verify(session)
    assert exc_info.value.status_code == 403


@VERIFIERS
def test_papi_error_status_is_passed_on_without_the_token(verify):
    """A PAPI 4xx reaches the caller with the same status, and its detail doesn't quote the token."""
    session = mock.Mock()
    session.post.return_value = _papi_response(401, '{"detail": "Token is not active"}')

    with pytest.raises(HTTPException) as exc_info:
        verify(session)

    assert exc_info.value.status_code == 401
    assert "Token is not active" in exc_info.value.detail
    assert TOKEN not in exc_info.value.detail
