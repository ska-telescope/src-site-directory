import requests

from ska_src_site_capabilities_api.common.exceptions import handle_client_exceptions


class SiteCapabilitiesClient:
    def __init__(self, api_url, session=None):
        self.api_url = api_url
        self.session = session

    @handle_client_exceptions
    def get_services(self):
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        if not self.session:
            resp = requests.get(services_endpoint)
        else:
            resp = self.session.get(services_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storages(self):
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        if not self.session:
            resp = requests.get(storages_endpoint)
        else:
            resp = self.session.get(storages_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storages_grafana(self):
        storages_grafana_endpoint = "{api_url}/storages/grafana".format(api_url=self.api_url)
        if not self.session:
            resp = requests.get(storages_grafana_endpoint)
        else:
            resp = self.session.get(storages_grafana_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def health(self):
        health_endpoint = "{api_url}/health".format(api_url=self.api_url)
        resp = requests.get(health_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def ping(self):
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = requests.get(ping_endpoint)
        resp.raise_for_status()
        return resp
