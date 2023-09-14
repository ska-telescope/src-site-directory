import ast
import asyncio
import json
import jsonschema
import jwt
import operator
import os
import pprint
import requests
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Union

import jinja2
import jsonref
import uvicorn
from authlib.integrations.requests_client import OAuth2Session
from fastapi import FastAPI, Depends, File, Header, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versioning import VersionedFastAPI, version
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

import ska_src_site_capabilities_api
from ska_src_site_capabilities_api.common.constants import Constants
from ska_src_site_capabilities_api.common.exceptions import handle_exceptions, PermissionDenied, SchemaNotFound, \
    SiteNotFound, SiteVersionNotFound
from ska_src_site_capabilities_api.db.backend import MongoBackend
from ska_src_permissions_api.client.permissions import PermissionsClient

config = Config('.env')

# Debug mode (runs unauthenticated)
#
DEBUG = True if config.get("DISABLE_AUTHENTICATION", default=None) == 'yes' else False

# Instantiate FastAPI() allowing CORS. Middleware and static mounts are added later to the instance of a VersionedApp.
#
app = FastAPI()
CORSMiddleware_params = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}


# Add amended HTTPBearer authz.
#
security = HTTPBearer()

# Instantiate an OAuth2 request session for the ska-src-site-capabilities-api client.
#
API_IAM_CLIENT = OAuth2Session(config.get("API_IAM_CLIENT_ID"),
                               config.get("API_IAM_CLIENT_SECRET"),
                               scope=config.get("API_IAM_CLIENT_SCOPES", default=""))

# Get instance of Constants.
#
CONSTANTS = Constants(client_conf_url=config.get('IAM_CLIENT_CONF_URL'))

# Get templates.
#
TEMPLATES = Jinja2Templates(directory="templates")

# Instantiate the backend api.
#
BACKEND = MongoBackend(
    mongo_username=config.get('MONGO_USERNAME'),
    mongo_password=config.get('MONGO_PASSWORD'),
    mongo_host=config.get('MONGO_HOST'),
    mongo_port=config.get('MONGO_PORT'),
    mongo_database=config.get('MONGO_DATABASE')
)

# Instantiate the permissions client.
#
PERMISSIONS = PermissionsClient(config.get('PERMISSIONS_API_URL'))
PERMISSIONS_SERVICE_NAME = config.get('PERMISSIONS_SERVICE_NAME')
PERMISSIONS_SERVICE_VERSION = config.get('PERMISSIONS_SERVICE_VERSION')

# Store service start time.
#
SERVICE_START_TIME = time.time()

# Keep track of number of managed requests.
#
REQUESTS_COUNTER = 0
REQUESTS_COUNTER_LOCK = asyncio.Lock()

# Dependencies.
# -------------
#
# Increment the request counter.
#
@handle_exceptions
async def increment_request_counter(request: Request) -> Union[dict, HTTPException]:
    global REQUESTS_COUNTER
    async with REQUESTS_COUNTER_LOCK:
        REQUESTS_COUNTER += 1


# Check service route permissions from user token groups.
#
@handle_exceptions
async def verify_permission_for_service_route(request: Request, authorization: str = Depends(security)) \
        -> Union[HTTPException, bool]:
    if authorization.credentials is None:
        raise PermissionDenied
    access_token = authorization.credentials
    rtn = PERMISSIONS.authorise_route_for_service(service=PERMISSIONS_SERVICE_NAME, version=PERMISSIONS_SERVICE_VERSION,
                                                  route=request.scope['route'].path, method=request.method,
                                                  token=access_token, body=request.path_params).json()
    if rtn.get('is_authorised', False):
        return
    raise PermissionDenied


# FIXME: SSO.
# Check service route permissions from user token groups (taking token from query parameters).
#
@handle_exceptions
async def verify_permission_for_service_route_query_params(request: Request, token: str = None) \
        -> Union[HTTPException, bool]:
    if token is None:
        raise PermissionDenied
    rtn = PERMISSIONS.authorise_route_for_service(service=PERMISSIONS_SERVICE_NAME, version=PERMISSIONS_SERVICE_VERSION,
                                                  route=request.scope['route'].path, method=request.method,
                                                  token=token, body=request.path_params).json()
    if rtn.get('is_authorised', False):
        return
    raise PermissionDenied


