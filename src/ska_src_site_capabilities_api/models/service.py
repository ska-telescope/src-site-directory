from typing import Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, NonNegativeInt


CoreServiceType = Literal[
    "Rucio Server",
    "Storage Inventory (Global)"
]

ProcessingServiceType = Literal[
    "JupyterHub",
    "BinderHub",
    "Dask",
    "ESAP"
]

StorageServiceType = Literal[
    "Rucio Storage Element (RSE)",
    "Data Ingest Area",
    "Storage Inventory (Local)",
    "SODA (sync)",
    "SODA (async)"
]


class Service(BaseModel):
    version: str = Field(examples=["1.0.0"])
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    port: NonNegativeInt = Field(examples=[443])
    path: str = Field(examples=["/path/to/service"])
    identifier: str = Field(examples=["SKAOSRC"])
    id: UUID = Field(default_factory=uuid4)
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])


class CoreService(Service):
    type: CoreServiceType = Field(examples=["Rucio Server"])


class ProcessingService(Service):
    type: ProcessingServiceType = Field(examples=["Dask"])
    associated_processing_id: UUID = Field(default_factory=uuid4)


class StorageService(Service):
    type: StorageServiceType = Field(examples=["Data Ingest Area"])
    associated_storage_id: UUID = Field(default_factory=uuid4)

