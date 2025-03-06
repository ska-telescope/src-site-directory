from typing import List, Literal, Union

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.compute import Compute
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


class ListResponse(Response):
    site_name: str = Field(examples=["SKAOSRC", "CNSRC", "KRSRC", "SPSRC", "JPSRC"])


ComputeGetResponse = Compute


class ComputeListResponse(ListResponse):
    compute: List[Compute]


LocalServiceGetResponse = LocalService

GlobalServiceGetResponse = GlobalService


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


SchemasListResponse = List[str]

SchemaGetResponse = Schema


class ServicesResponse(Response):
    services: List[Union[GlobalService, LocalService]]


class ServicesTypesResponse(Response):
    global_: List[GlobalServiceType] = Field(..., alias="global")
    local: List[LocalServiceType]


ServicesTypesLocalResponse = List[LocalServiceType]

ServicesTypesGlobalResponse = List[GlobalServiceType]

SiteGetVersionResponse = Site

SitesGetResponse = List[Site]

SitesDumpResponse = List[Site]

SitesListResponse = List[str]

StorageAreaGetResponse = StorageArea


class StorageAreasListResponse(ListResponse):
    storage_areas: List[StorageArea]


StorageAreasGrafanaResponse = List[StorageAreaGrafana]

StorageAreasTopojsonResponse = List[StorageAreaTopojson]

StorageAreasTypesResponse = List[str]

StorageGetResponse = Storage


class StoragesListResponse(ListResponse):
    storages: List[Storage]


StoragesGrafanaResponse = List[StorageGrafana]

StoragesTopojsonResponse = List[StorageTopojson]
