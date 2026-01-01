import os

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import ComputeNotFound, handle_exceptions
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions

compute_router = APIRouter()


@api_version(1)
@compute_router.get(
    "/compute",
    responses={
        200: {"model": models.response.ComputeListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Compute"],
    summary="List all compute",
)
@handle_exceptions
async def list_compute(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List all compute."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    rtn = request.app.state.backend.list_compute(node_names=node_names, site_names=site_names, include_inactive=include_inactive)
    return JSONResponse(rtn)


@api_version(1)
@compute_router.get(
    "/compute/{compute_id}",
    response_model=None,
    responses={
        200: {"model": models.response.ComputeGetResponse},
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
    tags=["Compute"],
    summary="Get compute from id",
)
@handle_exceptions
async def get_compute_from_id(
    request: Request,
    compute_id: str = Path(description="Unique compute identifier"),
) -> JSONResponse:
    """Get description of a compute element from a unique identifier."""
    rtn = request.app.state.backend.get_compute(compute_id)
    if not rtn:
        raise ComputeNotFound(compute_id)
    return JSONResponse(rtn)


@api_version(1)
@compute_router.put(
    "/compute/{compute_id}/enable",
    response_model=None,
    responses={
        200: {"model": models.response.ComputeEnableResponse},
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
    tags=["Compute"],
    summary="Unset a compute from being force disabled",
)
@handle_exceptions
async def set_compute_enabled(
    request: Request,
    compute_id: str = Path(description="Compute ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    response = request.app.state.backend.set_compute_force_disabled_flag(compute_id, False)
    return JSONResponse(response)


@api_version(1)
@compute_router.put(
    "/compute/{compute_id}/disable",
    response_model=None,
    responses={
        200: {"model": models.response.ComputeDisableResponse},
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
    tags=["Compute"],
    summary="Set a compute to be force disabled",
)
@handle_exceptions
async def set_compute_disabled(
    request: Request,
    compute_id: str = Path(description="Compute ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    response = request.app.state.backend.set_compute_force_disabled_flag(compute_id, True)
    return JSONResponse(response)
