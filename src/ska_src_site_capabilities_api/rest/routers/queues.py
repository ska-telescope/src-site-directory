import os

from fastapi import APIRouter, Depends, Path, Query
from fastapi_versionizer.versionizer import api_version
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import QueueNotFound, handle_exceptions
from ska_src_site_capabilities_api.rest.dependencies import Common, Permissions

queues_router = APIRouter()
config = Config(".env")

api_dependencies = (
    [Depends(Common.increment_requests_counter_depends)]
    if os.environ.get("DISABLE_AUTHENTICATION", "no") == "yes"
    else [
        Depends(Common.increment_requests_counter_depends),
        Depends(Permissions.conditional_verify_permission_for_service_route_depends),
    ]
)


@api_version(1)
@queues_router.get(
    "/queues",
    responses={
        200: {"model": models.response.QueuesListResponse},
        401: {},
        403: {},
    },
    dependencies=api_dependencies,
    tags=["Queues"],
    summary="List all queues",
)
@handle_exceptions
async def list_queues(
    request: Request,
    node_names: str = Query(default=None, description="Filter by node names (comma-separated)"),
    site_names: str = Query(default=None, description="Filter by site names (comma-separated)"),
    include_inactive: bool = Query(default=False, description="Include inactive (down/disabled) Queues?"),
) -> JSONResponse:
    """List all Queues."""
    if node_names:
        node_names = [name.strip() for name in node_names.split(",")]
    if site_names:
        site_names = [name.strip() for name in site_names.split(",")]

    queue_list_response = request.app.state.backend.list_queues(
        node_names=node_names,
        site_names=site_names,
        include_inactive=include_inactive,
    )
    return JSONResponse(queue_list_response)


@api_version(1)
@queues_router.get(
    "/queues/{queue_id}",
    responses={
        200: {"model": models.response.QueuesListResponse},
        401: {},
        403: {},
        404: {"model": models.response.GenericErrorResponse},
    },
    dependencies=api_dependencies,
    tags=["Queues"],
    summary="Get Queue from ID",
)
@handle_exceptions
async def get_queue_from_id(
    request: Request,
    queue_id: str = Path(description="Unique queue identifier"),
) -> JSONResponse:
    """Get Queue from ID."""

    queue = request.app.state.backend.get_queue_by_id(
        queue_id=queue_id,
    )
    if not queue:
        raise QueueNotFound(queue_id=queue_id)
    return JSONResponse(queue)
