"""
A module for site capabilities client
"""
import requests

from ska_src_site_capabilities_api.common.exceptions import (
    handle_client_exceptions,
)


class SiteCapabilitiesClient:
    """
    A site capabilities client class.
    """

    def __init__(self, api_url, session=None):
        self.api_url = api_url
        if session:
            self.session = session
        else:
            self.session = requests.Session()

    @handle_client_exceptions
    def get_add_site_www_url(self):
        """Get the add site www URL.

        :return: The URL.
        """
        add_site_www_url = "{api_url}/www/sites/add".format(
            api_url=self.api_url
        )
        return add_site_www_url

    @handle_client_exceptions
    def get_edit_site_www_url(self, site_name):
        """Get the edit site www URL.

        :return: The URL.
        """
        edit_site_www_url = "{api_url}/www/sites/add/{site_name}".format(
            api_url=self.api_url, site_name=site_name
        )
        return edit_site_www_url

    @handle_client_exceptions
    def get_compute(self, compute_id: str):
        """Get description of a compute element from an identifier.

        :param str compute_id: The unique compute id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_compute_by_id_endpoint = "{api_url}/compute/{compute_id}".format(
            api_url=self.api_url, compute_id=compute_id
        )
        resp = self.session.get(get_compute_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_schema(self, schema: str):
        """Get a schema.

        :param str schema: The name of the schema.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_schema_endpoint = "{api_url}/schemas/{schema}".format(
            api_url=self.api_url, schema=schema
        )
        resp = self.session.get(get_schema_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_service(self, service_id: str):
        """Get description of a service from an identifier.

        :param str service_id: The unique service id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_service_by_id_endpoint = "{api_url}/services/{service_id}".format(
            api_url=self.api_url, service_id=service_id
        )
        resp = self.session.get(get_service_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storage(self, storage_id: str):
        """Get description of a storage from an identifier.

        :param str storage_id: The unique storage id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_storage_by_id_endpoint = "{api_url}/storages/{storage_id}".format(
            api_url=self.api_url, storage_id=storage_id
        )
        resp = self.session.get(get_storage_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_storage_area(self, storage_area_id: str):
        """Get description of a storage area from an identifier.

        :param str storage_area_id: The unique storage area id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_storage_area_by_id_endpoint = (
            "{api_url}/storage-areas/{storage_area_id}".format(
                api_url=self.api_url, storage_area_id=storage_area_id
            )
        )
        resp = self.session.get(get_storage_area_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def health(self):
        """Get the service health.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        health_endpoint = "{api_url}/health".format(api_url=self.api_url)
        resp = self.session.get(health_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_compute(self):
        """Get a list of SRCNet compute elements.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        compute_endpoint = "{api_url}/compute".format(api_url=self.api_url)
        resp = self.session.get(compute_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_schemas(self):
        """Get a list of schemas.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        schemas_endpoint = "{api_url}/schemas".format(api_url=self.api_url)
        resp = self.session.get(schemas_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_services(
        self, include_associated_with_compute=True, include_disabled=False
    ):
        """Get a list of SRCNet services.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        params = {
            "include_associated_with_compute": include_associated_with_compute,
            "include_disabled": include_disabled,
        }
        resp = self.session.get(services_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_service_types(self):
        """Get a list of SRCNet service types.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        service_types_endpoint = "{api_url}/services/types".format(
            api_url=self.api_url
        )
        resp = self.session.get(service_types_endpoint)
        resp.raise_for_status()
        return resp

    def list_service_types_core(self):
        """Get a list of SRCNet core service types.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        service_types_core_endpoint = "{api_url}/services/types/core".format(
            api_url=self.api_url
        )
        resp = self.session.get(service_types_core_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_sites(self):
        """Get a list of SRCNet sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        sites_endpoint = "{api_url}/sites".format(api_url=self.api_url)
        resp = self.session.get(sites_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_sites_latest(self):
        """Get latest versions of all sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        sites_latest_endpoint = "{api_url}/sites/latest".format(
            api_url=self.api_url
        )
        resp = self.session.get(sites_latest_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages(self):
        """Get a list of SRCNet storages.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        resp = self.session.get(storages_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_grafana(self):
        """Get a list of SRCNet storages (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_grafana_endpoint = "{api_url}/storages/grafana".format(
            api_url=self.api_url
        )
        resp = self.session.get(storages_grafana_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_topojson(self):
        """Get a list of SRCNet storages (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_topojson_endpoint = "{api_url}/storages/topojson".format(
            api_url=self.api_url
        )
        resp = self.session.get(storages_topojson_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas(self):
        """Get a list of SRCNet storage areas.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_endpoint = "{api_url}/storage-areas".format(
            api_url=self.api_url
        )
        resp = self.session.get(storage_areas_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_grafana(self):
        """Get a list of SRCNet storage areas (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_grafana_endpoint = (
            "{api_url}/storage-areas/grafana".format(api_url=self.api_url)
        )
        resp = self.session.get(storage_areas_grafana_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_topojson(self):
        """Get a list of SRCNet storage areas (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_topojson_endpoint = (
            "{api_url}/storage-areas/topojson".format(api_url=self.api_url)
        )
        resp = self.session.get(storage_areas_topojson_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def ping(self):
        """Ping the service.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = self.session.get(ping_endpoint)
        resp.raise_for_status()
        return resp
