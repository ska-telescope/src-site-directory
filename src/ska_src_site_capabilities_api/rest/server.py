import ast
import asyncio
import copy
import io
import json
import jwt
import os
import pathlib
from plantuml import PlantUML
import tempfile
import time
import uuid
from datetime import datetime
from typing import Union

import jsonref
from authlib.integrations.requests_client import OAuth2Session
from fastapi import FastAPI, Depends, File, HTTPException, status, UploadFile, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versionizer.versionizer import api_version, versionize
from jinja2 import Template
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, StreamingResponse

from ska_src_site_capabilities_api import models
from ska_src_site_capabilities_api.common.constants import Constants
from ska_src_site_capabilities_api.common.exceptions import handle_exceptions, PermissionDenied, SchemaNotFound, \
    ServiceNotFound, SiteNotFound, SiteVersionNotFound, StorageNotFound

from ska_src_site_capabilities_api.common.utility import convert_readme_to_html_docs, get_api_server_url_from_request, \
    get_base_url_from_request, get_url_for_app_from_request
from ska_src_site_capabilities_api.db.backend import MongoBackend
from ska_src_permissions_api.client.permissions import PermissionsClient

config = Config('.env')

# Debug mode (runs unauthenticated)
#
DEBUG = True if config.get("DISABLE_AUTHENTICATION", default=None) == 'yes' else False

# Instantiate FastAPI() allowing CORS. Static mounts must be added later after the versionize() call.
#
app = FastAPI()
CORSMiddleware_params = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}
app.add_middleware(CORSMiddleware, **CORSMiddleware_params)

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
@api_version(1)
@app.get("/schemas",
         responses={
             200: {"model": models.response.SchemasResponse},
             401: {},
             403: {},
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)],
         tags=["Schemas"],
         summary="List schemas")
@handle_exceptions
async def list_schemas(request: Request) -> JSONResponse:
    """ Get a list of schema names used to define sites, services and storages. """
    schema_basenames = sorted([''.join(fi.split('.')[:-1]) for fi in os.listdir(config.get('SCHEMAS_RELPATH'))])
    return JSONResponse(schema_basenames)


@api_version(1)
@app.get("/schemas/{schema}",
         responses={
             200: {"model": models.response.SchemaGetResponse},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)],
         tags=["Schemas"],
         summary="Get schema")
