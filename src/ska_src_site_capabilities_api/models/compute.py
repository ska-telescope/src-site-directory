from typing import Literal, List
from uuid import uuid4, UUID

from pydantic import BaseModel, Field

from ska_src_site_capabilities_api.models.service import LocalService


class Compute(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str = Field(examples=["service.srcdev.skao.int"])
    latitude: float = Field(examples=[51.4964])
    longitude: float = Field(examples=[-0.1224])
    hardware_capabilities: str = Field(examples=["GPU"])
    hardware_type: str = Field(examples=["bare_metal"])
    description: str = Field(examples=["some description"])
    middleware_version: str = Field(examples=["1.0.0"])
    associated_local_services: List[LocalService]


