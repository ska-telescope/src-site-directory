import requests
from urllib.parse import urlparse

import markdown


def parse_oidc_well_known(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def convert_readme_to_html_docs(text, remove_first_heading=True, convert_mermaid_diagrams=True, exclude_sections=None):
    """ Take an application's README file and parse it for display in HTML documentation. """
    parsed_text_lines = []
    in_mermaid_diagram = False
    in_excluded_section = False
    in_excluded_section_level = None
    for line in text.split('\n'):
        if remove_first_heading:
            if line.startswith('# '):
                continue                                            # remove first heading
            elif line.startswith('##'):
                line = line[1:]                                     # reduce headings by 1
        if convert_mermaid_diagrams:
            if line.startswith('```mermaid'):                       # convert mermaid diagrams to divs
                line = '<div class="mermaid">'
                in_mermaid_diagram = True
            elif line.startswith('```') and in_mermaid_diagram:
                line = '</div>'
                in_mermaid_diagram = False
        if exclude_sections:
            if line.startswith('#'):
                level = line.count('#')
                heading = line.lstrip('# ')
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
    parsed_text = '\n'.join(parsed_text_lines)
    return markdown.markdown(parsed_text, extensions=['codehilite', 'fenced_code', 'toc', 'tables'])


def request_url_for_app(function_name, request, scheme='http'):
    """ Return an url for a particular (sub)application's function name, <function_name>, given an instance of Request,
    request.

    Note:
      - request.scope.get('root_path') returns either e.g. /v1 or /api/v1 (if proxied)
      - request.base_url returns the full path up to and including the proxied route (e.g. api)
      - request.app.url_path_for(function_name) returns the (sub)application path for a given function name
        (function_name)
    """
    parsed_url = urlparse(str(request.base_url))
    return parsed_url._replace(
        scheme=scheme,
        path="{}{}".format(request.scope.get('root_path'), request.app.url_path_for(function_name))).geturl()


def urljoin(*args):
    """ Joins given arguments into an url. """
    return '/'.join(arg.strip('/') for arg in args)
