import ast
import json
import os
import time
import uuid
from urllib.parse import urlparse

import jsonref
import markdown
import requests
from fastapi.openapi.utils import get_openapi
from jinja2 import Environment, FileSystemLoader

from ska_src_site_capabilities_api.common.exceptions import RetryRequestError


def convert_readme_to_html_docs(
    text,
    remove_first_heading=True,
    convert_mermaid_diagrams=True,
    exclude_sections=None,
):
    """Take an application's README file and parse it for display in HTML documentation.

    Options:

    remove_first_heading: removes any first level headings ("#")
    convert_mermaid_diagrams: change ```mermaid``` blocks into HTML <div>s
    exclude_sections: Remove sections with headings in the list <exclude_sections>.
    """
    parsed_text_lines = []
    in_mermaid_diagram = False
    in_excluded_section = False
    in_excluded_section_level = None
    for line in text.split("\n"):
        if remove_first_heading:
            if line.startswith("# "):
                continue  # remove first heading
            elif line.startswith("##"):
                line = line[1:]  # reduce headings by 1
        if convert_mermaid_diagrams:
            if line.startswith("```mermaid"):  # convert mermaid diagrams to divs
                line = '<div class="mermaid">'
                in_mermaid_diagram = True
            elif line.startswith("```") and in_mermaid_diagram:
                line = "</div>"
                in_mermaid_diagram = False
        if exclude_sections:
            if line.startswith("#"):
                level = line.count("#")
                heading = line.lstrip("# ")
                if in_excluded_section:
                    if level <= in_excluded_section_level:
                        in_excluded_section = False
                        in_excluded_section_level = None
                if heading in exclude_sections:
                    in_excluded_section = True
                    in_excluded_section_level = level
            if in_excluded_section:
                continue
        parsed_text_lines.append(line)
    parsed_text = "\n".join(parsed_text_lines)
    return markdown.markdown(parsed_text, extensions=["codehilite", "fenced_code", "toc", "tables"])


def get_api_server_url_from_request(request, scheme="http"):
    """Return the api server url given an instance of Request, <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Example returns:
     - http://localhost/v1/
     - https://service.srcdev.skao.int/api/v1

    Note:
      - request.scope.get('root_path') returns either e.g. /v1 or /api/v1 (if proxied)
      - request.base_url returns the full path up to and including the proxy base path (e.g. api)
      - request.app.url_path_for(function_name) returns the (sub)application path for a given function name
        (function_name)
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(scheme=scheme, path="{}".format(request.scope.get("root_path"))).geturl()


def get_base_url_from_request(request, scheme="http"):
    """Return the base url given an instance of Request, <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Example returns:
     - http://localhost
     - https://service.srcdev.skao.int/api
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(scheme=scheme).geturl()


