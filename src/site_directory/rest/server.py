import ast
from datetime import datetime
from functools import wraps
import json
import jsonschema
import operator
import os
from pathlib import Path
import requests
import types
from typing import Union

from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.oauth2.rfc7662 import IntrospectTokenValidator
from fastapi import FastAPI, Depends, File, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import jinja2
import jsonref
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
import uvicorn

from site_directory.api.backend import MongoBackend
from site_directory.rest.permissions import Permission

config = Config('.env')

# Instantiate FastAPI() allowing CORS.
#
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.get('SESSION_MIDDLEWARE_SECRET_KEY'))
origins = ["*"]     # security risk if service is used externally

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure OAuth2 client.
#
# The <name> specified here must have a corresponding <name>_CLIENT_ID and <name>_CLIENT_SECRET
# environment variable.
oauth = OAuth(config)
oauth.register(
    name=oauth.config.get('CLIENT_NAME'),
    server_metadata_url=oauth.config.get('CLIENT_CONF_URL'),
    client_kwargs={
        'scope': oauth.config.get('CLIENT_SCOPES')
    }
)
OAUTH_CLIENT = getattr(oauth, oauth.config.get('CLIENT_NAME'))

## Mount static files and get templates.
#
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Instantiate the backend api.
#
backend = MongoBackend(
    mongo_username = oauth.config.get('MONGO_USERNAME'),
    mongo_password = oauth.config.get('MONGO_PASSWORD'),
    mongo_host = oauth.config.get('MONGO_HOST'),
    mongo_port = oauth.config.get('MONGO_PORT'),
    mongo_database = oauth.config.get('MONGO_DATABASE')
)

## Instantiate permissions and roles modules to check authZ for routes.
#
permission_definition_abspath = os.path.join(oauth.config.get('PERMISSIONS_RELPATH'),
                                             oauth.config.get('PERMISSIONS_NAME'))
roles_definition_abspath = os.path.join(oauth.config.get('ROLES_RELPATH'),
                                        oauth.config.get('ROLES_NAME'))
PERMISSION = Permission(permissions_definition_path=permission_definition_abspath,
                        roles_definition_path=roles_definition_abspath,
                        root_group=oauth.config.get('PERMISSIONS_ROOT_GROUP'))

## Function to validate (and return) a token using the introspection endpoint.
#
async def validate_token_by_remote_introspection(request: Request) -> Union[dict, bool]:
    if request.session.get('user') and request.session.get('access_token'):
        if 'introspection_endpoint' not in OAUTH_CLIENT.server_metadata:
            await OAUTH_CLIENT.load_server_metadata()
        url = OAUTH_CLIENT.server_metadata['introspection_endpoint']
        data = {'token': request.session.get('access_token'), 'token_type_hint': 'access_token'}
        auth = (OAUTH_CLIENT.client_id, OAUTH_CLIENT.client_secret)
        resp = requests.post(url, data=data, auth=auth)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['active'] is not True:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token is invalid, please try logging in.")
        return resp_json
    return False

## Function to check permissions from user token groups.
#
async def verify_permission_for_route(request: Request) -> Union[HTTPException, RedirectResponse]:
    introspected_token = await validate_token_by_remote_introspection(request)
    if not introspected_token:
        groups = []
    else:
        groups = introspected_token['groups']
    try:
        route = request.scope['root_path'] + request.scope['route'].path
        method = request.method

        if PERMISSION.check_role_membership_for_route(
                route=route, method=method, groups=groups, **request.path_params):
            return
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are not authorised to view this resource.")
    except Exception as e:
        if hasattr(e, "http_error_status"):
            raise HTTPException(e.http_error_status, e.message)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, repr(e))


@app.get('/')
async def homepage(request: Request) -> HTMLResponse:
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await OAUTH_CLIENT.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request) -> RedirectResponse:
    try:
        token = await OAUTH_CLIENT.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    access_token = token.get('access_token')
    if user and access_token:
        request.session['user'] = dict(user)
        request.session['access_token'] = access_token
    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request) -> RedirectResponse:
    request.session.pop('user', None)
    request.session.pop('access_token', None)
    return RedirectResponse(url='/')


@app.post("/sites", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_route)])
async def add_site(request: Request) -> Union[HTMLResponse, HTTPException]:
    values = await request.json()
    values['created_at'] = datetime.now().isoformat()
    values['created_by_username'] = request.session['user']['preferred_username']
    id = backend.add_site(values)
    return HTMLResponse(repr(id))


@app.post("/sites/bulk", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_route)])
async def add_sites_bulk(request: Request, sites_file: UploadFile = File(...)) -> Union[HTMLResponse, HTTPException]:
    sites_bytes = await sites_file.read()
    sites_json = json.loads(sites_bytes.decode('UTF-8'))
    rtn = backend.add_sites_bulk(sites_json)
    return HTMLResponse(repr(rtn))


@app.delete('/sites/{site}', dependencies=[Depends(verify_permission_for_route)])
async def delete_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    rtn = backend.delete_site(site)
    if not rtn:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Site with name '{}' could not be found".format(site))
    return JSONResponse(repr(rtn))


@app.delete('/sites', dependencies=[Depends(verify_permission_for_route)])
async def delete_sites(request: Request) -> Union[JSONResponse, HTTPException]:
    rtn = backend.delete_sites()
    return JSONResponse(repr(rtn))


@app.delete('/sites/{site}/{version}', dependencies=[Depends(verify_permission_for_route)])
async def delete_site_version(request: Request, site: str, version: int) -> Union[JSONResponse, HTTPException]:
    rtn = backend.delete_site_version(site, version)
    if not rtn:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Version {} of site with name '{}' and could not be found".format(version, site))
    return JSONResponse(repr(rtn))


