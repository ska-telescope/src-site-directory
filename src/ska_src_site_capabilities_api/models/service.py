from typing import Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, NonNegativeInt

ComputeServiceType = Literal[
    "jupyterhub",
    "binderhub",
    "dask",
    "ingest",
    "soda_sync",
    "soda_async",
    "gatekeeper",
    "monitoring",
    "perfsonar",
    "canfar",
    "orchestrator",
    "carta"
]

CoreServiceType = Literal[
    "rucio",
    "iam"
]


class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    version: str = Field(examples=["1.0.0"])
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    port: NonNegativeInt = Field(examples=[443])
    path: str = Field(examples=["/path/to/service"])
    is_proxy: bool = Field(examples=[True, False])
    identifier: str = Field(examples=["SKAOSRC"])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])


class ComputeService(Service):
    type: ComputeServiceType = Field(examples=["dask"])
    associated_compute_id: UUID = Field(default_factory=uuid4)
    associated_storage_area_id: UUID = Field(default_factory=uuid4)


class CoreService(Service):
    type: CoreServiceType = Field(examples=["rucio"])
