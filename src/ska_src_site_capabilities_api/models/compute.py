import os
import pathlib
from typing import List, Literal
from uuid import UUID, uuid4

import jsonref
from pydantic import BaseModel, Field

from ska_src_site_capabilities_api.models.service import GlobalService, LocalService

# get hardware capabilities and types from schema
schema_path = pathlib.Path("{}.json".format(os.path.join(os.environ.get("SCHEMAS_RELPATH"), "compute"))).absolute()
with open(schema_path) as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
hardware_capabilities = dereferenced_schema.get("properties", {}).get("hardware_capabilities", {}).get("items", {}).get("enum", [])
hardware_type = dereferenced_schema.get("properties", {}).get("hardware_type", {}).get("enum", [])

HardwareCapabilities = Literal[tuple(hardware_capabilities)]
HardwareType = Literal[tuple(hardware_type)]


class Downtime(BaseModel):
    date_range: str = Field(examples=["2025-03-04T00:00:00.000Z to 2025-03-30T00:00:00.000Z"])
    type: Literal["Planned", "Unplanned"]
    reason: str = Field(examples=["Network issues."])
    id: UUID = Field(default_factory=uuid4)


class Compute(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(examples=["SKAOSRC"])
    url: str = Field(examples=["service.srcdev.skao.int"])
    compute_units: float = Field(examples=[10])
    hardware_capabilities: HardwareCapabilities = Field(examples=[*hardware_capabilities])
    hardware_type: HardwareType = Field(examples=[*hardware_type])
    description: str = Field(examples=["some description"])
    middleware_version: str = Field(examples=["1.0.0"])
    associated_global_services: List[GlobalService]
    associated_local_services: List[LocalService]
    downtime: List[Downtime]
    is_force_disabled: bool = Field(examples=[True, False])
