from typing import List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.compute import Compute
from ska_src_site_capabilities_api.models.node import Node
from ska_src_site_capabilities_api.models.schema import Schema
from ska_src_site_capabilities_api.models.service import (
    GlobalService,
    GlobalServiceType,
    LocalService,
    LocalServiceType,
)
from ska_src_site_capabilities_api.models.site import Site
from ska_src_site_capabilities_api.models.storage import (
    Storage,
    StorageArea,
    StorageAreaGrafana,
    StorageAreaTopojson,
    StorageGrafana,
    StorageTopojson,
)


class Response(BaseModel):
    pass


class ComputeWithParents(Compute):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


ComputeGetResponse = ComputeWithParents

ComputeListResponse = List[ComputeWithParents]


class LocalServiceWithParents(LocalService):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_compute_id: UUID = Field(default_factory=uuid4)


LocalServiceGetResponse = LocalServiceWithParents


class GlobalServiceWithParents(GlobalService):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_compute_id: UUID = Field(default_factory=uuid4)


GlobalServiceGetResponse = GlobalServiceWithParents


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


NodesDumpResponse = List[Node]

NodesGetResponse = Node

NodesListResponse = List[Node]


class PingResponse(Response):
    status: Literal["UP", "DOWN"]
    version: str


SchemasListResponse = List[str]

SchemaGetResponse = Schema


ServicesListResponse = List[Union[GlobalServiceWithParents, LocalServiceWithParents]]


class ServicesTypesResponse(Response):
    global_: List[GlobalServiceType] = Field(..., alias="global")
    local: List[LocalServiceType]


ServicesTypesLocalResponse = List[LocalServiceType]

ServicesTypesGlobalResponse = List[GlobalServiceType]


class SiteWithParents(Site):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])



SiteGetResponse = SiteWithParents

SitesListResponse = List[SiteWithParents]


class StorageAreaWithParents(StorageArea):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_storage_id: UUID = Field(default_factory=uuid4)


StorageAreaGetResponse = StorageAreaWithParents

StorageAreasListResponse = List[StorageAreaWithParents]

StorageAreasGrafanaResponse = List[StorageAreaGrafana]

StorageAreasTopojsonResponse = List[StorageAreaTopojson]

StorageAreasTypesResponse = List[str]


class StorageWithParents(Storage):
    parent_node_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])
    parent_site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


StorageGetResponse = StorageWithParents

StoragesListResponse = List[StorageWithParents]

StoragesGrafanaResponse = List[StorageGrafana]

StoragesTopojsonResponse = List[StorageTopojson]
