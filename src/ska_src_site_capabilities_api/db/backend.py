from abc import ABC, abstractmethod

from pymongo import MongoClient


class Backend(ABC):
    """Backend API abstract base class."""

    def __init__(self):
        pass

    @abstractmethod
    def add_site(self, json):
        raise NotImplementedError

    @abstractmethod
    def add_sites_bulk(self, json):
        raise NotImplementedError

    @abstractmethod
    def delete_site(self, site):
        raise NotImplementedError

    @abstractmethod
    def delete_sites(self):
        raise NotImplementedError

    @abstractmethod
    def delete_site_version(self, site, version):
        raise NotImplementedError

    @abstractmethod
    def dump_sites(self):
        raise NotImplementedError

    @abstractmethod
    def get_compute(self, compute_id):
        raise NotImplementedError

    @abstractmethod
    def get_service(self, service_id):
        raise NotImplementedError

    @abstractmethod
    def get_site(self, site):
        raise NotImplementedError

    @abstractmethod
    def get_site_version(self, site, version):
        raise NotImplementedError

    @abstractmethod
    def get_site_version_latest(self, site):
        raise NotImplementedError

    @abstractmethod
    def get_storage(self, storage_id):
        raise NotImplementedError

    @abstractmethod
    def get_storage_area(self, storage_area_id):
        raise NotImplementedError

    @abstractmethod
    def list_compute(self):
        raise NotImplementedError

    @abstractmethod
    def list_services(self):
        raise NotImplementedError

    @abstractmethod
    def list_service_types_from_schema(self, schema):
        raise NotImplementedError

    @abstractmethod
    def list_site_names_unique(self):
        raise NotImplementedError

    @abstractmethod
    def list_sites_version_latest(self):
        raise NotImplementedError

    @abstractmethod
    def list_storages(self):
        raise NotImplementedError

    @abstractmethod
    def list_storage_areas(self):
        raise NotImplementedError

    @abstractmethod
    def list_storage_area_types_from_schema(self, schema):
        raise NotImplementedError


