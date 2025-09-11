import ast
import json
import time
import uuid
from urllib.parse import urlparse

import jsonref
import markdown
import requests

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
