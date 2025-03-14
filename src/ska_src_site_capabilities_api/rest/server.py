import ast
import asyncio
import copy
import io
import json
import os
import pathlib
import tempfile
import time
import uuid
from datetime import datetime
from typing import Union

import jsonref
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
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common import constants
from ska_src_site_capabilities_api.common.exceptions import (
    ComputeNotFound,
    PermissionDenied,
    SchemaNotFound,
    ServiceNotFound,
    SiteNotFound,
    SiteVersionNotFound,
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
)
from ska_src_site_capabilities_api.db.backend import MongoBackend
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
async def list_compute(request: Request) -> JSONResponse:
    """List all compute."""
    rtn = BACKEND.list_compute()
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
async def get_schema(
    request: Request, schema: str = Path(description="Schema name")
) -> Union[JSONResponse, HTTPException]:
    """Get a schema by name."""
    try:
        schema_path = pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        return JSONResponse(ast.literal_eval(str(dereferenced_schema)))  # some issue with jsonref return != dict
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
async def render_schema(
    request: Request, schema: str = Path(description="Schema name")
) -> Union[JSONResponse, HTTPException]:
    """Render a schema by name."""
    try:
        schema_path = pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = ast.literal_eval(str(jsonref.load(f, base_uri=schema_path.as_uri())))
    except FileNotFoundError:
        raise SchemaNotFound

    # pop countries enum for readability
    dereferenced_schema.get("properties").get("country", {}).pop("enum", None)

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
        200: {"model": models.response.ServicesResponse},
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
    include_associated_with_compute: bool = Query(
        default=True, description="Include services associated with compute?"
    ),
    include_disabled: bool = Query(default=False, description="Include disabled services?"),
    service_type: str = Query(default=None, description="Filter by service type"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    compute_id: str = Query(default=None, description="Filter by compute ID"),
) -> JSONResponse:
    """List all services."""
    rtn = BACKEND.list_services(
        include_associated_with_compute=include_associated_with_compute,
        include_disabled=include_disabled,
        service_type=service_type,
        site_names=site_names,
        compute_id=compute_id,
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
        local_schema_path = pathlib.Path(
            "{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "local-service"))
        ).absolute()
        with open(local_schema_path) as f:
            dereferenced_local_schema = jsonref.load(f, base_uri=local_schema_path.as_uri())

        # global
        global_schema_path = pathlib.Path(
            "{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "global-service"))
        ).absolute()
        with open(global_schema_path) as f:
            dereferenced_global_schema = jsonref.load(f, base_uri=global_schema_path.as_uri())
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
@app.get(
    "/sites",
    responses={
        200: {"model": models.response.SitesListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Sites"],
    summary="List sites",
)
@handle_exceptions
async def list_sites(request: Request) -> JSONResponse:
    """List all sites."""
    rtn = BACKEND.list_site_names_unique()
    return JSONResponse(rtn)


@api_version(1)
@app.post(
    "/sites",
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
    tags=["Sites"],
    summary="Add a site",
)
@handle_exceptions
async def add_site(
    request: Request,
    values=Body(default="Site JSON."),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[HTMLResponse, HTTPException]:
    # add some custom fields e.g. date, user
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))
    values["created_at"] = datetime.now().isoformat()
    if DEBUG and not authorization:
        values["created_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["created_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    def recursive_autogen_id(data, autogen_keys=["id"], placeholder_value="to be assigned"):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in autogen_keys:
                    if value == placeholder_value:
                        data[key] = str(uuid.uuid4())
                elif isinstance(value, (dict, list)):
                    data[key] = recursive_autogen_id(value)
        elif isinstance(data, list):
            for i in range(len(data)):
                data[i] = recursive_autogen_id(data[i])
        return data

    values = recursive_autogen_id(values)

    id = BACKEND.add_site(values)
    return HTMLResponse(repr(id))


@api_version(1)
@app.post(
    "/sites/{site}",
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
    tags=["Sites"],
    summary="Edit a site",
)
@handle_exceptions
async def edit_site(
    request: Request,
    site: str = Path(description="Site name"),
    values=Body(default="Site JSON."),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> Union[HTMLResponse, HTTPException]:
    # add some custom fields e.g. date, user
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode("utf-8"))
    values["created_at"] = datetime.now().isoformat()
    if DEBUG and not authorization:
        values["created_by_username"] = "admin"
    else:
        access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
        values["created_by_username"] = access_token_decoded.get("preferred_username")

    # autogenerate ids for id keys
    def recursive_autogen_id(data, autogen_keys=["id"], placeholder_value="to be assigned"):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in autogen_keys:
                    if value == placeholder_value:
                        data[key] = str(uuid.uuid4())
                elif isinstance(value, (dict, list)):
                    data[key] = recursive_autogen_id(value)
        elif isinstance(data, list):
            for i in range(len(data)):
                data[i] = recursive_autogen_id(data[i])
        return data

    values = recursive_autogen_id(values)

    id = BACKEND.add_site(values)
    return HTMLResponse(repr(id))


@api_version(1)
@app.delete(
    "/sites",
    responses={
        200: {"model": models.response.GenericOperationResponse},
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
    summary="Delete all sites",
)
@handle_exceptions
async def delete_sites(request: Request) -> Union[JSONResponse, HTTPException]:
    """Delete all sites."""
    BACKEND.delete_sites()
    return JSONResponse({"successful": True})


@api_version(1)
@app.get(
    "/sites/dump",
    responses={
        200: {"model": models.response.SitesDumpResponse},
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
    summary="Dump all versions of sites",
)
@handle_exceptions
async def dump_sites(request: Request) -> Union[HTMLResponse, HTTPException]:
    """Dump sites."""
    rtn = BACKEND.dump_sites()
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/sites/latest",
    responses={
        200: {"model": models.response.SitesGetResponse},
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
    summary="Get latest versions of all sites",
)
@handle_exceptions
async def get_sites_latest(
    request: Request,
) -> Union[JSONResponse, HTTPException]:
    """Get the latest version of all sites."""
    rtn = BACKEND.list_sites_version_latest()
    return JSONResponse(rtn)


@api_version(1)
@app.get(
    "/sites/{site}",
    responses={
        200: {"model": models.response.SitesGetResponse},
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
    summary="Get all versions of site",
)
@handle_exceptions
async def get_site_versions(
    request: Request, site: str = Path(description="Site name")
) -> Union[JSONResponse, HTTPException]:
    """Get all versions of a site."""
    rtn = BACKEND.get_site(site)
    if not rtn:
        raise SiteNotFound(site)
    return JSONResponse(rtn)


@api_version(1)
@app.delete(
    "/sites/{site}",
    responses={
        200: {"model": models.response.GenericOperationResponse},
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
    summary="Delete all versions of site",
)
@handle_exceptions
async def delete_site(
    request: Request, site: str = Path(description="Site name")
) -> Union[JSONResponse, HTTPException]:
    """Delete all versions of a site."""
    rtn = BACKEND.delete_site(site)
    if rtn.deleted_count == 0:
        raise SiteNotFound(site)
    return JSONResponse({"successful": True})


@api_version(1)
@app.get(
    "/sites/{site}/{version}",
    responses={
        200: {"model": models.response.SiteGetVersionResponse},
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
    summary="Get version of site",
)
@handle_exceptions
async def get_site_version(
    request: Request,
    site: str = Path(description="Site name"),
    version: str = Path(example="latest", description="Site version"),
) -> HTMLResponse:
    """Get a version of a site."""
    if version == "latest":
        rtn = BACKEND.get_site_version_latest(site)
    else:
        rtn = BACKEND.get_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(rtn)


@api_version(1)
@app.delete(
    "/sites/{site}/{version}",
    responses={
        200: {"model": models.response.GenericOperationResponse},
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
    summary="Delete version of site",
)
@handle_exceptions
async def delete_site_version(
    request: Request,
    site: str = Path(description="Site name."),
    version: str = Path(example="latest", description="Site version"),
) -> Union[JSONResponse, HTTPException]:
    """Delete a version of a site."""
    rtn = BACKEND.delete_site_version(site, version)
    if rtn.deleted_count == 0:
        raise SiteVersionNotFound(site, version)
    return JSONResponse({"successful": True})


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
async def list_storages(request: Request) -> JSONResponse:
    """List all storages."""
    rtn = BACKEND.list_storages()
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
async def list_storages_for_grafana(request: Request) -> JSONResponse:
    """List all storages in a format digestible by Grafana world map panels."""
    rtn = BACKEND.list_storages(for_grafana=True)
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
async def list_storages_in_topojson_format(request: Request) -> JSONResponse:
    """List all storages in topojson format."""
    rtn = BACKEND.list_storages(topojson=True)
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
async def list_storages(request: Request) -> JSONResponse:
    """List all storage areas."""
    rtn = BACKEND.list_storage_areas()
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
async def list_storage_areas_for_grafana(request: Request) -> JSONResponse:
    """List all storage areas in a format digestible by Grafana world map panels."""
    rtn = BACKEND.list_storage_areas(for_grafana=True)
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
) -> JSONResponse:
    """List all storage areas in topojson format."""
    rtn = BACKEND.list_storage_areas(topojson=True)
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
        storage_area_schema_path = pathlib.Path(
            "{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "storage-area"))
        ).absolute()
        with open(storage_area_schema_path) as f:
            dereferenced_storage_area_schema = jsonref.load(f, base_uri=storage_area_schema_path.as_uri())
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
        "/sites": ["get"],
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
async def www_login(request: Request) -> Union[HTMLResponse, RedirectResponse]:
    if request.session.get("access_token"):
        return HTMLResponse("You are logged in.")
    elif request.query_params.get("code"):
        # get token from authorization code
        code = request.query_params.get("code")
        original_request_uri = request.url.remove_query_params(keys=["code", "state"])
        response = AUTH.token(code=code, redirect_uri=original_request_uri)

        # exchange token for site-capabilities-api
        access_token = response.json().get("token", {}).get("access_token")
        if access_token:
            response = AUTH.exchange_token(service="site-capabilities-api", access_token=access_token)
            request.session["access_token"] = response.json().get("access_token")

        # redirect back now we have a valid token
        return RedirectResponse(original_request_uri)
    else:
        # start login process
        response = AUTH.login(flow="legacy", redirect_uri=request.url)
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
    return HTMLResponse(
        "You are logged out. Click <a href="
        + get_url_for_app_from_request("www_login", request)
        + ">here</a> to login."
    )


@api_version(1)
@app.get(
    "/www/sites/add",
    responses={200: {}, 401: {}, 403: {}},
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Sites"],
    summary="Add site form",
)
@handle_exceptions
async def add_site_form(
    request: Request,
) -> Union[TEMPLATES.TemplateResponse, RedirectResponse]:
    """Web form to add a new site with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
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

        # Get schema.
        schema_path = pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "site.json")).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        schema = ast.literal_eval(str(dereferenced_schema))
        return TEMPLATES.TemplateResponse(
            "site.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "add_site_url": get_url_for_app_from_request(
                    "add_site",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
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
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + ">login</a> first."
        )


@api_version(1)
@app.get(
    "/www/sites/add/{site}",
    responses={200: {}, 401: {}, 403: {}},
    dependencies=[Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter)],
    tags=["Sites"],
    summary="Update existing site form",
)
@handle_exceptions
async def add_site_form_existing(request: Request, site: str) -> Union[TEMPLATES.TemplateResponse, HTMLResponse]:
    """Web form to update an existing site with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
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

        # Get schema.
        schema_path = pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "site.json")).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        schema = ast.literal_eval(str(dereferenced_schema))

        # Get latest values for requested site.
        latest = BACKEND.get_site_version_latest(site)
        if not latest:
            raise SiteVersionNotFound(site, "latest")
        try:
            latest.pop("comments")
        except KeyError:
            pass

        # Quote nested JSON "other_attribute" dictionaries otherwise JSONForm parses as [Object object].
        def recursive_stringify(data, stringify_keys=["other_attributes"]):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in stringify_keys:
                        data[key] = json.dumps(value)
                    elif isinstance(value, (dict, list)):
                        data[key] = recursive_stringify(value)
            elif isinstance(data, list):
                for i in range(len(data)):
                    data[i] = recursive_stringify(data[i])
            return data

        latest = recursive_stringify(latest)

        return TEMPLATES.TemplateResponse(
            "site.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "add_site_url": get_url_for_app_from_request(
                    "edit_site",
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
                "values": latest,
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + ">login</a> first."
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
    permissions_api_response = PERMISSIONS.ping()

    # Set return code dependent on criteria e.g. dependent service statuses
    #
    healthy_criteria = [permissions_api_response.status_code == 200]
    return JSONResponse(
        status_code=status.HTTP_200_OK if all(healthy_criteria) else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "uptime": round(time.time() - SERVICE_START_TIME),
            "number_of_managed_requests": REQUESTS_COUNTER,
            "dependent_services": {
                "permissions-api": {
                    "status": "UP" if permissions_api_response.status_code == 200 else "DOWN",
                }
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
