from typing import List

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
    def get_add_node_www_url(self):
        """Get the url to add a node.

        :return: The url.
        """
        add_node_www_url = "{api_url}/www/nodes".format(api_url=self.api_url)
        return add_node_www_url

    @handle_client_exceptions
    def get_edit_node_www_url(self, node_name):
        """Get the url to edit a node.

        :return: The url.
        """
        edit_node_www_url = "{api_url}/www/nodes/{node_name}".format(api_url=self.api_url, node_name=node_name)
        return edit_node_www_url

    @handle_client_exceptions
    def get_compute(self, compute_id: str):
        """Get description of a compute element from an identifier.

        :param str compute_id: The unique compute id.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_compute_by_id_endpoint = "{api_url}/compute/{compute_id}".format(api_url=self.api_url, compute_id=compute_id)
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
        get_service_by_id_endpoint = "{api_url}/services/{service_id}".format(api_url=self.api_url, service_id=service_id)
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
        get_storage_by_id_endpoint = "{api_url}/storages/{storage_id}".format(api_url=self.api_url, storage_id=storage_id)
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
        get_storage_area_by_id_endpoint = "{api_url}/storage-areas/{storage_area_id}".format(api_url=self.api_url, storage_area_id=storage_area_id)
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
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List compute elements.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        compute_endpoint = "{api_url}/compute".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
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
    def list_queues(self, node_names: str | None = None, site_names: str | None = None, include_inactive: bool = False):
        """List queues.

        :param node_names: Filter by node names (comma-separated string).
        :param site_names: Filter by site names (comma-separated string).
        :param include_inactive: Include inactive queues.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        queues_endpoint = "{api_url}/queues".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(queues_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def get_queue_from_id(self, queue_id: str):
        """Get Queue from ID.

        :param str queue_id: Unique queue identifier

        :return: A requests response.
        :rtype: requests.models.Response
        """
        get_queue_by_id_endpoint = "{api_url}/queues/{queue_id}".format(api_url=self.api_url, queue_id=queue_id)
        resp = self.session.get(get_queue_by_id_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_services(
        self,
        include_inactive: bool = False,
        associated_storage_area_id: str = None,
        site_names: List[str] = None,
        node_names: List[str] = None,
        service_types: List[str] = None,
        service_scope: str = "all",
        output: str = None,
    ):
        """List services.

        :param include_inactive: Include inactive services.
        :param associated_storage_area_id: Include services associated with storage.
        :param site_names: Filter by site names (comma-separated string).
        :param node_names: Filter by node names (comma-separated string).
        :param service_types: Filter by service types (comma-separated string).
        :param service_scope: Filter by scope of service (all||local||global).
        :param output: Output format (e.g., 'prometheus' for Prometheus HTTP SD response)

        :return: A requests response.
        :rtype: requests.models.Response
        """
        services_endpoint = "{api_url}/services".format(api_url=self.api_url)
        params = {
            "include_inactive": include_inactive,
            "associated_storage_area_id": associated_storage_area_id,
            "site_names": site_names,
            "node_names": node_names,
            "service_types": service_types,
            "service_scope": service_scope,
            "output": output,
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

    @handle_client_exceptions
    def list_sites(
        self,
        only_names: bool = False,
        node_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List sites.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        sites_endpoint = "{api_url}/sites".format(api_url=self.api_url)
        params = {
            "only_names": only_names,
            "node_names": node_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(sites_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storages.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_endpoint = "{api_url}/storages".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_grafana(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storages (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_grafana_endpoint = "{api_url}/storages/grafana".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_grafana_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storages_topojson(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storages (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storages_topojson_endpoint = "{api_url}/storages/topojson".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storages_topojson_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_endpoint = "{api_url}/storage-areas".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storage_areas_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_grafana(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas (for grafana).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_grafana_endpoint = "{api_url}/storage-areas/grafana".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
            "include_inactive": include_inactive,
        }
        resp = self.session.get(storage_areas_grafana_endpoint, params=params)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def list_storage_areas_topojson(
        self,
        node_names: List[str] = None,
        site_names: List[str] = None,
        include_inactive: bool = False,
    ):
        """List storage areas (topojson).

        :return: A requests response.
        :rtype: requests.models.Response
        """
        storage_areas_topojson_endpoint = "{api_url}/storage-areas/topojson".format(api_url=self.api_url)
        params = {
            "node_names": node_names,
            "site_names": site_names,
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

    @handle_client_exceptions
    def set_site_enabled(self, site_id: str):
        """Unset site force disabled.

        :param str site_id: The unique identifier of the site.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/sites/{site_id}/enable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_site_disabled(self, site_id: str):
        """Set site force disabled.

        :param str site_id: The unique identifier of the site.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/sites/{site_id}/disable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_compute_enabled(self, compute_id: str):
        """Unset compute force disabled.

        :param str compute_id: The unique identifier of the compute.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/compute/{compute_id}/enable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_compute_disabled(self, compute_id: str):
        """Set compute force disabled.

        :param str compute_id: The unique identifier of the compute.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/compute/{compute_id}/disable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_service_enabled(self, service_id: str):
        """Unset service force disabled.

        :param str service_id: The unique identifier of the service.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/services/{service_id}/enable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_service_disabled(self, service_id: str):
        """Set service force disabled.

        :param str service_id: The unique identifier of the service.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/services/{service_id}/disable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_storage_enabled(self, storage_id: str):
        """Unset storage force disabled.

        :param str storage_id: The unique identifier of the storage.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/storages/{storage_id}/enable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_storage_disabled(self, storage_id: str):
        """Set storage force disabled.

        :param str storage_id: The unique identifier of the storage.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/storages/{storage_id}/disable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_storage_area_enabled(self, storage_area_id: str):
        """Unset storage area force disabled.

        :param str storage_area_id: The unique identifier of the storage area.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/storage-areas/{storage_area_id}/enable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def set_storage_area_disabled(self, storage_area_id: str):
        """Set storage area force disabled.

        :param str storage_area_id: The unique identifier of the storage area.
        :return: A requests response.
        :rtype: requests.models.Response
        """
        endpoint = f"{self.api_url}/storage-areas/{storage_area_id}/disable"
        resp = self.session.put(endpoint)
        resp.raise_for_status()
        return resp
