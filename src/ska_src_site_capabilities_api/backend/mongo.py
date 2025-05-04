from datetime import datetime, timezone

import dateutil.parser
from pymongo import MongoClient

from ska_src_site_capabilities_api.backend.backend import Backend


class MongoBackend(Backend):
    """Backend API for MongoDB."""

    def __init__(
        self, mongo_database, mongo_username=None, mongo_password=None, mongo_host=None, mongo_port=None, client=None
    ):
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
            self.connection_string = "mongodb://{}:{}@{}:{}/".format(
                mongo_username, mongo_password, mongo_host, int(mongo_port)
            )
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
            if compute.get("id") == compute_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, **compute}
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
            parent_compute_id = service.get("parent_compute_id")
            if service.get("id") == service_id:
                response = {
                    "parent_node_name": parent_node_name,
                    "parent_site_name": parent_site_name,
                    "parent_compute_id": parent_compute_id,
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
            if storage.get("id") == storage_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, **storage}
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
            parent_storage_id = storage_area.get("parent_storage_id")
            if storage_area.get("id") == storage_area_id:
                response = {
                    "parent_node_name": parent_node_name,
                    "parent_site_name": parent_site_name,
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
            for compute in site.get("compute", []):
                if site_names and parent_site_name not in site_names:
                    continue
                compute_with_parent = {
                    "parent_node_name": site.get("parent_node_name"),
                    "parent_site_name": parent_site_name,
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

        Returns:
            A list of service dictionaries, each containing scope and parent information.
        """
        response = []

        # Handle None cases for input lists
        node_names = node_names or []
        site_names = site_names or []
        service_types = service_types or []

        for compute in self.list_compute(
            node_names=node_names,
            site_names=site_names,
            include_inactive=include_inactive,
        ):
            if service_scope in ["all", "local"]:
                for service in compute.get("associated_local_services", []):
                    # Apply filters for service type and associated storage area ID
                    if service_types and service.get("type") not in service_types:
                        continue
                    if (
                        associated_storage_area_id
                        and service.get("associated_storage_area_id") != associated_storage_area_id
                    ):
                        continue
                    # Add parent information
                    response.append(
                        {
                            "scope": "local",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_site_name"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )

            if service_scope in ["all", "global"]:
                for service in compute.get("associated_global_services", []):
                    # Apply filters for service type and associated storage area ID
                    if service_types and service.get("type") not in service_types:
                        continue
                    if (
                        associated_storage_area_id
                        and service.get("associated_storage_area_id") != associated_storage_area_id
                    ):
                        continue
                    # Add parent information
                    response.append(
                        {
                            "scope": "global",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_site_name"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )

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

    def list_storages(
        self, node_names=None, site_names=None, topojson=False, for_grafana=False, include_inactive=False
    ):
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
                    response.append(
                        {
                            "key": storage.get("identifier"),
                            "latitude": site["latitude"],
                            "longitude": site["longitude"],
                            "name": storage.get("identifier"),
                        }
                    )
                else:
                    # Add parent information
                    response.append(
                        {
                            "parent_node_name": site.get("parent_node_name"),
                            "parent_site_name": parent_site_name,
                            **storage,
                        }
                    )
        return response

    def list_storage_areas(
        self, node_names=None, site_names=None, topojson=False, for_grafana=False, include_inactive=False
    ):
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
        for storage in self.list_storages(
            node_names=node_names, site_names=site_names, include_inactive=include_inactive
        ):
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
                            "parent_storage_id": storage.get("id"),
                            **storage_area,
                        }
                    )
        return response

    def list_storage_area_types_from_schema(self, schema):
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response

    def set_site_disabled_flag(self, site_id: str, flag: bool):
        """Set is_force_disabled flag for sites"""
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes
        node = nodes.find_one({"sites.id": site_id})
        if not node:
            return {}

        # Update the is_force_disabled flag for the requested site
        nodes.update_one({"sites.id": site_id}, {"$set": {"sites.$.is_force_disabled": flag}})

        updated_node = nodes.find_one({"sites.id": site_id})
        updated_site = next(site for site in updated_node["sites"] if site["id"] == site_id)
        return {"site_id": site_id, "is_force_disabled": updated_site.get("is_force_disabled")}

    def set_compute_disabled_flag(self, compute_id: str, flag: bool):
        """Set is_force_disabled flag for compute"""
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes
        node = nodes.find_one({"sites.compute.id": compute_id})
        print("node", node)
        if not node:
            return {}

        # Update the is_force_disabled flag for the requested compute
        nodes.update_one({"sites.compute.id": compute_id}, {"$set": {"sites.compute.$.is_force_disabled": flag}})
        print("nodes:::", nodes)

        updated_node = nodes.find_one({"sites.compute.id": compute_id})
        print("updated_node:::", updated_node)
        updated_site = next(compute for compute in updated_node["compute"] if compute["id"] == compute_id)
        print("updated_node:::", updated_node)
        return {"compute_id": compute_id, "is_force_disabled": updated_site.get("is_force_disabled")}

    def set_storages_forced_flag(self, storage_id: str, flag: bool):
        """Set forced flag for storages"""
        response = self.get_storage(storage_id)
        response["is_force_disabled"] = flag
        if response["is_force_disabled"] is False:
            return {"storageID": storage_id, "enabled": True}
        else:
            return {"storageID": storage_id, "enabled": False}
