from typing import List, Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, NonNegativeInt


StorageAreaType = Literal[
    "rse",
    "ingest"
]


class StorageArea(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: StorageAreaType = Field(examples=["Rucio Storage Element (RSE)"])
    rel_path: str = Field(examples=["/rel/path/to/storage/area"])
    identifier: str = Field(examples=["STFC_STORM"])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])


class StorageProtocol(BaseModel):
    prefix: str = Field(examples=["https"])
    port: NonNegativeInt = Field(examples=[443])


class Storage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    host: str = Field(examples=["storm.srcdev.skao.int"])
    base_path: str = Field(examples=["/path/to/storage"])
    latitude: float = Field(examples=[51.4964])
    longitude: float = Field(examples=[-0.1224])
    srm: str = Field(examples=["srm"])
    device_type: str = Field(examples=["hdd"])
    size_in_terabytes: float = Field(examples=[10])
    identifier: str = Field(examples=["SKAOSRC"])
    supported_protocols: List[StorageProtocol]
    areas: List[StorageArea]


class StorageAreaGrafana(BaseModel):
    key: str = Field(examples=["JPSRC"])
    latitude: float = Field(examples=[35.6754])
    longitude: float = Field(examples=[139.5369])
    name: str = Field(examples=["JPSRC"])


class StorageGrafana(BaseModel):
    key: str = Field(examples=["JPSRC_STORM"])
    latitude: float = Field(examples=[35.6754])
    longitude: float = Field(examples=[139.5369])
    name: str = Field(examples=["JPSRC_STORM"])


class StorageAreaTopojsonObjectSiteGeometry(BaseModel):
    type: str = Field(examples=["Point"])
    coordinates: List[float]


class StorageAreaTopojsonObjectSite(BaseModel):
    type: str = Field(examples=["GeometryCollection"])
    geometries: List[StorageAreaTopojsonObjectSiteGeometry]


class StorageAreaTopojsonObject(BaseModel):
    sites: StorageAreaTopojsonObjectSite


class StorageAreaTopojson(BaseModel):
    type: str = Field(examples=["Topology"])
    objects: StorageAreaTopojsonObject


class StorageTopojsonObjectSiteGeometry(BaseModel):
    type: str = Field(examples=["Point"])
    coordinates: List[float]


class StorageTopojsonObjectSite(BaseModel):
    type: str = Field(examples=["GeometryCollection"])
    geometries: List[StorageTopojsonObjectSiteGeometry]


class StorageTopojsonObject(BaseModel):
    sites: StorageTopojsonObjectSite


class StorageTopojson(BaseModel):
    type: str = Field(examples=["Topology"])
    objects: StorageTopojsonObject