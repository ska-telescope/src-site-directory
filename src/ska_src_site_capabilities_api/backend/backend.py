from abc import ABC, abstractmethod


class Backend(ABC):
    """Backend API abstract base class."""

    def __init__(self):
        pass

    @abstractmethod
    def add_edit_node(self, node_values):
        raise NotImplementedError

    @abstractmethod
    def delete_all_nodes(self):
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
    def list_compute(self, node_names, site_names, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_nodes(self, include_archived, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_services(self, node_names, site_names, service_types, service_scope, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_service_types_from_schema(self, schema):
        raise NotImplementedError

    @abstractmethod
    def list_sites(self, node_names, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storages(self, node_names, site_names, topojson, for_grafana, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storage_areas(self, node_names, site_names, topojson, for_grafana, include_inactive):
        raise NotImplementedError

    @abstractmethod
    def list_storage_area_types_from_schema(self, schema):
        raise NotImplementedError

    @abstractmethod
    def set_site_force_disabled_flag(self, site_id: str, flag: bool):
        raise NotImplementedError

    @abstractmethod
    def set_compute_force_disabled_flag(self, compute_id: str, flag: bool):
        raise NotImplementedError

    @abstractmethod
    def set_service_force_disabled_flag(self, service_id: str, flag: bool):
        raise NotImplementedError

    @abstractmethod
    def set_storage_force_disabled_flag(self, storage_id: str, flag: bool):
        raise NotImplementedError

    @abstractmethod
    def set_storage_area_force_disabled_flag(self, storage_area_id: str, flag: bool):
        raise NotImplementedError
