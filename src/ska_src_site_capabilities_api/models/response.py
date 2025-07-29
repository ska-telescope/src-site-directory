from typing import Dict, List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, NonNegativeInt

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


class PrometheusServiceLabels(BaseModel):
    scope: str = Field(examples=["local", "global"])
    parent_node_name: str = Field(examples=["SKAOSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC"])
    parent_compute_id: str = Field(examples=["db1d3ee3-74e4-48aa-afaf-8d7709a2f57c"])
    id: str = Field(examples=["7b20faca-b4d3-4d1f-8349-4dc38dcc8a1f"])
    type: str = Field(examples=["rucio"])
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    path: str = Field(examples=["/path/to/service"])
    model_config = ConfigDict(extra="allow")


class PrometheusServiceTarget(BaseModel):
    targets: List[HttpUrl]
    labels: PrometheusServiceLabels


ServicesPrometheusResponse = PrometheusServiceTarget

ServicesListResponseGeneric = List[Union[GlobalServiceWithParentsAndType, LocalServiceWithParentsAndType]]
ServicesListResponsePrometheus = List[ServicesPrometheusResponse]

ServicesListResponse = Union[ServicesListResponseGeneric, ServicesListResponsePrometheus]


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