@handle_exceptions
async def get_schema(request: Request,
                     schema: str = Path(description="Schema name")) \
        -> Union[JSONResponse, HTTPException]:
    """ Get a schema by name. """
    try:
        schema_path = pathlib.Path("{}.json".format(os.path.join(config.get('SCHEMAS_RELPATH'), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        return JSONResponse(ast.literal_eval(str(dereferenced_schema)))         # some issue with jsonref return != dict
    except FileNotFoundError:
        raise SchemaNotFound


@api_version(1)
@app.get("/schemas/render/{schema}",
         responses={
             200: {},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)],
         tags=["Schemas"],
         summary="Render a schema")
@handle_exceptions
async def render_schema(request: Request,
                     schema: str = Path(description="Schema name")) \
        -> Union[JSONResponse, HTTPException]:
    """ Render a schema by name. """
    try:
        schema_path = pathlib.Path("{}.json".format(os.path.join(config.get('SCHEMAS_RELPATH'), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = ast.literal_eval(str(jsonref.load(f, base_uri=schema_path.as_uri())))
    except FileNotFoundError:
        raise SchemaNotFound

    # pop countries enum for readability
    dereferenced_schema.get('properties').get('country').pop('enum')

    plantuml = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as schema_file:
        schema_file.write("@startjson\n{}\n@endjson\n".format(json.dumps(dereferenced_schema, indent=2)))
        schema_file.flush()

        image_temp_file_descriptor, image_temp_file_name = tempfile.mkstemp()
        plantuml.processes_file(filename=schema_file.name, outfile=image_temp_file_name)
        with open(image_temp_file_name, 'rb') as image_temp_file:
            png = image_temp_file.read()
        os.close(image_temp_file_descriptor)

    return StreamingResponse(io.BytesIO(png), media_type="image/png")


@api_version(1)
@app.get('/services',
         responses={
             200: {"model": models.response.ServicesResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Services"],
         summary="List all services")
@handle_exceptions
async def list_services(request: Request) -> JSONResponse:
    """ List all services. """
    rtn = BACKEND.list_services()
    return JSONResponse(rtn)


@api_version(1)
@app.get('/services/{service_id}',
         responses={
             200: {"model": models.response.ServiceGetResponse},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Services"],
         summary="Get service from id")
@handle_exceptions
async def get_service_from_id(request: Request,
                              service_id: str = Path(description="Unique service identifier")) \
        -> Union[JSONResponse, HTTPException]:
    """ Get a service description from a unique identifier. """
    rtn = BACKEND.get_service(service_id)
    if not rtn:
        raise ServiceNotFound(service_id)
    return JSONResponse(rtn)


@api_version(1)
@app.get('/sites',
         responses={
             200: {"model": models.response.SitesResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="List sites")
@handle_exceptions
async def list_sites(request: Request) -> JSONResponse:
    """ List all sites. """
    rtn = BACKEND.list_site_names_unique()
    return JSONResponse(rtn)


# FIXME: SSO.
@api_version(1)
@app.post("/sites",
          include_in_schema=False,
          responses={
              200: {"model": models.response.ServicesResponse},
              401: {},
              403: {}
          },
          dependencies=[Depends(increment_request_counter)] if DEBUG else [
              Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
          tags=["Sites"],
          summary="Add a site")
@handle_exceptions
async def add_site(request: Request, values=Body(default="Site JSON."), authorization=Depends(security)) \
        -> Union[HTMLResponse, HTTPException]:
    # add some custom fields e.g. date, user
    if isinstance(values, (bytes, bytearray)):
        values = json.loads(values.decode('utf-8'))
    values['created_at'] = datetime.now().isoformat()
    if DEBUG and authorization.credentials == 'null':
        values['created_by_username'] = 'admin'
    else:
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


@api_version(1)
@app.delete('/sites',
            responses={
                200: {"model": models.response.GenericOperationResponse},
                401: {},
                403: {}
            },
            dependencies=[Depends(increment_request_counter)] if DEBUG else [
                Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
            tags=["Sites"],
            summary="Delete all sites")
@handle_exceptions
async def delete_sites(request: Request) -> Union[JSONResponse, HTTPException]:
    """ Delete all sites. """
    BACKEND.delete_sites()
    return JSONResponse({"successful": True})


@api_version(1)
@app.get("/sites/dump",
         responses={
             200: {"model": models.response.SitesDumpResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="Dump all versions of sites")
@handle_exceptions
async def dump_sites(request: Request) -> Union[HTMLResponse, HTTPException]:
    """ Dump sites. """
    rtn = BACKEND.dump_sites()
    return JSONResponse(rtn)


@api_version(1)
@app.get('/sites',
         responses={
             200: {"model": models.response.SitesResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="List sites")
@handle_exceptions
async def list_sites(request: Request) -> JSONResponse:
    """ List all sites. """
    rtn = BACKEND.list_site_names_unique()
    return JSONResponse(rtn)


@api_version(1)
@app.get('/sites/latest',
         responses={
             200: {"model": models.response.SiteGetResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="Get latest versions of all sites")
@handle_exceptions
async def get_sites_latest(request: Request) -> Union[JSONResponse, HTTPException]:
    """ Get the latest version of all sites. """
    rtn = BACKEND.list_sites_version_latest()
    return JSONResponse(rtn)


@api_version(1)
@app.get('/sites/{site}',
         responses={
             200: {"model": models.response.SiteGetResponse},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="Get all versions of site")
@handle_exceptions
async def get_site_versions(request: Request,
                            site: str = Path(description="Site name")) \
        -> Union[JSONResponse, HTTPException]:
    """ Get all versions of a site. """
    rtn = BACKEND.get_site(site)
    if not rtn:
        raise SiteNotFound(site)
    return JSONResponse(rtn)


@api_version(1)
@app.delete('/sites/{site}',
            responses={
                200: {"model": models.response.GenericOperationResponse},
                401: {},
                403: {},
                404: {"model": models.response.GenericErrorResponse}
            },
            dependencies=[Depends(increment_request_counter)] if DEBUG else [
                Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
            tags=["Sites"],
            summary="Delete all versions of site")
@handle_exceptions
async def delete_site(request: Request,
                      site: str = Path(description="Site name")) \
        -> Union[JSONResponse, HTTPException]:
    """ Delete all versions of a site. """
    rtn = BACKEND.delete_site(site)
    if rtn.deleted_count == 0:
        raise SiteNotFound(site)
    return JSONResponse({"successful": True})


@api_version(1)
@app.get('/sites/{site}/{version}',
         responses={
             200: {"model": models.response.SiteGetVersionResponse},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Sites"],
         summary="Get version of site")
@handle_exceptions
async def get_site_version(request: Request,
                           site: str = Path(description="Site name"),
                           version: str = Path(example='latest', description='Site version')) \
        -> HTMLResponse:
    """ Get a version of a site. """
    if version == 'latest':
        rtn = BACKEND.get_site_version_latest(site)
    else:
        rtn = BACKEND.get_site_version(site, version)
    if not rtn:
        raise SiteVersionNotFound(site, version)
    return JSONResponse(rtn)


@api_version(1)
@app.delete('/sites/{site}/{version}',
            responses={
                200: {"model": models.response.GenericOperationResponse},
                401: {},
                403: {},
                404: {"model": models.response.GenericErrorResponse}
            },
            dependencies=[Depends(increment_request_counter)] if DEBUG else [
                Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
            tags=["Sites"],
            summary="Delete version of site")
@handle_exceptions
async def delete_site_version(request: Request,
                              site: str = Path(description="Site name."),
                              version: str = Path(example='latest', description='Site version')) \
        -> Union[JSONResponse, HTTPException]:
    """ Delete a version of a site. """
    rtn = BACKEND.delete_site_version(site, version)
    if rtn.deleted_count == 0:
        raise SiteVersionNotFound(site, version)
    return JSONResponse({"successful": True})


@api_version(1)
@app.get('/storages',
         responses={
             200: {"model": models.response.StoragesResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Storages"],
         summary="List all storages")
@handle_exceptions
async def list_storages(request: Request) -> JSONResponse:
    """ List all storages. """
    rtn = BACKEND.list_storages()
    print(rtn)
    return JSONResponse(rtn)


#FIXME this really should be /service/grafana
@api_version(1)
@app.get('/storages/grafana',
         responses={
             200: {"model": models.response.StoragesGrafanaResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)],
         tags=["Storages"],
         summary="List all storages (Grafana format)")
@handle_exceptions
async def list_storages_for_grafana(request: Request) -> JSONResponse:
    """ List all storages in a format digestible by Grafana world map panels. """
    rtn = BACKEND.list_storages(for_grafana=True)
    return JSONResponse(rtn)


#FIXME this really should be /services/topojson
@api_version(1)
@app.get('/storages/topojson',
         responses={
             200: {"model": models.response.StoragesTopojsonResponse},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)],
         tags=["Storages"],
         summary="List all storages (topojson format)")
@handle_exceptions
async def list_storages_in_topojson_format(request: Request) -> JSONResponse:
    """ List all storages in topojson format. """
    rtn = BACKEND.list_storages(topojson=True)
    return JSONResponse(rtn)


@api_version(1)
@app.get('/storages/{storage_id}',
         responses={
             200: {"model": models.response.StorageGetResponse},
             401: {},
             403: {},
             404: {"model": models.response.GenericErrorResponse}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route)],
         tags=["Storages"],
         summary="Get storage from id")
@handle_exceptions
async def get_storage_from_id(request: Request,
                              storage_id: str = Path(description="Unique storage identifier")) \
        -> Union[JSONResponse, HTTPException]:
    """ Get a storage description from a unique identifier. """
    rtn = BACKEND.get_storage(storage_id)
    if not rtn:
        raise StorageNotFound(storage_id)
    return JSONResponse(rtn)


@api_version(1)
@app.get("/www/docs/oper",
         include_in_schema=False,
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)])
@handle_exceptions
async def oper_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get('README_MD', "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(readme_text_md, exclude_sections=[
        "Development", "Deployment", "Prototype", "References"])

    openapi_schema = request.scope.get('app').openapi_schema
    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse("docs.html", {
        "request": request,
        "base_url": get_base_url_from_request(request, config.get('API_SCHEME', default='http')),
        "page_title": "Site Capabilities API Operator Documentation",
        "openapi_schema": openapi_schema_template.render({
            "api_server_url": get_api_server_url_from_request(request, config.get('API_SCHEME', default='http'))
        }),
        "readme_text_md": readme_text_html,
    })


@api_version(1)
@app.get("/www/docs/user",
         include_in_schema=False,
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter)])
@handle_exceptions
async def user_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get('README_MD', "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(readme_text_md, exclude_sections=[
        "Authorisation", "Workflows", "Schemas", "Development", "Deployment", "Prototype", "References"])

    # Exclude unnecessary paths.
    paths_to_exclude = {
        '/schemas': ['get'],
        '/schemas/{schema}': ['get'],
        '/schemas/render/{schema}': ['get'],
        '/services/{service_id}': ['get'],
        '/sites': ['post', 'delete'],
        '/sites/bulk': ['post'],
        '/sites/dump': ['get'],
        '/sites/latest': ['get'],
        '/sites/{site}': ['get', 'delete'],
        '/sites/{site}/{version}': ['get', 'delete'],
        '/storages': ['get'],
        '/storages/{storage_id}': ['get'],
        '/storages/grafana': ['get'],
        '/storages/topojson': ['get'],
        '/www/sites/add': ['get'],
        '/www/sites/add/{site}': ['get']
    }
    openapi_schema = copy.deepcopy(request.scope.get('app').openapi_schema)
    included_paths = copy.deepcopy(openapi_schema.get('paths', {}))
    for path, methods in openapi_schema.get('paths', {}).items():
        for method, attr in methods.items():
            if method in paths_to_exclude.get(path, []):
                included_paths[path].pop(method)
    openapi_schema.update({'paths': included_paths})

    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse("docs.html", {
        "request": request,
        "base_url": get_base_url_from_request(request, config.get('API_SCHEME', default='http')),
        "page_title": "Site Capabilities API User Documentation",
        "openapi_schema": openapi_schema_template.render({
            "api_server_url": get_api_server_url_from_request(request, config.get('API_SCHEME', default='http'))
        }),
        "readme_text_md": readme_text_html,
    })


# FIXME: SSO.
@api_version(1)
@app.get("/www/sites/add",
         responses={
             200: {},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route_query_params)],
         tags=["Sites"],
         summary="Add site form")
@handle_exceptions
async def add_site_form(request: Request, token: str = None) -> TEMPLATES.TemplateResponse:
    """ Web form to add a new site with JSON schema validation.

    A valid token must be included in the <b>token</b> query parameter.

    """
    schema_path = pathlib.Path(os.path.join(config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    return TEMPLATES.TemplateResponse("site.html", {
        "request": request,
        "base_url": get_base_url_from_request(request, config.get('API_SCHEME', default='http')),
        "schema": schema,
        "add_site_url": get_url_for_app_from_request(
            'add_site', request, scheme=config.get('API_SCHEME', default='http'))
    })


# FIXME: SSO.
@api_version(1)
@app.get("/www/sites/add/{site}",
         responses={
             200: {},
             401: {},
             403: {}
         },
         dependencies=[Depends(increment_request_counter)] if DEBUG else [
             Depends(increment_request_counter), Depends(verify_permission_for_service_route_query_params)],
         tags=["Sites"],
         summary="Update existing site form")
@handle_exceptions
async def add_site_form_existing(request: Request, site: str, token: str = None) -> TEMPLATES.TemplateResponse:
    """ Web form to update an existing site with JSON schema validation.

    A valid token must be included in the <b>token</b> query parameter.

    """
    schema_path = pathlib.Path(os.path.join(config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    latest = BACKEND.get_site_version_latest(site)
    if not latest:
        raise SiteVersionNotFound(site, 'latest')
    try:
        latest.pop('comments')
    except KeyError:
        pass

    # quote nested dictionaries otherwise JSONForm parses as [Object object].
    if latest.get('services', None):
        for idx in range(len(latest['services'])):
            if latest['services'][idx].get('other_attributes', None):
                latest['services'][idx]['other_attributes'] = json.dumps(
                    latest['services'][idx]['other_attributes'])
    if latest.get('other_attributes', None):
        latest['other_attributes'] = json.dumps(latest['other_attributes'])

    return TEMPLATES.TemplateResponse("site.html", {
        "request": request,
        "base_url": get_base_url_from_request(request, config.get('API_SCHEME', default='http')),
        "schema": schema,
        "add_site_url": get_url_for_app_from_request(
            'add_site', request, scheme=config.get('API_SCHEME', default='http')),
        "values": latest
    })


@api_version(1)
@app.get('/ping',
         responses={
             200: {"model": models.response.PingResponse}
         },
         tags=["Status"],
         summary="Check API status")
@handle_exceptions
async def ping(request: Request):
    """ Service aliveness. """
    return JSONResponse({
        'status': "UP",
        'version': os.environ.get('SERVICE_VERSION'),
    })


@api_version(1)
@app.get('/health',
         responses={
             200: {"model": models.response.HealthResponse},
             500: {"model": models.response.HealthResponse}
         },
         tags=["Status"],
         summary="Check API health")
@handle_exceptions
async def health(request: Request):
    """ Service health.

    This endpoint will return a 500 if any of the dependent services are down.
    """

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

# Versionise the API.
#
versions = versionize(
    app=app,
    prefix_format='/v{major}',
    docs_url=None,
    redoc_url=None
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Customise openapi.json.
#
# - Add schema server, title and tags.
# - Add request code samples to routes.
# - Remove 422 responses.
#
for route in app.routes:
    if isinstance(route.app, FastAPI):              # find any FastAPI subapplications (e.g. /v1/, /v2/, ...)
        subapp = route.app
        subapp_base_path = '{}{}'.format(os.environ.get('API_ROOT_PATH', default=''), route.path)
        subapp.openapi()
        subapp.openapi_schema['servers'] = [{"url": subapp_base_path}]
        subapp.openapi_schema['info']['title'] = 'Site Capabilities API Overview'
        subapp.openapi_schema['tags'] = [
            {"name": "Sites", "description": "Operations on sites.", "x-tag-expanded": False},
            {"name": "Storages", "description": "Operations on storages offered by sites.", "x-tag-expanded": False},
            {"name": "Services", "description": "Operations on services offered by sites.", "x-tag-expanded": False},
            {"name": "Schemas", "description": "Schema operations.", "x-tag-expanded": False},
            {"name": "Status", "description": "Operations describing the status of the API.", "x-tag-expanded": False},
        ]
        # add request code samples and strip out 422s
        for language in ['shell', 'python', 'go', 'js']:
            for path, methods in subapp.openapi_schema['paths'].items():
                path = path.strip('/')
                for method, attr in methods.items():
                    if attr.get('responses', {}).get('422'):
                        del attr.get('responses')['422']
                    method = method.strip('/')
                    sample_template_filename = "{}-{}-{}.j2".format(
                        language, path, method).replace('/', '-')
                    sample_template_path = os.path.join('request-code-samples', sample_template_filename)
                    if os.path.exists(sample_template_path):
                        with open(sample_template_path, 'r') as f:
                            sample_source_template = f.read()
                        code_samples = attr.get('x-code-samples', [])
                        code_samples.append({
                            'lang': language,
                            'source': str(sample_source_template)            # rendered later in route
                        })
                        attr['x-code-samples'] = code_samples
