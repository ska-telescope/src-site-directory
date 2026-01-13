import os
import pathlib

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from ska_src_logging import LogContext
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import SchemaNotFound, StorageAreaNotFound, handle_exceptions
from ska_src_site_capabilities_api.common.utility import load_and_dereference_schema
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions
from ska_src_site_capabilities_api.rest.logger import logger

storage_areas_router = APIRouter()
config = Config(".env")


@api_version(1)
@storage_areas_router.get(
    "/storage-areas",
    responses={
        200: {"model": models.response.StorageAreasListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Storage Areas"],
    summary="List all storage areas",
)
@handle_exceptions
async def list_storage_areas(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storage areas."""
    with LogContext(resource_id="storage_areas", operation="list_storage_areas"):
        logger.info(f"Listing storage areas (include_inactive={include_inactive})")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storage_areas(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
        return JSONResponse(rtn)


@api_version(1)
@storage_areas_router.get(
    "/storage-areas/grafana",
    responses={
        200: {"model": models.response.StorageAreasGrafanaResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Storage Areas"],
    summary="List all storage areas (Grafana format)",
)
@handle_exceptions
async def list_storage_areas_for_grafana(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storage areas in a format digestible by Grafana world map panels."""
    with LogContext(resource_id="storage_areas", operation="list_storage_areas_grafana"):
        logger.info("Listing storage areas for Grafana")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storage_areas(
            node_names=node_names,
            site_names=site_names,
            for_grafana=True,
            include_inactive=include_inactive,
        )
        return JSONResponse(rtn)


@api_version(1)
@storage_areas_router.get(
    "/storage-areas/topojson",
    responses={
        200: {"model": models.response.StorageAreasTopojsonResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Storage Areas"],
    summary="List all storage areas (topojson format)",
)
@handle_exceptions
async def list_storage_areas_in_topojson_format(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all storage areas in topojson format."""
    with LogContext(resource_id="storage_areas", operation="list_storage_areas_topojson"):
        logger.info("Listing storage areas in topojson format")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]

        rtn = request.app.state.backend.list_storage_areas(
            node_names=node_names,
            site_names=site_names,
            topojson=True,
            include_inactive=include_inactive,
        )
        return JSONResponse(rtn)


@api_version(1)
@storage_areas_router.get(
    "/storage-areas/types",
    responses={
        200: {"model": models.response.StorageAreasTypesResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Storage Areas"],
    summary="List storage area types",
)
@handle_exceptions
async def list_storage_area_types(request: Request) -> JSONResponse:
    """List storage area types."""
    with LogContext(resource_id="storage_area_types", operation="list_storage_area_types"):
        logger.info("Listing storage area types")
        try:
            dereferenced_storage_area_schema = load_and_dereference_schema(
                schema_path=pathlib.Path("{}.json".format(os.path.join(config.get("SCHEMAS_RELPATH"), "storage-area"))).absolute()
            )
        except FileNotFoundError:
            raise SchemaNotFound
        rtn = request.app.state.backend.list_storage_area_types_from_schema(schema=dereferenced_storage_area_schema)
        return JSONResponse(rtn)


@api_version(1)
@storage_areas_router.get(
    "/storage-areas/{storage_area_id}",
    response_model=None,
    responses={
        200: {"model": models.response.StorageAreaGetResponse},
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
    tags=["Storage Areas"],
    summary="Get storage area from id",
)
@handle_exceptions
async def get_storage_area_from_id(
    request: Request,
    storage_area_id: str = Path(description="Unique storage area identifier"),
) -> JSONResponse:
    """Get a storage area description from a unique identifier."""
    with LogContext(resource_id=storage_area_id, operation="get_storage_area"):
        logger.info(f"Retrieving storage area: {storage_area_id}")
        rtn = request.app.state.backend.get_storage_area(storage_area_id)
        if not rtn:
            raise StorageAreaNotFound(storage_area_id)
        return JSONResponse(rtn)


@api_version(1)
@storage_areas_router.put(
    "/storage-areas/{storage_area_id}/enable",
    response_model=None,
    responses={
        200: {"model": models.response.StorageAreaEnableResponse},
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
    tags=["Storage Areas"],
    summary="Unset a storage area from being force disabled",
)
@handle_exceptions
async def set_storage_area_enabled(
    request: Request,
    storage_area_id: str = Path(description="Storage Area ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    with LogContext(resource_id=storage_area_id, operation="enable_storage_area"):
        logger.info(f"Enabling storage area: {storage_area_id}")
        response = request.app.state.backend.set_storage_area_force_disabled_flag(storage_area_id, False)
        return JSONResponse(response)


@api_version(1)
@storage_areas_router.put(
    "/storage-areas/{storage_area_id}/disable",
    response_model=None,
    responses={
        200: {"model": models.response.StorageAreaDisableResponse},
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
    tags=["Storage Areas"],
    summary="Set a storage area to be force disabled",
)
@handle_exceptions
async def set_storage_area_disabled(
    request: Request,
    storage_area_id: str = Path(description="Storage Area ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    with LogContext(resource_id=storage_area_id, operation="disable_storage_area"):
        logger.info(f"Disabling storage area: {storage_area_id}")
        response = request.app.state.backend.set_storage_area_force_disabled_flag(storage_area_id, True)
        return JSONResponse(response)
