import os
import pathlib
from typing import List, Literal
from uuid import UUID, uuid4

import jsonref
from pydantic import BaseModel, Field

# get storage area type from schema
schema_path = pathlib.Path(
    "{}.json".format(os.path.join(os.environ.get("SCHEMAS_RELPATH"), "storage-area"))
).absolute()
with open(schema_path) as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
hardware_capabilities = (
    dereferenced_schema.get("properties", {})
    .get("hardware_capabilities", {})
    .get("items", {})
    .get("enum", [])
)
storage_area_types = (
    dereferenced_schema.get("properties", {}).get("type", {}).get("enum", [])
)

StorageAreaType = Literal[tuple(storage_area_types)]


class Downtime(BaseModel):
    date_range: str = Field(
        examples=["2025-03-04T00:00:00.000Z to 2025-03-30T00:00:00.000Z"]
    )
    type: Literal["Planned", "Unplanned"]
    reason: str = Field(examples=["Network issues."])
    id: UUID = Field(default_factory=uuid4)


class StorageArea(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: StorageAreaType = Field(examples=["rse"])
    relative_path: str = Field(examples=["/rel/path/to/storage/area"])
    name: str = Field(examples=["STFC_STORM"])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])
    tier: int = Field(examples=[0, 1])
    downtime: List[Downtime]
    is_force_disabled: bool = Field(examples=[True, False])


class StorageProtocol(BaseModel):
    prefix: str = Field(examples=["https"])
    port: int = Field(ge=0, examples=[443])


class Storage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(examples=["SKAOSRC"])
    host: str = Field(examples=["storm.srcdev.skao.int"])
    base_path: str = Field(examples=["/path/to/storage"])
    srm: str = Field(examples=["srm"])
    device_type: str = Field(examples=["hdd"])
    size_in_terabytes: float = Field(examples=[10])
    supported_protocols: List[StorageProtocol]
    areas: List[StorageArea]
    downtime: List[Downtime]
    is_force_disabled: bool = Field(examples=[True, False])


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