# Routes
# ------
#
@app.get("/schemas", response_class=JSONResponse, dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_schemas(request: Request) -> JSONResponse:
    """ List schemas used to define sites, services and storages. """
    schema_basenames = sorted([''.join(fi.split('.')[:-1]) for fi in os.listdir(config.get('SCHEMAS_RELPATH'))])
    return JSONResponse(schema_basenames)


@app.get("/schemas/{schema}", response_class=JSONResponse, dependencies=[
    Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter),
                                                       Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_schema(request: Request, schema: str) -> Union[JSONResponse, HTTPException]:
    """ Get a particular schema. """
    try:
        schema_path = Path("{}.json".format(os.path.join(config.get('SCHEMAS_RELPATH'), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        return JSONResponse(ast.literal_eval(str(dereferenced_schema)))         # some issue with jsonref return != dict
    except FileNotFoundError:
        raise SchemaNotFound


@app.get('/services', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_services(request: Request) -> JSONResponse:
    """ List all services. """
    rtn = BACKEND.list_services()
    return JSONResponse(rtn)


@app.get('/sites', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_sites(request: Request) -> JSONResponse:
    """ List all sites. """
    rtn = BACKEND.list_site_names_unique()
    return JSONResponse(rtn)


#FIXME: uses sessions, see TODO.
@app.post("/sites", response_class=HTMLResponse, dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
async def add_site(request: Request, authorization = Depends(security)) -> Union[HTMLResponse, HTTPException]:
    values = await request.json()

    # add some custom fields e.g. date, user
    values['created_at'] = datetime.now().isoformat()
    access_token_decoded = jwt.decode(authorization.credentials, options={"verify_signature": False})
    values['created_by_username'] = access_token_decoded.get('preferred_username')

    # add ids for services
    services = values.get('services')
    if services:
        for service in services:
            if not service.get('id'):
                service['id'] = str(uuid.uuid4())

    # add ids for storages
    storages = values.get('storages')
    if storages:
        for storage in storages:
            if not storage.get('id'):
                storage['id'] = str(uuid.uuid4())

    id = BACKEND.add_site(values)
    return HTMLResponse(repr(id))


@app.delete('/sites', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def delete_sites(request: Request) -> Union[JSONResponse, HTTPException]:
    """ Delete all sites. """
    rtn = BACKEND.delete_sites()
    return JSONResponse(repr(rtn))


@app.post("/sites/bulk", response_class=HTMLResponse, dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def add_sites_bulk(request: Request, sites_file: UploadFile = File(...)) -> Union[HTMLResponse, HTTPException]:
    """ Bulk add sites from a file. """
    sites_bytes = await sites_file.read()
    sites_json = json.loads(sites_bytes.decode('UTF-8'))
    rtn = BACKEND.add_sites_bulk(sites_json)
    return HTMLResponse(repr(rtn))


@app.get('/sites/latest', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_sites_latest(request: Request) -> Union[JSONResponse, HTTPException]:
    """ Get the latest version of all sites. """
    rtn = BACKEND.list_sites_version_latest()
    return JSONResponse(rtn)


@app.get('/sites/{site}', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    """ Get all versions of a site. """
    rtn = BACKEND.get_site(site)
    if not rtn:
        SiteNotFound(site)
    return JSONResponse(rtn)


@app.delete('/sites/{site}', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
async def delete_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    """ Delete all versions of a site. """
    rtn = BACKEND.delete_site(site)
    if not rtn:
        raise SiteNotFound(site)
    return JSONResponse(repr(rtn))


@app.get('/sites/{site}/{version}', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_site_version(request: Request, site: str, version: Union[int, str]) -> HTMLResponse:
    """ Get a particular version of a site. """
    if version == 'latest':
        rtn = BACKEND.get_site_version_latest(version)
    else:
        rtn = BACKEND.get_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(rtn)


@app.delete('/sites/{site}/{version}', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def delete_site_version(request: Request, site: str, version: Union[int, str]) \
        -> Union[JSONResponse, HTTPException]:
    """ Delete a particular version of a site. """
    rtn = BACKEND.delete_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(repr(rtn))


@app.get('/storages', dependencies=[Depends(increment_request_counter)] if DEBUG else [
    Depends(increment_request_counter), Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_storages(request: Request) -> JSONResponse:
    """ List all storages. """
    rtn = BACKEND.list_storages()
    return JSONResponse(rtn)


@app.get('/storages/grafana', dependencies=[])
@handle_exceptions
@version(1)
async def list_storages_grafana(request: Request) -> JSONResponse:
    """ List all storages in a format digestible by Grafana world map panels. """
    rtn = BACKEND.list_storages(for_grafana=True)
    return JSONResponse(rtn)


@app.get('/storages/topojson', dependencies=[])
@handle_exceptions
@version(1)
async def list_storages_topojson(request: Request) -> JSONResponse:
    """ List all storages in topojson format. """
    rtn = BACKEND.list_storages(topojson=True)
    return JSONResponse(rtn)


# FIXME: SSO.
@app.get("/www/sites/add", response_class=HTMLResponse, dependencies=[
    Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter),
                                                       Depends(verify_permission_for_service_route_query_params)])
@handle_exceptions
@version(1)
async def add_site_form(request: Request, token: str = None) -> TEMPLATES.TemplateResponse:
    schema_path = Path(os.path.join(config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    return TEMPLATES.TemplateResponse("site.html", {
        "request": request,
        "base_path": os.path.join(str(request.base_url), config.get('API_ROOT_PATH', default='')),
        "schema": schema,
        "add_site_url": request.url_for('add_site')
    })


# FIXME: SSO.
@app.get("/www/sites/add/{site}", response_class=HTMLResponse, dependencies=[
    Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter),
                                                       Depends(verify_permission_for_service_route_query_params)])
@handle_exceptions
@version(1)
async def add_site_form_existing(request: Request, site: str) -> TEMPLATES.TemplateResponse:
    schema_path = Path(os.path.join(config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    latest = BACKEND.get_site_version_latest(site)
    if not latest:
        raise SiteVersionNotFound(site, version)
    try:
        latest.pop('comments')
    except KeyError:
        pass

    # Quote nested dictionaries otherwise JSONForm parses as [Object object].
    if latest.get('services', None):
        for idx in range(len(latest['services'])):
            if latest['services'][idx].get('other_attributes', None):
                latest['services'][idx]['other_attributes'] = json.dumps(
                    latest['services'][idx]['other_attributes'])
    if latest.get('other_attributes', None):
        latest['other_attributes'] = json.dumps(latest['other_attributes'])

    return TEMPLATES.TemplateResponse("site.html", {
        "request": request,
        "base_path": os.path.join(str(request.base_url), config.get('API_ROOT_PATH', default='')),
        "schema": schema,
        "add_site_url": request.url_for('add_site'),
        "values": latest
    })


# FIXME: SSO.
@app.get("/www/sites/visualise", response_class=HTMLResponse, dependencies=[
    Depends(increment_request_counter)] if DEBUG else [Depends(increment_request_counter),
                                                       Depends(verify_permission_for_service_route_query_params)])
@handle_exceptions
@version(1)
async def visualise(request: Request) -> TEMPLATES.TemplateResponse:
    return TEMPLATES.TemplateResponse("visualise.html", {
        "request": request,
        "base_path": os.path.join(str(request.base_url), config.get('API_ROOT_PATH', default='')),
        "sites_latest_url": request.url_for('get_sites_latest'),
        "storages_topojson_url": request.url_for('list_storages_topojson')
    })


@app.get('/ping')
@handle_exceptions
@version(1)
async def ping(request: Request):
    """ Service aliveness. """
    return JSONResponse({
        'status': "UP",
        'version': os.environ.get('SERVICE_VERSION'),
    })


@app.get('/health')
@handle_exceptions
@version(1)
async def health(request: Request):
    """ Service health. """

    # Dependent services.
    #
    # Permissions API
    #
    permissions_api_response = PERMISSIONS.ping()

    # Set return code dependent on criteria e.g. dependent service statuses
    #
    healthy_criteria = [
        permissions_api_response.status_code == 200
    ]
    return JSONResponse(
        status_code=status.HTTP_200_OK if all(healthy_criteria) else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'uptime': round(time.time() - SERVICE_START_TIME),
            'number_of_managed_requests': REQUESTS_COUNTER,
            'dependent_services': {
                'permissions-api': {
                    'status': "UP" if permissions_api_response.status_code == 200 else "DOWN",
                }
            }
        }
    )

app = VersionedFastAPI(app, version_format='{major}', prefix_format='/v{major}')
app.add_middleware(CORSMiddleware, **CORSMiddleware_params)
app.mount("/static", StaticFiles(directory="static"), name="static")

