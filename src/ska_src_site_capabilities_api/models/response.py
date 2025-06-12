from typing import List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.compute import Compute
from ska_src_site_capabilities_api.models.node import Node
from ska_src_site_capabilities_api.models.schema import Schema
from ska_src_site_capabilities_api.models.service import GlobalService, GlobalServiceType, LocalService, LocalServiceType
from ska_src_site_capabilities_api.models.site import Site
from ska_src_site_capabilities_api.models.storage import (
    Storage,
    StorageArea,
    StorageAreaGrafana,
    StorageAreaTopojson,
    StorageGrafana,
    StorageTopojson,
)


# =======================
# Base Response Class
# =======================
class Response(BaseModel):
    pass


# =======================
# Compute Responses
# =======================
class ComputeWithParents(Compute):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


ComputeGetResponse = ComputeWithParents
ComputeListResponse = List[ComputeWithParents]


class ComputeEnableResponse(Response):
    compute_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=False, examples=[False])


class ComputeDisableResponse(Response):
    compute_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=True, examples=[True])


# =======================
# Service Responses
# =======================
class GlobalServiceWithParentsAndType(GlobalService):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_compute_id: UUID = Field(default_factory=uuid4)
    scope: str = "global"


GlobalServiceGetResponse = GlobalServiceWithParentsAndType


class LocalServiceWithParentsAndType(LocalService):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_compute_id: UUID = Field(default_factory=uuid4)
    scope: str = "local"


LocalServiceGetResponse = LocalServiceWithParentsAndType

ServicesListResponse = List[Union[GlobalServiceWithParentsAndType, LocalServiceWithParentsAndType]]


class ServiceEnableResponse(Response):
    service_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=False, examples=[False])


class ServiceDisableResponse(Response):
    service_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=True, examples=[True])


class ServicesTypesResponse(Response):
    global_: List[GlobalServiceType] = Field(..., alias="global")
    local: List[LocalServiceType]


ServicesTypesGlobalResponse = List[GlobalServiceType]
ServicesTypesLocalResponse = List[LocalServiceType]


# =======================
# Site Responses
# =======================
class SiteWithParents(Site):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


SiteGetResponse = SiteWithParents
SitesListResponse = List[SiteWithParents]


class SiteEnableResponse(Response):
    site_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=False, examples=[False])


class SiteDisableResponse(Response):
    site_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=True, examples=[True])


# =======================
# Storage Responses
# =======================
class StorageWithParents(Storage):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


StorageGetResponse = StorageWithParents
StoragesListResponse = List[StorageWithParents]
StoragesGrafanaResponse = List[StorageGrafana]
StoragesTopojsonResponse = List[StorageTopojson]


class StorageEnableResponse(Response):
    storage_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=False, examples=[False])


class StorageDisableResponse(Response):
    storage_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=True, examples=[True])


class StorageAreaWithParents(StorageArea):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_storage_id: UUID = Field(default_factory=uuid4)


StorageAreaGetResponse = StorageAreaWithParents
StorageAreasListResponse = List[StorageAreaWithParents]
StorageAreasGrafanaResponse = List[StorageAreaGrafana]
StorageAreasTopojsonResponse = List[StorageAreaTopojson]
StorageAreasTypesResponse = List[str]


class StorageAreaEnableResponse(Response):
    storage_area_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=False, examples=[False])


class StorageAreaDisableResponse(Response):
    storage_area_id: UUID = Field(default_factory=uuid4)
    is_force_disabled: bool = Field(default=True, examples=[True])


# =======================
# Node Responses
# =======================
NodesGetResponse = Node
NodesListResponse = List[Node]
NodesDumpResponse = List[Node]


class DeleteNodeByNameResponse(Response):
    deleted_from_nodes_count: int = Field(examples=[1])
    deleted_from_nodes_archived_count: int = Field(examples=[1])


# =======================
# Schema Responses
# =======================
SchemaGetResponse = Schema
SchemasListResponse = List[str]


# =======================
# Miscellaneous Responses
# =======================
class GenericErrorResponse(Response):
    detail: str


class GenericOperationResponse(Response):
    successful: bool = Field(examples=[True])


class HealthResponse(Response):
    class DependentServices(BaseModel):
        class DependentServiceStatus(BaseModel):
            status: Literal["UP", "DOWN"] = Field(examples=["UP"])

        permissions_api: DependentServiceStatus = Field(alias="permissions-api")

    uptime: NonNegativeInt = Field(examples=[1000])
    number_of_managed_requests: NonNegativeInt = Field(examples=[50])
    dependent_services: DependentServices


class PingResponse(Response):
    status: Literal["UP", "DOWN"]
    version: str
