from typing import Dict, List, Literal, Union

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.service import Service
from ska_src_site_capabilities_api.models.schema import Schema
from ska_src_site_capabilities_api.models.site import Site
from ska_src_site_capabilities_api.models.storage import Storage, StorageGrafana, StorageTopojson


class Response(BaseModel):
    pass


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


SchemasResponse = List[str]


SchemaGetResponse = Schema


ServiceGetResponse = Service


class ServicesResponse(BaseModel):
    site_name: str = Field(examples=["JPSRC"])
    services: List[Service]


SitesResponse = List[str]


SiteGetVersionResponse = Site


SiteGetResponse = List[Site]


StorageGetResponse = Storage


class StoragesResponse(BaseModel):
    site_name: str = Field(examples=["JPSRC"])
    storages: List[Storage]


StoragesGrafanaResponse = List[StorageGrafana]


StoragesTopojsonResponse = List[StorageTopojson]