@app.get('/sites/latest', dependencies=[Depends(verify_permission_for_route)])
async def get_sites_latest(request: Request) -> Union[JSONResponse, HTTPException]:
    rtn = backend.list_sites_version_latest()
    if not rtn:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Site with name '{}' could not be found".format(site))
    return JSONResponse(rtn)


@app.get('/sites/{site}', dependencies=[Depends(verify_permission_for_route)])
async def get_site(request: Request, site: str) -> Union[JSONResponse, HTTPException]:
    if site == 'latest':
        rtn = backend.list_sites_version_latest()
    else:
        rtn = backend.get_site(site)
    if not rtn:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Site with name '{}' could not be found".format(site))
    return JSONResponse(rtn)


@app.get('/sites/{site}/{version}', dependencies=[Depends(verify_permission_for_route)])
async def get_site_version(request: Request, site: str, version: Union[int, str]) -> HTMLResponse:
    if version == 'latest':
        rtn = backend.get_site_version_latest(site)
    else:
        rtn = backend.get_site_version(site, version)
    if not rtn:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Version {} of site with name '{}' and could not be found".format(version, site))
    return JSONResponse(rtn)


@app.get('/sites', dependencies=[Depends(verify_permission_for_route)])
async def list_sites(request: Request) -> JSONResponse:
    rtn = backend.list_site_names_unique()
    return JSONResponse(rtn)

@app.get('/storages', dependencies=[Depends(verify_permission_for_route)])
async def list_storages(request: Request) -> JSONResponse:
    rtn = backend.list_storages()
    return JSONResponse(rtn)


@app.get('/storages/topojson', dependencies=[Depends(verify_permission_for_route)])
async def list_storages(request: Request) -> JSONResponse:
    rtn = backend.list_storages(topojson=True)
    return JSONResponse(rtn)


@app.get('/storages/grafana', dependencies=[Depends(verify_permission_for_route)])
async def list_storages(request: Request) -> JSONResponse:
    rtn = backend.list_storages(for_grafana=True)
    return JSONResponse(rtn)


@app.get("/permissions", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def list_permissions(request: Request) -> JSONResponse:
    permission_basenames = sorted(
        [''.join(fi.split('.')[:-1]) for fi in os.listdir(oauth.config.get('PERMISSIONS_RELPATH'))])
    return JSONResponse(permission_basenames)


@app.get("/permissions/{permission}", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def get_permission(request: Request, permission: str) -> JSONResponse:
    try:
        with open("{}.json".format(os.path.join(oauth.config.get('PERMISSIONS_RELPATH'), permission))) as f:
            contents = json.load(f)
        return JSONResponse(contents)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Permission with name '{}' not found".format(permission))


@app.get("/roles", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def list_roles(request: Request) -> JSONResponse:
    role_basenames = sorted([''.join(fi.split('.')[:-1]) for fi in os.listdir(oauth.config.get('ROLES_RELPATH'))])
    return JSONResponse(role_basenames)


@app.get("/roles/{role}", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def get_role(request: Request, role: str) -> Union[JSONResponse, HTTPException]:
    try:
        with open("{}.json".format(os.path.join(oauth.config.get('ROLES_RELPATH'), role))) as f:
            contents = json.load(f)
        return JSONResponse(contents)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role with name '{}' not found".format(role))


@app.get("/schemas", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def list_schemas(request: Request) -> JSONResponse:
    schema_basenames = sorted([''.join(fi.split('.')[:-1]) for fi in os.listdir(oauth.config.get('SCHEMAS_RELPATH'))])
    return JSONResponse(schema_basenames)


@app.get("/schemas/{schema}", response_class=JSONResponse, dependencies=[Depends(verify_permission_for_route)])
async def get_schema(request: Request, schema: str) -> Union[JSONResponse, HTTPException]:
    try:
        schema_path = Path("{}.json".format(os.path.join(oauth.config.get('SCHEMAS_RELPATH'), schema))).absolute()
        with open(schema_path) as f:
            dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
        return JSONResponse(ast.literal_eval(str(dereferenced_schema)))         # some issue with jsonref return != dict
    except FileNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Schema with name '{}' not found".format(schema))


@app.get("/www/sites/add", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_route)])
async def add_site_form(request: Request) -> templates.TemplateResponse:
    schema_path = Path(os.path.join(oauth.config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    return templates.TemplateResponse("site.html", {
        "request": request,
        "schema": schema,
        "api_prefix": oauth.config.get('API_PREFIX'),
        "api_host": oauth.config.get('API_HOST'),
        "api_port": oauth.config.get('API_PORT')
    })

@app.get("/www/sites/add/{site}", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_route)])
async def add_site_form_existing(request: Request, site: str) -> templates.TemplateResponse:
    schema_path = Path(os.path.join(oauth.config.get('SCHEMAS_RELPATH'), "site.json")).absolute()
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    schema = ast.literal_eval(str(dereferenced_schema))
    latest = backend.get_site_version_latest(site)
    if not latest:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Version {} of site with name '{}' and could not be found".format(
                "latest", site))
    try:
        latest.pop('comments')
    except KeyError:
        pass
    return templates.TemplateResponse("site.html", {
        "request": request,
        "schema": schema,
        "api_prefix": oauth.config.get('API_PREFIX'),
        "api_host": oauth.config.get('API_HOST'),
        "api_port": oauth.config.get('API_PORT'),
        "values": json.dumps(latest)
    })


@app.get("/www/sites/visualise", response_class=HTMLResponse, dependencies=[Depends(verify_permission_for_route)])
async def visualise(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("visualise.html", {
        "request": request,
        "api_prefix": oauth.config.get('API_PREFIX'),
        "api_host": oauth.config.get('API_HOST'),
        "api_port": oauth.config.get('API_PORT')
    })