def get_url_for_app_from_request(function_name, request, path_params={}, scheme="http"):
    """Return an url for a particular (sub)application's function name, <function_name>, with path params,
    <path_params>, given an instance of Request, <request>, and scheme, <scheme>.

    Scheme is required in case the original scheme is not forwarded correctly through proxies.

    Examples:
     - on localhost, function_name="add_site": http://localhost/v1/www/sites/add
     - in production, function_name="add_site": https://service.srcdev.skao.int/api/v1/www/sites/add

    Note:
      - request.scope.get('root_path') returns either e.g. /v1 or /api/v1 (if proxied)
      - request.base_url returns the full path up to and including the proxy base path (e.g. api)
      - request.app.url_path_for(function_name) returns the (sub)application path for a given function name
        (function_name)
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(
        scheme=scheme,
        path="{}{}".format(
            request.scope.get("root_path"),
            request.app.url_path_for(function_name, **path_params),
        ),
    ).geturl()


def load_and_dereference_schema(schema_path):
    """Load a schema and dereference it."""
    with open(schema_path) as f:
        dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
    return ast.literal_eval(str(dereferenced_schema))


def recursive_autogen_id(input, autogen_keys=["id"], placeholder_value="to be assigned"):
    """Recursively autogenerate uuids in input for placeholder keys, autogen_keys, if their value
    equals a given placerholder_value."""
    if isinstance(input, dict):
        for key, value in input.items():
            if key in autogen_keys:
                if value == placeholder_value:
                    input[key] = str(uuid.uuid4())
            elif isinstance(value, (dict, list)):
                input[key] = recursive_autogen_id(value)
    elif isinstance(input, list):
        for i in range(len(input)):
            input[i] = recursive_autogen_id(input[i])
    return input


def recursive_stringify(input, stringify_keys=["other_attributes"]):
    """Recursively stringify keys, stringify_keys, in input."""
    if isinstance(input, dict):
        for key, value in input.items():
            if key in stringify_keys:
                input[key] = json.dumps(value)
            elif isinstance(value, (dict, list)):
                input[key] = recursive_stringify(value)
    elif isinstance(input, list):
        for i in range(len(input)):
            input[i] = recursive_stringify(input[i])
    return input


def retry_request(
    method,
    url,
    headers={},
    data=None,
    params=None,
    json=None,
    session=None,
    n_max_retries=3,
    wait_for_s=0.1,
    timeout_s=3,
):
    """Retries generic HTTP requests using the requests library (non-streamed response)."""
    # Assign requests session if provided, otherwise create a new one.
    #
    session = session or requests.Session()

    # Attempt request <n_max_retries>, waiting <wait_for_s> between each attempt.
    #
    n_current_retry = 1
    while n_current_retry <= n_max_retries:
        try:
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json,
                params=params,
                timeout=timeout_s,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            if 500 <= response.status_code < 600:
                last_response = response
                last_error = err
                n_current_retry += 1
            else:
                raise err
        time.sleep(wait_for_s)
    raise RetryRequestError(last_error, last_response)


def _get_param_placeholder(param_type: str) -> str:
    """Get placeholder value for parameter type."""
    if param_type == "boolean":
        return "SOME_BOOLEAN_VALUE"
    if param_type == "integer":
        return "SOME_INTEGER_VALUE"
    return "SOME_STRING_VALUE"


def _build_query_params(parameters: list) -> tuple:
    """Build query string and dict from parameters."""
    query_params = []
    query_params_dict = {}
    for param in parameters:
        if param.get("in") == "query":
            param_name = param["name"]
            param_type = param.get("schema", {}).get("type", "string")
            value = _get_param_placeholder(param_type)
            query_params.append(f"{param_name}={value}")
            query_params_dict[param_name] = "SOME_STRING_VALUE"
    return "&".join(query_params), query_params_dict


def generate_code_sample(language: str, method: str, path: str, parameters: list, base_url: str = "") -> str:
    """Generate code sample for a given language, method, and path.

    Uses Jinja2 templates to generate code samples dynamically at runtime.
    The generated code includes a placeholder __API_SERVER_URL__ that will be
    replaced with the actual URL during documentation rendering.

    Args:
        language: The programming language (shell, python, go, js)
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        parameters: List of OpenAPI parameter definitions
        base_url: Base URL for the API (optional, defaults to empty string)

    Returns:
        Generated code sample as a string with __API_SERVER_URL__ placeholder
    """
    # Initialize Jinja2 environment on first call (cached via function attribute)
    if not hasattr(generate_code_sample, "_jinja_env"):
        code_template_dir = os.path.join(os.path.dirname(__file__), "..", "rest", "templates", "code_samples")
        generate_code_sample._jinja_env = Environment(loader=FileSystemLoader(code_template_dir))  # pylint: disable=protected-access

    template = generate_code_sample._jinja_env.get_template(f"{language}.j2")  # pylint: disable=protected-access
    query_string, query_params_dict = _build_query_params(parameters)
    parsed_url = urlparse(base_url)

    rendered = template.render(
        method=method,
        path=path.removeprefix("/v1"),
        base_url=base_url,
        query_params=query_string,
        query_params_dict=query_params_dict,
        hostname=parsed_url.hostname or "localhost",
        port=str(parsed_url.port) if parsed_url.port else "8080",
    )

    # Replace __API_SERVER_URL__ placeholder with template variable for docs.py to render
    return rendered.replace("__API_SERVER_URL__", "{{ api_server_url }}")


def create_custom_openapi_schema(app, logger):
    """Create custom OpenAPI schema with code samples and customizations.

    This function is compatible with FastAPI 0.124+ which aggressively caches
    OpenAPI schemas. Instead of mutating a cached schema, we generate a fresh
    schema using get_openapi() and customize it before caching.

    Args:
        app: FastAPI application instance
        logger: Logger instance for debugging

    Returns:
        Customized OpenAPI schema dictionary
    """
    base_path = os.environ.get("API_ROOT_PATH", "")

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    # Set server URL
    openapi_schema["servers"] = [{"url": f"{base_path}/v1"}]

    # Set custom tags
    openapi_schema["tags"] = [
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

    # Add code samples and remove 422 responses
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, operation in methods.items():
            # Remove 422 validation error responses
            if operation.get("responses", {}).get("422"):
                del operation["responses"]["422"]

            # Generate code samples for each language
            parameters = operation.get("parameters", [])
            code_samples = []

            for language in ["shell", "python", "go", "js"]:
                try:
                    sample = generate_code_sample(language, method, path, parameters)
                    code_samples.append({"lang": language, "source": sample})
                except Exception as e:
                    logger.warning(f"Failed to generate {language} code sample for {method} {path}: {e}")

            if code_samples:
                operation["x-code-samples"] = code_samples

    return openapi_schema
