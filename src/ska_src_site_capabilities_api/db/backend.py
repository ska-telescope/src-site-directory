from abc import ABC, abstractmethod

from pymongo import MongoClient


class Backend(ABC):
    """Backend API abstract base class."""

    def __init__(self):
        pass

    @abstractmethod
    def add_site(self):
        raise NotImplementedError

    @abstractmethod
    def add_sites_bulk(self):
        raise NotImplementedError

    @abstractmethod
    def delete_site(self):
        raise NotImplementedError

    @abstractmethod
    def delete_sites(self):
        raise NotImplementedError

    @abstractmethod
    def delete_site_version(self):
        raise NotImplementedError

    @abstractmethod
    def dump_sites(self):
        raise NotImplementedError

    @abstractmethod
    def get_compute(self):
        raise NotImplementedError

    @abstractmethod
    def get_site(self):
        raise NotImplementedError

    @abstractmethod
    def get_service(self):
        raise NotImplementedError

    @abstractmethod
    def get_storage(self):
        raise NotImplementedError

    @abstractmethod
    def get_storage_area(self):
        raise NotImplementedError

    @abstractmethod
    def get_site_version(self):
        raise NotImplementedError

    @abstractmethod
    def get_site_version_latest(self):
        raise NotImplementedError

    @abstractmethod
    def list_compute(self):
        raise NotImplementedError

    @abstractmethod
    def list_services(self):
        raise NotImplementedError

    @abstractmethod
    def list_service_types_from_schema(self):
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


class MongoBackend(Backend):
    """Backend API for mongodb."""

    def __init__(
        self,
        mongo_username,
        mongo_password,
        mongo_host,
        mongo_port,
        mongo_database,
    ):
        self.connection_string = "mongodb://{}:{}@{}:{}/".format(
            mongo_username,
            mongo_password,
            mongo_host,
            int(mongo_port),
        )
        self.mongo_database = mongo_database

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
        for site in self.list_sites_version_latest():
            for compute in site.get("compute", []):
                if compute["id"] == compute_id:
                    response = compute
                    break
        return response

    def get_service(self, service_id):
        response = {}
        for entry in self.list_services(
            include_associated_with_compute=True, include_disabled=True, service_type=None, site_names=None
        ):
            site_name = entry.get("site_name")
            services = entry.get("services", [])
            for service in services:
                if service.get("id") == service_id:
                    response = {"site_name": site_name, **service}
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

        latest = None
        for site_version in site_versions:
            if latest:
                if site_version.get("version") > latest.get("version"):
                    latest = site_version
            else:
                latest = site_version
        return latest

    def get_storage(self, storage_id):
        response = {}
        for site in self.list_sites_version_latest():
            for storage in site.get("storages", []):
                if storage["id"] == storage_id:
                    response = storage
                    break
        return response

    def get_storage_area(self, storage_area_id):
        response = {}
        for site in self.list_sites_version_latest():
            for storage in site.get("storages", []):
                for storage_area in storage.get("areas", []):
                    if storage_area["id"] == storage_area_id:
                        response = {
                            "associated_storage_id": storage.get("id"),
                            **storage_area,
                        }
                        break
        return response

    def list_compute(self):
        response = []
        for site in self.list_sites_version_latest():
            if site.get("compute"):
                response.append(
                    {
                        "site_name": site.get("name"),
                        "compute": site.get("compute"),
                    }
                )
        return response

    def list_services(
        self,
        include_associated_with_compute=True,
        include_disabled=True,
        service_type=None,
        site_names=None,
        compute_id=None,
    ):
        response = []
        # Convert site_names to list if it's a string
        if isinstance(site_names, str):
            # Handle comma-separated strings
            site_names = [name.strip() for name in site_names.split(",")]
        elif site_names is None:
            site_names = None

        for site_name in self.list_site_names_unique():
            # Skip sites that don't match the filter
            if site_names is not None and site_name not in site_names:
                continue

            full_site_json = self.get_site_version_latest(site_name)

            services = []
            # concatenate services (global + associated local services)
            for service in full_site_json.get("global_services", []):
                if service_type is None or service.get("type") == service_type:
                    services.append(service)
            if include_associated_with_compute:
                for compute in full_site_json.get("compute", []):
                    # Skip if compute_id filter is set and doesn't match
                    if compute_id is not None and compute.get("id") != compute_id:
                        continue
                    # add the associated compute id
                    for service in compute.get("associated_local_services", []):
                        if service_type is None or service.get("type") == service_type:
                            services.append(
                                {
                                    "associated_compute_id": compute.get("id"),
                                    **service,
                                }
                            )

            if services:  # Only add to response if there are matching services
                response.append({"site_name": full_site_json.get("name"), "services": services})
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

    def list_sites_version_latest(self):
        response = []
        for site_name in self.list_site_names_unique():
            response.append(self.get_site_version_latest(site_name))
        return response

    def list_storages(self, topojson=False, for_grafana=False):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []

        for site_name in self.list_site_names_unique():
            full_site_json = self.get_site_version_latest(site_name)
            if topojson or for_grafana:
                for storage in full_site_json.get("storages", []):
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
                if full_site_json.get("storages"):
                    response.append(
                        {
                            "site_name": full_site_json.get("name"),
                            "storages": full_site_json.get("storages"),
                        }
                    )
        return response

    def list_storage_areas(self, topojson=False, for_grafana=False, site_name=None, identifier=None):
        if topojson:
            response = {
                "type": "Topology",
                "objects": {"sites": {"type": "GeometryCollection", "geometries": []}},
            }
        else:
            response = []

        ### filter by site_name (storage-areas?site_name= )
        if site_name:
            sites = [site_name]
        else:
            sites = self.list_site_names_unique()

        for site in sites:
            full_site_json = self.get_site_version_latest(site)
            if not full_site_json:
                continue
            ###

            storage_areas = []
            for storage in full_site_json.get("storages", []):
                for storage_area in storage.get("areas", []):

                    if identifier and identifier != storage_area.get("identifier"):
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
                        # add the associated storage id
                        storage_areas.append(
                            {
                                "associated_storage_id": storage.get("id"),
                                **storage_area,
                            }
                        )
            if storage_areas and not for_grafana and not topojson:
                response.append(
                    {
                        "site_name": full_site_json.get("name"),
                        "storage_areas": storage_areas,
                    }
                )
        return response

    def list_storage_area_types_from_schema(self, schema):
        response = schema.get("properties", {}).get("type", {}).get("enum", [])
        return response
