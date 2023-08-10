import ast
import json
import jsonschema
import operator
import os
import pprint
import requests
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
from ska_src_permissions_api.common.constants import Constants
from ska_src_site_capabilities_api.common.exceptions import handle_exceptions, PermissionDenied, SchemaNotFound, \
    SiteNotFound, SiteVersionNotFound
from ska_src_site_capabilities_api.db.backend import MongoBackend
from ska_src_permissions_api.client.permissions import PermissionsClient

config = Config('.env')

# Instantiate FastAPI() allowing CORS. Middleware and static mounts are added later to the instance of a VersionedApp.
#
app = FastAPI()
CORSMiddleware_params = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}

# Add HTTPBearer authz.
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


# Dependencies.
# -------------
#
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
                                                  token=access_token, body=request.path_params)
    if rtn.get('is_authorised', False):
        return
    raise PermissionDenied


# Routes
# ------
#
@app.get("/schemas", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_schemas(request: Request) -> JSONResponse:
    schema_basenames = sorted([''.join(fi.split('.')[:-1]) for fi in os.listdir(config.get('SCHEMAS_RELPATH'))])
    return JSONResponse(schema_basenames)


@app.get("/schemas/{schema}", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_schema(request: Request, schema: str) -> Union[JSONResponse, HTTPException]:
    try:
        schema_path = Path("{}.json".format(os.path.join(config.get('SCHEMAS_RELPATH'), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        return JSONResponse(ast.literal_eval(str(dereferenced_schema)))         # some issue with jsonref return != dict
    except FileNotFoundError:
        raise SchemaNotFound


@app.get('/services', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_storages(request: Request) -> JSONResponse:
    rtn = BACKEND.list_services()
    return JSONResponse(rtn)


@app.get('/sites', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_sites(request: Request) -> JSONResponse:
    rtn = BACKEND.list_site_names_unique()
    return JSONResponse(rtn)


@app.post("/sites", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def add_site(request: Request) -> Union[HTMLResponse, HTTPException]:
    values = await request.json()
    values['created_at'] = datetime.now().isoformat()
    values['created_by_username'] = request.session['user']['preferred_username']
    id = BACKEND.add_site(values)
    return HTMLResponse(repr(id))


@app.delete('/sites', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def delete_sites(request: Request) -> Union[JSONResponse, HTTPException]:
    rtn = BACKEND.delete_sites()
    return JSONResponse(repr(rtn))


@app.post("/sites/bulk", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def add_sites_bulk(request: Request, sites_file: UploadFile = File(...)) -> Union[HTMLResponse, HTTPException]:
    sites_bytes = await sites_file.read()
    sites_json = json.loads(sites_bytes.decode('UTF-8'))
    rtn = BACKEND.add_sites_bulk(sites_json)
    return HTMLResponse(repr(rtn))


@app.get('/sites/latest', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_sites_latest(request: Request) -> Union[JSONResponse, HTTPException]:
    rtn = BACKEND.list_sites_version_latest()
    if not rtn:
        raise SiteNotFound(site)
    return JSONResponse(rtn)


@app.get('/sites/{site}', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    if site == 'latest':
        rtn = BACKEND.list_sites_version_latest()
    else:
        rtn = BACKEND.get_site(site)
    if not rtn:
        SiteNotFound(site)
    return JSONResponse(rtn)


@app.delete('/sites/{site}', dependencies=[Depends(verify_permission_for_service_route)])
async def delete_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    rtn = BACKEND.delete_site(site)
    if not rtn:
        raise SiteNotFound(site)
    return JSONResponse(repr(rtn))


@app.get('/sites/{site}/{version}', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def get_site_version(request: Request, site: str, version: Union[int, str]) -> HTMLResponse:
    if version == 'latest':
        rtn = BACKEND.get_site_version_latest(site)
    else:
        rtn = BACKEND.get_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(rtn)


@app.delete('/sites/{site}/{version}', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def delete_site_version(request: Request, site: str, version: int) -> Union[JSONResponse, HTTPException]:
    rtn = BACKEND.delete_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(repr(rtn))


@app.get('/storages', dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def list_storages(request: Request) -> JSONResponse:
    rtn = backend.list_storages()
    return JSONResponse(rtn)


@app.get('/storages/grafana', dependencies=[])
@handle_exceptions
@version(1)
async def list_storages(request: Request) -> JSONResponse:
    rtn = BACKEND.list_storages(for_grafana=True)
    return JSONResponse(rtn)


@app.get('/storages/topojson', dependencies=[])
@handle_exceptions
@version(1)
async def list_storages(request: Request) -> JSONResponse:
    rtn = BACKEND.list_storages(topojson=True)
    return JSONResponse(rtn)


@app.get("/www/sites/add", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def add_site_form(request: Request) -> TEMPLATES.TemplateResponse:
    schema_path = Path(os.path.join(config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    return TEMPLATES.TemplateResponse("site.html", {
        "request": request,
        "schema": schema,
        "api_prefix": config.get('API_PREFIX'),
        "api_host": config.get('API_HOST'),
        "api_port": config.get('API_PORT')
    })


@app.get("/www/sites/add/{site}", response_class=HTMLResponse,
         dependencies=[Depends(verify_permission_for_service_route)])
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
        "schema": schema,
        "api_prefix": config.get('API_PREFIX'),
        "api_host": config.get('API_HOST'),
        "api_port": config.get('API_PORT'),
        "values": latest
    })


@app.get("/www/sites/visualise", response_class=HTMLResponse,
         dependencies=[Depends(verify_permission_for_service_route)])
@handle_exceptions
@version(1)
async def visualise(request: Request) -> TEMPLATES.TemplateResponse:
    return TEMPLATES.TemplateResponse("visualise.html", {
        "request": request,
        "api_prefix": config.get('API_PREFIX'),
        "api_host": config.get('API_HOST'),
        "api_port": config.get('API_PORT')
    })


@app.get('/ping')
@handle_exceptions
@version(1)
async def ping(request: Request):
    return JSONResponse('pong')


app = VersionedFastAPI(app, version_format='{major}', prefix_format='/v{major}')
app.add_middleware(CORSMiddleware, **CORSMiddleware_params)
app.mount("/static", StaticFiles(directory="static"), name="static")