class MongoBackend(Backend):
    """Backend API for mongodb."""

    def __init__(self, mongo_username, mongo_password, mongo_host, mongo_port, mongo_database):
        super().__init__()
        self.connection_string = "mongodb://{}:{}@{}:{}/".format(
            mongo_username,
            mongo_password,
            mongo_host,
            int(mongo_port),
        )
        self.mongo_database = mongo_database

    def _is_compute_down_or_disabled(self, compute):
        return compute.get("disabled", False)

    def _is_service_down_or_disabled(self, service):
        return service.get("disabled", False)

    def _is_site_down_or_disabled(self, site):
        return site.get("disabled", False)

    def _is_storage_down_or_disabled(self, storage):
        print(storage)
        return storage.get("disabled", False)

    def _is_storage_area_down_or_disabled(self, storage_area):
        return storage_area.get("disabled", False)

    def add_site(self, site_values):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        existing_versions = self.get_site(site_values["name"])
        if not existing_versions:
            site_values["version"] = 1
        else:
            site_values["version"] = len(existing_versions) + 1
        return sites.insert_one(site_values).inserted_id

    def add_sites_bulk(self, json):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        return sites.insert_many(json)

    def delete_site(self, site):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        return sites.delete_many({"name": site})

    def delete_sites(self):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        return sites.delete_many({})

    def delete_site_version(self, site, version):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        return sites.delete_one({"name": site, "version": version})

    def dump_sites(self):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = list(sites.find({}))
        for site in response:
            site.pop("_id")
        return response

    def get_compute(self, compute_id):
        response = {}
        for entry in self.list_compute(include_inactive=True):
            site_name = entry.get("site_name")
            for element in entry.get("compute", []):
                if element.get("id") == compute_id:
                    response = {
                        "site_name": site_name,
                        **element
                    }
                    break
        return response

    def get_service(self, service_id):
        response = {}
        for entry in self.list_services(include_inactive=True):
            site_name = entry.get("site_name")
            for element in entry.get("services", []):
                if element.get("id") == service_id:
                    response = {
                        "site_name": site_name,
                        **element
                    }
                    break
        return response

    def get_site(self, site):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = []
        for site in sites.find({"name": site}):
            site["_id"] = str(site["_id"])
            response.append(site)
        return response

    def get_site_version(self, site, version):
        site_versions = self.get_site(site)
        this_version = None
        for site_version in site_versions:
            if str(site_version["version"]) == version:
                this_version = site_version
                break
        return this_version

    def get_site_version_latest(self, site):
        site_versions = self.get_site(site)
        site = None
        for site_version in site_versions:
            if site:
                if site_version.get("version"):
                    site = site_version
            else:
                site = site_version
        return site

    def get_storage(self, storage_id):
        response = {}
        for entry in self.list_storages(include_inactive=True):
            site_name = entry.get("site_name")
            for element in entry.get("storages", []):
                if element.get("id") == storage_id:
                    response = {
                        "site_name": site_name,
                        **element
                    }
                    break
        return response

    def get_storage_area(self, storage_area_id):
        response = {}
        for entry in self.list_storage_areas(include_inactive=True):
            site_name = entry.get("site_name")
            for element in entry.get("storage_areas", []):
                if element.get("id") == storage_area_id:
                    response = {
                        "site_name": site_name,
                        **element
                    }
                    break
        return response

    def list_compute(self, include_inactive=False):
        response = []
        for site in self.list_sites_version_latest(include_inactive=include_inactive):
            if site.get("compute"):
                response.append(
                    {
                        "site_name": site.get("name"),
                        "compute": [compute for compute in site.get("compute") if
                                     include_inactive or
                                     (not include_inactive and
                                      not self._is_compute_down_or_disabled(compute))],
                    }
                )
        return response

    def list_services(self, service_scope="all", include_inactive=False):
        response = []
        for entry in self.list_compute(include_inactive=include_inactive):
            site_name = entry.get("site_name")
            services = []
            for compute in entry.get("compute", []):
                if not include_inactive and self._is_compute_down_or_disabled(compute):
                    continue
                if service_scope in ['all', 'local']:
                    for service in compute.get("associated_local_services", []):
                        if not include_inactive and self._is_service_down_or_disabled(service):
                            continue
                        services.append(
                            {
                                "scope": "local",
                                "parent_compute_id": compute.get("id"),
                                **service,
                            }
                        )
                if service_scope in ['all', 'global']:
                    for service in compute.get("associated_global_services", []):
                        if not include_inactive and self._is_service_down_or_disabled(service):
                            continue
                        services.append(
                            {
                                "scope": "global",
                                "parent_compute_id": compute.get("id"),
                                **service,
                            }
                        )
            response.append(
                {
                    "site_name": site_name,
                    "services": services
                }
            )
        return response

    def list_service_types_from_schema(self, schema):
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response

    def list_site_names_unique(self):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = []
        for site in sites.find({}):
            site_name = site.get("name")
            if site_name not in response:
                response.append(site_name)
        return response

    def list_sites_version_latest(self, include_inactive=False):
        response = []
        for site_name in self.list_site_names_unique():
            site = self.get_site_version_latest(site_name)
            if include_inactive:
                response.append(site)
            else:
                if not self._is_site_down_or_disabled(site):
                    response.append(site)
        return response

    def list_storages(self, topojson=False, for_grafana=False, include_inactive=False):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []
        for site in self.list_sites_version_latest(include_inactive=include_inactive):
            if topojson or for_grafana:
                for storage in site.get("storages", []):
                    if not include_inactive and self._is_storage_down_or_disabled(storage):
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
                if site.get("storages"):
                    response.append(
                        {
                            "site_name": site.get("name"),
                            "storages": [storage for storage in site.get("storages") if
                                         include_inactive or
                                         (not include_inactive and
                                          not self._is_storage_down_or_disabled(storage))],
                        }
                    )
        return response

    def list_storage_areas(self, topojson=False, for_grafana=False, include_inactive=False):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []

        for entry in self.list_storages(include_inactive=include_inactive):
            site_name = entry.get("site_name")
            storage_areas = []
            for storage in entry.get("storages"):
                if not include_inactive and self._is_storage_down_or_disabled(storage):
                    continue
                for storage_area in storage.get("areas", []):
                    if (not include_inactive and
                            self._is_storage_area_down_or_disabled(storage_area)):
                        continue
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
                        # add the parent storage id
                        storage_areas.append(
                            {
                                "parent_storage_id": storage.get("id"),
                                **storage_area,
                            }
                        )
            if not for_grafana and not topojson:
                response.append(
                    {
                        "site_name": site_name,
                        "storage_areas": storage_areas,
                    }
                )
        return response

    def list_storage_area_types_from_schema(self, schema):
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response
