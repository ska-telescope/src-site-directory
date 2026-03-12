import os
import pathlib
from typing import Union

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from ska_src_logging import LogContext
from ska_src_logging.integrations.fastapi import extract_username_from_token
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import SchemaNotFound, ServiceNotFound, handle_exceptions
from ska_src_site_capabilities_api.common.utility import load_and_dereference_schema
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions
from ska_src_site_capabilities_api.rest.logger import logger

services_router = APIRouter()
config = Config(".env")


@api_version(1)
@services_router.get(
    "/services",
    responses={
        200: {"model": models.response.ServicesListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
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
    output: str = Query(
        default=None,
        description="Output format (e.g., 'prometheus' for Prometheus HTTP SD response)",
    ),
) -> JSONResponse:
    """List all services."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id="services", operation="list_services", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Listing services (scope={service_scope}, output={output}, include_inactive={include_inactive})")
        if node_names:
            node_names = [name.strip() for name in node_names.split(",")]
        if site_names:
            site_names = [name.strip() for name in site_names.split(",")]
        if service_types:
            service_types = [name.strip() for name in service_types.split(",")]

        for_prometheus = output == "prometheus"

        rtn = request.app.state.backend.list_services(
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
@services_router.get(
    "/services/types",
    responses={
        200: {"model": models.response.ServicesTypesResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Services"],
    summary="List service types",
)
@handle_exceptions
async def list_service_types(request: Request) -> JSONResponse:
    """List service types."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id="service_types", operation="list_service_types", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info("Listing service types")
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
            "local": request.app.state.backend.list_service_types_from_schema(schema=dereferenced_local_schema),
            "global": request.app.state.backend.list_service_types_from_schema(schema=dereferenced_global_schema),
        }
        return JSONResponse(rtn)


@api_version(1)
@services_router.get(
    "/services/{service_id}",
    response_model=None,
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
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Services"],
    summary="Get service from id",
)
@handle_exceptions
async def get_service_from_id(
    request: Request,
    service_id: str = Path(description="Unique service identifier"),
) -> JSONResponse:
    """Get a service description from a unique identifier."""
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    enduser_id = extract_username_from_token(token) if token else None
    with LogContext(resource_id=service_id, operation="get_service", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Retrieving service: {service_id}")
        rtn = request.app.state.backend.get_service(service_id)
        if not rtn:
            raise ServiceNotFound(service_id)
        return JSONResponse(rtn)


@api_version(1)
@services_router.put(
    "/services/{service_id}/enable",
    response_model=None,
    responses={
        200: {"model": models.response.ServiceEnableResponse},
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
    tags=["Services"],
    summary="Unset a service from being force disabled",
)
@handle_exceptions
async def set_service_enabled(
    request: Request,
    service_id: str = Path(description="Service ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    enduser_id = extract_username_from_token(authorization.credentials) if authorization else None
    with LogContext(resource_id=service_id, operation="enable_service", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Enabling service: {service_id}")
        response = request.app.state.backend.set_service_force_disabled_flag(service_id, False)
        if not response:
            raise ServiceNotFound(service_id)
        return JSONResponse(response)


@api_version(1)
@services_router.put(
    "/services/{service_id}/disable",
    response_model=None,
    responses={
        200: {"model": models.response.ServiceDisableResponse},
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
    tags=["Services"],
    summary="Set a service to be force disabled",
)
@handle_exceptions
async def set_service_disabled(
    request: Request,
    service_id: str = Path(description="Service ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    enduser_id = extract_username_from_token(authorization.credentials) if authorization else None
    with LogContext(resource_id=service_id, operation="disable_service", **({"enduser_id": enduser_id} if enduser_id else {})):
        logger.info(f"Disabling service: {service_id}")
        response = request.app.state.backend.set_service_force_disabled_flag(service_id, True)
        if not response:
            raise ServiceNotFound(service_id)
        return JSONResponse(response)
