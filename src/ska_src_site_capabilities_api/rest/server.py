import logging
import os
import time
from contextlib import asynccontextmanager

from authlib.integrations.requests_client import OAuth2Session
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versionizer import Versionizer
from ska_src_auth_api.client.authentication import AuthenticationClient
from ska_src_permissions_api.client.permissions import PermissionsClient
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from ska_src_site_capabilities_api.backend.mongo import MongoBackend
from ska_src_site_capabilities_api.common import constants
from ska_src_site_capabilities_api.common.utility import create_custom_openapi_schema
from ska_src_site_capabilities_api.rest import dependencies
from ska_src_site_capabilities_api.rest.routers.compute import compute_router
from ska_src_site_capabilities_api.rest.routers.docs import docs_router
from ska_src_site_capabilities_api.rest.routers.nodes import nodes_router
from ska_src_site_capabilities_api.rest.routers.schemas import schemas_router
from ska_src_site_capabilities_api.rest.routers.services import services_router
from ska_src_site_capabilities_api.rest.routers.sites import sites_router
from ska_src_site_capabilities_api.rest.routers.status import status_router
from ska_src_site_capabilities_api.rest.routers.storage_areas import storage_areas_router
from ska_src_site_capabilities_api.rest.routers.storages import storages_router

config = Config(".env")

# Set logging to use uvicorn logger.
#
logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes application state and resources on startup.
    """
    # Get instance of IAM constants
    iam_endpoints = constants.IAM(client_conf_url=config.get("IAM_CLIENT_CONF_URL"))

    # Instantiate a Permissions client
    permissions = PermissionsClient(config.get("PERMISSIONS_API_URL"))
    permissions_service_name = config.get("PERMISSIONS_SERVICE_NAME")
    permissions_service_version = config.get("PERMISSIONS_SERVICE_VERSION")

    # Instantiate permissions dependencies
    permissions_dependencies = dependencies.Permissions(
        permissions=permissions,
        permissions_service_name=permissions_service_name,
        permissions_service_version=permissions_service_version,
    )

    # Instantiate OAuth2 request session for the ska_src_site_capabilities_api client
    api_iam_client = OAuth2Session(
        config.get("API_IAM_CLIENT_ID"),
        config.get("API_IAM_CLIENT_SECRET"),
        scope=config.get("API_IAM_CLIENT_SCOPES", default=""),
    )

    # Instantiate Mongo backend
    backend = MongoBackend(
        mongo_username=config.get("MONGO_USERNAME"),
        mongo_password=config.get("MONGO_PASSWORD"),
        mongo_host=config.get("MONGO_HOST"),
        mongo_port=config.get("MONGO_PORT"),
        mongo_database=config.get("MONGO_DATABASE"),
    )

    # Instantiate authentication client for browser based www/ routes
    auth = AuthenticationClient(config.get("AUTH_API_URL"))

    # Store state in app
    app.state.iam_endpoints = iam_endpoints
    app.state.permissions_dependencies = permissions_dependencies
    app.state.api_iam_client = api_iam_client
    app.state.backend = backend
    app.state.auth = auth

    yield


# Instantiate FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Site CapabilitiesAPI Overview",
)

# Store app state (accessible through request.app.state)
app.state.debug = config.get("DISABLE_AUTHENTICATION", default=None) == "yes"
app.state.templates = Jinja2Templates(directory="templates")
app.state.service_version = os.environ.get("SERVICE_VERSION")
app.state.permissions_service_name = config.get("PERMISSIONS_SERVICE_NAME")
app.state.permissions_service_version = config.get("PERMISSIONS_SERVICE_VERSION")
app.state.common_dependencies = dependencies.Common()
app.state.service_start_time = time.time()

# Add CORS middleware. Static mounts must be added later after the versionize() call.
#
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

# Add routers.
#
app.include_router(docs_router)
app.include_router(nodes_router)
app.include_router(sites_router)
app.include_router(compute_router)
app.include_router(storages_router)
app.include_router(storage_areas_router)
app.include_router(services_router)
app.include_router(schemas_router)
app.include_router(status_router)


# Customize OpenAPI schema generation (must be set before versionize)
def custom_openapi():
    """Custom OpenAPI schema generator compatible with FastAPI 0.124+."""
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = create_custom_openapi_schema(app, logger)
    return app.openapi_schema


app.openapi = custom_openapi

# Versionize the API
versions = Versionizer(
    app=app,
    prefix_format="/v{major}",
    semantic_version_format="{major}",
).versionize()

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
