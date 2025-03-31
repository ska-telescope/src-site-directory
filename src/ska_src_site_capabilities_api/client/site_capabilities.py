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
        """Get the url to add a site.

        :return: The url.
        """
        add_site_www_url = "{api_url}/www/sites/add".format(api_url=self.api_url)
        return add_site_www_url

    @handle_client_exceptions
    def get_edit_site_www_url(self, site_name):
        """Get the url to edit a site.

        :return: The url.
        """
        edit_site_www_url = "{api_url}/www/sites/add/{site_name}".format(api_url=self.api_url, site_name=site_name)
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
        get_schema_endpoint = "{api_url}/schemas/{schema}".format(api_url=self.api_url, schema=schema)
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
        get_storage_area_by_id_endpoint = "{api_url}/storage-areas/{storage_area_id}".format(
            api_url=self.api_url, storage_area_id=storage_area_id
        )
        resp = self.session.get(get_storage_area_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_node_version(self, node_name: str, node_version: str = "latest"):
        """Get description of a node version.

        :param str node_name: The unique name of the node.
        :param str node_version: The version of the node (default to "latest").

        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/nodes/{node_name}"
        params = {"node_version": node_version}
        resp = self.session.get(endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_site_from_node_version(self, node_name: str, site_name: str, node_version: str = "latest"):
        """Get description of a site from a specific node version.

        :param str node_name: The name of the node.
        :param str site_name: The name of the site associated with the node.
        :param str node_version: The version of the node (default to "latest").

        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/nodes/{node_name}/sites/{site_name}"
        params = {"node_version": node_version}
        resp = self.session.get(endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_site_from_id(self, site_id: str):
        """Get description of a site from an identifier.

        :param str site_id: The unique identifier of the site.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/sites/{site_id}"
        resp = self.session.get(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def dump_nodes(self):
        """Dump all information about all available nodes.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/nodes/dump"
        resp = self.session.get(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def health(self):
        """Get API health.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        health_endpoint = "{api_url}/health".format(api_url=self.api_url)
        resp = self.session.get(health_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_compute(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List compute elements.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        compute_endpoint = "{api_url}/compute".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(compute_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_nodes(
        self,
        only_names: bool = False,
        include_inactive: bool = False,
    ):
        """List nodes with an option to return only node names.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        nodes_endpoint = "{api_url}/nodes".format(api_url=self.api_url)
        params = {
            "only_names": only_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(nodes_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_schemas(self):
        """List schemas.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        schemas_endpoint = "{api_url}/schemas".format(api_url=self.api_url)
        resp = self.session.get(schemas_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_services(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        only_service_types: list[str] = None,
        only_service_scope: str = "all",
        include_inactive: bool = False,
        associated_storage_area_id: str = None,
    ):
        """List services.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "only_service_types": ",".join(only_service_types) if only_service_types else None,
            "only_service_scope": only_service_scope,
            "include_inactive": include_inactive,
            "associated_storage_area_id": associated_storage_area_id,
        }
        resp = self.session.get(services_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_service_types(self):
        """List service types.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        service_types_endpoint = "{api_url}/services/types".format(api_url=self.api_url)
        resp = self.session.get(service_types_endpoint)
        resp.raise_for_status()
        return resp

    def list_service_types_core(self):
        """List core service types.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        service_types_core_endpoint = "{api_url}/services/types/core".format(api_url=self.api_url)
        resp = self.session.get(service_types_core_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_sites(
        self,
        only_node_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        sites_endpoint = "{api_url}/sites".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(sites_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_sites_latest(self):
        """List the latest versions of all sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        sites_latest_endpoint = "{api_url}/sites/latest".format(api_url=self.api_url)
        resp = self.session.get(sites_latest_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storages.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_grafana(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storages (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_grafana_endpoint = "{api_url}/storages/grafana".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_grafana_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_topojson(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storages (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_topojson_endpoint = "{api_url}/storages/topojson".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_topojson_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_endpoint = "{api_url}/storage-areas".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storage_areas_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_grafana(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_grafana_endpoint = "{api_url}/storage-areas/grafana".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storage_areas_grafana_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_topojson(
        self,
        only_node_names: list[str] = None,
        only_site_names: list[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_topojson_endpoint = "{api_url}/storage-areas/topojson".format(api_url=self.api_url)
        params = {
            "only_node_names": ",".join(only_node_names) if only_node_names else None,
            "only_site_names": ",".join(only_site_names) if only_site_names else None,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storage_areas_topojson_endpoint, params=params)
        resp.raise_for_status()
        return resp

    def list_storage_area_types(self):
        """List storage area types.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/storage-areas/types"
        resp = self.session.get(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def ping(self):
        """Ping the API.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = self.session.get(ping_endpoint)
        resp.raise_for_status()
        return resp
