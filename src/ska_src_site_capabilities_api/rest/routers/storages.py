import os

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from ska_src_logging import LogContext
from ska_src_logging.integrations.fastapi import extract_username_from_token
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import StorageNotFound, handle_exceptions
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions
from ska_src_site_capabilities_api.rest.logger import logger

storages_router = APIRouter()


@api_version(1)
@storages_router.get(
    "/storages",
    responses={
        200: {"model": models.response.StoragesListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Storages"],
    summary="List all storages",
)
@handle_exceptions
async def list_storages(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storages."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id="storages", operation="list_storages", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Listing storages (include_inactive={include_inactive})")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storages(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
        return JSONResponse(rtn)


@api_version(1)
@storages_router.get(
    "/storages/grafana",
    responses={
        200: {"model": models.response.StoragesGrafanaResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Storages"],
    summary="List all storages (Grafana format)",
)
@handle_exceptions
async def list_storages_for_grafana(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storages in a format digestible by Grafana world map panels."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id="storages", operation="list_storages_grafana", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info("Listing storages for Grafana")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storages(
            node_names=node_names,
            site_names=site_names,
            for_grafana=True,
            include_inactive=include_inactive,
        )
        return JSONResponse(rtn)


@api_version(1)
@storages_router.get(
    "/storages/topojson",
    responses={
        200: {"model": models.response.StoragesTopojsonResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Storages"],
    summary="List all storages (topojson format)",
)
@handle_exceptions
async def list_storages_in_topojson_format(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storages in topojson format."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id="storages", operation="list_storages_topojson", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info("Listing storages in topojson format")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storages(
            node_names=node_names,
            site_names=site_names,
            topojson=True,
            include_inactive=include_inactive,
        )
        return JSONResponse(rtn)


@api_version(1)
@storages_router.get(
    "/storages/{storage_id}",
    response_model=None,
    responses={
        200: {"model": models.response.StorageGetResponse},
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
    tags=["Storages"],
    summary="Get storage from id",
)
@handle_exceptions
async def get_storage_from_id(
    request: Request,
    storage_id: str = Path(description="Unique storage identifier"),
) -> JSONResponse:
    """Get a storage description from a unique identifier."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id=storage_id, operation="get_storage", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Retrieving storage: {storage_id}")
        rtn = request.app.state.backend.get_storage(storage_id)
        if not rtn:
            raise StorageNotFound(storage_id)
        return JSONResponse(rtn)


@api_version(1)
@storages_router.put(
    "/storages/{storage_id}/enable",
    response_model=None,
    responses={
        200: {"model": models.response.StorageEnableResponse},
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
    tags=["Storages"],
    summary="Unset a storage from being force disabled",
)
@handle_exceptions
async def set_storage_enabled(
    request: Request,
    storage_id: str = Path(description="Storage ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    enduser_id = extract_username_from_token(authorization.credentials) if authorization else None
    with LogContext(resource_id=storage_id, operation="enable_storage", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Enabling storage: {storage_id}")
        response = request.app.state.backend.set_storage_force_disabled_flag(storage_id, False)
        if not response:
            raise StorageNotFound(storage_id)
        return JSONResponse(response)


@api_version(1)
@storages_router.put(
    "/storages/{storage_id}/disable",
    response_model=None,
    responses={
        200: {"model": models.response.StorageDisableResponse},
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
    tags=["Storages"],
    summary="Set a storage to be force disabled",
)
@handle_exceptions
async def set_storage_disabled(
    request: Request,
    storage_id: str = Path(description="Storage ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    enduser_id = extract_username_from_token(authorization.credentials) if authorization else None
    with LogContext(resource_id=storage_id, operation="disable_storage", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Disabling storage: {storage_id}")
        response = request.app.state.backend.set_storage_force_disabled_flag(storage_id, True)
        if not response:
            raise StorageNotFound(storage_id)
        return JSONResponse(response)
