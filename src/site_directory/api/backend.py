from abc import ABC, abstractmethod
import json

from pymongo import MongoClient

class Backend(ABC):
    """ Backend API abstract base class. """
    def __init__(self):
        pass

    @abstractmethod
    def add_site(self):
        raise NotImplementedError

    @abstractmethod
    def get_site(self):
        raise NotImplementedError

    @abstractmethod
    def get_site_version(self):
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
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
        response = []
        for site in sites.find({"name": site, "version": version}):
            site['_id'] = str(site['_id'])
            response.append(site)
        return response

    def get_site_version_latest(self, site):
        site_versions = self.get_site(site)

        latest = {}
        version = 0
        for site_version in site_versions:
            if site_version['version'] > version:
                latest = site_version
        return latest

    def list_services(self):
        response = []
        for site_name in self.list_site_names_unique():
            full_site_json = self.get_site_version_latest(site_name)
            response.append({
                'name': full_site_json['name'],
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
        client = MongoClient(self.connection_string)
        db = client[self.mongo_database]
        sites = db.sites
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
        for site in self.list_sites_version_latest():
            all_supported_protocols_for_site = {}
            for storage in site['storages']:
                for supported_protocol in storage.get('supported_protocols', []):
                    all_supported_protocols_for_site["{}://{}:{}/{}".format(
                        supported_protocol['prefix'],
                        supported_protocol['host'].rstrip('/'),
                        supported_protocol['port'],
                        supported_protocol['base_path'].lstrip('/').rstrip('/'))] = \
                    (storage['latitude'], storage['longitude'])

            for service in site.get('services', []):
                if 'Rucio Storage Element (RSE)' in service['type']:
                    service_endpoint = "{}://{}:{}/{}".format(
                        service['prefix'],
                        service['host'].rstrip('/'),
                        service['port'],
                        service['path'].lstrip('/').rstrip('/'))
                    for protocol, (lat, long) in all_supported_protocols_for_site.items():
                        if protocol in service_endpoint:
                            if topojson:
                                response['objects']['sites']['geometries'].append({
                                    "type":"Point",
                                    "coordinates": [long, lat],
                                    "properties": {
                                      "rucio_name": service.get('identifier'),
                                    }
                                })
                            elif for_grafana:
                                for storage in site['storages']:
                                    response.append({
                                        "key": service.get('identifier'),
                                        "latitude": storage['latitude'],
                                        "longitude": storage['longitude'],
                                        "name": service.get('identifier')
                                    })
                            else:
                                response.append(*site['storages'])
        return response
