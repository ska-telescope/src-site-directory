"""A module to represent different services classes"""
import os
import pathlib
from typing import Literal
from uuid import UUID, uuid4

import jsonref
from pydantic import BaseModel, Field, NonNegativeInt

# get local services from schema
schema_path = pathlib.Path(
    "{}.json".format(
        os.path.join(os.environ.get("SCHEMAS_RELPATH"), "local-service")
    )
).absolute()
with open(schema_path, encoding="utf-8") as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
local_services = (
    dereferenced_schema.get("properties", {}).get("type", {}).get("enum", [])
)

LocalServiceType = Literal[tuple(local_services)]

# get global services from schema
schema_path = pathlib.Path(
    "{}.json".format(
        os.path.join(os.environ.get("SCHEMAS_RELPATH"), "global-service")
    )
).absolute()
with open(schema_path, encoding="utf-8") as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
global_services = (
    dereferenced_schema.get("properties", {}).get("type", {}).get("enum", [])
)

GlobalServiceType = Literal[tuple(global_services)]


class Service(BaseModel):
    """
    A service base class
    """

    id: UUID = Field(default_factory=uuid4)
    version: str = Field(examples=["1.0.0"])
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    port: NonNegativeInt = Field(examples=[443])
    path: str = Field(examples=["/path/to/service"])
    is_mandatory: bool = Field(examples=[True, False])
    is_proxied: bool = Field(examples=[True, False])
    identifier: str = Field(examples=["SKAOSRC"])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])


class LocalService(Service):
    """
    A class for local service
    """

    type: LocalServiceType = Field(examples=["dask"])
    associated_compute_id: UUID = Field(default_factory=uuid4)
    associated_storage_area_id: UUID = Field(default_factory=uuid4)


class GlobalService(Service):
    """
    A class for global service
    """

    type: GlobalServiceType = Field(examples=["rucio"])
