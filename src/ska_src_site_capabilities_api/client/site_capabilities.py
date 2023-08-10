import json
import requests

from ska_src_site_capabilities_api.common.exceptions import handle_client_exceptions


class SiteCapabilitiesClient:
    def __init__(self, api_url):
        self.api_url = api_url

    @handle_client_exceptions
    def ping(self):
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = requests.get(ping_endpoint)
        resp.raise_for_status()
        return resp.json()
