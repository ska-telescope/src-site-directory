import copy
import json
import os
import pathlib
from typing import Union

from fastapi import APIRouter, Depends, Query
from fastapi_versionizer.versionizer import api_version
from jinja2 import Template
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from ska_src_site_capabilities_api.common.exceptions import NodeVersionNotFound, PermissionDenied, handle_exceptions
from ska_src_site_capabilities_api.common.utility import (
    convert_readme_to_html_docs,
    get_api_server_url_from_request,
    get_base_url_from_request,
    get_url_for_app_from_request,
    load_and_dereference_schema,
    recursive_stringify,
)
from ska_src_site_capabilities_api.rest.dependencies import Common

docs_router = APIRouter()
config = Config(".env")


@api_version(1)
@docs_router.get(
    "/www/docs/oper",
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
)
@handle_exceptions
async def oper_docs(request: Request):
    # Read and parse README.md, omitting excluded sections.
    readme_text_md = (
        os.environ.get("README_MD", "")
        if not request.app.state.debug
        else open("../../../README.md", encoding="utf-8").read()  # pylint: disable=consider-using-with
    )
    readme_text_html = convert_readme_to_html_docs(readme_text_md, exclude_sections=["Deployment"])
    openapi_schema = request.scope.get("app").openapi()
    openapi_schema_template = Template(json.dumps(openapi_schema))
    return request.app.state.templates.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
            "page_title": "Site Capabilities API Operator Documentation",
            "openapi_schema": openapi_schema_template.render(
                {"api_server_url": get_api_server_url_from_request(request, config.get("API_SCHEME", default="http"))}
            ),
            "readme_text_md": readme_text_html,
            "version": "v{version}".format(version=os.environ.get("SERVICE_VERSION")),
        },
    )


@api_version(1)
@docs_router.get(
    "/www/docs/user",
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
)
@handle_exceptions
async def user_docs(request: Request):
    # Read and parse README.md, omitting excluded sections.
    readme_text_md = (
        os.environ.get("README_MD", "")
        if not request.app.state.debug
        else open("../../../README.md", encoding="utf-8").read()  # pylint: disable=consider-using-with
    )
    readme_text_html = convert_readme_to_html_docs(
        readme_text_md,
        exclude_sections=["Authorisation", "Schemas", "Deployment"],
    )

    # Exclude unnecessary paths.
    paths_to_include = {
        "/nodes": ["get"],
        "/sites": ["get"],
        "/compute": ["get"],
        "/services": ["get"],
        "/storages": ["get"],
        "/storage-areas": ["get"],
        "/ping": ["get"],
        "/health": ["get"],
    }
    openapi_schema = copy.deepcopy(request.scope.get("app").openapi())
    included_paths = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, attr in methods.items():
            if method in paths_to_include.get(path, []):
                if path not in included_paths:
                    included_paths[path] = {}
                included_paths[path][method] = attr
    openapi_schema.update({"paths": included_paths})

    openapi_schema_template = Template(json.dumps(openapi_schema))
    return request.app.state.templates.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
            "page_title": "Site Capabilities API User Documentation",
            "openapi_schema": openapi_schema_template.render(
                {"api_server_url": get_api_server_url_from_request(request, config.get("API_SCHEME", default="http"))}
            ),
            "readme_text_md": readme_text_html,
            "version": "v{version}".format(version=os.environ.get("SERVICE_VERSION")),
        },
    )


def _strip_version_prefix(route_path: str) -> str:
    """Strip version prefix from route path (e.g., /v1/nodes -> /nodes)."""
    if route_path.startswith("/v"):
        parts = route_path.split("/", 2)
        if len(parts) >= 3:
            return "/" + parts[2]
    return route_path


