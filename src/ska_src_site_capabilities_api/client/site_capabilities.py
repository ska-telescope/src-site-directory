import requests

from ska_src_site_capabilities_api.common.exceptions import handle_client_exceptions


class SiteCapabilitiesClient:
    def __init__(self, api_url, session=None):
        self.api_url = api_url
        if session:
            self.session = session
        else:
            self.session = requests.Session()

    @handle_client_exceptions
    def get_services(self):
        """ Get a list of SRCNet services.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        resp = self.session.get(services_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storages(self):
        """ Get a list of SRCNet storages.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        resp = self.session.get(storages_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storages_grafana(self):
        """ Get a list of SRCNet storages (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_grafana_endpoint = "{api_url}/storages/grafana".format(api_url=self.api_url)
        resp = self.session.get(storages_grafana_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def health(self):
        """ Get the service health.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        health_endpoint = "{api_url}/health".format(api_url=self.api_url)
        resp = self.session.get(health_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def ping(self):
        """ Ping the service.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = self.session.get(ping_endpoint)
        resp.raise_for_status()
        return resp
