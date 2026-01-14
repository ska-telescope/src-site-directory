import json
import os
from datetime import datetime

import jwt
from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import IncorrectNodeVersionType, NodeAlreadyExists, SiteNotFoundInNodeVersion, handle_exceptions
from ska_src_site_capabilities_api.common.utility import recursive_autogen_id
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions

nodes_router = APIRouter()


@api_version(1)
@nodes_router.get(
    "/nodes",
    responses={
        200: {"model": models.response.NodesListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="List all nodes",
)
@handle_exceptions
async def list_nodes(
    request: Request,
    only_names: bool = Query(default=False, description="Return only node names"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List nodes with an option to return only node names."""
    rtn = request.app.state.backend.list_nodes(include_archived=False, include_inactive=include_inactive)
    if only_names:
        names = [node["name"] for node in rtn if "name" in node]
        return JSONResponse(names)

    return JSONResponse(rtn)


@api_version(1)
@nodes_router.post(
    "/nodes",
    response_model=None,
    include_in_schema=False,
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="Add a node",
)
@handle_exceptions
async def add_node(
    request: Request,
    values=Body(default="Node JSON."),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> HTMLResponse:
    # load json values
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))

    # check node doesn't already exist
    node_name = values.get("name")
    if request.app.state.backend.get_node(node_name, node_version="latest"):
        raise NodeAlreadyExists(node_name=node_name)

    # add some custom fields e.g. date, user
    values["created_at"] = datetime.now().isoformat()
    if request.app.state.debug and not authorization:
        values["created_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["created_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    values = recursive_autogen_id(values)

    id = request.app.state.backend.add_edit_node(values)
    return HTMLResponse(repr(id))


@api_version(1)
@nodes_router.post(
    "/nodes/{node_name}",
    response_model=None,
    include_in_schema=False,
    responses={200: {}, 401: {}, 403: {}},
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="Edit a node",
)
@handle_exceptions
async def edit_node(
    request: Request,
    node_name: str = Path(description="Node name"),
    values=Body(default="Site JSON."),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> HTMLResponse:
    # load json values
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))

    # add some custom fields e.g. date, user
    values["last_updated_at"] = datetime.now().isoformat()
    if request.app.state.debug and not authorization:
        values["last_updated_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["last_updated_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    values = recursive_autogen_id(values)

    id = request.app.state.backend.add_edit_node(values, node_name=node_name)
    return HTMLResponse(repr(id))


@api_version(1)
@nodes_router.delete(
    "/nodes/{node_name}",
    response_model=None,
    responses={
        200: {"model": models.response.DeleteNodeByNameResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="Delete a node by name",
)
@handle_exceptions
async def delete_node_by_name(
    request: Request,
    node_name: str = Path(description="Node name"),
) -> JSONResponse:
    result = request.app.state.backend.delete_node_by_name(node_name)
    return JSONResponse(result)


@api_version(1)
@nodes_router.get(
    "/nodes/dump",
    response_model=None,
    responses={
        200: {"model": models.response.NodesDumpResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="Dump all versions of all nodes",
)
@handle_exceptions
async def dump_nodes(request: Request) -> HTMLResponse:
    """Dump all versions of all nodes."""
    rtn = request.app.state.backend.list_nodes(include_archived=True)
    return JSONResponse(rtn)


@api_version(1)
@nodes_router.get(
    "/nodes/{node_name}",
    response_model=None,
    responses={
        200: {"model": models.response.NodesGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Nodes"],
    summary="Get node from name",
)
@handle_exceptions
async def get_node_version(
    request: Request,
    node_name: str = Path(description="Node name"),
    node_version: str = Query(default="latest", description="Version of node ({version}||latest"),
) -> JSONResponse:
    """Get a version of a node."""
    if node_version != "latest":
        try:
            int(node_version)
        except ValueError:
            raise IncorrectNodeVersionType
    return JSONResponse(request.app.state.backend.get_node(node_name=node_name, node_version=node_version))


@api_version(1)
@nodes_router.get(
    "/nodes/{node_name}/sites/{site_name}",
    response_model=None,
    responses={
        200: {"model": models.response.SiteGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Sites"],
    summary="Get site from node and site names",
)
@handle_exceptions
async def get_site_from_node_version(
    request: Request,
    node_name: str = Path(description="Node name"),
    site_name: str = Path(description="Site name"),
    node_version: str = Query(default="latest", description="Version of node ({version}||latest"),
) -> JSONResponse:
    """Get site from node version."""
    if node_version != "latest":
        try:
            int(node_version)
        except ValueError:
            raise IncorrectNodeVersionType
    rtn = request.app.state.backend.get_site_from_names(node_name=node_name, node_version=node_version, site_name=site_name)
    if not rtn:
        raise SiteNotFoundInNodeVersion(node_name=node_name, node_version=node_version, site_name=site_name)
    return JSONResponse(rtn)
