"""OpenAPI schema customization and code sample generation."""

import os
from urllib.parse import urlparse

from fastapi.openapi.utils import get_openapi
from jinja2 import Environment, FileSystemLoader


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
        code_template_dir = os.path.join(os.path.dirname(__file__), "templates", "code_samples")
        generate_code_sample._jinja_env = Environment(loader=FileSystemLoader(code_template_dir))  # pylint: disable=protected-access

    template = generate_code_sample._jinja_env.get_template(f"{language}.j2")  # pylint: disable=protected-access
    query_string, query_params_dict = _build_query_params(parameters)
    parsed_url = urlparse(base_url)

    rendered = template.render(
        method=method,
        path=path,
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
        version=os.environ.get("SERVICE_VERSION", app.version),
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
