import os
import pathlib
from typing import Literal, List
from uuid import uuid4, UUID

import jsonref

from pydantic import BaseModel, Field

from ska_src_site_capabilities_api.models.service import LocalService

# get hardware capabilities and types from schema
schema_path = pathlib.Path(
    "{}.json".format(os.path.join(os.environ.get('SCHEMAS_RELPATH'), "compute"))).absolute()
with open(schema_path) as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
hardware_capabilities = dereferenced_schema.get('properties', {}).get('hardware_capabilities', {}).get(
    'items', {}).get('enum', [])
hardware_type = dereferenced_schema.get('properties', {}).get('hardware_type', {}).get(
    'items', {}).get('enum', [])

HardwareCapabilities = Literal[tuple(hardware_capabilities)]
HardwareType = Literal[tuple(hardware_type)]

class Compute(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str = Field(examples=["service.srcdev.skao.int"])
    latitude: float = Field(examples=[51.4964])
    longitude: float = Field(examples=[-0.1224])
    hardware_capabilities: HardwareCapabilities = Field(examples=[*hardware_capabilities])
    hardware_type: HardwareType = Field(examples=[*hardware_type])
    description: str = Field(examples=["some description"])
    middleware_version: str = Field(examples=["1.0.0"])
    associated_local_services: List[LocalService]


