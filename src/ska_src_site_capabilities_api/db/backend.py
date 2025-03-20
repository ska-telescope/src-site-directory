from abc import ABC, abstractmethod
from functools import wraps
from datetime import datetime, timezone

import dateutil.parser
from pymongo import MongoClient


class Backend(ABC):
    """Backend API abstract base class."""

    def __init__(self):
        pass

    @abstractmethod
    def add_edit_node(self, node_values):
        raise NotImplementedError

    @abstractmethod
    def get_compute(self, compute_id):
        raise NotImplementedError

    @abstractmethod
    def get_node(self, node_name, node_version):
        raise NotImplementedError

    @abstractmethod
    def get_service(self, service_id):
        raise NotImplementedError

    @abstractmethod
    def get_site(self, site_id):
        raise NotImplementedError

    def get_site_from_names(self, node_name, node_version, site_name):
        raise NotImplementedError

    @abstractmethod
    def get_storage(self, storage_id):
        raise NotImplementedError

    @abstractmethod
    def get_storage_area(self, storage_area_id):
        raise NotImplementedError

    @abstractmethod
    def list_compute(self, only_node_names, only_site_names, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_nodes(self, include_archived, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_services(self, only_node_names, only_site_names, only_service_types, only_service_scope, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_service_types_from_schema(self, schema):
        raise NotImplementedError

    @abstractmethod
    def list_sites(self, only_node_names, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storages(self, only_node_names, only_site_names, topojson, for_grafana, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storage_areas(self, only_node_names, only_site_names, topojson, for_grafana, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storage_area_types_from_schema(self, schema):
        raise NotImplementedError


class MongoBackend(Backend):
    """Backend API for mongodb."""

    def __init__(self, mongo_database, mongo_username=None, mongo_password=None, mongo_host=None,
                 mongo_port=None, client=None):
        super().__init__()
        if mongo_database and mongo_username and mongo_password and mongo_host:
            self.connection_string = "mongodb://{}:{}@{}:{}/".format(
                mongo_username, mongo_password, mongo_host, int(mongo_port)
            )
        self.mongo_database = mongo_database

        self.client = client    # used for mocking

    def _get_mongo_client(self):
        if self.client:
            return self.client
        else:
            return MongoClient(self.connection_string)

    def _is_element_in_downtime(self, downtime):
        """Checks if an element is in downtime."""
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
        client = self._get_mongo_client()
        db = client[self.mongo_database]
        nodes = db.nodes
        nodes_archived = db.nodes_archived

        # get latest version of this node
        latest_node = self.get_node(node_name=node_name, node_version="latest")
        if not latest_node:  # adding new node
            node_values["version"] = 1
        else:  # updating existing node
            node_values["version"] = latest_node.get("version") + 1

        # insert this new version of node into the nodes collection
        inserted_node = nodes.insert_one(node_values)

        # move the previous version of the node to nodes_archived collection only if a previous
        # version existed & insertion into nodes was successful
        if latest_node and inserted_node.inserted_id:
            # only delete it from nodes if we successfully added the previous version to
            # nodes_archived
            if nodes_archived.insert_one(latest_node).inserted_id:
                nodes.delete_one({"name": node_name, "version": latest_node.get("version")})

        return inserted_node.inserted_id

    def get_compute(self, compute_id):
        response = {}
        for compute in self.list_compute(include_inactive=True):
            parent_node_name = compute.get("parent_node_name")
            parent_site_name = compute.get("parent_site_name")
            if compute.get("id") == compute_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, **compute}
                break
        return response

    def get_node(self, node_name, node_version="latest"):
        """Get a version of a node."""
        # If node_version is latest, only search the latest collection, otherwise search both latest
        # and archived.
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
        response = {}
        for site in self.list_sites(include_inactive=True):
            parent_node_name = site.get("parent_node_name")
            if site.get("id") == site_id:
                response = {"parent_node_name": parent_node_name, **site}
                break
        return response

    def get_site_from_names(self, node_name, node_version, site_name):
        """Get site at a given node and version."""
        node = self.get_node(node_name=node_name, node_version=node_version)
        if not node:
            return None

        for site in node.get("sites", []):
            if site.get("name") == site_name:
                return {
                    "parent_node_name": node.get("name"),
                    **site
                }
        return None

    def get_storage(self, storage_id):
        response = {}
        for storage in self.list_storages(include_inactive=True):
            parent_node_name = storage.get("parent_node_name")
            parent_site_name = storage.get("parent_site_name")
            if storage.get("id") == storage_id:
                response = {"parent_node_name": parent_node_name, "parent_site_name": parent_site_name, **storage}
                break
        return response

    def get_storage_area(self, storage_area_id):
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

    def list_compute(self, only_node_names=[], only_site_names=[], include_inactive=False):
        response = []
        for site in self.list_sites(only_node_names=only_node_names, include_inactive=include_inactive):
            parent_site_name = site.get("name")
            for compute in site.get("compute", []):
                if only_site_names:
                    if parent_site_name not in only_site_names:
                        continue
                # add parent information
                response.append(
                    {"parent_node_name": site.get("parent_node_name"), "parent_site_name": parent_site_name, **compute}
                )
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
        only_node_names=[],
        only_site_names=[],
        only_service_types=[],
        only_service_scope="all",
        include_inactive=False,
    ):
        response = []
        for compute in self.list_compute(
            only_node_names=only_node_names, only_site_names=only_site_names, include_inactive=include_inactive
        ):
            if only_service_scope in ["all", "local"]:
                for service in compute.get("associated_local_services", []):
                    if only_service_types:
                        if service.get("type") not in only_service_types:
                            continue
                    # add parent information
                    response.append(
                        {
                            "scope": "local",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_site_name"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )
            if only_service_scope in ["all", "global"]:
                for service in compute.get("associated_global_services", []):
                    if only_service_types:
                        if service.get("type") not in only_service_types:
                            continue
                    # add parent information
                    response.append(
                        {
                            "scope": "global",
                            "parent_node_name": compute.get("parent_node_name"),
                            "parent_site_name": compute.get("parent_node_name"),
                            "parent_compute_id": compute.get("id"),
                            **service,
                        }
                    )
        return response

    def list_service_types_from_schema(self, schema):
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response

    def list_sites(self, only_node_names=[], include_inactive=False):
        """List versions of all sites."""
        response = []
        for node in self.list_nodes(include_inactive=include_inactive):
            parent_node_name = node.get("name")
            for site in node.get("sites", []):
                if only_node_names:
                    if parent_node_name not in only_node_names:
                        continue
                response.append({"parent_node_name": parent_node_name, **site})
        return response

    def list_storages(
        self, only_node_names=[], only_site_names=[], topojson=False, for_grafana=False, include_inactive=False
    ):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []
        for site in self.list_sites(only_node_names=only_node_names, include_inactive=include_inactive):
            parent_site_name = site.get("name")
            for storage in site.get("storages", []):
                if only_site_names:
                    if parent_site_name not in only_site_names:
                        continue
                if topojson:
                    response["objects"]["sites"]["geometries"].append(
                        {
                            "type": "Point",
                            "coordinates": [
                                storage.get("longitude"),
                                storage.get("latitude"),
                            ],
                            "properties": {"name": storage.get("identifier")},
                        }
                    )
                elif for_grafana:
                    response.append(
                        {
                            "key": storage.get("identifier"),
                            "latitude": storage["latitude"],
                            "longitude": storage["longitude"],
                            "name": storage.get("identifier"),
                        }
                    )
                else:
                    # add parent information
                    response.append(
                        {
                            "parent_node_name": site.get("parent_node_name"),
                            "parent_site_name": parent_site_name,
                            **storage,
                        }
                    )
        return response

    def list_storage_areas(
        self, only_node_names=[], only_site_names=[], topojson=False, for_grafana=False, include_inactive=False
    ):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []
        for storage in self.list_storages(
            only_node_names=only_node_names, only_site_names=only_site_names, include_inactive=include_inactive
        ):
            for storage_area in storage.get("areas", []):
                if topojson:
                    response["objects"]["sites"]["geometries"].append(
                        {
                            "type": "Point",
                            "coordinates": [
                                storage.get("longitude"),
                                storage.get("latitude"),
                            ],
                            "properties": {"name": storage_area.get("identifier")},
                        }
                    )
                elif for_grafana:
                    response.append(
                        {
                            "key": storage_area.get("identifier"),
                            "latitude": storage["latitude"],
                            "longitude": storage["longitude"],
                            "name": storage_area.get("identifier"),
                        }
                    )
                else:
                    # add parent information
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
