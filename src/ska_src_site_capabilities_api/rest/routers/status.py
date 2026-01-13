import os
import time

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response
from fastapi_versionizer.versionizer import api_version
from prometheus_client import REGISTRY, generate_latest
from ska_src_logging import LogContext
from starlette.requests import Request

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.exceptions import handle_exceptions
from ska_src_site_capabilities_api.rest.logger import logger

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
    with LogContext(resource_id="status", operation="ping"):
        logger.debug("Ping request received")
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
    with LogContext(resource_id="status", operation="health_check"):
        logger.info("Health check requested")

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
        health_status = "healthy" if all(healthy_criteria) else "unhealthy"
        logger.info(f"Health check result: {health_status}")

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


@status_router.get(
    "/metrics",
    response_class=Response,
    responses={200: {"description": "Prometheus metrics"}},
    tags=["Status"],
    summary="Prometheus metrics endpoint",
    include_in_schema=False,  # Don't show in OpenAPI docs
)
async def metrics():
    """Expose Prometheus metrics.

    This endpoint returns metrics in Prometheus text format for scraping.
    Metrics include log counts, HTTP request stats, and other application metrics.
    """
    return Response(content=generate_latest(REGISTRY), media_type="text/plain; version=0.0.4")
