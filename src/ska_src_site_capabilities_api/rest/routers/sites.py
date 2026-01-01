import os

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import SiteNotFound, handle_exceptions
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions

sites_router = APIRouter()


@api_version(1)
@sites_router.get(
    "/sites",
    responses={
        200: {"model": models.response.SitesListResponse},
        401: {},
        403: {},
    },
    dependencies=[Depends(Common.increment_requests_counter_depends)]
    + (
        []
        if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
        else [Depends(Permissions.conditional_verify_permission_for_service_route_depends)]
    ),
    tags=["Sites"],
    summary="List all sites",
)
@handle_exceptions
async def list_sites(
    request: Request,
    only_names: bool = Query(default=False, description="Return only site names"),
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    include_inactive: bool = Query(
        default=False,
        description="Include inactive resources? e.g. in downtime, force disabled",
    ),
) -> JSONResponse:
    """List versions of all sites."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]

    rtn = request.app.state.backend.list_sites(node_names=node_names, include_inactive=include_inactive)
    if only_names:
        names = [site["name"] for site in rtn if "name" in site]
        return JSONResponse(names)

    return JSONResponse(rtn)


@api_version(1)
@sites_router.get(
    "/sites/{site_id}",
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
    summary="Get site from id",
)
@handle_exceptions
async def get_site_from_id(
    request: Request,
    site_id: str = Path(description="Unique site identifier"),
) -> JSONResponse:
    """Get a site description from a unique identifier."""
    rtn = request.app.state.backend.get_site(site_id)
    if not rtn:
        raise SiteNotFound(site_id)
    return JSONResponse(rtn)


@api_version(1)
@sites_router.put(
    "/sites/{site_id}/enable",
    response_model=None,
    responses={
        200: {"model": models.response.SiteEnableResponse},
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
    summary="Unset a site from being force disabled",
)
@handle_exceptions
async def set_site_enabled(
    request: Request,
    site_id: str = Path(description="Site ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    response = request.app.state.backend.set_site_force_disabled_flag(site_id, False)
    if not response:
        raise SiteNotFound(site_id)
    return JSONResponse(response)


@api_version(1)
@sites_router.put(
    "/sites/{site_id}/disable",
    response_model=None,
    responses={
        200: {"model": models.response.SiteDisableResponse},
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
    summary="Set a site to be force disabled",
)
@handle_exceptions
async def set_site_disabled(
    request: Request,
    site_id: str = Path(description="Site ID"),
    authorization=Depends(HTTPBearer(auto_error=False)),
) -> JSONResponse:
    response = request.app.state.backend.set_site_force_disabled_flag(site_id, True)
    if not response:
        raise SiteNotFound(site_id)
    return JSONResponse(response)
