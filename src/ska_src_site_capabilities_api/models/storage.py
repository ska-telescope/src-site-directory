"""
A module for storage class
"""
import os
import pathlib
from typing import List, Literal
from uuid import UUID, uuid4

import jsonref
from pydantic import BaseModel, Field, NonNegativeInt

# get storage area type from schema
schema_path = pathlib.Path(
    "{}.json".format(
        os.path.join(os.environ.get("SCHEMAS_RELPATH"), "storage-area")
    )
).absolute()
with open(schema_path, encoding="utf-8") as f:
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


class StorageArea(BaseModel):
    """
    Class for storage area details
    """

    id: UUID = Field(default_factory=uuid4)
    type: StorageAreaType = Field(examples=["rse"])
    rel_path: str = Field(examples=["/rel/path/to/storage/area"])
    identifier: str = Field(examples=["STFC_STORM"])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])


class StorageProtocol(BaseModel):
    """
    Class for storage protocols
    """

    prefix: str = Field(examples=["https"])
    port: NonNegativeInt = Field(examples=[443])


class Storage(BaseModel):
    """
    Class for storage details
    e.g storage id, host, base_path etc
    """

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


# need check for class duplication
class StorageAreaGrafana(BaseModel):
    """
    Class for storage area grafana
    e.g longitude, latitude etc
    """

    key: str = Field(examples=["JPSRC"])
    latitude: float = Field(examples=[35.6754])
    longitude: float = Field(examples=[139.5369])
    name: str = Field(examples=["JPSRC"])


class StorageGrafana(BaseModel):
    """
    Class for storage grafana
    """

    key: str = Field(examples=["JPSRC_STORM"])
    latitude: float = Field(examples=[35.6754])
    longitude: float = Field(examples=[139.5369])
    name: str = Field(examples=["JPSRC_STORM"])


class StorageAreaTopojsonObjectSiteGeometry(BaseModel):
    """
    A class for storage area site object
    """

    type: str = Field(examples=["Point"])
    coordinates: List[float]


class StorageAreaTopojsonObjectSite(BaseModel):
    """
    A class for storage area geometry objects
    """

    type: str = Field(examples=["GeometryCollection"])
    geometries: List[StorageAreaTopojsonObjectSiteGeometry]


class StorageAreaTopojsonObject(BaseModel):
    """
    A class for storage area sites
    """

    sites: StorageAreaTopojsonObjectSite


class StorageAreaTopojson(BaseModel):
    """
    A class for storage area json objects
    """

    type: str = Field(examples=["Topology"])
    objects: StorageAreaTopojsonObject


class StorageTopojsonObjectSiteGeometry(BaseModel):
    """
    A class for storage geometry objects
    """

    type: str = Field(examples=["Point"])
    coordinates: List[float]


class StorageTopojsonObjectSite(BaseModel):
    """
    A class for storage site objects
    """

    type: str = Field(examples=["GeometryCollection"])
    geometries: List[StorageTopojsonObjectSiteGeometry]


class StorageTopojsonObject(BaseModel):
    """
    A class for storage json object
    """

    sites: StorageTopojsonObjectSite


class StorageTopojson(BaseModel):
    """
    A class for storage json
    """

    type: str = Field(examples=["Topology"])
    objects: StorageTopojsonObject
