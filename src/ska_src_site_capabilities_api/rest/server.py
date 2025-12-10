import logging
import os
import time

from authlib.integrations.requests_client import OAuth2Session
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versionizer.versionizer import versionize
from ska_src_authn_api.client.authentication import AuthenticationClient
from ska_src_permissions_api.client.permissions import PermissionsClient
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from ska_src_site_capabilities_api.backend.mongo import MongoBackend
from ska_src_site_capabilities_api.common import constants
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

# Instantiate FastAPI app and add some resources that are shared between routers.
# See (http://starlette.io/applications/#storing-state-on-the-app-instance)
#
# The following resources are accessible through request.state.app:
#
# - Debug mode i.e. whether to run service unauthenticated (debug)
# - j2 templates (templates)
# - Service version (service_version)
# - Permissions service name and version (permissions_service_name & permissions_service_version)
# - Common dependencies (common_dependencies)
# - Permissions based dependencies (permissions_dependencies)
# - OAuth2 request session for the ska_src_site_capabilities_api client (api_iam_client).
# - IAM endpoints (iam_endpoints).
# - Mongo backend (backend).
# - Authentication client for browser based www/ routes (auth).
# - Service start time (service_start_time).
#
app = FastAPI()
app.state.debug = config.get("DISABLE_AUTHENTICATION", default=None) == "yes"
app.state.templates = Jinja2Templates(directory="templates")
app.state.service_version = os.environ.get("SERVICE_VERSION")
app.state.permissions_service_name = config.get("PERMISSIONS_SERVICE_NAME")
app.state.permissions_service_version = config.get("PERMISSIONS_SERVICE_VERSION")
app.state.common_dependencies = dependencies.Common()
app.state.permissions_dependencies = dependencies.Permissions(
    permissions=PermissionsClient(config.get("PERMISSIONS_API_URL")),
    permissions_service_name=app.state.permissions_service_name,
    permissions_service_version=app.state.permissions_service_version,
)
app.state.api_iam_client = OAuth2Session(
    config.get("API_IAM_CLIENT_ID"), config.get("API_IAM_CLIENT_SECRET"), scope=config.get("API_IAM_CLIENT_SCOPES", default="")
)
app.state.iam_endpoints = constants.IAM(client_conf_url=config.get("IAM_CLIENT_CONF_URL"))
app.state.backend = MongoBackend(
    mongo_username=config.get("MONGO_USERNAME"),
    mongo_password=config.get("MONGO_PASSWORD"),
    mongo_host=config.get("MONGO_HOST"),
    mongo_port=config.get("MONGO_PORT"),
    mongo_database=config.get("MONGO_DATABASE"),
)
app.state.auth = AuthenticationClient(config.get("AUTH_API_URL"))
app.state.service_start_time = time.time()

# Add CORS middleware. Static mounts must be added later after the versionize() call.
#
CORSMiddleware_params = {"allow_origins": ["*"], "allow_credentials": True, "allow_methods": ["*"], "allow_headers": ["*"]}
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
        subapp.state = app.state  # copy original app state to all subapps
        subapp_base_path = "{}{}".format(os.environ.get("API_ROOT_PATH", default=""), route.path)
        subapp.openapi()
        subapp.openapi_schema["servers"] = [{"url": subapp_base_path}]
        subapp.openapi_schema["info"]["title"] = "Site Capabilities API Overview"
        subapp.openapi_schema["tags"] = [
            {
                "name": "Nodes",
                "description": "Operations on nodes.",
                "x-tag-expanded": False,
            },
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
                        with open(sample_template_path, "r", encoding="utf-8") as f:
                            sample_source_template = f.read()
                        code_samples = attr.get("x-code-samples", [])
                        code_samples.append({"lang": language, "source": str(sample_source_template)})
                        attr["x-code-samples"] = code_samples
