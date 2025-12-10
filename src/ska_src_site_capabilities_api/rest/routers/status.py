import os
import time

from fastapi import APIRouter, status
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import handle_exceptions

status_router = APIRouter()


@api_version(1)
@status_router.get(
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
@status_router.get(
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
        response = request.app.state.permissions_dependencies.permissions.ping()
        permissions_api_healthy = response.status_code == 200
    except Exception:
        permissions_api_healthy = False

    # Auth API
    #
    try:
        response = request.app.state.auth.ping()
        auth_api_healthy = response.status_code == 200
    except Exception:
        auth_api_healthy = False

    # Set return code dependent on criteria e.g. dependent service statuses
    #
    healthy_criteria = [permissions_api_healthy, auth_api_healthy]
    return JSONResponse(
        status_code=status.HTTP_200_OK if all(healthy_criteria) else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "uptime": round(time.time() - request.app.state.service_start_time),
            "number_of_managed_requests": request.app.state.common_dependencies.requests_counter,
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
