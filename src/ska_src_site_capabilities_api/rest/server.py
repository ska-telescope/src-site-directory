import asyncio
import copy
import io
import json
import logging
import os
import pathlib
import tempfile
import time
from datetime import datetime
from typing import Union

import jwt
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versionizer.versionizer import api_version, versionize
from jinja2 import Template
from plantuml import PlantUML
from ska_src_authn_api.client.authentication import AuthenticationClient
from ska_src_permissions_api.client.permissions import PermissionsClient
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.backend.mongo import MongoBackend
from ska_src_site_capabilities_api.common import constants
from ska_src_site_capabilities_api.common.exceptions import (
    ComputeNotFound,
    IncorrectNodeVersionType,
    NodeAlreadyExists,
    NodeVersionNotFound,
    PermissionDenied,
    SchemaNotFound,
    ServiceNotFound,
    SiteNotFound,
    SiteNotFoundInNodeVersion,
    StorageAreaNotFound,
    StorageNotFound,
    UnauthorizedRequest,
    handle_exceptions,
)
from ska_src_site_capabilities_api.common.utility import (
    convert_readme_to_html_docs,
    get_api_server_url_from_request,
    get_base_url_from_request,
    get_url_for_app_from_request,
    load_and_dereference_schema,
    recursive_autogen_id,
    recursive_stringify,
)
from ska_src_site_capabilities_api.rest import dependencies

config = Config(".env")

# Debug mode (runs unauthenticated)
#
DEBUG = True if config.get("DISABLE_AUTHENTICATION", default=None) == "yes" else False

# Instantiate FastAPI() allowing CORS. Static mounts must be added later after the versionize() call.
#
app = FastAPI()
CORSMiddleware_params = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
app.add_middleware(CORSMiddleware, **CORSMiddleware_params)
app.add_middleware(
    SessionMiddleware,
    max_age=3600,
    secret_key=config.get("SESSIONS_SECRET_KEY"),
)

# Get instance of IAM constants.
#
IAM_CONSTANTS = constants.IAM(client_conf_url=config.get("IAM_CLIENT_CONF_URL"))

# Get templates.
#
TEMPLATES = Jinja2Templates(directory="templates")

# Instantiate the backend api.
#
BACKEND = MongoBackend(
    mongo_username=config.get("MONGO_USERNAME"),
    mongo_password=config.get("MONGO_PASSWORD"),
    mongo_host=config.get("MONGO_HOST"),
    mongo_port=config.get("MONGO_PORT"),
    mongo_database=config.get("MONGO_DATABASE"),
)

# Instantiate the authentication client.
#
# This is used to create a session for browser based www/ routes.
#
AUTH = AuthenticationClient(config.get("AUTH_API_URL"))

# Instantiate the permissions client.
#
PERMISSIONS = PermissionsClient(config.get("PERMISSIONS_API_URL"))
PERMISSIONS_SERVICE_NAME = config.get("PERMISSIONS_SERVICE_NAME")
PERMISSIONS_SERVICE_VERSION = config.get("PERMISSIONS_SERVICE_VERSION")

# Instantiate permissions based dependencies.
#
permission_dependencies = dependencies.Permissions(
    permissions=PERMISSIONS,
    permissions_service_name=PERMISSIONS_SERVICE_NAME,
    permissions_service_version=PERMISSIONS_SERVICE_VERSION,
)

# Store service start time.
#
SERVICE_START_TIME = time.time()

# Keep track of number of managed requests.
#
REQUESTS_COUNTER = 0
REQUESTS_COUNTER_LOCK = asyncio.Lock()


@handle_exceptions
async def increment_request_counter(
    request: Request,
) -> Union[dict, HTTPException]:
    """Dependency to keep track of API requests."""
    global REQUESTS_COUNTER
    async with REQUESTS_COUNTER_LOCK:
        REQUESTS_COUNTER += 1


