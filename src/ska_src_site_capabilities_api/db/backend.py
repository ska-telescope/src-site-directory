from abc import ABC, abstractmethod

from pymongo import MongoClient


class Backend(ABC):
    """ Backend API abstract base class. """
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
    def get_site(self):
        raise NotImplementedError

    @abstractmethod
    def get_site_version(self):
        raise NotImplementedError

    @abstractmethod
    def get_site_version_latest(self):
        raise NotImplementedError

    @abstractmethod
    def list_services(self):
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


class MongoBackend(Backend):
    """ Backend API for mongodb. """
    def __init__(self, mongo_username, mongo_password, mongo_host, mongo_port, mongo_database):
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
        existing_versions = self.get_site(site_values['name'])
        if not existing_versions:
            site_values['version'] = 1
        else:
            site_values['version'] = len(existing_versions) + 1
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
            site.pop('_id')
        return response

    def get_service(self, service_id):
        response = {}
        for site in self.list_sites_version_latest():
            for service in site['services']:
                if service['id'] == service_id:
                    response = service
        return response

    def get_site(self, site):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = []
        for site in sites.find({"name": site}):
            site['_id'] = str(site['_id'])
            response.append(site)
        return response

    def get_site_version(self, site, version):
        site_versions = self.get_site(site)

        this_version = None
        for site_version in site_versions:
            if str(site_version['version']) == version:
                this_version = site_version
                break
        return this_version

    def get_site_version_latest(self, site):
        site_versions = self.get_site(site)

        latest = None
        version = -1
        for site_version in site_versions:
            if site_version['version'] > version:
                latest = site_version
        return latest

    def get_storage(self, storage_id):
        response = {}
        for site in self.list_sites_version_latest():
            for storage in site['storages']:
                if storage['id'] == storage_id:
                    response = storage
        return response

    def list_services(self):
        response = []
        for site_name in self.list_site_names_unique():
            full_site_json = self.get_site_version_latest(site_name)
            response.append({
                'site_name': full_site_json['name'],
                'services': full_site_json['services']
            })
        return response

    def list_site_names_unique(self):
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = []
        for site in sites.find({}):
            site_name = site['name']
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
                "objects": {
                    "sites": {
                        "type": "GeometryCollection",
                        "geometries": []
                    }
                }
            }
        else:
            response = []

        services_list = self.list_services()
        for site in self.list_sites_version_latest():
            for storage in site['storages']:
                if topojson:
                    # for topojson output we attach the service identifier to the storage also, this means that there
                    # may be same storage output multiple times if different services are attached to it.
                    #
                    # see route /storages/topojson FIXME
                    for site_from_services_list in services_list:
                        if site_from_services_list.get('site_name') == site.get('name'):
                            for service in site_from_services_list.get('services'):
                                if service.get('associated_storage_id', '') == storage.get('id'):
                                    response['objects']['sites']['geometries'].append({
                                        "type": "Point",
                                        "coordinates": [storage.get('longitude'), storage.get('latitude')],
                                        "properties": {'associated_service': service}
                                    })
                elif for_grafana:
                    # for grafana output we attach the service identifier to the storage also, this means that there
                    # may be same storage output multiple times if different services are attached to it.
                    #
                    # see route /storages/topojson FIXME
                    for site_from_services_list in services_list:
                        if site_from_services_list.get('site_name') == site.get('name'):
                            for service in site_from_services_list.get('services'):
                                if service.get('associated_storage_id', '') == storage.get('id'):
                                    if service.get('type') == 'Rucio Storage Element (RSE)':
                                        response.append({
                                            "key": service.get('identifier'),
                                            "latitude": storage['latitude'],
                                            "longitude": storage['longitude'],
                                            "name": service.get('identifier')
                                        })
                else:
                    response.append({
                        "site_name": site.get('name'),
                        "storages": site['storages']
                    })
        return response
