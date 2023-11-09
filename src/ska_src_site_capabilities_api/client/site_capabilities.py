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
    def get_add_site_www_url(self):
        """ Get the add site www URL.

        :return: The URL.
        """
        add_site_www_url = "{api_url}/www/sites/add".format(api_url=self.api_url)
        return add_site_www_url

    @handle_client_exceptions
    def get_edit_site_www_url(self, site_name):
        """ Get the edit site www URL.

        :return: The URL.
        """
        edit_site_www_url = "{api_url}/www/sites/add/{site_name}".format(api_url=self.api_url, site_name=site_name)
        return edit_site_www_url

    @handle_client_exceptions
    def get_service(self, service_id: str):
        """ Get description of a service from an identifier.

        :param str service_id: The unique service id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_service_by_id_endpoint = "{api_url}/services/{service_id}".format(api_url=self.api_url,
                                                                              service_id=service_id)
        resp = self.session.get(get_service_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storage(self, storage_id: str):
        """ Get description of a storage from an identifier.

        :param str storage_id: The unique service id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_storage_by_id_endpoint = "{api_url}/storages/{storage_id}".format(api_url=self.api_url,
                                                                              storage_id=storage_id)
        resp = self.session.get(get_storage_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_services(self):
        """ Get a list of SRCNet services.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        resp = self.session.get(services_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_sites(self):
        """ Get a list of SRCNet sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/sites".format(api_url=self.api_url)
        resp = self.session.get(services_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages(self):
        """ Get a list of SRCNet storages.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        resp = self.session.get(storages_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_grafana(self):
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