@api_version(1)
@docs_router.get(
    "/www/downtime/{node_name}",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Nodes", "Downtimes"],
    summary="Get the downtime statusboard for a node",
)
@handle_exceptions
async def get_downtime_statusboard(request: Request, node_name: str) -> Union[HTMLResponse, RedirectResponse]:
    """Dashboard to get all the downtimes for node."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not request.app.state.debug:
            try:
                rtn = request.app.state.permissions_dependencies.permissions.authorise_service_route(
                    service=request.app.state.permissions_service_name,
                    version=request.app.state.permissions_service_version,
                    route=_strip_version_prefix(request.scope["route"].path),
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied

        node = request.app.state.backend.get_node(node_name=node_name)
        if not node:
            raise NodeVersionNotFound(node_name=node_name, node_version="latest")

        try:
            node.pop("comments")
        except KeyError:
            pass

        node = recursive_stringify(node)

        return request.app.state.templates.TemplateResponse(
            "downtime-statusboard.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "title": "Downtimes SRCNet Node ({})".format(node_name),
                "submit_endpoint_url": get_url_for_app_from_request(
                    "edit_node",
                    request,
                    path_params=request.path_params,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": node,
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@docs_router.get(
    "/www/login",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    summary="Login",
)
@handle_exceptions
async def www_login(
    request: Request,
    landing_page: str = Query(default=None, description="Landing page to redirect back to."),
) -> Union[HTMLResponse, RedirectResponse]:
    if request.session.get("access_token"):
        if request.session.get("landing_page"):
            return RedirectResponse(request.session.get("landing_page"))
        else:
            return HTMLResponse("You are logged in.")
    elif request.query_params.get("code"):
        # get token from authorization code
        code = request.query_params.get("code")
        original_request_url = request.url.remove_query_params(keys=["code", "state"])
        response = request.app.state.auth.token(code=code, redirect_uri=original_request_url)

        # exchange token for site-capabilities-api
        access_token = response.json().get("token", {}).get("access_token")
        if access_token:
            response = request.app.state.auth.exchange_token(service="site-capabilities-api", access_token=access_token)
            request.session["access_token"] = response.json().get("access_token")

        # redirect back now we have a valid token
        return RedirectResponse(original_request_url)
    else:
        # start login process
        request.session["landing_page"] = landing_page  # if being redirected from /www/sites
        redirect_uri = request.url.remove_query_params(keys=["landing_page"])
        response = request.app.state.auth.login(flow="legacy", redirect_uri=redirect_uri)
        authorization_uri = response.json().get("authorization_uri")
        return RedirectResponse(authorization_uri)


@api_version(1)
@docs_router.get(
    "/www/logout",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    summary="Logout",
)
@handle_exceptions
async def www_logout(request: Request) -> Union[HTMLResponse]:
    if request.session.get("access_token"):
        request.session.pop("access_token")
    return HTMLResponse("You are logged out. Click <a href=" + get_url_for_app_from_request("www_login", request) + ">here</a> to login.")


@api_version(1)
@docs_router.get(
    "/www/nodes",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Nodes"],
    summary="Add node form",
)
@handle_exceptions
async def add_node_form(
    request: Request,
) -> Union[HTMLResponse, RedirectResponse]:
    """Web form to add a new node with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not request.app.state.debug:
            try:
                rtn = request.app.state.permissions_dependencies.permissions.authorise_service_route(
                    service=request.app.state.permissions_service_name,
                    version=request.app.state.permissions_service_version,
                    route=_strip_version_prefix(request.scope["route"].path),
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied

        # Load schema.
        schema = load_and_dereference_schema(schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "node.json")).absolute())
        downtime_schema = load_and_dereference_schema(
            schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "downtime.json")).absolute()
        )
        # Remove sites
        schema.get("properties", {}).pop("sites")

        return request.app.state.templates.TemplateResponse(
            "node.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "title": "Add SRCNet Node",
                "form_name": "add-node-form-ui.js",
                "downtime_schema": downtime_schema,
                "downtime_scheduler_form": "downtime-scheduler-form-ui.js",
                "downtime_values": {},
                "submit_form_endpoint": get_url_for_app_from_request(
                    "add_node",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": {},
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@docs_router.get(
    "/www/nodes/{node_name}",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Nodes"],
    summary="Edit existing node form",
)
@handle_exceptions
async def edit_node_form(request: Request, node_name: str) -> Union[HTMLResponse, RedirectResponse]:
    """Web form to edit an existing node with JSON schema validation."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not request.app.state.debug:
            try:
                rtn = request.app.state.permissions_dependencies.permissions.authorise_service_route(
                    service=request.app.state.permissions_service_name,
                    version=request.app.state.permissions_service_version,
                    route=_strip_version_prefix(request.scope["route"].path),
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied

        # Load schema.
        schema = load_and_dereference_schema(schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "node.json")).absolute())
        downtime_schema = load_and_dereference_schema(
            schema_path=pathlib.Path(os.path.join(config.get("SCHEMAS_RELPATH"), "downtime.json")).absolute()
        )
        # Get latest values for requested node.
        node = request.app.state.backend.get_node(node_name=node_name)
        if not node:
            raise NodeVersionNotFound(node_name=node_name, node_version="latest")

        # Pop comments from version.
        try:
            node.pop("comments")
        except KeyError:
            pass

        # Quote nested JSON "other_attribute" dictionaries otherwise JSONForm parses as
        # [Object object].
        node = recursive_stringify(node)

        return request.app.state.templates.TemplateResponse(
            "node.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "schema": schema,
                "downtime_schema": downtime_schema,
                "title": "Edit SRCNet Node ({})".format(node_name),
                "form_name": "edit-node-form-ui.js",
                "downtime_scheduler_form": "downtime-scheduler-form-ui.js",
                "submit_form_endpoint": get_url_for_app_from_request(
                    "edit_node",
                    request,
                    path_params=request.path_params,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
                "values": node,
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )


@api_version(1)
@docs_router.get(
    "/www/topology",
    response_model=None,
    responses={200: {}, 401: {}, 403: {}, 409: {}},
    include_in_schema=False,
    dependencies=[Depends(Common.increment_requests_counter_depends)],
    tags=["Topology"],
    summary="Topology",
)
@handle_exceptions
async def topology(request: Request) -> Union[HTMLResponse, RedirectResponse]:
    """Topology."""
    if request.session.get("access_token"):
        # Check access permissions.
        if not request.app.state.debug:
            try:
                rtn = request.app.state.permissions_dependencies.permissions.authorise_service_route(
                    service=request.app.state.permissions_service_name,
                    version=request.app.state.permissions_service_version,
                    route=_strip_version_prefix(request.scope["route"].path),
                    method=request.method,
                    token=request.session.get("access_token"),
                    body=request.path_params,
                ).json()
            except Exception as err:
                raise err
            if not rtn.get("is_authorised", False):
                raise PermissionDenied
        return request.app.state.templates.TemplateResponse(
            "topology.html",
            {
                "request": request,
                "base_url": get_base_url_from_request(request, config.get("API_SCHEME", default="http")),
                "title": "Topology of SRCNet",
                "data": request.app.state.backend.list_nodes(include_archived=False, include_inactive=True),
                "sign_out_url": get_url_for_app_from_request(
                    "www_logout",
                    request,
                    scheme=config.get("API_SCHEME", default="http"),
                ),
                "access_token": request.session.get("access_token"),
            },
        )
    else:
        return HTMLResponse(
            "Please <a href=" + get_url_for_app_from_request("www_login", request) + "?landing_page={}>login</a> first.".format(request.url)
        )
