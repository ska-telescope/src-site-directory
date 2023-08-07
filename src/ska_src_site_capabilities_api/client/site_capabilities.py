import json
import requests


class SiteCapabilitiesClient:
    def __init__(self, site_capabilities_api_url):
        self.site_capabilities_api_url = site_capabilities_api_url

    def ping(self):
        ping_endpoint = "{api_url}/ping".format(api_url=self.site_capabilities_api_url)
        resp = requests.get(ping_endpoint)
        print(resp.json())
        resp.raise_for_status()
        return resp.json()
