from typing import Dict, List, Literal, Union

from pydantic import BaseModel, Field, NonNegativeInt


from ska_src_site_capabilities_api.models.service import Service
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
        permissions_api: DependentServiceStatus
    uptime: NonNegativeInt = Field(examples=[1000])
    number_of_managed_requests: NonNegativeInt = Field(examples=[50])
    dependent_services: DependentServices


class PingResponse(Response):
    status: Literal["UP", "DOWN"]
    version: str


SchemaResponse = List[str]


class SchemaGetResponse(BaseModel):
    version: NonNegativeInt = Field(examples=[1])
    type: str = Field(examples=["object"])
    description: str = Field(examples=["Site definition schema"])
    properties: Dict[str, Union[str, Dict]]


class ServicesResponse(BaseModel):
    site_name: str = Field(examples=["JPSRC"])
    services: List[Service]


class StoragesResponse(BaseModel):
    site_name: str = Field(examples=["JPSRC"])
    services: List[Storage]


StoragesGrafanaResponse = List[StorageGrafana]


StoragesTopojsonResponse = List[StorageTopojson]


SitesResponse = List[str]


class SiteGetVersionResponse(BaseModel):
    _id: str = Field(examples=["651d7968ebc02f9f2d66b3df"])
    name: str = Field(examples=["SKAOSRC"])
    comments: str = Field(examples=["Some version comments"])
    description: str = Field(examples=["Some description"])
    country: str = Field(examples=["GB"])
    primary_contact_email: str = Field(Examples=["someone1@email.com"])
    secondary_contact_email: str = Field(Examples=["someone2@email.com"])
    storages: List[Storage]
    services: List[Service]
    schema_: SchemaGetResponse = Field(alias="schema")
    created_at: str = Field(examples=["2023-09-14T13:43:09.239513"])
    created_by_username: str = Field(examples=["username"])
    version: NonNegativeInt = Field(examples=[1])


SiteGetResponse = List[SiteGetVersionResponse]


