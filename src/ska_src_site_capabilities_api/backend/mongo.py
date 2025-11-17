import copy
import json
from datetime import datetime, timezone

import dateutil.parser
from pymongo import MongoClient

from ska_src_site_capabilities_api.backend.backend import Backend


class MongoBackend(Backend):
    """Backend API for MongoDB."""

    def __init__(self, mongo_database, mongo_username=None, mongo_password=None, mongo_host=None, mongo_port=None, client=None):
        """
        Initialises a MongoBackend instance.

        Args:
            mongo_database: Name of the MongoDB database.
            mongo_username: Username for MongoDB authentication.
            mongo_password: Password for MongoDB authentication.
            mongo_host: Hostname of the MongoDB server.
            mongo_port: Port of the MongoDB server.
            client: Optional MongoDB client for mocking/testing.
        """
        super().__init__()
        if mongo_database and mongo_username and mongo_password and mongo_host:
            self.connection_string = "mongodb://{}:{}@{}:{}/".format(mongo_username, mongo_password, mongo_host, int(mongo_port))
        self.mongo_database = mongo_database
        self.client = client  # used for mocking

    def _get_mongo_client(self):
        """
        Retrieves the MongoDB client.

        Returns:
            A MongoDB client instance.
        """
        if self.client:
            return self.client
        else:
            return MongoClient(self.connection_string)

    def _get_service_labels_for_prometheus(self, service):
        """
        Returns Prometheus labels for a service, including downtime status and metadata if applicable.

        Args:
            service: Service data with optional downtime details.

        Returns:
            dict: Prometheus label key-value pairs.
        """
        labels = {}

        for key, value in service.items():
            if isinstance(value, (dict, list)):
                if key == "downtime":
                    now = datetime.now(timezone.utc)
                    upcoming_downtimes = []
                    nearest_downtime = None
                    is_down = False
                    for dt in value:
                        try:
                            start_str, end_str = dt.get("date_range", "").split(" to ")
                            print(start_str, end_str, dt)
                            start = dateutil.parser.parse(start_str)
                            end = dateutil.parser.parse(end_str)
                            upcoming_downtimes.append((start, end, dt))
                        except Exception:
                            print("Failed to parse date range:", dt)
                            continue
                    upcoming_downtimes.sort(key=lambda x: x[0])
                    for start, end, dt in upcoming_downtimes:
                        if start <= now <= end:
                            is_down = True
                            nearest_downtime = dt
                            print(nearest_downtime)
                            break
                        if start > now and nearest_downtime is None:
                            nearest_downtime = dt
                    if nearest_downtime:
                        labels["in_downtime"] = str(is_down).lower()
                        labels["downtime_type"] = nearest_downtime.get("type", "")
                        labels["downtime_date_range"] = nearest_downtime.get("date_range", "")
                        labels["downtime_reason"] = nearest_downtime.get("reason", "")
                else:
                    labels[key] = json.dumps(value)
            else:
                labels[key] = str(value)

        return labels

    def _format_services_with_targets_for_prometheus(self, services):
        """
        Returns a list of services formatted for Prometheus Service Discovery.

        Args:
            services: List of service dictionaries.
        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """
        formatted_services = []
        for service in services:
            if not service.get("host"):
                continue
            path = service.get("path", "")
            path = path.strip() if path else ""
            if path and not path.startswith("/"):
                path = "/" + path

            target = f'{service.get("prefix", "https").replace("://", "")}://{service.get("host")}'
            if service.get("port") is not None:
                target += f':{service.get("port")}'

            target += path

            if service.get("type") == "gatekeeper":
                target += "/ping"

            labels = self._get_service_labels_for_prometheus(service=service)
            formatted_services.append({"targets": [target], "labels": labels})

        return formatted_services

    def _get_storage_areas_with_host_for_prometheus(self, node_names=None, site_names=None):
        """
        Returns a list of storage areas with host information formatted for Prometheus Service Discovery.

        Args:
            node_names: List of node names to filter storage areas by. If None, no node filtering is applied.
            site_names: List of site names to filter storage areas by. If None, no site filtering is applied.

        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """
        node_names = node_names or []
        site_names = site_names or []
        response = []
        for storage in self.list_storages(node_names=node_names, site_names=site_names, include_inactive=True):
            supported_protocols = storage.get("supported_protocols", [])

            if not supported_protocols:
                supported_protocols = [{"prefix": "https", "port": 443}]

            for storage_area in storage.get("areas", []):
                for protocol in supported_protocols:
                    response.append(
                        {
                            "parent_node_name": storage.get("parent_node_name"),
                            "parent_site_name": storage.get("parent_site_name"),
                            "parent_site_id": storage.get("parent_site_id"),
                            "parent_storage_id": storage.get("id"),
                            "host": storage.get("host"),
                            "base_path": storage.get("base_path"),
                            "prefix": protocol.get("prefix"),
                            "port": protocol.get("port"),
                            **storage_area,
                            "type": f"{storage_area.get('type', '').upper()}-T{storage_area.get('tier', '0')}",
                        }
                    )

        return self.format_label_response(response)

    def format_label_response(self, response: list) -> list:
        """
        Formats a list of resources for Prometheus Service Discovery.

        Args:
            response: List of resource dictionaries.

        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """
        formatted = []
        for resource in response:
            target = f'{resource.get("prefix", "https").replace("://", "")}://{resource.get("host")}'
            if resource.get("port") is not None:
                target += f':{resource.get("port")}'
            target += f'{resource.get("base_path")}'
            relative_path = resource.get("relative_path") or ""
            if relative_path.startswith(("http://", "https://")):
                target = relative_path
            else:
                target += f'/{relative_path.lstrip("/")}'
            formatted.append({"targets": [target], "labels": self._get_service_labels_for_prometheus(resource)})
        return formatted

    def _get_storage_with_labels_for_prometheus(self, node_names=None, site_names=None):
        """
        Returns a list of storage resources formatted for Prometheus Service Discovery.
        Args:
            node_names: List of node names to filter storage resources by. If None, no node filtering is applied.
            site_names: List of site names to filter storage resources by. If None, no site filtering is applied.
            include_inactive: Boolean to include inactive storage resources.
        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """

        storages = self.list_storages(node_names=node_names, site_names=site_names, include_inactive=True)
        response = []

        for storage in storages:
            supported_protocols = storage.get("supported_protocols", [])

            if not supported_protocols:
                supported_protocols = [{"prefix": "https", "port": 443}]

            for protocol in supported_protocols:
                response.append(
                    {
                        "parent_node_name": storage.get("parent_node_name"),
                        "parent_site_name": storage.get("parent_site_name"),
                        "parent_site_id": storage.get("parent_site_id"),
                        "parent_storage_id": storage.get("id"),
                        "host": storage.get("host"),
                        "base_path": storage.get("base_path"),
                        "prefix": protocol.get("prefix"),
                        "port": protocol.get("port"),
                        "downtime": storage.get("downtime"),
                    }
                )

        return self.format_label_response(response)

    def _get_sites_with_labels_for_prometheus(self, node_names=None):
        """
        Returns a list of sites formatted for Prometheus Service Discovery.

        Args:
            node_names: List of node names to filter sites by. If None, no node filtering is applied.
            include_inactive: Boolean to include inactive sites.

        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """
        sites = self.list_sites(node_names=node_names, include_inactive=True)
        print(sites)
        response = []

        for site in sites:
            response.append(
                {
                    "site_name": site.get("name"),
                    "country": site.get("country"),
                    "latitude": site.get("latitude"),
                    "longitude": site.get("longitude"),
                    "downtime": site.get("downtime"),
                }
            )

        formatted_sites = []

        for site in response:
            formatted_sites.append({"targets": [f'site_{site.get("site_name")}'], "labels": self._get_service_labels_for_prometheus(site)})
            print(formatted_sites)
        return formatted_sites

    def _get_compute_with_labels_for_prometheus(self, node_names=None, site_names=None):
        """
        Returns a list of compute resources formatted for Prometheus Service Discovery.

        Args:
            node_names: List of node names to filter compute resources by. If None, no node filtering is applied.
            site_names: List of site names to filter compute resources by. If None, no site filtering is applied.

        Returns:
            A list of dictionaries formatted for Prometheus Service Discovery.
        """
        computes = self.list_compute(node_names=node_names, site_names=site_names, include_inactive=True)
        print(computes)
        response = []

        for compute in computes:
            response.append(
                {
                    "compute_name": compute.get("name"),
                    "parent_node_name": compute.get("parent_node_name"),
                    "parent_site_name": compute.get("parent_site_name"),
                    "parent_site_id": compute.get("parent_site_id"),
                    "downtime": compute.get("downtime"),
                }
            )

        formatted_computes = []

        for compute in response:
            formatted_computes.append({"targets": [], "labels": self._get_service_labels_for_prometheus(compute)})
        return formatted_computes

    def _is_element_in_downtime(self, downtime):
        """
        Checks if an element is in downtime.

        Args:
            downtime: A list of downtime entries, each containing a date range.

        Returns:
            Boolean indicating whether the element is in downtime.
        """
        for entry in downtime:
            if entry.get("date_range"):
                start_date_str_utc, end_date_str_utc = entry.get("date_range").split(" to ")
                start_date_utc = dateutil.parser.isoparse(start_date_str_utc)
                end_date_utc = dateutil.parser.isoparse(end_date_str_utc)
                now_utc = datetime.now(timezone.utc)

                if start_date_utc < now_utc < end_date_utc:
                    return True
        return False

    def _remove_inactive_elements(self, element):
        """
        Recursively removes elements from a nested structure if they are in downtime or disabled.

        Args:
            element: A dictionary or list representing the structure to filter.

        Returns:
            The filtered structure with inactive elements removed.
        """
        if isinstance(element, dict):
            if self._is_element_in_downtime(element.get("downtime", [])) or element.get("is_force_disabled", False):
                return None

            # Recurse through the element, checking downtime at each level
            filtered_element = {}
            for key, value in element.items():
                filtered_child = self._remove_inactive_elements(value)
                if filtered_child:
                    filtered_element[key] = filtered_child
            return filtered_element if filtered_element else None

        elif isinstance(element, list):
            filtered_list = [self._remove_inactive_elements(item) for item in element]
            return [item for item in filtered_list if item is not None]
        return element

    def add_edit_node(self, node_values, node_name=None):
        """
        Adds or edits a node in the database.

        Args:
            node_values: Dictionary containing the node's attributes.
            node_name: Name of the node to edit. If None, a new node is added.

        Returns:
            The ID of the inserted or updated node.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes
        nodes_archived = db.nodes_archived

        # Get the latest version of this node
        latest_node = self.get_node(node_name=node_name, node_version="latest")
        if not latest_node:  # Adding a new node
            node_values["version"] = 1
        else:  # Updating an existing node
            node_values["version"] = latest_node.get("version") + 1

        node_values.pop("_id", None)

        # Insert this new version of the node into the nodes collection
        inserted_node = nodes.insert_one(node_values)

        # Move the previous version of the node to the nodes_archived collection
        # only if a previous version existed and insertion into nodes was successful
        if latest_node and inserted_node.inserted_id:
            # Only delete it from nodes if we successfully added the previous version
            # to nodes_archived
            if nodes_archived.insert_one(latest_node).inserted_id:
                nodes.delete_one({"name": node_name, "version": latest_node.get("version")})

        return inserted_node.inserted_id

    def delete_all_nodes(self):
        """
        Deletes all node documents from both active and archived collections.

        This method removes all documents from the `nodes` and `nodes_archived` collections.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]

        result_nodes = db.nodes.delete_many({})
        result_archived = db.nodes_archived.delete_many({})
        return {
            "deleted_from_nodes_count": result_nodes.deleted_count,
            "deleted_from_nodes_archived_count": result_archived.deleted_count,
        }

    def delete_node_by_name(self, node_name):
        """
        Deletes a node document with the specified name from both active and archived collections.

        Args:
            node_name (str): The name of the node to delete.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]

        result_nodes = db.nodes.delete_many({"name": node_name})
        result_archived = db.nodes_archived.delete_many({"name": node_name})
        return {
            "deleted_from_nodes_count": result_nodes.deleted_count,
            "deleted_from_nodes_archived_count": result_archived.deleted_count,
        }

    def get_compute(self, compute_id):
        """
        Retrieves a compute resource by its ID.

        Args:
            compute_id: The ID of the compute resource.

        Returns:
            A dictionary containing the compute resource and its parent information.
        """
        response = {}
        for compute in self.list_compute(include_inactive=True):
            parent_node_name = compute.get("parent_node_name")
            parent_site_name = compute.get("parent_site_name")
            parent_site_id = compute.get("parent_site_id")
            if compute.get("id") == compute_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, "parent_site_id": parent_site_id, **compute}
                break
        return response

    def get_node(self, node_name, node_version="latest"):
        """
        Retrieves a version of a node.

        Args:
            node_name: The name of the node.
            node_version: The version of the node to retrieve. Defaults to "latest".

        Returns:
            A dictionary containing the node's attributes.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]

        if node_version == "latest":
            this_node = db.nodes.find_one({"name": node_name})
        else:
            this_node = db.nodes.find_one({"name": node_name, "version": int(node_version)})
            if not this_node:
                this_node = db.nodes_archived.find_one({"name": node_name, "version": int(node_version)})

        if this_node:
            this_node.pop("_id")
        return this_node if this_node else {}

    def get_service(self, service_id):
        """
        Retrieves a service by its ID.

        Args:
            service_id: The ID of the service.

        Returns:
            A dictionary containing the service and its parent information.
        """
        response = {}
        for service in self.list_services(include_inactive=True):
            parent_node_name = service.get("parent_node_name")
            parent_site_name = service.get("parent_site_name")
            parent_site_id = service.get("parent_site_id")
            parent_compute_id = service.get("parent_compute_id")

            # get compute element to establish if local or global service
            compute = self.get_compute(parent_compute_id)
            if any(s.get("id") == service_id for s in compute.get("associated_global_services", [])):
                service_scope = "associated_global_services"
            elif any(s.get("id") == service_id for s in compute.get("associated_local_services", [])):
                service_scope = "associated_local_services"
            else:
                service_scope = None

            if service.get("id") == service_id:
                response = {
                    "parent_node_name": parent_node_name,
                    "parent_site_name": parent_site_name,
                    "parent_site_id": parent_site_id,
                    "parent_compute_id": parent_compute_id,
                    "scope": service_scope,
                    **service,
                }
                break
        return response

    def get_site(self, site_id):
        """
        Retrieves a site by its ID.

        Args:
            site_id: The ID of the site.

        Returns:
            A dictionary containing the site and its parent information.
        """
        response = {}
        for site in self.list_sites(include_inactive=True):
            parent_node_name = site.get("parent_node_name")
            if site.get("id") == site_id:
                response = {"parent_node_name": parent_node_name, **site}
                break
        return response

    def get_site_from_names(self, node_name, node_version, site_name):
        """
        Retrieves a site by its name, node, and version.

        Args:
            node_name: The name of the node.
            node_version: The version of the node.
            site_name: The name of the site.

        Returns:
            A dictionary containing the site and its parent information, or None if not found.
        """
        node = self.get_node(node_name=node_name, node_version=node_version)
        if not node:
            return None

        for site in node.get("sites", []):
            if site.get("name") == site_name:
                return {"parent_node_name": node.get("name"), **site}
        return None

    def get_storage(self, storage_id):
        """
        Retrieves a storage resource by its ID.

        Args:
            storage_id: The ID of the storage resource.

        Returns:
            A dictionary containing the storage resource and its parent information.
        """
        response = {}
        for storage in self.list_storages(include_inactive=True):
            parent_node_name = storage.get("parent_node_name")
            parent_site_name = storage.get("parent_site_name")
            parent_site_id = storage.get("parent_site_id")
            if storage.get("id") == storage_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, "parent_site_id": parent_site_id, **storage}
                break
        return response

    def get_storage_area(self, storage_area_id):
        """
        Retrieves a storage area by its ID.

        Args:
            storage_area_id: The ID of the storage area.

        Returns:
            A dictionary containing the storage area and its parent information.
        """
        response = {}
        for storage_area in self.list_storage_areas(include_inactive=True):
            parent_node_name = storage_area.get("parent_node_name")
            parent_site_name = storage_area.get("parent_site_name")
            parent_site_id = storage_area.get("parent_site_id")
            parent_storage_id = storage_area.get("parent_storage_id")
            if storage_area.get("id") == storage_area_id:
                response = {
                    "parent_node_name": parent_node_name,
                    "parent_site_name": parent_site_name,
                    "parent_site_id": parent_site_id,
                    "parent_storage_id": parent_storage_id,
                    **storage_area,
                }
                break
        return response

    def list_compute(self, node_names=None, site_names=None, include_inactive=False):
        """
        Lists compute resources based on specified filters.

        Args:
            node_names: List of node names to filter compute resources by. If None, no node filtering is applied.
            site_names: List of site names to filter compute resources by. If None, no site filtering is applied.
            include_inactive: Boolean to include inactive compute resources.

        Returns:
            A list of compute dictionaries, each containing parent information.
        """
        node_names = node_names or []
        site_names = site_names or []
        response = []
        for site in self.list_sites(node_names=node_names, include_inactive=include_inactive):
            parent_site_name = site.get("name")
            parent_site_id = site.get("id")
            for compute in site.get("compute", []):
                if site_names and parent_site_name not in site_names:
                    continue
                compute_with_parent = {
                    "parent_node_name": site.get("parent_node_name"),
                    "parent_site_name": parent_site_name,
                    "parent_site_id": parent_site_id,
                    **compute,
                }
                response.append(compute_with_parent)
        return response

    def list_nodes(self, include_archived=False, include_inactive=True):
        """Retrieve versions of all nodes."""
        client = self._get_mongo_client()
        db = client[self.mongo_database]

        nodes = list(db.nodes.find({}))  # query for active nodes

        if include_archived:
            nodes.extend(db.nodes_archived.find({}))  # include archived nodes

        if not include_inactive:
            nodes = self._remove_inactive_elements(nodes)  # filter out inactive nodes

        for node in nodes:
            node.pop("_id", None)

        return nodes or []

    def list_services(
        self,
        node_names=None,
        site_names=None,
        service_types=None,
        service_scope="all",
        include_inactive=False,
        associated_storage_area_id=None,
        for_prometheus=False,
    ):
        """
        Lists services based on specified filters.

        Args:
            node_names: List of node names to filter services by. If None, no node filtering is applied.
            site_names: List of site names to filter services by. If None, no site filtering is applied.
            service_types: List of service types to filter services by. If None, no type filtering is applied.
            service_scope: String ("all", "local", "global") to filter by service scope.
            include_inactive: Boolean to include inactive compute resources.
            associated_storage_area_id: String to filter services by associated storage area ID.
            for_prometheus: Boolean to return data formatted for Prometheus Service Discovery Config.

        Returns:
            A list of service dictionaries, each containing scope and parent information.
        """
        response = []

        # Handle None cases for input lists
        node_names = node_names or []
        site_names = site_names or []
        service_types = service_types or []

        include_inactive = for_prometheus or include_inactive

        print(include_inactive)
        computes = self.list_compute(
            node_names=node_names,
            site_names=site_names,
            include_inactive=include_inactive,
        )

        for compute in computes:
            if service_scope in ["all", "local"]:
                for service in compute.get("associated_local_services", []):
                    # Apply filters for service type and associated storage area ID
                    if service_types and service.get("type") not in service_types:
                        continue
                    if associated_storage_area_id and service.get("associated_storage_area_id") != associated_storage_area_id:
                        continue
                    # Add parent information
                    response.append(
                        {
                            "scope": "local",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_site_name"),
                            "parent_site_id": compute.get("parent_site_id"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )

            if service_scope in ["all", "global"]:
                for service in compute.get("associated_global_services", []):
                    # Apply filters for service type and associated storage area ID
                    if service_types and service.get("type") not in service_types:
                        continue
                    if associated_storage_area_id and service.get("associated_storage_area_id") != associated_storage_area_id:
                        continue
                    # Add parent information
                    response.append(
                        {
                            "scope": "global",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_site_name"),
                            "parent_site_id": compute.get("parent_site_id"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )

        if for_prometheus:
            formatted = []
            services = self._format_services_with_targets_for_prometheus(response)
            formatted.extend(services)

            storage_areas = self._get_storage_areas_with_host_for_prometheus(node_names, site_names)
            formatted.extend(storage_areas)

            storages = self._get_storage_with_labels_for_prometheus(node_names, site_names)
            formatted.extend(storages)

            sites = self._get_sites_with_labels_for_prometheus(node_names)
            formatted.extend(sites)

            computes = self._get_compute_with_labels_for_prometheus(node_names, site_names)
            formatted.extend(computes)

            return formatted

        return response

    def list_service_types_from_schema(self, schema):
        """
        Retrieves a list of service types from a schema.

        Args:
            schema: A dictionary representing the schema.

        Returns:
            A list of service types defined in the schema.
        """
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response

    def list_sites(self, node_names=None, include_inactive=False):
        """
        Lists sites based on specified filters.

        Args:
            node_names: List of node names to filter sites by. If None, no node filtering is applied.
            include_inactive: Boolean to include inactive sites.

        Returns:
            A list of site dictionaries, each containing parent information.
        """
        node_names = node_names or []
        response = []
        for node in self.list_nodes(include_inactive=include_inactive):
            parent_node_name = node.get("name")
            for site in node.get("sites", []):
                if node_names:
                    if parent_node_name not in node_names:
                        continue
                response.append({"parent_node_name": parent_node_name, **site})
        return response

    def list_storages(self, node_names=None, site_names=None, topojson=False, for_grafana=False, include_inactive=False):
        """
        Lists storage resources based on specified filters.

        Args:
            node_names: List of node names to filter storages by. If None, no node filtering is applied.
            site_names: List of site names to filter storages by. If None, no site filtering is applied.
            topojson: Boolean to return data in TopoJSON format.
            for_grafana: Boolean to return data formatted for Grafana.
            include_inactive: Boolean to include inactive storages.

        Returns:
            A list of storage dictionaries, each containing parent information,
            or a TopoJSON object if `topojson` is True.
        """
        node_names = node_names or []
        site_names = site_names or []
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []
        for site in self.list_sites(node_names=node_names, include_inactive=include_inactive):
            parent_site_name = site.get("name")
            parent_site_id = site.get("id")
            for storage in site.get("storages", []):
                if site_names:
                    if parent_site_name not in site_names:
                        continue
                if topojson:
                    response["objects"]["sites"]["geometries"].append(
                        {
                            "type": "Point",
                            "coordinates": [
                                site.get("longitude"),
                                site.get("latitude"),
                            ],
                            "properties": {"name": storage.get("identifier")},
                        }
                    )
                elif for_grafana:
                    # Skip sites without latitude/longitude (required for Grafana format)
                    site_latitude = site.get("latitude")
                    site_longitude = site.get("longitude")
                    if site_latitude is not None and site_longitude is not None:
                        response.append(
                            {
                                "key": storage.get("identifier"),
                                "latitude": site_latitude,
                                "longitude": site_longitude,
                                "name": storage.get("identifier"),
                            }
                        )
                else:
                    # Add parent information
                    response.append(
                        {
                            "parent_node_name": site.get("parent_node_name"),
                            "parent_site_name": parent_site_name,
                            "parent_site_id": parent_site_id,
                            **storage,
                        }
                    )
        return response

    def list_storage_areas(self, node_names=None, site_names=None, topojson=False, for_grafana=False, include_inactive=False):
        """
        Lists storage areas based on specified filters.

        Args:
            node_names: List of node names to filter storage areas by. If None, no node filtering is applied.
            site_names: List of site names to filter storage areas by. If None, no site filtering is applied.
            topojson: Boolean to return data in TopoJSON format.
            for_grafana: Boolean to return data formatted for Grafana.
            include_inactive: Boolean to include inactive storage areas.

        Returns:
            A list of storage area dictionaries, each containing parent information,
            or a TopoJSON object if `topojson` is True.
        """
        node_names = node_names or []
        site_names = site_names or []

        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []
        for storage in self.list_storages(node_names=node_names, site_names=site_names, include_inactive=include_inactive):
            parent_storage = self.get_site_from_names(
                node_name=storage.get("parent_node_name"),
                node_version="latest",
                site_name=storage.get("parent_site_name"),
            )
            site_latitude = parent_storage.get("latitude")
            site_longitude = parent_storage.get("longitude")
            for storage_area in storage.get("areas", []):
                if topojson:
                    print()
                    response["objects"]["sites"]["geometries"].append(
                        {
                            "type": "Point",
                            "coordinates": [site_longitude, site_latitude],
                            "properties": {"name": storage_area.get("identifier")},
                        }
                    )
                elif for_grafana:
                    response.append(
                        {
                            "key": storage_area.get("identifier"),
                            "latitude": site_latitude,
                            "longitude": site_longitude,
                            "name": storage_area.get("identifier"),
                        }
                    )
                else:
                    # Add parent information
                    response.append(
                        {
                            "parent_node_name": storage.get("parent_node_name"),
                            "parent_site_name": storage.get("parent_site_name"),
                            "parent_site_id": storage.get("parent_site_id"),
                            "parent_storage_id": storage.get("id"),
                            **storage_area,
                        }
                    )
        return response

    def list_storage_area_types_from_schema(self, schema):
        """
        Extracts the list of storage area types from a given JSON schema.

        This method retrieves the enumeration of valid storage area types defined
        under the 'type' property in the provided schema.

        Args:
            schema (dict): A JSON schema dictionary that may contain a 'type' property with an enum.

        Returns:
            list: A list of valid storage area types, or an empty list if not defined in the schema.
        """
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response

    def set_site_force_disabled_flag(self, site_id: str, flag: bool):
        """
        Sets the 'is_force_disabled' flag for a specific site within a node.

        This method updates the `is_force_disabled` field for the site identified
        by `site_id` in the MongoDB `nodes` collection.

        Args:
            site_id (str): The ID of the site whose flag should be updated.
            flag (bool): The value to set for the `is_force_disabled` flag.

        Returns:
            dict: The updated site dictionary if the site is found and updated,
                  or an empty dictionary if the site is not found.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes
        node = nodes.find_one({"sites.id": site_id})
        if not node:
            return {}

        updated_node = copy.deepcopy(node)
        updated_site = None
        for site in updated_node.get("sites", []):
            if site.get("id") == site_id:
                site["is_force_disabled"] = flag
                updated_site = site
                break

        if updated_site is None:
            return {}

        # Pass the modified node to add_edit_node
        self.add_edit_node(updated_node, node_name=updated_node.get("name"))
        return {"site_id": site_id, "is_force_disabled": updated_site.get("is_force_disabled")}

    def set_compute_force_disabled_flag(self, compute_id: str, flag: bool):
        """
        Sets the 'is_force_disabled' flag for a specific compute resource.

        This method updates the `is_force_disabled` field for the compute entry
        identified by `compute_id` within a site's compute list in the MongoDB `nodes` collection.

        Args:
            compute_id (str): The ID of the compute resource to update.
            flag (bool): The value to set for the `is_force_disabled` flag.

        Returns:
            dict: A dictionary containing the `compute_id` and the new `is_force_disabled` value,
                  or an empty dictionary if the compute resource is not found.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes

        # Get the compute with parent context
        compute = self.get_compute(compute_id)
        if not compute:
            return {}
        parent_node_name = compute.get("parent_node_name")
        parent_site_name = compute.get("parent_site_name")

        # Find the full node document by node name
        node = nodes.find_one({"name": parent_node_name})
        if not node:
            return {}

        updated_node = copy.deepcopy(node)
        updated_compute = None
        for site in updated_node.get("sites", []):
            if site.get("name") != parent_site_name:
                continue
            for compute in site.get("compute", []):
                if compute.get("id") == compute_id:
                    compute["is_force_disabled"] = flag
                    updated_compute = compute
                    break
            if updated_compute:
                break

        if updated_compute is None:
            return {}

        # Pass the modified node to add_edit_node
        self.add_edit_node(updated_node, node_name=parent_node_name)
        return {"compute_id": compute_id, "is_force_disabled": updated_compute.get("is_force_disabled")}

    def set_service_force_disabled_flag(self, service_id: str, flag: bool):
        """
        Sets the 'is_force_disabled' flag for a specific service.

        This method locates the service by its ID, determines whether it is a global
        or local service, and updates the `is_force_disabled` field accordingly within
        the compute configuration of the appropriate site in the MongoDB `nodes` collection.

        Args:
            service_id (str): The ID of the service to update.
            flag (bool): The value to set for the `is_force_disabled` flag.

        Returns:
            dict: A dictionary containing the updated service ID and status,
                  or an empty dictionary if the service is not found.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes

        # Get the service with parent context
        service = self.get_service(service_id)
        if not service:
            return {}
        parent_node_name = service.get("parent_node_name")
        parent_site_name = service.get("parent_site_name")
        parent_compute_id = service.get("parent_compute_id")
        service_scope = service.get("scope")

        # Find the full node document by node name
        node = nodes.find_one({"name": parent_node_name})
        if not node:
            return {}

        updated_node = copy.deepcopy(node)
        updated_service = None
        for site in updated_node.get("sites", []):
            if site.get("name") != parent_site_name:
                continue
            for compute in site.get("compute", []):
                if compute.get("id") != parent_compute_id:
                    continue
                for svc in compute.get("associated_{}_services".format(service_scope), []):
                    if svc.get("id") == service_id:
                        svc["is_force_disabled"] = flag
                        updated_service = svc
                        break
                if updated_service:
                    break
            if updated_service:
                break

        if not updated_service:
            return {}

        self.add_edit_node(updated_node, node_name=parent_node_name)
        return {"service_id": service_id, "is_force_disabled": updated_service.get("is_force_disabled")}

    def set_storage_force_disabled_flag(self, storage_id: str, flag: bool):
        """
        Sets the 'is_force_disabled' flag for a specific storage resource.

        This method updates the `is_force_disabled` field for the storage entry
        identified by `storage_id` within a site's storages list in the MongoDB `nodes` collection.

        Args:
            storage_id (str): The ID of the storage resource to update.
            flag (bool): The value to set for the `is_force_disabled` flag.

        Returns:
            dict: A dictionary containing the `storage_id` and the new `is_force_disabled` value,
                  or an empty dictionary if the storage resource is not found.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes

        # Get the storage with parent context
        storage = self.get_storage(storage_id)
        if not storage:
            return {}
        parent_node_name = storage.get("parent_node_name")
        parent_site_name = storage.get("parent_site_name")

        # Find the full node document by node name
        node = nodes.find_one({"name": parent_node_name})
        if not node:
            return {}

        updated_node = copy.deepcopy(node)
        updated_storage = None
        for site in updated_node.get("sites", []):
            if site.get("name") != parent_site_name:
                continue
            for storage in site.get("storages", []):
                if storage.get("id") == storage_id:
                    storage["is_force_disabled"] = flag
                    updated_storage = storage
                    break
            if updated_storage:
                break

        if not updated_storage:
            return {}

        # Pass the modified node to add_edit_node
        self.add_edit_node(updated_node, node_name=parent_node_name)

        return {"storage_id": storage_id, "is_force_disabled": updated_storage.get("is_force_disabled")}

    def set_storage_area_force_disabled_flag(self, storage_area_id: str, flag: bool):
        """
        Sets the 'is_force_disabled' flag for a specific storage area.

        This method updates the `is_force_disabled` field for the storage area
        identified by `storage_area_id` within a site's storages list in the
        MongoDB `nodes` collection.

        Args:
            storage_area_id (str): The ID of the storage area to update.
            flag (bool): The value to set for the `is_force_disabled` flag.

        Returns:
            dict: A dictionary containing the `storage_area_id` and the new `is_force_disabled` value,
                  or an empty dictionary if the storage area is not found.
        """
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes

        # Get the storage area with parent context
        storage_area = self.get_storage_area(storage_area_id)
        if not storage_area:
            return {}
        parent_node_name = storage_area.get("parent_node_name")
        parent_site_name = storage_area.get("parent_site_name")
        parent_storage_id = storage_area.get("parent_storage_id")

        # Load the full node document
        node = nodes.find_one({"name": parent_node_name})
        if not node:
            return {}

        updated_node = copy.deepcopy(node)
        updated_storage_area = None
        for site in updated_node.get("sites", []):
            if site.get("name") != parent_site_name:
                continue
            for storage in site.get("storages", []):
                if storage.get("id") != parent_storage_id:
                    continue
                for area in storage.get("areas", []):
                    if area.get("id") == storage_area_id:
                        area["is_force_disabled"] = flag
                        updated_storage_area = area
                        break
                if updated_storage_area:
                    break
            if updated_storage_area:
                break
        if not updated_storage_area:
            return {}

        # Pass the modified node to add_edit_node
        self.add_edit_node(updated_node, node_name=parent_node_name)

        return {"storage_area_id": storage_area_id, "is_force_disabled": updated_storage_area.get("is_force_disabled")}