# Routes
# ------
#
@api_version(1)
@app.get(
    "/compute",
    responses={
        200: {"model": models.response.ComputeListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Compute"],
    summary="List all compute",
)
@handle_exceptions
async def list_compute(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all compute."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_compute(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/compute/{compute_id}",
    responses={
        200: {"model": models.response.ComputeGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Compute"],
    summary="Get compute from id",
)
@handle_exceptions
async def get_compute_from_id(
    request: Request,
    compute_id: str = Path(description="Unique compute identifier"),
) -> Union[JSONResponse, HTTPException]:
    """Get description of a compute element from a unique identifier."""
    rtn = BACKEND.get_compute(compute_id)
    if not rtn:
        raise ComputeNotFound(compute_id)
    return JSONResponse(rtn)


@api_version(1)
@app.put(
    "/compute/{compute_id}/enable",
    responses={
        200: {"model": models.response.ComputeEnableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Compute"],
    summary="Unset a compute from being force disabled",
)
@handle_exceptions
async def set_compute_enabled(
    request: Request,
    compute_id: str = Path(description="Compute ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_compute_force_disabled_flag(compute_id, False)
    return JSONResponse(response)


@api_version(1)
@app.put(
    "/compute/{compute_id}/disable",
    responses={
        200: {"model": models.response.ComputeDisableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Compute"],
    summary="Set a compute to be force disabled",
)
@handle_exceptions
async def set_compute_disabled(
    request: Request,
    compute_id: str = Path(description="Compute ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_compute_force_disabled_flag(compute_id, True)
    return JSONResponse(response)


@api_version(1)
@app.get(
    "/nodes",
    responses={
        200: {"model": models.response.NodesListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Nodes"],
    summary="List all nodes",
)
@handle_exceptions
async def list_nodes(
    request: Request,
    only_names: bool = Query(default=False, description="Return only node names"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List nodes with an option to return only node names."""
    rtn = BACKEND.list_nodes(include_archived=False, include_inactive=include_inactive)
    if only_names:
        names = [node["name"] for node in rtn if "name" in node]
        return JSONResponse(names)

    return JSONResponse(rtn)


@api_version(1)
@app.post(
    "/nodes",
    include_in_schema=False,
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Nodes"],
    summary="Add a node",
)
@handle_exceptions
async def add_node(
    request: Request,
    values=Body(default="Node JSON."),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[HTMLResponse, HTTPException]:
    # load json values
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))

    # check node doesn't already exist
    node_name = values.get("name")
    if BACKEND.get_node(node_name, node_version="latest"):
        raise NodeAlreadyExists(node_name=node_name)

    # add some custom fields e.g. date, user
    values["created_at"] = datetime.now().isoformat()
    if DEBUG and not authorization:
        values["created_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["created_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    values = recursive_autogen_id(values)

    id = BACKEND.add_edit_node(values)
    return HTMLResponse(repr(id))


@api_version(1)
@app.post(
    "/nodes/{node_name}",
    include_in_schema=False,
    responses={200: {}, 401: {}, 403: {}},
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
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
) -> Union[HTMLResponse, HTTPException]:
    # load json values
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))

    # add some custom fields e.g. date, user
    values["last_updated_at"] = datetime.now().isoformat()
    if DEBUG and not authorization:
        values["last_updated_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["last_updated_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    values = recursive_autogen_id(values)

    id = BACKEND.add_edit_node(values, node_name=node_name)
    return HTMLResponse(repr(id))


@api_version(1)
@app.delete(
    "/nodes/{node_name}",
    responses={200: {"model": models.response.DeleteNodeByNameResponse}, 401: {}, 403: {}},
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Nodes"],
    summary="Delete a node by name",
)
@handle_exceptions
async def delete_node_by_name(
    request: Request,
    node_name: str = Path(description="Node name"),
) -> Union[JSONResponse, HTTPException]:
    result = BACKEND.delete_node_by_name(node_name)
    return JSONResponse(result)


@api_version(1)
@app.get(
    "/nodes/dump",
    responses={
        200: {"model": models.response.NodesDumpResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Nodes"],
    summary="Dump all versions of all nodes",
)
@handle_exceptions
async def dump_nodes(request: Request) -> Union[HTMLResponse, HTTPException]:
    """Dump all versions of all nodes."""
    rtn = BACKEND.list_nodes(include_archived=True)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/nodes/{node_name}",
    responses={
        200: {"model": models.response.NodesGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Nodes"],
    summary="Get node from name",
)
@handle_exceptions
async def get_node_version(
    request: Request,
    node_name: str = Path(description="Node name"),
    node_version: str = Query(default="latest", description="Version of node ({version}||latest"),
) -> Union[JSONResponse, HTTPException]:
    """Get a version of a node."""
    if node_version != "latest":
        try:
            int(node_version)
        except ValueError:
            raise IncorrectNodeVersionType
    return JSONResponse(BACKEND.get_node(node_name=node_name, node_version=node_version))


@api_version(1)
@app.get(
    "/nodes/{node_name}/sites/{site_name}",
    responses={
        200: {"model": models.response.SiteGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
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
) -> Union[JSONResponse, HTTPException]:
    """Get site from node version."""
    if node_version != "latest":
        try:
            int(node_version)
        except ValueError:
            raise IncorrectNodeVersionType
    rtn = BACKEND.get_site_from_names(node_name=node_name, node_version=node_version, site_name=site_name)
    if not rtn:
        raise SiteNotFoundInNodeVersion(node_name=node_name, node_version=node_version, site_name=site_name)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/schemas",
    responses={
        200: {"model": models.response.SchemasListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Schemas"],
    summary="List schemas",
)
@handle_exceptions
async def list_schemas(request: Request) -> JSONResponse:
    """Get a list of schema names used to define entities."""
    schema_basenames = sorted(["".join(fi.split(".")[:-1]) for fi in os.listdir(config.get("SCHEMAS_RELPATH"))])
    return JSONResponse(schema_basenames)


@api_version(1)
@app.get(
    "/schemas/{schema}",
    responses={
        200: {"model": models.response.SchemaGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Schemas"],
    summary="Get schema",
)
@handle_exceptions
async def get_schema(request: Request, schema: str = Path(description="Schema name")) -> Union[JSONResponse, HTTPException]:
    """Get a schema by name."""
    try:
        dereferenced_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        )
        return JSONResponse(dereferenced_schema)  # some issue with jsonref return != dict
    except FileNotFoundError:
        raise SchemaNotFound


@api_version(1)
@app.get(
    "/schemas/render/{schema}",
    responses={
        200: {},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Schemas"],
    summary="Render a schema",
)
@handle_exceptions
async def render_schema(request: Request, schema: str = Path(description="Schema name")) -> Union[JSONResponse, HTTPException]:
    """Render a schema by name."""
    try:
        dereferenced_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        )
    except FileNotFoundError:
        raise SchemaNotFound

    # pop countries enum for readability
    dereferenced_schema.get("properties").get("sites", {}).get("items", {}).get("properties", {}).get("country", {}).pop("enum", None)

    plantuml = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as schema_file:
        schema_file.write("@startjson\n{}\n@endjson\n".format(json.dumps(dereferenced_schema, indent=2)))
        schema_file.flush()

        image_temp_file_descriptor, image_temp_file_name = tempfile.mkstemp()
        plantuml.processes_file(filename=schema_file.name, outfile=image_temp_file_name)
        with open(image_temp_file_name, "rb") as image_temp_file:
            png = image_temp_file.read()
        os.close(image_temp_file_descriptor)

    return StreamingResponse(io.BytesIO(png), media_type="image/png")


@api_version(1)
@app.get(
    "/services",
    responses={
        200: {"model": models.response.ServicesListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Services"],
    summary="List all services",
)
@handle_exceptions
async def list_services(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    service_types: str = Query(default=None, description="Filter by service types (comma-separated)"),
    service_scope: str = Query(default="all", description="Filter by scope of service (all||local||global)"),
    include_inactive: bool = Query(default=False, description="Include inactive (down/disabled) services?"),
    associated_storage_area_id: str = Query(default=None, description="Filter by associated storage area ID"),
    output: str = Query(default=None, description="Output format (e.g., 'prometheus' for Prometheus HTTP SD response)"),
) -> JSONResponse:
    """List all services."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]
    if service_types:
        service_types = [name.strip() for name in service_types.split(",")]

    for_prometheus = output == "prometheus"

    rtn = BACKEND.list_services(
        node_names=node_names,
        site_names=site_names,
        service_types=service_types,
        service_scope=service_scope,
        include_inactive=include_inactive,
        associated_storage_area_id=associated_storage_area_id,
        for_prometheus=for_prometheus,
    )
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/services/types",
    responses={
        200: {"model": models.response.ServicesTypesResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Services"],
    summary="List service types",
)
@handle_exceptions
async def list_service_types(request: Request) -> JSONResponse:
    """List service types."""
    try:
        # local
        dereferenced_local_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "local-service"))).absolute()
        )

        # global
        dereferenced_global_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "global-service"))).absolute()
        )
    except FileNotFoundError:
        raise SchemaNotFound
    rtn = {
        "local": BACKEND.list_service_types_from_schema(schema=dereferenced_local_schema),
        "global": BACKEND.list_service_types_from_schema(schema=dereferenced_global_schema),
    }
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/services/{service_id}",
    responses={
        200: {
            "model": Union[
                models.response.GlobalServiceGetResponse,
                models.response.LocalServiceGetResponse,
            ]
        },
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Services"],
    summary="Get service from id",
)
@handle_exceptions
async def get_service_from_id(
    request: Request,
    service_id: str = Path(description="Unique service identifier"),
) -> Union[JSONResponse, HTTPException]:
    """Get a service description from a unique identifier."""
    rtn = BACKEND.get_service(service_id)
    if not rtn:
        raise ServiceNotFound(service_id)
    return JSONResponse(rtn)


@api_version(1)
@app.put(
    "/services/{service_id}/enable",
    responses={
        200: {"model": models.response.ServiceEnableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Services"],
    summary="Unset a service from being force disabled",
)
@handle_exceptions
async def set_service_enabled(
    request: Request,
    service_id: str = Path(description="Service ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_service_force_disabled_flag(service_id, False)
    return JSONResponse(response)


@api_version(1)
@app.put(
    "/services/{service_id}/disable",
    responses={
        200: {"model": models.response.ServiceDisableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Services"],
    summary="Set a service to be force disabled",
)
@handle_exceptions
async def set_service_disabled(
    request: Request,
    service_id: str = Path(description="Service ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_service_force_disabled_flag(service_id, True)
    return JSONResponse(response)


@api_version(1)
@app.get(
    "/sites",
    responses={
        200: {"model": models.response.SitesListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Sites"],
    summary="List all sites",
)
@handle_exceptions
async def list_sites(
    request: Request,
    only_names: bool = Query(default=False, description="Return only site names"),
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List versions of all sites."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]

    rtn = BACKEND.list_sites(node_names=node_names, include_inactive=include_inactive)
    if only_names:
        names = [site["name"] for site in rtn if "name" in site]
        return JSONResponse(names)

    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/sites/{site_id}",
    responses={
        200: {"model": models.response.SiteGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Sites"],
    summary="Get site from id",
)
@handle_exceptions
async def get_site_from_id(
    request: Request,
    site_id: str = Path(description="Unique site identifier"),
) -> Union[JSONResponse, HTTPException]:
    """Get a site description from a unique identifier."""
    rtn = BACKEND.get_site(site_id)
    if not rtn:
        raise SiteNotFound(site_id)
    return JSONResponse(rtn)


@api_version(1)
@app.put(
    "/sites/{site_id}/enable",
    responses={
        200: {"model": models.response.SiteEnableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Sites"],
    summary="Unset a site from being force disabled",
)
@handle_exceptions
async def set_site_enabled(
    request: Request,
    site_id: str = Path(description="Site ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_site_force_disabled_flag(site_id, False)
    if not response:
        raise SiteNotFound(site_id)
    return JSONResponse(response)


@api_version(1)
@app.put(
    "/sites/{site_id}/disable",
    responses={
        200: {"model": models.response.SiteDisableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Sites"],
    summary="Set a site to be force disabled",
)
@handle_exceptions
async def set_site_disabled(
    request: Request,
    site_id: str = Path(description="Site ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_site_force_disabled_flag(site_id, True)
    if not response:
        raise SiteNotFound(site_id)
    return JSONResponse(response)


@api_version(1)
@app.get(
    "/storages",
    responses={
        200: {"model": models.response.StoragesListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storages"],
    summary="List all storages",
)
@handle_exceptions
async def list_storages(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storages."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storages(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storages/grafana",
    responses={
        200: {"model": models.response.StoragesGrafanaResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Storages"],
    summary="List all storages (Grafana format)",
)
@handle_exceptions
async def list_storages_for_grafana(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storages in a format digestible by Grafana world map panels."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storages(
        node_names=node_names,
        site_names=site_names,
        for_grafana=True,
        include_inactive=include_inactive,
    )
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storages/topojson",
    responses={
        200: {"model": models.response.StoragesTopojsonResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Storages"],
    summary="List all storages (topojson format)",
)
@handle_exceptions
async def list_storages_in_topojson_format(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storages in topojson format."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storages(
        node_names=node_names,
        site_names=site_names,
        topojson=True,
        include_inactive=include_inactive,
    )
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storages/{storage_id}",
    responses={
        200: {"model": models.response.StorageGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storages"],
    summary="Get storage from id",
)
@handle_exceptions
async def get_storage_from_id(
    request: Request,
    storage_id: str = Path(description="Unique storage identifier"),
) -> Union[JSONResponse, HTTPException]:
    """Get a storage description from a unique identifier."""
    rtn = BACKEND.get_storage(storage_id)
    if not rtn:
        raise StorageNotFound(storage_id)
    return JSONResponse(rtn)


@api_version(1)
@app.put(
    "/storages/{storage_id}/enable",
    responses={
        200: {"model": models.response.StorageEnableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storages"],
    summary="Unset a storage from being force disabled",
)
@handle_exceptions
async def set_storage_enabled(
    request: Request,
    storage_id: str = Path(description="Storage ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_storage_force_disabled_flag(storage_id, False)
    return JSONResponse(response)


@api_version(1)
@app.put(
    "/storages/{storage_id}/disable",
    responses={
        200: {"model": models.response.StorageDisableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storages"],
    summary="Set a storage to be force disabled",
)
@handle_exceptions
async def set_storage_disabled(
    request: Request,
    storage_id: str = Path(description="Storage ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_storage_force_disabled_flag(storage_id, True)
    return JSONResponse(response)


@api_version(1)
@app.get(
    "/storage-areas",
    responses={
        200: {"model": models.response.StorageAreasListResponse},
        401: {},
        403: {},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storage Areas"],
    summary="List all storage areas",
)
@handle_exceptions
async def list_storage_areas(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storage areas."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storage_areas(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storage-areas/grafana",
    responses={
        200: {"model": models.response.StorageAreasGrafanaResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Storage Areas"],
    summary="List all storage areas (Grafana format)",
)
@handle_exceptions
async def list_storage_areas_for_grafana(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storage areas in a format digestible by Grafana world map panels."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storage_areas(
        node_names=node_names,
        site_names=site_names,
        for_grafana=True,
        include_inactive=include_inactive,
    )
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storage-areas/topojson",
    responses={
        200: {"model": models.response.StorageAreasTopojsonResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Storage Areas"],
    summary="List all storage areas (topojson format)",
)
@handle_exceptions
async def list_storage_areas_in_topojson_format(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive resources? e.g. in downtime, force disabled"),
) -> JSONResponse:
    """List all storage areas in topojson format."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = BACKEND.list_storage_areas(
        node_names=node_names,
        site_names=site_names,
        topojson=True,
        include_inactive=include_inactive,
    )
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storage-areas/types",
    responses={
        200: {"model": models.response.StorageAreasTypesResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Storage Areas"],
    summary="List storage area types",
)
@handle_exceptions
async def list_storage_area_types(request: Request) -> JSONResponse:
    """List storage area types."""
    try:
        dereferenced_storage_area_schema = load_and_dereference_schema(
            schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "storage-area"))).absolute()
        )
    except FileNotFoundError:
        raise SchemaNotFound
    rtn = BACKEND.list_storage_area_types_from_schema(schema=dereferenced_storage_area_schema)
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/storage-areas/{storage_area_id}",
    responses={
        200: {"model": models.response.StorageAreaGetResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storage Areas"],
    summary="Get storage area from id",
)
@handle_exceptions
async def get_storage_area_from_id(
    request: Request,
    storage_area_id: str = Path(description="Unique storage area identifier"),
) -> Union[JSONResponse, HTTPException]:
    """Get a storage area description from a unique identifier."""
    rtn = BACKEND.get_storage_area(storage_area_id)
    if not rtn:
        raise StorageAreaNotFound(storage_area_id)
    return JSONResponse(rtn)


@api_version(1)
@app.put(
    "/storage-areas/{storage_area_id}/enable",
    responses={
        200: {"model": models.response.StorageAreaEnableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storage Areas"],
    summary="Unset a storage area from being force disabled",
)
@handle_exceptions
async def set_storage_area_enabled(
    request: Request,
    storage_area_id: str = Path(description="Storage Area ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_storage_area_force_disabled_flag(storage_area_id, False)
    return JSONResponse(response)


@api_version(1)
@app.put(
    "/storage-areas/{storage_area_id}/disable",
    responses={
        200: {"model": models.response.StorageAreaDisableResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=(
        [Depends(increment_request_counter)]
        if DEBUG
        else [
            Depends(increment_request_counter),
            Depends(permission_dependencies.verify_permission_for_service_route),
        ]
    ),
    tags=["Storage Areas"],
    summary="Set a storage area to be force disabled",
)
@handle_exceptions
async def set_storage_area_disabled(
    request: Request,
    storage_area_id: str = Path(description="Storage Area ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[JSONResponse, HTTPException]:
    response = BACKEND.set_storage_area_force_disabled_flag(storage_area_id, True)
    return JSONResponse(response)


@api_version(1)
@app.get(
    "/www/docs/oper",
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
)
@handle_exceptions
async def oper_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get("README_MD", "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(readme_text_md, exclude_sections=["Deployment"])

    openapi_schema = request.scope.get("app").openapi_schema
    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
            "page_title": "Site Capabilities API Operator Documentation",
            "openapi_schema": openapi_schema_template.render(
                {"api_server_url": get_api_server_url_from_request(request, config.get("API_SCHEME", default="http"))}
            ),
            "readme_text_md": readme_text_html,
            "version": "v{version}".format(version=os.environ.get("SERVICE_VERSION")),
        },
    )


@api_version(1)
@app.get(
    "/www/docs/user",
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
)
@handle_exceptions
async def user_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get("README_MD", "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(
        readme_text_md,
        exclude_sections=["Authorisation", "Schemas", "Deployment"],
    )

    # Exclude unnecessary paths.
    paths_to_include = {
        "/nodes": ["get"],
        "/sites": ["get"],
        "/compute": ["get"],
        "/services": ["get"],
        "/storages": ["get"],
        "/storage-areas": ["get"],
        "/ping": ["get"],
        "/health": ["get"],
    }
    openapi_schema = copy.deepcopy(request.scope.get("app").openapi_schema)
    included_paths = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, attr in methods.items():
            if method in paths_to_include.get(path, []):
                if path not in included_paths:
                    included_paths[path] = {}
                included_paths[path][method] = attr
    openapi_schema.update({"paths": included_paths})

    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
            "page_title": "Site Capabilities API User Documentation",
            "openapi_schema": openapi_schema_template.render(
                {"api_server_url": get_api_server_url_from_request(request, config.get("API_SCHEME", default="http"))}
            ),
            "readme_text_md": readme_text_html,
            "version": "v{version}".format(version=os.environ.get("SERVICE_VERSION")),
        },
    )


@api_version(1)
@app.get(
    "/www/login",
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    summary="Login",
)
@handle_exceptions
async def www_login(
    request: Request, landing_page: str = Query(default=None, description="Landing page to redirect back to.")
) -> Union[HTMLResponse, RedirectResponse]:
    if request.session.get("access_token"):
        if request.session.get("landing_page"):
            return RedirectResponse(request.session.get("landing_page"))
        else:
            return HTMLResponse("You are logged in.")
    elif request.query_params.get("code"):
        # get token from authorization code
        code = request.query_params.get("code")
        original_request_url = request.url.remove_query_params(keys=["code", "state"])
        response = AUTH.token(code=code, redirect_uri=original_request_url)

        # exchange token for site-capabilities-api
        access_token = response.json().get("token", {}).get("access_token")
        if access_token:
            response = AUTH.exchange_token(service="site-capabilities-api", access_token=access_token)
            request.session["access_token"] = response.json().get("access_token")

        # redirect back now we have a valid token
        return RedirectResponse(original_request_url)
    else:
        # start login process
        request.session["landing_page"] = landing_page  # if being redirected from /www/sites
        redirect_uri = request.url.remove_query_params(keys=["landing_page"])
        response = AUTH.login(flow="legacy", redirect_uri=redirect_uri)
        authorization_uri = response.json().get("authorization_uri")
        return RedirectResponse(authorization_uri)


@api_version(1)
@app.get(
    "/www/logout",
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    summary="Logout",
)
@handle_exceptions
async def www_logout(request: Request) -> Union[HTMLResponse]:
    if request.session.get("access_token"):
        request.session.pop("access_token")
    return HTMLResponse("You are logged out. Click <a href=" + get_url_for_app_from_request("www_login", request) + ">here</a> to login.")


@api_version(1)
@app.get(
    "/www/nodes",
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Nodes"],
    summary="Add node form",
)
@handle_exceptions
async def add_node_form(
    request: Request,
) -> Union[TEMPLATES.TemplateResponse, RedirectResponse]:
    """Web form to add a new node with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not DEBUG:
            try:
                rtn = PERMISSIONS.authorise_service_route(
                    service=PERMISSIONS_SERVICE_NAME,
                    version=PERMISSIONS_SERVICE_VERSION,
                    route=request.scope["route"].path,
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied

        # Load schema.
        schema = load_and_dereference_schema(schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "node.json")).absolute())
        downtime_schema = load_and_dereference_schema(
            schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "downtime.json")).absolute()
        )
        # Remove sites
        schema.get("properties", {}).pop("sites")

        return TEMPLATES.TemplateResponse(
            "node.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "title": "Add SRCNet Node",
                "form_name": "add-node-form-ui.js",
                "downtime_schema": downtime_schema,
                "downtime_scheduler_form": "downtime-scheduler-form-ui.js",
                "downtime_values": {},
                "submit_form_endpoint": get_url_for_app_from_request(
                    "add_node",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": {},
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@app.get(
    "/www/nodes/{node_name}",
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Nodes"],
    summary="Edit existing node form",
)
@handle_exceptions
async def edit_node_form(request: Request, node_name: str) -> Union[TEMPLATES.TemplateResponse, HTMLResponse]:
    """Web form to edit an existing node with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not DEBUG:
            try:
                rtn = PERMISSIONS.authorise_service_route(
                    service=PERMISSIONS_SERVICE_NAME,
                    version=PERMISSIONS_SERVICE_VERSION,
                    route=request.scope["route"].path,
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied

        # Load schema.
        schema = load_and_dereference_schema(schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "node.json")).absolute())
        downtime_schema = load_and_dereference_schema(
            schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "downtime.json")).absolute()
        )
        # Get latest values for requested node.
        node = BACKEND.get_node(node_name=node_name)
        if not node:
            raise NodeVersionNotFound(node_name=node_name, node_version="latest")

        # Pop comments from version.
        try:
            node.pop("comments")
        except KeyError:
            pass

        # Quote nested JSON "other_attribute" dictionaries otherwise JSONForm parses as
        # [Object object].
        node = recursive_stringify(node)

        return TEMPLATES.TemplateResponse(
            "node.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "downtime_schema": downtime_schema,
                "title": "Edit SRCNet Node ({})".format(node_name),
                "form_name": "edit-node-form-ui.js",
                "downtime_scheduler_form": "downtime-scheduler-form-ui.js",
                "submit_form_endpoint": get_url_for_app_from_request(
                    "edit_node",
                    request,
                    path_params=request.path_params,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": node,
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@app.get(
    "/www/downtime/{node_name}",
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Nodes"],
    summary="Edit existing node form",
)
@handle_exceptions
async def get_downtime_statusboard(request: Request, node_name: str) -> Union[TEMPLATES.TemplateResponse, HTMLResponse]:
    """Dashboard to get all the downtimes for node."""
    if request.session.get("access_token"):
        # Check access permissions.
        # if not DEBUG:
        #     try:
        #         rtn = PERMISSIONS.authorise_service_route(
        #             service=PERMISSIONS_SERVICE_NAME,
        #             version=PERMISSIONS_SERVICE_VERSION,
        #             route=request.scope["route"].path,
        #             method=request.method,
        #             token=request.session.get("access_token"),
        #             body=request.path_params,
        #         ).json()
        #     except Exception as err:
        #         raise err
        #     if not rtn.get("is_authorised", False):
        #         raise PermissionDenied

        # Get latest values for requested node.
        node = BACKEND.get_node(node_name=node_name)
        if not node:
            raise NodeVersionNotFound(node_name=node_name, node_version="latest")

        # Pop comments from version.
        try:
            node.pop("comments")
        except KeyError:
            pass

        node = recursive_stringify(node)

        return TEMPLATES.TemplateResponse(
            "downtime-statusboard.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "title": "Downtimes SRCNet Node ({})".format(node_name),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": node,
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


# TODO
@api_version(1)
@app.get(
    "/www/reports/services",
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Reports"],
    summary="Services report",
)
@handle_exceptions
async def report_overview(request: Request) -> Union[TEMPLATES.TemplateResponse, RedirectResponse]:
    """Services report."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not DEBUG:
            try:
                rtn = PERMISSIONS.authorise_service_route(
                    service=PERMISSIONS_SERVICE_NAME,
                    version=PERMISSIONS_SERVICE_VERSION,
                    route=request.scope["route"].path,
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied
        return TEMPLATES.TemplateResponse(
            "services-report.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "title": "Services Report for SRCNet nodes",
                "data": BACKEND.list_nodes(include_archived=False, include_inactive=True),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@app.get(
    "/www/topology",
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Topology"],
    summary="Topology",
)
@handle_exceptions
async def topology(request: Request) -> Union[TEMPLATES.TemplateResponse, RedirectResponse]:
    """Topology."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not DEBUG:
            try:
                rtn = PERMISSIONS.authorise_service_route(
                    service=PERMISSIONS_SERVICE_NAME,
                    version=PERMISSIONS_SERVICE_VERSION,
                    route=request.scope["route"].path,
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied
        return TEMPLATES.TemplateResponse(
            "topology.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "title": "Topology of SRCNet",
                "data": BACKEND.list_nodes(include_archived=False, include_inactive=True),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@app.get(
    "/ping",
    responses={200: {"model": models.response.PingResponse}},
    tags=["Status"],
    summary="Check API status",
)
@handle_exceptions
async def ping(request: Request):
    """Service aliveness."""
    return JSONResponse(
        {
            "status": "UP",
            "version": os.environ.get("SERVICE_VERSION"),
        }
    )


@api_version(1)
@app.get(
    "/health",
    responses={
        200: {"model": models.response.HealthResponse},
        500: {"model": models.response.HealthResponse},
    },
    tags=["Status"],
    summary="Check API health",
)
@handle_exceptions
async def health(request: Request):
    """Service health.

    This endpoint will return a 500 if any of the dependent services are down.
    """

    # Dependent services.
    #
    # Permissions API
    #
    try:
        response = PERMISSIONS.ping()
        permissions_api_healthy = response.status_code == 200
    except Exception:
        permissions_api_healthy = False

    # Auth API
    #
    try:
        response = AUTH.ping()
        auth_api_healthy = response.status_code == 200
    except Exception:
        auth_api_healthy = False

    # Set return code dependent on criteria e.g. dependent service statuses
    #
    healthy_criteria = [permissions_api_healthy, auth_api_healthy]
    return JSONResponse(
        status_code=status.HTTP_200_OK if all(healthy_criteria) else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "uptime": round(time.time() - SERVICE_START_TIME),
            "number_of_managed_requests": REQUESTS_COUNTER,
            "dependent_services": {
                "permissions-api": {
                    "status": "UP" if permissions_api_healthy else "DOWN",
                },
                "auth-api": {
                    "status": "UP" if auth_api_healthy else "DOWN",
                },
            },
        },
    )


# Versionise the API.
#
versions = versionize(app=app, prefix_format="/v{major}", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Customise openapi.json.
#
# - Add schema server, title and tags.
# - Add request code samples to routes.
# - Remove 422 responses.
#
for route in app.routes:
    if isinstance(route.app, FastAPI):  # find any FastAPI subapplications (e.g. /v1/, /v2/, ...)
        subapp = route.app
        subapp_base_path = "{}{}".format(os.environ.get("API_ROOT_PATH", default=""), route.path)
        subapp.openapi()
        subapp.openapi_schema["servers"] = [{"url": subapp_base_path}]
        subapp.openapi_schema["info"]["title"] = "Site Capabilities API Overview"
        subapp.openapi_schema["tags"] = [
            {
                "name": "Nodes",
                "description": "Operations on nodes.",
                "x-tag-expanded": False,
            },
            {
                "name": "Sites",
                "description": "Operations on sites.",
                "x-tag-expanded": False,
            },
            {
                "name": "Compute",
                "description": "Operations on site compute.",
                "x-tag-expanded": False,
            },
            {
                "name": "Reports",
                "description": "Reports",
                "x-tag-expanded": False,
            },
            {
                "name": "Storages",
                "description": "Operations on site storages.",
                "x-tag-expanded": False,
            },
            {
                "name": "Storage Areas",
                "description": "Operations on site storage areas.",
                "x-tag-expanded": False,
            },
            {
                "name": "Services",
                "description": "Operations on site services.",
                "x-tag-expanded": False,
            },
            {
                "name": "Schemas",
                "description": "Schema operations.",
                "x-tag-expanded": False,
            },
            {
                "name": "Status",
                "description": "Operations describing the status of the API.",
                "x-tag-expanded": False,
            },
        ]
        # add request code samples and strip out 422s
        for language in ["shell", "python", "go", "js"]:
            for path, methods in subapp.openapi_schema["paths"].items():
                path = path.strip("/")
                for method, attr in methods.items():
                    if attr.get("responses", {}).get("422"):
                        del attr.get("responses")["422"]
                    method = method.strip("/")
                    sample_template_filename = "{}-{}-{}.j2".format(language, path, method).replace("/", "-")
                    sample_template_path = os.path.join("request-code-samples", sample_template_filename)
                    if os.path.exists(sample_template_path):
                        with open(sample_template_path, "r") as f:
                            sample_source_template = f.read()
                        code_samples = attr.get("x-code-samples", [])
                        code_samples.append(
                            {
                                "lang": language,
                                "source": str(sample_source_template),  # rendered later in route
                            }
                        )
                        attr["x-code-samples"] = code_samples
